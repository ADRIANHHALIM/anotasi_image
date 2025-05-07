from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('master', '0005_jobprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='job_images/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='master.jobprofile')),
                ('status', models.CharField(choices=[
                    ('unannotated', 'Unannotated'),
                    ('in_review', 'In Review'),
                    ('in_rework', 'In Rework'),
                    ('finished', 'Finished'),
                    ('has_issues', 'Has Issues')
                ], default='unannotated', max_length=20)),
            ],
        ),
    ]