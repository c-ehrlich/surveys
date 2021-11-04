# Generated by Django 3.2.9 on 2021-11-04 17:15

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('answer_text', models.CharField(max_length=1000, verbose_name='Answer Text')),
                ('answer_boolean', models.BooleanField(verbose_name='Answer Boolean')),
            ],
        ),
        migrations.CreateModel(
            name='AnswerOption',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=200, verbose_name='Text')),
                ('order', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=200, verbose_name='Question')),
                ('subheading', models.CharField(max_length=1000, verbose_name='Subheading')),
                ('is_required', models.BooleanField(default=True, verbose_name='Is Required')),
                ('question_type', models.CharField(choices=[('MCS', 'Multiple Choice (Single Answer)'), ('MCM', 'Multiple Choice (Multiple Answers)'), ('TR', 'Text Response')], max_length=3)),
                ('order', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(default='Unnamed Survey', max_length=200, verbose_name='Title')),
                ('description', models.CharField(blank=True, default=None, max_length=1000, null=True, verbose_name='Description')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('survey_start_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Survey Start Date')),
                ('survey_end_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Survey End Date')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('allow_anonymous_responses', models.BooleanField(default=True, verbose_name='Allow Anonymous Responses')),
                ('limit_one_response_per_user', models.BooleanField(default=True, verbose_name='Limit to One Response per User')),
                ('allow_edits_after_submit', models.BooleanField(default=True, verbose_name='Allow Edits after Logged In User has submitted a response')),
            ],
        ),
        migrations.CreateModel(
            name='SurveySection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Section Name')),
                ('subheading', models.CharField(max_length=1000, verbose_name='Section Subheading')),
                ('order', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='surveys.survey', verbose_name='Survey')),
            ],
        ),
        migrations.CreateModel(
            name='SurveyParticipation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_complete', models.BooleanField(default=False)),
                ('last_interaction', models.DateTimeField(auto_now_add=True)),
                ('user_session', models.CharField(max_length=100)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='survey_participations', to='surveys.survey')),
            ],
        ),
    ]