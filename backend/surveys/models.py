from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models import F, Max
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from django.conf import settings


class Survey(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_surveys",
        verbose_name="Creator",
    )

    title = models.CharField(
        default="Unnamed Survey",
        max_length=200,
        verbose_name="Title",
    )

    description = models.CharField(
        default=None,
        blank=True,
        null=True,
        max_length=1000,
        verbose_name="Description",
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creation Date",
    )

    survey_start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Survey Start Date",
    )

    survey_end_date = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        verbose_name="Survey End Date",
    )

    is_active = models.BooleanField(
        default=True,
        editable=True,
        verbose_name="Is Active",
    )

    allow_anonymous_responses = models.BooleanField(
        default=True,
        editable=True,
        verbose_name="Allow Anonymous Responses",
    )

    limit_one_response_per_user = models.BooleanField(
        default=True,
        editable=True,
        verbose_name="Limit to One Response per User",
    )

    allow_edits_after_submit = models.BooleanField(
        default=True,
        editable=True,
        verbose_name="Allow Edits after Logged In User has submitted a response",
    )

    def __str__(self):
        return f"Survey {self.id} - {self.title}"


class SurveySectionManager(models.Manager):
    """
    Manager code derived from https://www.reddit.com/r/django/comments/bfx9n0/best_way_to_create_ordered_lists_with_models/elhhy1h/
    TODO: make the three functions generic to improve DRY
    """

    def create(self, *args, **kwargs):
        """
        Creates a new SurveySection
        If an `order` is given, it is inserted in the correct location
        Otherwise it is inserted at the end
        """
        instance = self.model(**kwargs)
        with transaction.atomic():
            queryset = self._make_order_consecutive(instance.survey)
            current_order = queryset.aggregate(Max("order"))["order__max"]
            if current_order is None:
                current_order = 0

            if not "order" in kwargs or kwargs["order"] > current_order + 1:
                instance.order = current_order + 1
            else:
                self.filter(order__gte=kwargs["order"]).update(order=F("order") + 1)

            instance.save()
            return instance

    def move(self, obj, new_order):
        """
        Move an object and fix the relative position of all other objects
        This returns nothing, so all vars that represent objects from the queryset might be outdated after running this function
        """
        queryset = self._make_order_consecutive(obj.survey)
        with transaction.atomic():
            if obj.order > int(new_order):
                # Move other objects up (because we're moving the current object back)
                queryset.filter(order__lt=obj.order, order__gte=new_order,).exclude(
                    pk=obj.pk
                ).update(order=F("order") + 1)
            elif obj.order < int(new_order):
                # Move other objects down (because we're moving the current object forward)
                queryset.filter(order__lte=new_order, order__gt=obj.order,).exclude(
                    pk=obj.pk
                ).update(order=F("order") - 1)
            # Move the object itself
            obj.order = new_order
            obj.save()
            return obj  # TODO are we actually going to use this?

    def _make_order_consecutive(self, survey):
        """
        Takes a Survey, and puts all SurveySections of that Survey in correct sequential order
        ie for 4 items with orders (5, 9, 1, 3) their new orders would be (1 => 1, 3 => 2, 5 => 3, 9 => 4)
        Returns that queryset of ordered and sequential SurveySections
        """
        queryset = self.filter(survey=survey).order_by("order")
        with transaction.atomic():
            for index, section in enumerate(queryset):
                if section.order != index + 1:
                    section.order = index + 1
                    section.save()
        return queryset  # can choose not to use this, but it's nice
        # if we want to keep working with the data


