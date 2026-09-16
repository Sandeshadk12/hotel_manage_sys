from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resultapp', '0004_booking_checkin_checkout_time'),
    ]

    operations = [
        # Add 'Cleaning' to Room status choices (no DB change needed, just validation)
        migrations.AlterField(
            model_name='room',
            name='status',
            field=models.CharField(
                choices=[
                    ('Available', 'Available'),
                    ('Occupied', 'Occupied'),
                    ('Cleaning', 'Cleaning'),
                    ('Maintenance', 'Maintenance'),
                    ('Reserved', 'Reserved'),
                ],
                default='Available',
                max_length=20,
            ),
        ),
        # Create RoomCleaning table
        migrations.CreateModel(
            name='RoomCleaning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('Pending', 'Pending'),
                        ('In Progress', 'In Progress'),
                        ('Completed', 'Completed'),
                    ],
                    default='Pending',
                    max_length=20,
                )),
                ('notes', models.TextField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('room', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cleaning_sessions',
                    to='resultapp.room',
                )),
                ('booking', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='cleaning_session',
                    to='resultapp.booking',
                )),
                ('assigned_to', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='cleaning_tasks',
                    to='resultapp.staff',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
