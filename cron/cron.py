import models
import website.models
import website.query
from django.core.mail import send_mail
import uuid
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.MIMEImage import MIMEImage
import logging
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from website.get_db_engine import get_db_engine


class Job:

    def __init__(self, id, job=None):
        self.id = id
        if job is None:
            job = models.Job.objects.filter(id=id).first()
        self.dashboard_id = job.dashboard_id
        self.title = website.models.Dashboard.objects.filter(
            id=self.dashboard_id
        ).first().title
        self.owner = job.owner

    def run(self):
        """
        does all the things and send the emails too!
        """
        self.get_email_list()
        query_data = self.run_queries()
        mail_msg = self.send_mail()
        self.delete_images()
        return (query_data, mail_msg)

    def get_email_list(self):
        """
        Get list for a scheduele
        """
        email_list = models.EmailUser.objects.filter(job=self.id)
        self.email_list = [i.user.email for i in email_list]

    def run_queries(self):
        """
        runs the dashboards queries and returns results to self.result_data
        """
        self.return_dict = {}
        for dq in website.models.DashboardQuery.objects.filter(
                dashboard_id=self.dashboard_id):
            lq = website.query.LoadQuery(query_id=dq.query_id, user=self.owner)
            q = lq.prepare_query()
            q.run_query()
            q.run_manipulations()
            table = q.html_table()
            if q.query_model.chart_type != 'None':
                image = q.generate_image('//tmp/%s.png' % uuid.uuid1())
            else:
                image = None
            # TODO fix this it is ugly!
            self.return_dict[dq.query_id] = {
                'id': dq.query_id,
                'table': table,
                'title': q.query_model.title,
                'description': q.query_model.description,
                'img': image}
        return self.return_dict

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

        context = {'query_list': [v for k, v in self.return_dict.iteritems()]}
        html_content = render_to_string(
            os.path.join('email/email_report.html'), context
        )
        text_content = render_to_string(
            os.path.join('email/email_report.txt'), context
        )

        msg = EmailMultiAlternatives(subject, text_content,
                                     sender, to_mail)

        msg.attach_alternative(html_content, "text/html")

        msg.mixed_subtype = 'related'
        # print subject, text_content, sender, to_mail
        for k, f in self.return_dict.iteritems():
            f = f['img']
            if f is not None:
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
        # subject = 'Email Failure SQLVIZ!'
        # sender = self.owner.email
        # to_mail = self.owner.email
        send_mail(
            'JOB FAILURE : %s' % (self.id),
            trace_string,
            self.owner.email,
            [self.owner.email],
            fail_silently=False
        )


def cache_buster(days_back=2):
    """
    When run will remove all tables that are for old cache
    """
    # Get all dead tables
    qc = website.models.QueryCache.objects.filter(
        run_time__lt=timezone.now() - relativedelta(days=days_back)
    ).order_by('run_time').all()[:100]
    for q in qc:
        if q.is_expired:
            # Drop them like they are hot!
            logging.warning('Dropping table %s' % (q.table_name))
            drop_table(q.table_name)
            q.delete()


def drop_table(table_name):
    """
    Drops given table from the scratch disk
    """
    engine = get_db_engine()
    c = engine.connect()
    query_text = """drop table %s""" % (table_name)
    c.execute(query_text)
    c.close()


def scheduled_job(frequency):
    """
    Run this every n hours and send out each email for that particular
    frequency
    """
    jobs = models.Job.objects.filter(type=frequency)  # Get current jos
    for job in jobs:  # Iterate through all jobs
        # 1 job = 1 dashboard
        j = Job(job.id, job)
        if True:  # try:
            j.run()
            job.save()
        # except Exception, e:
        #    print str(sys.exc_info()) + str(e)
        #    j.failure(str(sys.exc_info()) + str(e))
