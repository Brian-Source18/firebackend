from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_auditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='emergencyreport',
            name='resolution_notes',
            field=models.TextField(blank=True, default=''),
        ),
    ]
