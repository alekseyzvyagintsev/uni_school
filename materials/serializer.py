##############################################################################################################
from rest_framework import serializers

from materials.models import Lesson, Course


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('id',)


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('id',)


##############################################################################################################
