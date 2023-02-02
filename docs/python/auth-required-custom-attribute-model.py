from django.contrib.auth.models import AbstractBaseUser


class CustomUserModel(AbstractBaseUser):
    @property
    def is_really_cool(self):
        return True
