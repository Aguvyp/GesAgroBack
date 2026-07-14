from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_usuario_groups_usuario_is_staff_usuario_is_superuser_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='campo',
            name='polygon_geojson',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
