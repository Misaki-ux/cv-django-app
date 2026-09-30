from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


AVATARS = [
    ('avatars/avatar-default.png', _('Default avatar')),
    ('avatars/avatar-boy.png', _('Boy avatar')),
    ('avatars/avatar-girl-01.png', _('Girl avatar 1')),
    ('avatars/avatar-girl-02.png', _('Girl avatar 2')),
    ('avatars/avatar-girl-03.png', _('Girl avatar 3')),
    ('avatars/avatar-hindu.png', _('Hindu avatar')),
    ('avatars/avatar-indian.png', _('Indian avatar')),
    ('avatars/avatar-man-01.png', _('Man avatar 1')),
    ('avatars/avatar-man.png', _('Man avatar')),
    ('avatars/avatar-nerd.png', _('Nerd avatar')),
    ('avatars/avatar-tax-inspector.png', _('Tax inspector avatar')),
    ('avatars/avatar-woman-01.png', _('Woman avatar 1')),
    ('avatars/avatar-woman.png', _('Woman avatar')),
    ('avatars/avatar-young-boy.png', _('Young boy avatar')),
]

RENAMES = {
    'avatars/avatar.png': 'avatars/avatar-default.png',
    'avatars/boy.png': 'avatars/avatar-boy.png',
    'avatars/girl.png': 'avatars/avatar-girl-01.png',
    'avatars/girl (1).png': 'avatars/avatar-girl-02.png',
    'avatars/girl (2).png': 'avatars/avatar-girl-03.png',
    'avatars/hindu.png': 'avatars/avatar-hindu.png',
    'avatars/indian.png': 'avatars/avatar-indian.png',
    'avatars/man (1).png': 'avatars/avatar-man-01.png',
    'avatars/man.png': 'avatars/avatar-man.png',
    'avatars/nerd.png': 'avatars/avatar-nerd.png',
    'avatars/tax-inspector.png': 'avatars/avatar-tax-inspector.png',
    'avatars/woman (1).png': 'avatars/avatar-woman-01.png',
    'avatars/woman.png': 'avatars/avatar-woman.png',
    'avatars/young-boy.png': 'avatars/avatar-young-boy.png',
}


def rename_saved_avatar_choices(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    for old, new in RENAMES.items():
        UserProfile.objects.filter(avatar=old).update(avatar=new)


class Migration(migrations.Migration):
    dependencies = [('accounts', '0004_profile_avatar_media_choices')]

    operations = [
        migrations.RunPython(rename_saved_avatar_choices, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.CharField(blank=True, choices=AVATARS, max_length=40, verbose_name=_('Avatar')),
        ),
    ]
