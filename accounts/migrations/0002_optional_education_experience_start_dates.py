from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='education',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name=_('Start Date')),
        ),
        migrations.AlterField(
            model_name='experience',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name=_('Start Date')),
        ),
    ]
