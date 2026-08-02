from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations

ADMIN_PERMS = [
    ('vehicles', 'add_vehicleentry'), ('vehicles', 'change_vehicleentry'),
    ('vehicles', 'delete_vehicleentry'), ('vehicles', 'view_vehicleentry'),
    ('vehicles', 'add_vehicletype'), ('vehicles', 'change_vehicletype'),
    ('vehicles', 'delete_vehicletype'), ('vehicles', 'view_vehicletype'),
    ('cashbox', 'add_payment'), ('cashbox', 'change_payment'),
    ('cashbox', 'delete_payment'), ('cashbox', 'view_payment'),
    ('cashbox', 'add_cashmovement'), ('cashbox', 'change_cashmovement'),
    ('cashbox', 'delete_cashmovement'), ('cashbox', 'view_cashmovement'),
    ('cashbox', 'add_cashclosure'), ('cashbox', 'change_cashclosure'),
    ('cashbox', 'delete_cashclosure'), ('cashbox', 'view_cashclosure'),
    ('cashbox', 'close_period'),
    ('services', 'add_service'), ('services', 'change_service'),
    ('services', 'delete_service'), ('services', 'view_service'),
    ('services', 'add_serviceprice'), ('services', 'change_serviceprice'),
    ('services', 'delete_serviceprice'), ('services', 'view_serviceprice'),
    ('audit', 'add_reconciliation'), ('audit', 'change_reconciliation'),
    ('audit', 'delete_reconciliation'), ('audit', 'view_reconciliation'),
    ('accounts', 'add_user'), ('accounts', 'change_user'),
    ('accounts', 'delete_user'), ('accounts', 'view_user'),
    ('accounts', 'view_admin_dashboard'),
]

OPERADOR_REGISTO_PERMS = [
    ('vehicles', 'add_vehicleentry'), ('vehicles', 'change_vehicleentry'),
    ('vehicles', 'delete_vehicleentry'), ('vehicles', 'view_vehicleentry'),
]

CAIXA_PERMS = [
    ('cashbox', 'add_payment'), ('cashbox', 'view_payment'),
    ('cashbox', 'add_cashmovement'), ('cashbox', 'view_cashmovement'),
    ('cashbox', 'add_cashclosure'),
    ('services', 'add_service'), ('services', 'view_service'),
]

GROUP_PERMS = {
    'Admin': ADMIN_PERMS,
    'Operador de Registo': OPERADOR_REGISTO_PERMS,
    'Caixa': CAIXA_PERMS,
}


def assign_permissions(apps, schema_editor):
    # Permission rows are normally created by a post_migrate signal that only
    # fires once the whole `migrate` run finishes - force it now so the
    # lookups below find the permissions even on a fresh/from-scratch install.
    for app_config in global_apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    for group_name, perms in GROUP_PERMS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        permission_ids = []
        for app_label, codename in perms:
            try:
                perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
            except Permission.DoesNotExist:
                continue
            permission_ids.append(perm.pk)
        group.permissions.set(permission_ids)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_options'),
        ('cashbox', '0005_alter_cashclosure_options'),
        ('vehicles', '0006_rename_claimed_at_vehicleentry_completed_at_and_more'),
        ('services', '0003_alter_service_price_serviceprice'),
        ('audit', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(assign_permissions, noop),
    ]
