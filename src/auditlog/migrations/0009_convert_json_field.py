from django.db import migrations
from django.contrib.auth.management import create_permissions
from django.db.models import F

def convert_json_field(apps, schema_editor):
    LogEntry = apps.get_model("auditlog", "LogEntry")
    LogEntry.objects.all().update(additional_data_new=F("additional_data"))


class Migration(migrations.Migration):

    dependencies = [("auditlog", "0008_logentry_additional_data_new")]

    operations = [
        migrations.RunPython(
            convert_json_field,
            reverse_code=migrations.RunPython.noop,
        )
    ]
