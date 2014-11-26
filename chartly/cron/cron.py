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

def scheduled_job(frequency):
    schedueles = models.Scheduele.objects.filter(type = frequency)
    for scheduele in schedueles:
        # Run Dashboard stuff
        dashboard_query_list = website.models.DashboardQuery.objects.filter(
                dashboard_id = scheduele.id).order_by('order')
        email_list = models.EmailUser.objects.filter(scheduele = schedueles)
        email_list_str = [i.user.email for i in email_list]

        response_array = []
        for q in dashboard_query_list:
            query_info = website.models.Query.objects.filter(id = q.query_id)[0]

            response_array.append("<h2> %s </h2>\n <p> %s </p>" %
                    (query_info.title, query_info.description_long))
            # TODO add a link here!
            response_array.append(DM.returnHTMLTable())

        message = '\n'.join(response_array)
        #print message
        send_mail('Schedueled Report: %s' % (scheduele.name), 'send',
            'no-reply@chartly.com', email_list_str, fail_silently=False,
            html_message = message)
        scheduele.save()

def run_query(query):
    """
    runs the query and makes a chart
    returns html to include and img path
    """
    DM = website.query.DataManager(query.id)
    DM.prepareQuery()
    response_data = DM.runQuery()
    table = DM.returnHTMLTable()
    if query.chart != None:
        output = {
            "data":
                {"columns" : response_data.pop(0), "data" : response_data},
            "time_elapsed" : time_elapsed,
            "error" : False}
        output_json = json.loads(output)
        guid_name = uuid.uuid1()
        output_file = '%s.json' % (guid_name)
        output_image = '%s.png'% (guid_name)


def template_email():
    # You probably want all the following code in a function or method.
    # You also need to set subject, sender and to_mail yourself.
    context = [{'title':'test1','description':'test2','table':'<table></table>','/home/ubuntu/phantom_test/example.png'},
            {'title':'test3','description':'test4','table':'<table></table>','/home/ubuntu/phantom_test/example.png'}]
    html_content = render_to_string('templates/cron/cron.html', context)
    text_content = render_to_string('templates/cron/cron.txt', context)
    msg = EmailMultiAlternatives(subject, text_content,
                                 sender, [to_mail])

    msg.attach_alternative(html_content, "text/html")

    msg.mixed_subtype = 'related'

    for f in ['img1.png', 'img2.png']:
        fp = open(os.path.join(os.path.dirname(__file__), f), 'rb')
        msg_img = MIMEImage(fp.read())
        fp.close()
        msg_img.add_header('Content-ID', '<{}>'.format(f))
        msg.attach(msg_img)        

""" PLAN
1) get all dashboards 
2) run all queries in all dashboards
3)  Generate HTML & images
    test this part!

4)  Put into template
5)  Mail"""