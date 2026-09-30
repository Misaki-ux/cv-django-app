from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('cv_builder', '0004_cv_target_job_and_cvskill_category')]

    operations = [
        migrations.AddField(
            model_name='cv',
            name='canvas_state',
            field=models.JSONField(blank=True, default=dict, verbose_name='Canvas Layout'),
        ),
    ]
