from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):
    dependencies = [('accounts', '0005_rename_avatar_images')]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='terms_accepted_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name=_('Terms Accepted At')),
        ),
    ]
