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

class Job:
    def __init__(self, dashboard_id, owner):
        self.dashboard_id = dashboard_id
        self.title = self.models.Dashboard.objects.filter(id = dashboard_id)[0].title
        self.owner = owner

    def run(self):
        """
        does all the things and send the emails too!
        """
        self.email_list = self.get_email_list()
        self.run_queries()
        self.generate_images()
        self.send_mail()
        self.delete_images()

    def get_email_list(self):
        """
        Get list for a scheduele
        """
        email_list = models.EmailUser.objects.filter(dashboard = self.dashboard_id)
        return [i.user.email for i in email_list]

    def run_queries(self):
        """
        runs the dashboards queries and returns results to self.result_data
        """
        self.return_dict = {}
        for query in models.DashboardQuery.objects.filter(dashboard_id = self.dashboard_id):
            DM = website.query.DataManager(query.id)
            DM.prepareQuery()
            data = DM.runQuery()
            table = DM.returnHTMLTable()
            self.return_dict[query.id] = {'data': data, table' : table, 'title': query.title, 'description': query.description}

    def generate_image(self, data):
        """
        does some subprocess magic on the js files to create images in the tmp folder
        """
        # Transform data into json file using Phantom JS
        current_path = os.getcwd()
        file_output = uuid.uuid1()
        cli = """phantomjs %s/../website/static/js/phantom_make_chart.js '%s' %s.json""" % (current_path, data, file_output)
        subprocess.call([cli], shell = True)
        # Transform JSON file into image using CLI and Phantom JS
        output_image = '//tmp/%s.png' % (file_output)
        cli = """phantomjs %s/../website/static/highcharts-convert.js -infile %s.js -outfile %s -scale 2.5 -width 400""" % (current_path, file_output, output_image)
        subprocess.call([cli], shell = True)
        return output_image

    def generate_images(self):
        """
        operates on self.result_data and returns a dict of {qry_id: img_location}
        """
        for k, v in self.return_dict.iteritems():
            self.return_dict[k]['img'] = generate_image(v.data)

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
        to_mail = [self.email_list_str]
        
        context = [v for k,v in self.return_data.iteritems()]
        html_content = render_to_string(os.path.join('email_report.html'), context)
        text_content = render_to_string(os.path.join('cron.txt'), context)

        msg = EmailMultiAlternatives(subject, text_content,
                                     sender, [to_mail])

        msg.attach_alternative(html_content, "text/html")

        msg.mixed_subtype = 'related'

        for k,f in self.return_dict.iteritems():
            f = f['img']
            fp = open(os.path.join(os.path.dirname(__file__), f), 'rb')
            msg_img = MIMEImage(fp.read())
            fp.close()
            msg_img.add_header('Content-ID', '<{}>'.format(f))
            msg.attach(msg_img)
        msg.send()
        return msg

    def failure(self):
        """
        send a stack trace to the owner of the mailing list
        """
        pass

def scheduled_job(frequency):
    """
    Run this every n hours and send out each email for that particular frequency
    """
    jobs = models.Job.objects.filter(type = frequency) # Get current jos
    for job in jobs:  # Iterate through all jobs
        # 1 job = 1 dashboard
        j = Job(job.dashboard_id, job.owner)
        j.run()
        job.save()


"""def template_email():
    # You probably want all the following code in a function or method.
    # You also need to set subject, sender and to_mail yourself.
    context = {'query_list':
                [
                    {'id':7,'title':'test1','description':'test2','table':'<table></table>','img':'/home/ubuntu/phantom_test/example.png'},
                    {'id':4,'title':'test3','description':'test4','table':'<table></table>','img':'/home/ubuntu/phantom_test/example.png'}
                ]
            }
    html_content = render_to_string(os.path.join('email_report.html'), context)
    text_content = render_to_string(os.path.join('cron.txt'), context)
    subject ='does this work'
    sender = 'matthew.feldman@gmail.com'
    to_mail = 'matthew.feldman@gmail.com'

    msg = EmailMultiAlternatives(subject, text_content,
                                 sender, [to_mail])

    msg.attach_alternative(html_content, "text/html")

    msg.mixed_subtype = 'related'

    for f in ['/home/ubuntu/phantom_test/example.png']:
        fp = open(os.path.join(os.path.dirname(__file__), f), 'rb')
        msg_img = MIMEImage(fp.read())
        fp.close()
        msg_img.add_header('Content-ID', '<{}>'.format(f))
        msg.attach(msg_img)
    msg.send()
    return msg        """