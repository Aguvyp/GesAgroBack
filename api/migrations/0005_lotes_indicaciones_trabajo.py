# Generated manually for operational work orders, lots and instructions

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_trabajopersonal_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('hectareas', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
                ('polygon_geojson', models.JSONField(blank=True, null=True)),
                ('punto_acceso_latitud', models.DecimalField(blank=True, decimal_places=8, max_digits=10, null=True)),
                ('punto_acceso_longitud', models.DecimalField(blank=True, decimal_places=8, max_digits=11, null=True)),
                ('punto_entrada_latitud', models.DecimalField(blank=True, decimal_places=8, max_digits=10, null=True)),
                ('punto_entrada_longitud', models.DecimalField(blank=True, decimal_places=8, max_digits=11, null=True)),
                ('notas_acceso', models.TextField(blank=True, null=True)),
                ('cliente_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('usuario_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('campo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lotes', to='api.campo')),
            ],
            options={
                'db_table': 'lotes',
                'indexes': [
                    models.Index(fields=['campo'], name='lotes_campo_i_d355d2_idx'),
                    models.Index(fields=['usuario_id'], name='lotes_usuario_e9a795_idx'),
                    models.Index(fields=['cliente_id'], name='lotes_cliente_5bcf48_idx'),
                ],
            },
        ),
        migrations.AddField(
            model_name='trabajo',
            name='estado_indicaciones',
            field=models.CharField(blank=True, default='Borrador', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='trabajo',
            name='indicaciones',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='trabajo',
            name='indicaciones_enviadas_a',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='trabajo',
            name='indicaciones_enviadas_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='trabajo',
            name='lote',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trabajos', to='api.lote'),
        ),
    ]
