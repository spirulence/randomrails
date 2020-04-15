# Generated by Django 3.0.5 on 2020-04-14 23:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20200411_2148'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playerslot',
            name='joincode',
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('expires_at', models.DateTimeField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Game')),
            ],
        ),
    ]
