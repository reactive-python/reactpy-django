from django import forms

from .. import models


class BasicForm(forms.Form):
    # Render one of every Django field type
    # https://docs.djangoproject.com/en/stable/ref/forms/fields/#field-types
    boolean_field = forms.BooleanField(label="boolean")
    char_field = forms.CharField(label="chars")
    choice_field = forms.ChoiceField(label="choice", choices=[("1", "One"), ("2", "Two")])
    date_field = forms.DateField(label="date")
    date_time_field = forms.DateTimeField(label="date time")
    decimal_field = forms.DecimalField(label="decimal")
    duration_field = forms.DurationField(label="duration")
    email_field = forms.EmailField(label="email")
    file_path_field = forms.FilePathField("./", label="file path")
    float_field = forms.FloatField(label="float")
    generic_ip_address_field = forms.GenericIPAddressField(label="Generic IP")
    integer_field = forms.IntegerField(label="integer")
    json_field = forms.JSONField(label="JSON")
    multiple_choice_field = forms.MultipleChoiceField(
        label="multiple choice", choices=[("1", "One"), ("2", "Two"), ("3", "Three")]
    )
    null_boolean_field = forms.NullBooleanField(label="null boolean")
    regex_field = forms.RegexField(label="regex", regex=r"^\d{1,2}$")
    slug_field = forms.SlugField(label="slug")
    time_field = forms.TimeField(label="time")
    typed_choice_field = forms.TypedChoiceField(label="typed choice field", choices=[("1", "One"), ("2", "Two")])
    typed_multiple_choice_field = forms.TypedMultipleChoiceField(
        label="typed multiple choice", choices=[("1", "One"), ("2", "Two")]
    )
    url_field = forms.URLField(label="URL")
    uuid_field = forms.UUIDField(label="UUID")
    combo_field = forms.ComboField(label="combo", fields=[forms.CharField(), forms.EmailField()])
    password_field = forms.CharField(label="password", widget=forms.PasswordInput)
    model_choice_field = forms.ModelChoiceField(label="model choice field", queryset=models.TodoItem.objects.all())
    model_multiple_choice_field = forms.ModelMultipleChoiceField(
        label="model multiple choice field", queryset=models.TodoItem.objects.all()
    )


class DatabaseBackedForm(forms.ModelForm):
    class Meta:
        model = models.TodoItem
        fields = "__all__"


class EventForm(forms.Form):
    char_field = forms.CharField(label="chars")


class BootstrapForm(forms.Form):
    # Render a handful of Django field types
    boolean_field = forms.BooleanField(label="boolean")
    char_field = forms.CharField(label="chars")
    choice_field = forms.ChoiceField(label="choice", choices=[("1", "One"), ("2", "Two")])
