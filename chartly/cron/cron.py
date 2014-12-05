import models
import website.models
import website.query
from django.core.mail import send_mail
import json
import uuid
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.MIMEImage import MIMEImage
import subprocess
import sys

class Job:
    def __init__(self, id, dashboard_id, owner):
        self.id = id
        self.dashboard_id = dashboard_id
        self.title = website.models.Dashboard.objects.filter(id = dashboard_id)[0].title
        self.owner = owner

    def run(self):
        """
        does all the things and send the emails too!
        """
        self.get_email_list()
        self.run_queries()
        self.generate_images()
        self.send_mail()
        self.delete_images()

    def get_email_list(self):
        """
        Get list for a scheduele
        """
        email_list = models.EmailUser.objects.filter(job = self.id)
        self.email_list = [i.user.email for i in email_list]

    def run_queries(self):
        """
        runs the dashboards queries and returns results to self.result_data
        """
        self.return_dict = {}
        for dq in website.models.DashboardQuery.objects.filter(dashboard_id = self.dashboard_id):
            query = website.models.Query.objects.filter(id = dq.query_id)[0]
            DM = website.query.DataManager(query.id)
            DM.prepareQuery()
            data = DM.runQuery()
            table = DM.returnHTMLTable()
            #TODO fix this it is ugly!
            self.return_dict[query.id] = {'id' : dq.query_id,
                    'data': 
                        {'columns' : data.pop(0),
                        'data' : data,
                        'chart_type':query.chart_type,
                        'graph_extra': query.graph_extra,
                        'yAxis_log' : query.log_scale_y,
                        'stacked' : query.stacked,
                        'xAxis' : '', 'yAxis' : '',
                        'graph_extra' : query.graph_extra,
                        'title' : query.title
                    },
                    'table' : table, 'title': query.title,
                    'description': query.description}

    def generate_image(self, data):
        """
        does some subprocess magic on the js files to create images in the tmp folder
        """
        # Transform data into json file using Phantom JS


        static_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'website/static'))
        print static_path
        file_output = uuid.uuid1()
        cli = """phantomjs %s/js/phantom_make_chart.js '%s' //tmp/%s.json""" % (static_path, json.dumps(data), file_output)
        print cli
        subprocess.call([cli], shell = True)
        # Transform JSON file into image using CLI and Phantom JS
        output_image = '//tmp/%s.png' % (file_output)
        cli = """phantomjs %s/Highcharts-4.0.3/exporting-server/phantomjs/highcharts-convert.js -infile //tmp/%s.json -outfile %s -scale 2.5 -width 400""" % (static_path, file_output, output_image)
        print cli
        subprocess.call([cli], shell = True)
        return output_image

    def generate_images(self):
        """
        operates on self.result_data and returns a dict of {qry_id: img_location}
        """
        for k, v in self.return_dict.iteritems():
            #print k,v
            self.return_dict[k]['img'] = self.generate_image(v['data'])

    def delete_images(self):
        """
        operates on an image location dict and deletes them
        """
        pass

    def send_mail(self):
        """
        sends a schedueled email to all participants
        """
        subject = self.title
        sender = self.owner.email
        to_mail = self.email_list
        
        context = {'query_list':[v for k,v in self.return_dict.iteritems()]}
        html_content = render_to_string(os.path.join('email_report.html'), context)
        text_content = render_to_string(os.path.join('email_report.txt'), context)

        msg = EmailMultiAlternatives(subject, text_content,
                                     sender, to_mail)

        msg.attach_alternative(html_content, "text/html")

        msg.mixed_subtype = 'related'
        #print subject, text_content, sender, to_mail
        for k,f in self.return_dict.iteritems():
            f = f['img']
            fp = open(os.path.join(os.path.dirname(__file__), f), 'rb')
            msg_img = MIMEImage(fp.read())
            fp.close()
            msg_img.add_header('Content-ID', '<{}>'.format(f))
            msg.attach(msg_img)
        msg.send()
        return msg

    def failure(self, trace_string):
        """
        send a stack trace to the owner of the mailing list
        """
        subject = 'Email Failure Chartly!'
        sender = self.owner.email
        to_mail = self.owner.email
        send_mail('JOB FAILURE : %s' % (self.id), trace_string,self.owner.email,
            [self.owner.email], fail_silently=False)

def scheduled_job(frequency):
    """
    Run this every n hours and send out each email for that particular frequency
    """
    jobs = models.Job.objects.filter(type = frequency) # Get current jos
    for job in jobs:  # Iterate through all jobs
        # 1 job = 1 dashboard
        j = Job(job.id, job.dashboard_id, job.owner)
        try:
            j.run()
            job.save()
        except Exception, e:
            print str(sys.exc_info()) + str(e)
            j.failure(str(sys.exc_info()) + str(e))