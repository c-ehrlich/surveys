from rest_framework import serializers

from .models import *


class AnswerOptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AnswerOption
        fields = [
            "id",
            "text",
            "order",
        ]

class QuestionSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "question",
            "subheading",
            "is_required",
            "question_type",
            "section",
            "dependency_question",
            "dependency_answer_option",
            "order",
            "answer_options",
        ]

class SurveySectionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = SurveySection
        fields = [
            "id",
            "name",
            "subheading",
            "order",
            "questions",
        ]

class SurveySerializer(serializers.ModelSerializer):
    sections = SurveySectionSerializer(many=True, read_only=True)
    # creator

    class Meta:
        model = Survey
        fields = [
            "id",
            # "creator", # might need this for some kind of verification in the future? or do it serverside?
            "title",
            "description",
            "creation_date",
            "survey_start_date",
            "survey_end_date",
            "is_active",
            "allow_anonymous_responses",
            "limit_one_response_per_user",
            "allow_edits_after_submit",
            "sections",
        ]
