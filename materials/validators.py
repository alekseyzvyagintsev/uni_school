##############################################################################################################
from rest_framework.serializers import ValidationError


class ValidateYoutubeLink:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        """
        Метод, выполняемый при проверке значения
        """
        tmp_val = dict(value).get(self.field)
        if tmp_val is not None:
            if not any(domain in tmp_val for domain in ["youtube.com", "youtu.be"]):
                raise ValidationError("Ссылка должна вести на ресурс YouTube.")


##############################################################################################################
