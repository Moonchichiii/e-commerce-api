from django.core.exceptions import ValidationError
import re

class ComplexPasswordValidator:
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError("The password must contain at least 1 digit, 0-9.")
        if not re.findall('[A-Z]', password):
            raise ValidationError("The password must contain at least 1 uppercase letter, A-Z.")
        if not re.findall('[a-z]', password):
            raise ValidationError("The password must contain at least 1 lowercase letter, a-z.")
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError("The password must contain at least 1 special character: " +
                                  "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?")

    def get_help_text(self):
        return "Your password must contain at least 1 digit, 1 uppercase letter, 1 lowercase letter, and 1 special character."