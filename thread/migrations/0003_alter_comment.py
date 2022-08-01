# Generated by Django 3.2.2 on 2022-05-20 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thread', '0002_alter_playlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='attachment',
        ),
        migrations.AddField(
            model_name='comment',
            name='attachments',
            field=models.ManyToManyField(blank=True, to='thread.Attachment'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(),
        ),
    ]
