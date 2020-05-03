from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordResetForm
from django.core.validators import RegexValidator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from Net640.apps.user_profile.models import User
from Net640.settings import MAX_PAGE_SIZE, DATE_FORMAT
from Net640.errors import ERR_EXCEED_LIMIT


username_validator = RegexValidator(r'^[\w\d_\-]+$',
                                    "Username should contain only letters, digits, underscores, and dashes")


class CleanPasswordMixin:

    def _clean_password(self, cleaned_data):
        password = cleaned_data['password']
        password_again = cleaned_data['password_again']
        validation_errors = list()

        if len(password) == 0 and len(password_again) == 0:
            return cleaned_data, validation_errors
        if password != password_again:
            validation_errors.append(forms.ValidationError("Passwords mismatch"))
        elif len(password) < 8:
            validation_errors.append(forms.ValidationError("Password length must be at least 8 symbols"))
        return cleaned_data, validation_errors


class UserForm(CleanPasswordMixin, forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput, max_length=120, min_length=3, validators=[username_validator])
    email = forms.EmailField(widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput)
    password_again = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_again', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False
        self.fields['avatar'].label = 'Upload Avatar:'
        self.fields['avatar'].widget.attrs.update({
            'class': 'form-control-file'
        })

        if self.fields.get('username', None):
            self.fields['username'].widget.attrs.update({
                'placeholder': 'Username', 'class': 'form-control mb-3'
            })
            self.fields['username'].help_text = ''
            self.fields['username'].label = ''

        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email', 'class': 'form-control mb-3'
        })
        self.fields['email'].help_text = ''
        self.fields['email'].label = ''

        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password', 'class': 'form-control mb-3'
        })
        self.fields['password'].help_text = ''
        self.fields['password'].label = ''

        self.fields['password_again'].widget.attrs.update({
            'placeholder': 'Repeat password', 'class': 'form-control mb-3'
        })
        self.fields['password_again'].help_text = ''
        self.fields['password_again'].label = ''

        # this code is for descendants
        # remove unnecessary fields
        unnecessary = set(self.fields.keys()) - set(self.Meta.fields)
        for field in unnecessary:
            self.fields.pop(field)

    def clean(self):
        cleaned_data = super().clean()
        validation_errors = list()

        # Calculate form size
        # use latest id as reference
        try:
            form_size = len(str(User.objects.latest('id').id))
        except ObjectDoesNotExist:
            form_size = 1
        # if we already had errors, than we will skip this fields
        for field_name in set(self.changed_data) - set(self.errors):
            if field_name in ['password_again']:
                continue
            if field_name == 'avatar':
                form_size += cleaned_data['avatar'].size
                continue
            form_size += len(str(cleaned_data[field_name]))
        if form_size > MAX_PAGE_SIZE:
            validation_errors.append(forms.ValidationError(_('You have only 640Kb for all purposes!'), code='oversize'))

        # Clean password
        cleaned_data, password_clean_errors = self._clean_password(cleaned_data)

        validation_errors += password_clean_errors
        if validation_errors:
            raise forms.ValidationError(validation_errors)

        cleaned_data['password'] = make_password(cleaned_data['password'])

        return cleaned_data


class UserUpdateForm(UserForm):
    firstname = forms.CharField(widget=forms.TextInput)
    lastname = forms.CharField(widget=forms.TextInput)
    patronymic = forms.CharField(widget=forms.TextInput)
    birth_date = forms.DateField(widget=forms.DateInput, input_formats=[DATE_FORMAT])

    class Meta(UserForm.Meta):
        fields = ('firstname', 'lastname', 'patronymic', 'birth_date', 'password', 'password_again', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

        self.fields['firstname'].widget.attrs.update({
            'placeholder': 'First Name', 'class': 'form-control mb-3'
        })
        self.fields['firstname'].help_text = ''
        self.fields['firstname'].label = ''

        self.fields['lastname'].widget.attrs.update({
            'placeholder': 'Last Name', 'class': 'form-control mb-3'
        })
        self.fields['lastname'].help_text = ''
        self.fields['lastname'].label = ''

        self.fields['patronymic'].widget.attrs.update({
            'placeholder': 'Patronymic', 'class': 'form-control mb-3'
        })
        self.fields['patronymic'].help_text = ''
        self.fields['patronymic'].label = ''

        self.fields['birth_date'].widget.attrs.update({
            'placeholder': 'Birth Date', 'class': 'form-control mb-3'
        })
        self.fields['birth_date'].widget.format = DATE_FORMAT
        self.fields['birth_date'].help_text = ''
        self.fields['birth_date'].label = ''

        self.fields['password'].widget.attrs.update({
            'placeholder': 'New password'})
        self.fields['password_again'].widget.attrs.update({
            'placeholder': 'Repeat new password'})

    def clean(self):
        cleaned_data = super().clean()
        delta = 0
        # if we have empty password field then skip updating this field
        if 'password' in self.changed_data:
            password = cleaned_data['password']
            if len(password) == 0:
                index = self.changed_data.index('password')
                self.changed_data.pop(index)
                cleaned_data.pop('password')
        # get approximate size of user fields
        original_sizes = self.instance.get_fields_size()
        # check delta for all fields except password_again (not exist in DB)
        for field_name in self.changed_data:
            if field_name in ['password_again']:
                continue
            updated_value = cleaned_data[field_name]
            if not updated_value:
                updated_len = 0
            elif field_name == 'avatar':
                updated_len = updated_value.size
            else:
                updated_len = len(str(updated_value))

            original_len = original_sizes[field_name]
            delta += updated_len - original_len

        if self.instance.get_size() + delta > MAX_PAGE_SIZE:
            raise forms.ValidationError(_(ERR_EXCEED_LIMIT), code='oversize')

        return cleaned_data


class UserRequestPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput, max_length=256)

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email', 'class': 'form-control mb-3'
        })
        self.fields['email'].help_text = ''
        self.fields['email'].label = ''


class UserPasswordUpdateForm(UserForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_again = forms.CharField(widget=forms.PasswordInput)

    class Meta(UserForm.Meta):
        fields = ('password', 'password_again')


class UserPasswordResetConfirmForm(CleanPasswordMixin, forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    password_again = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data, password_clean_errors = self._clean_password(cleaned_data)

        if password_clean_errors:
            raise forms.ValidationError(password_clean_errors)

        return cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data["password"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
