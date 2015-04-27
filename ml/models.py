from django.db import models


class machine_learning_model(models.Model):
    title = models.CharField(unique=True, max_length=100)
    type = models.CharField(max_length=10,
                            choices=(
                                ('logistic', 'logistic'), ('linear', 'linear'),
                                ('tree', 'tree')),
                            default='None')
    query = models.ForeignKey('website.Query')
    target_column = models.CharField(max_length=100)

    class Meta:
        unique_together = ['query', 'target_column', 'type']

    def __str__(self):
        return '%s %s %s' % (self.title, self.type, self.target_column)

    # TODO make a validation method to validate columns existance


class model_blob(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    model_id = models.ForeignKey('machine_learning_model')
    blob = models.TextField()
