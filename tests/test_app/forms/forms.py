from django import forms


class BasicForm(forms.Form):
    # Render one of every Django field type
    # https://docs.djangoproject.com/en/stable/ref/forms/fields/#field-types
    boolean_field = forms.BooleanField(label="boolean", initial=True)
    char_field = forms.CharField(label="chars", max_length=7, initial="Example")
    choice_field = forms.ChoiceField(label="choice", initial="2", choices=[("1", "One"), ("2", "Two")])
    date_field = forms.DateField(label="date", initial="2000-01-01")
    date_time_field = forms.DateTimeField(label="date time", initial="2000-01-01 00:00:00")
    decimal_field = forms.DecimalField(label="decimal", initial=0.0)
    duration_field = forms.DurationField(label="duration", initial=0)
    email_field = forms.EmailField(label="email", initial="example@gmail.com")
    file_path_field = forms.FilePathField("./", label="file path")
    float_field = forms.FloatField(label="float", initial=0.0)
    generic_ip_address_field = forms.GenericIPAddressField(label="Generic IP", initial="127.0.0.1")
    integer_field = forms.IntegerField(label="integer", initial=0)
    json_field = forms.JSONField(label="JSON", initial={"key": "value"})
    multiple_choice_field = forms.MultipleChoiceField(
        label="multiple choice", initial=["1", "2"], choices=[("1", "One"), ("2", "Two"), ("3", "Three")]
    )
    null_boolean_field = forms.NullBooleanField(label="null boolean", initial=True)
    regex_field = forms.RegexField(label="regex", regex=r"^\d{1,2}$", initial="12")
    slug_field = forms.SlugField(label="slug", initial="your-slug")
    time_field = forms.TimeField(label="time", initial="00:00:00")
    typed_choice_field = forms.TypedChoiceField(
        label="typed choice field", initial="1", choices=[("1", "One"), ("2", "Two")]
    )
    typed_multiple_choice_field = forms.TypedMultipleChoiceField(
        label="typed multiple choice", initial="1", choices=[("1", "One"), ("2", "Two")]
    )
    url_field = forms.URLField(label="URL", initial="https://example.com")
    uuid_field = forms.UUIDField(label="UUID", initial="550e8400-e29b-41d4-a716-446655440000")
    combo_field = forms.ComboField(
        label="combo", fields=[forms.CharField(), forms.EmailField()], initial="example@gmail.com"
    )
    password_field = forms.CharField(label="password", widget=forms.PasswordInput)

