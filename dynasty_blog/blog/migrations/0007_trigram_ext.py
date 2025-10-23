from django.db import migrations


def enable_trigram(apps, schema_editor):
    # Only run on PostgreSQL
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def disable_trigram(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("DROP EXTENSION IF EXISTS pg_trgm;")


class Migration(migrations.Migration):
    # Chain to your last migration to avoid multiple-leaf conflict
    dependencies = [
        ("blog", "0006_alter_comment_options_alter_post_options"),
    ]

    operations = [
        migrations.RunPython(enable_trigram, reverse_code=disable_trigram),
    ]
