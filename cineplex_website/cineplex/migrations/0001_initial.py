# Generated by Django 4.1.2 on 2022-12-08 00:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DateToQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('filmId', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Showing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('cc_enabled', models.BooleanField(default=False)),
                ('ds_enabled', models.BooleanField(default=False)),
                ('showing_type', models.TextField()),
                ('auditorium', models.TextField()),
                ('seatsRemaining', models.IntegerField(default=0)),
                ('seatMapUrl', models.TextField()),
                ('visible', models.BooleanField(default=True)),
                ('last_row', models.TextField(null=True)),
                ('payment_url', models.TextField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cineplex.movie')),
            ],
        ),
        migrations.CreateModel(
            name='MovieAndDateIntersection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cineplex.datetoquery')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cineplex.movie')),
            ],
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_audited', models.DateTimeField()),
                ('audit_log', models.TextField()),
                ('showing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cineplex.showing')),
            ],
        ),
    ]
