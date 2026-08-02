from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations


def add_permission(apps, schema_editor):
    for app_config in global_apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    try:
        perm = Permission.objects.get(content_type__app_label='vehicles', codename='manage_trash')
    except Permission.DoesNotExist:
        return
    admin_group = Group.objects.filter(name='Admin').first()
    if admin_group:
        admin_group.permissions.add(perm)


def remove_permission(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    perm = Permission.objects.filter(content_type__app_label='vehicles', codename='manage_trash').first()
    admin_group = Group.objects.filter(name='Admin').first()
    if perm and admin_group:
        admin_group.permissions.remove(perm)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_assign_group_permissions'),
        ('vehicles', '0007_alter_vehicleentry_options'),
    ]

    operations = [
        migrations.RunPython(add_permission, remove_permission),
    ]
