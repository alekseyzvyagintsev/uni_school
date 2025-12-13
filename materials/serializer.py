##############################################################################################################
from rest_framework import serializers

from materials.models import Lesson, Course


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('id',)


class CourseSerializer(serializers.ModelSerializer):
    many_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'title',
            'preview',
            'description',
            'many_lessons',
        )
        read_only_fields = ('id',)

    def get_many_lessons(self, course):
        lessons = course.lessons.all()
        lessons_count = lessons.count()
        lessons_serializer = LessonSerializer(lessons, many=True)
        return f'Курс содержит {lessons_count} урок(а/ов)', lessons_serializer.data


##############################################################################################################
