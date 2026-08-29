from django.db import migrations, models


def migrate_roles(apps, schema_editor):
    Usuario = apps.get_model('api', 'Usuario')
    Usuario.objects.filter(is_superuser=True).update(rol='Superadmin')
    Usuario.objects.filter(rol='Administrador', is_superuser=False).update(rol='Dueño')
    Usuario.objects.filter(rol__in=['Contable', 'Operario']).update(rol='Empleado')


class Migration(migrations.Migration):
    dependencies = [('api', '0008_tarea_recordatorio')]

    operations = [
        migrations.RunPython(migrate_roles, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.CharField(
                blank=True,
                choices=[('Superadmin', 'Superadmin'), ('Dueño', 'Dueño'), ('Empleado', 'Empleado')],
                default='Empleado',
                max_length=50,
                null=True,
            ),
        ),
    ]
