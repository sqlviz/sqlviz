from django.db import models


class machine_learning_model(models.Model):
    name_short = models.CharField(unique=True, max_length=10)
    name_long = models.CharField(unique=True, max_length=128)
    type = models.CharField(max_length=10,
                            choices=(
                                ('logistic', 'logistic'), ('linear', 'linear'),
                                ('tree', 'tree')),
                            default='None')
    query = models.ForeignKey('website.Query')
    target_column = models.CharField(max_length=100)

    def __str__(self):
        return '%s %s %s' % (self.name_short, self.type, self.target_column)


class model_blob(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, editable=False, db_index = True)
    model_id = models.ForeignKey('machine_learning_model')
    blob = models.TextField()
