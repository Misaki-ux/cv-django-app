from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):
    dependencies = [('accounts', '0002_optional_education_experience_start_dates')]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='avatar',
            field=models.CharField(blank=True, choices=[(f'avatars/avatar-{index:02d}.svg', _('Avatar %(number)s') % {'number': index}) for index in range(1, 9)], max_length=40, verbose_name=_('Avatar')),
        ),
    ]
