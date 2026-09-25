from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ('cv_builder', '0002_cv_custom_primary_color_cv_custom_secondary_color_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cv',
            name='show_photo',
            field=models.BooleanField(default=True, verbose_name=_('Show photo on CV')),
        ),
    ]
