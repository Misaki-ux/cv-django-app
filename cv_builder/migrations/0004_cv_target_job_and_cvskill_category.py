from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ('cv_builder', '0003_cv_show_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='cv',
            name='target_job_title',
            field=models.CharField(blank=True, max_length=200, verbose_name=_('Target Job Title')),
        ),
        migrations.AddField(
            model_name='cvskill',
            name='category',
            field=models.CharField(
                choices=[('hard', _('Savoir-faire / Hard skill')), ('soft', _('Savoir-être / Soft skill'))],
                default='hard',
                max_length=10,
                verbose_name=_('Skill Category'),
            ),
        ),
    ]
