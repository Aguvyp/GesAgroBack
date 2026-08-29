from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_campo_polygon_geojson'),
    ]

    operations = [
        migrations.CreateModel(
            name='TareaRecordatorio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.CharField(max_length=500)),
                ('urgencia', models.CharField(choices=[('high', 'Alta'), ('medium', 'Media'), ('low', 'Baja')], default='medium', max_length=20)),
                ('completada', models.BooleanField(default=False)),
                ('usuario_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'tareas_recordatorio',
                'ordering': ['-created_at'],
            },
        ),
    ]