class SurveySection(models.Model):
    """
    Only create SurveySection items by using `SurveySection.objects.create()`!
    (ie not `SurveySection()`)
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Section Name",
    )

    subheading = models.CharField(
        max_length=1000,
        verbose_name="Section Subheading",
    )

    survey = models.ForeignKey(
        "Survey",
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="Survey",
    )

    order = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
    )

    objects = SurveySectionManager()

    def __str__(self):
        return f"Survey Section {self.id} - {self.name}"


class QuestionManager(models.Manager):
    """
    Manager for creating, moving, and fixing the order of Question objects
    Refer to SurveySectionManager for more documentation and possible improvements
    """

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        with transaction.atomic():
            queryset = self._make_order_consecutive(instance.section)
            current_order = queryset.aggregate(Max("order"))["order__max"]
            if current_order is None:
                current_order = 0

            if not "order" in kwargs or kwargs["order"] > current_order + 1:
                instance.order = current_order + 1
            else:
                self.filter(order__gte=kwargs["order"]).update(order=F("order") + 1)

            instance.save()
            return instance

    def move(self, obj, new_order):
        queryset = self._make_order_consecutive(obj.section)
        with transaction.atomic():
            if obj.order > int(new_order):
                # Move other objects up (because we're moving the current object back)
                queryset.filter(order__lt=obj.order, order__gte=new_order,).exclude(
                    pk=obj.pk
                ).update(order=F("order") + 1)
            elif obj.order < int(new_order):
                # Move other objects down (because we're moving the current object forward)
                queryset.filter(order__lte=new_order, order__gt=obj.order,).exclude(
                    pk=obj.pk
                ).update(order=F("order") - 1)
            # move the object itself
            obj.order = new_order
            obj.save()
            return obj

    def _make_order_consecutive(self, section):
        queryset = self.filter(section=section).order_by("order")
        with transaction.atomic():
            for index, question in enumerate(queryset):
                if question.order != index + 1:
                    question.order = index + 1
                    question.save()
        return queryset


class Question(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    question = models.CharField(
        max_length=200,
        verbose_name="Question",
    )

    subheading = models.CharField(
        max_length=1000,
        verbose_name="Subheading",
    )

    is_required = models.BooleanField(
        default=True,
        verbose_name="Is Required",
    )

    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE_SINGLE = "MCS", _("Multiple Choice (Single Answer)")
        MULTIPLE_CHOICE_MULTI = "MCM", _("Multiple Choice (Multiple Answers)")
        TEXT_RESPONSE = "TR", _("Text Response")
        # BOOLEAN? (or just use MCS for that, easy to name answers that way)

    question_type = models.CharField(
        max_length=3,
        choices=QuestionType.choices,
    )

    section = models.ForeignKey(
        "SurveySection",
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Section",
    )

    dependency_question = models.ForeignKey(
        "Question",
        default=None,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # Maybe ask the user what they want to happen?
        related_name="questions_dependent_on_question",
        verbose_name="This question's Question dependency",
    )

    dependency_answer_option = models.ForeignKey(
        "AnswerOption",
        default=None,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # Maybe ask the user what they want to happen?
        related_name="questions_dependent_on_answer_option",
        verbose_name="This question's Answer Option dependency",
    )

    order = models.PositiveIntegerField()

    objects = QuestionManager()

    def __str__(self):
        return f"Question {self.id} - {self.question}"


class AnswerOptionManager(models.Manager):
    """
    Manager for creating, moving, and fixing the order of AnswerOption objects
    Refer to SurveySectionManager for more documentation and possible improvements
    """

    def create(self, *args, **kwargs):
        instance = self.model(**kwargs)
        with transaction.atomic():
            queryset = self._make_order_consecutive(instance.question)
            current_order = queryset.aggregate(Max("order"))["order__max"]
            if current_order is None:
                current_order = 0

            if not "order" in kwargs or kwargs["order"] > current_order + 1:
                instance.order = current_order + 1
            else:
                self.filter(order__gte=kwargs["order"]).update(order=F("order") + 1)

            instance.save()
            return instance

    def move(self, obj, new_order):
        queryset = self._make_order_consecutive(obj.question)
        with transaction.atomic():
            if obj.order > int(new_order):
                # Move other objects up (because we're moving the current object back)
                queryset.filter(order__lt=obj.order, order__gte=new_order,).exclude(
                    pk=obj.pk
                ).update(order=F("order") + 1)
            elif obj.order < int(new_order):
                # Move other objects down (because we're moving the current object forward)
                queryset.filter(order__lte=new_order, order__gt=obj.order,).exclude(
                    pk=obj.pk
                ).update(order=F("order") - 1)
            # Move the object itself
            obj.order = new_order
            obj.save()
            return obj

    def _make_order_consecutive(self, question):
        queryset = self.filter(question=question).order_by("order")
        with transaction.atomic():
            for index, answer_option in enumerate(queryset):
                if answer_option.order != index + 1:
                    answer_option.order = index + 1
                    answer_option.save()
        return queryset


class AnswerOption(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    text = models.CharField(
        max_length=200,
        verbose_name="Text",
    )

    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="answer_options",
    )

    order = models.PositiveIntegerField()

    objects = AnswerOptionManager()


class Answer(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="answers",
    )

    answer_text = models.CharField(
        max_length=1000,
        verbose_name="Answer Text",
    )

    answer_boolean = models.BooleanField(
        editable=True,
        verbose_name="Answer Boolean",
    )

    answer_option = models.ForeignKey(
        "AnswerOption",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="have_chosen_this_option",
    )

    survey_participation = models.ForeignKey(
        "SurveyParticipation",
        on_delete=models.CASCADE,
        related_name="answers_of_survey_participation",
    )

    def __str__(self):
        return f"Answer {self.id} to {self.question}"


@receiver(post_save, sender=Answer)
def hear_signal(sender, instance, **kwargs):
    # TODO update this to work if no survey participation exists yet?
    instance.survey_participation.last_interaction = timezone.now()


class SurveyParticipation(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    survey = models.ForeignKey(
        "Survey",
        on_delete=models.CASCADE,
        related_name="survey_participations",
    )
    is_complete = models.BooleanField(
        default=False,
    )

    last_interaction = models.DateTimeField(
        auto_now_add=True,
    )

    user_account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="survey_participations",
    )

    user_session = models.CharField(
        max_length=100,
    )

    def __str__(self):
        return f"Survey Participation {self.id} of {self.survey}"

    class Meta:
        constraints = [
            # ensure that either user_account or user_session contains data
            # (we don't want both to have data or both to be empty)
            models.CheckConstraint(
                name="api_surveyparticipation_useraccount_or_usersession",
                check=(
                    models.Q(user_account__isnull=True, user_session__isnull=False)
                    | models.Q(user_account__isnull=False, user_session__isnull=True)
                ),
            ),
        ]
