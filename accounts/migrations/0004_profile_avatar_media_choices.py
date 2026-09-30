from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


AVATARS = [
    ('avatars/avatar.png', _('Avatar 1')),
    ('avatars/boy.png', _('Avatar 2')),
    ('avatars/girl.png', _('Avatar 3')),
    ('avatars/girl (1).png', _('Avatar 4')),
    ('avatars/girl (2).png', _('Avatar 5')),
    ('avatars/man.png', _('Avatar 6')),
    ('avatars/woman.png', _('Avatar 7')),
    ('avatars/indian.png', _('Avatar 8')),
]


def move_existing_avatar_selections(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    for profile in UserProfile.objects.all().iterator():
        value = profile.avatar or ''
        if value.startswith('avatars/avatar-') and value.endswith('.svg'):
            try:
                index = int(value.removeprefix('avatars/avatar-').removesuffix('.svg'))
            except ValueError:
                continue
            if 1 <= index <= len(AVATARS):
                profile.avatar = AVATARS[index - 1][0]
                profile.save(update_fields=['avatar'])


class Migration(migrations.Migration):
    dependencies = [('accounts', '0003_userprofile_avatar')]

    operations = [
        migrations.RunPython(move_existing_avatar_selections, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.CharField(blank=True, choices=AVATARS, max_length=40, verbose_name=_('Avatar')),
        ),
    ]
