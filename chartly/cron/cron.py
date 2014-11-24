import models
import website.models
import website.query
from django.core.mail import send_mail

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
            DM = website.query.DataManager(q.query_id)
            DM.prepareQuery()
            DM.runQuery()
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
