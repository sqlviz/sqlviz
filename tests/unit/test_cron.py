from django.test import TransactionTestCase
from django.core import mail

from cron import cron

from ..factories import (QueryFactory, DashboardFactory, UserFactory,
                         DashboardQueryFactory, JobFactory, EmailUserFactory)


class EmailTest(TransactionTestCase):
    number_users_create = 5

    def test_send_email(self):
        # Send message.
        mail.send_mail(
            'Subject here', 'Here is the message.',
            'from@example.com', ['to@example.com'],
            fail_silently=False,
        )

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Subject here')

    def test_cron_email(self):
        self.mock_dashboard_cron()
        job_instance = cron.Job(self.job.id)
        return_data = job_instance.run()[0][self.query.id]
        del return_data['table']
        valid_data = {'description': u'description',
                      'id': self.query.id,
                      'img': None,
                      'title': u'title'}

        self.assertEqual(return_data, valid_data)
        self.assertEqual(mail.outbox[0].subject, self.dashboard.title)

    def mock_dashboard_cron(self):
        self.user = UserFactory()
        self.query = QueryFactory(
            query_text="""
                select
                    first_name
                from
                    auth_user
                limit
                    1
            """,
            owner=self.user,
        )
        self.dashboard = DashboardFactory(
            owner=self.user,
        )
        self.dashboard_query = DashboardQueryFactory(
            query=self.query,
            dashboard=self.dashboard,
        )
        self.job = JobFactory(
            owner=self.user,
            dashboard=self.dashboard,
        )
        EmailUserFactory(job=self.job, user=self.user)
