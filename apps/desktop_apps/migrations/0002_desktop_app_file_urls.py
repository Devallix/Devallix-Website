from django.db import migrations, models

INSTALLER_HELP_TEXT = (
    'Direct URL to the installer file (GitHub Releases, S3, Dropbox, etc.).'
)
ZIP_HELP_TEXT = 'Optional direct URL to a ZIP archive of the app.'


def copy_existing_file_urls(apps, schema_editor):
    """Keep any values that were already absolute URLs."""
    DesktopApplication = apps.get_model('desktop_apps', 'DesktopApplication')
    ApplicationVersion = apps.get_model('desktop_apps', 'ApplicationVersion')

    for model in (DesktopApplication, ApplicationVersion):
        for obj in model.objects.all():
            updates = {}
            installer = getattr(obj.installer_file, 'name', '') or ''
            archive = getattr(obj.zip_file, 'name', '') or ''

            if installer.lower().startswith(('http://', 'https://')):
                updates['installer_url'] = installer
            if archive.lower().startswith(('http://', 'https://')):
                updates['zip_url'] = archive

            if updates:
                model.objects.filter(pk=obj.pk).update(**updates)


class Migration(migrations.Migration):

    dependencies = [
        ('desktop_apps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='desktopapplication',
            name='installer_url',
            field=models.URLField(
                blank=True,
                help_text=INSTALLER_HELP_TEXT,
                max_length=500,
                verbose_name='installer file URL',
            ),
        ),
        migrations.AddField(
            model_name='desktopapplication',
            name='zip_url',
            field=models.URLField(
                blank=True,
                help_text=ZIP_HELP_TEXT,
                max_length=500,
                verbose_name='ZIP file URL',
            ),
        ),
        migrations.AddField(
            model_name='applicationversion',
            name='installer_url',
            field=models.URLField(
                blank=True,
                help_text=INSTALLER_HELP_TEXT,
                max_length=500,
                verbose_name='installer file URL',
            ),
        ),
        migrations.AddField(
            model_name='applicationversion',
            name='zip_url',
            field=models.URLField(
                blank=True,
                help_text=ZIP_HELP_TEXT,
                max_length=500,
                verbose_name='ZIP file URL',
            ),
        ),
        migrations.RunPython(copy_existing_file_urls, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='desktopapplication',
            name='installer_file',
        ),
        migrations.RemoveField(
            model_name='desktopapplication',
            name='zip_file',
        ),
        migrations.RemoveField(
            model_name='applicationversion',
            name='installer_file',
        ),
        migrations.RemoveField(
            model_name='applicationversion',
            name='zip_file',
        ),
    ]
