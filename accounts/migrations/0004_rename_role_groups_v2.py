from django.db import migrations

RENAMES = {
    'Segurança': 'Operador de Registo',
    'Tesoureira': 'Caixa',
}


def rename_forward(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for old_name, new_name in RENAMES.items():
        Group.objects.filter(name=old_name).update(name=new_name)


def rename_backward(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for old_name, new_name in RENAMES.items():
        Group.objects.filter(name=new_name).update(name=old_name)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_rename_role_groups_pt'),
    ]

    operations = [
        migrations.RunPython(rename_forward, rename_backward),
    ]
