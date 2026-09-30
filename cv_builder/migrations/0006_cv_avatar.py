from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):
    dependencies = [('cv_builder', '0005_cv_canvas_state')]

    operations = [
        migrations.AddField(
            model_name='cv',
            name='avatar',
            field=models.CharField(blank=True, max_length=40, verbose_name=_('CV Avatar')),
        ),
    ]
