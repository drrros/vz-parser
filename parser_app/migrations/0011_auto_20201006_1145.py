# Generated by Django 3.0.7 on 2020-10-06 07:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('parser_app', '0010_auto_20200707_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageRecipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(verbose_name='Telegram ID')),
                ('name', models.CharField(max_length=200, verbose_name='Имя получателя сообщения')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='order_comments',
            field=models.CharField(blank=True, max_length=20000, null=True, verbose_name='Комментарии к заявке'),
        ),
        migrations.AddField(
            model_name='order',
            name='prev_order_comments',
            field=models.CharField(blank=True, max_length=20000, null=True,
                                   verbose_name='Предыдущие комментарии к заявке'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='contract',
            name='price',
            field=models.FloatField(blank=True, null=True, verbose_name='Сумма контракта'),
        ),
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
