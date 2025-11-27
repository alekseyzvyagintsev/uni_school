####################################################################################################################
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=250, verbose_name='название')
    preview = models.ImageField(upload_to="preview/", blank=True, null=True)
    description = models.TextField(verbose_name='описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = [
            "title",
        ]
        db_table = "courses"


class Lesson(models.Model):
    title = models.CharField(max_length=250, verbose_name='название')
    preview = models.ImageField(upload_to="preview/", blank=True, null=True)
    description = models.TextField(verbose_name='описание')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = [
            "title",
        ]
        db_table = "lessons"


####################################################################################################################
