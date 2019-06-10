from django import forms
from django.contrib.auth.hashers import make_password
# from django.core.validators import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from Net640.apps.user_profile.models import User
from Net640.settings import MAX_PAGE_SIZE
from Net640.errors import ERR_EXCEED_LIMIT


class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput)
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

    def clean(self):
        cleaned_data = super().clean()
        validation_errors = list()

        # Calculate form size
        # use latest id as reference
        try:
            form_size = len(str(User.objects.latest('id').id))
        except ObjectDoesNotExist:
            form_size = 1
        for field_name in self.changed_data:
            if field_name in ['password_again']:
                continue
            form_size += len(str(cleaned_data[field_name]))
        if form_size > MAX_PAGE_SIZE:
            validation_errors.append(forms.ValidationError(_('You have only 640Kb for all purposes!'), code='oversize'))

        # Clean password
        password = cleaned_data['password']
        password_again = cleaned_data['password_again']
        if len(password) == 0 and len(password_again) == 0:
            return cleaned_data
        if password != password_again:
            validation_errors.append(forms.ValidationError("Passwords mismatch"))
        elif len(password) < 8:
            validation_errors.append(forms.ValidationError("Password length must be at least 8 symbols"))
        else:
            # TODO is it ok?
            cleaned_data['password'] = make_password(password)

        if validation_errors:
            raise forms.ValidationError(validation_errors)

        return cleaned_data


class UserUpdateForm(UserForm):
    firstname = forms.CharField(widget=forms.TextInput)
    lastname = forms.CharField(widget=forms.TextInput)
    patronymic = forms.CharField(widget=forms.TextInput)
    # birth_date = forms.DateField(widget=forms.DateInput, input_formats=['%d-%m-%Y', '%d.%m.%Y'])
    birth_date = forms.DateField(widget=forms.DateInput, input_formats=['%d.%m.%Y'])

    class Meta(UserForm.Meta):
        fields = ('firstname', 'lastname', 'patronymic', 'birth_date', 'password', 'password_again', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

        # TODO UGLY HACK
        if self.fields.get('username', None):
            self.fields.pop('username')

        if self.fields.get('email', None):
            self.fields.pop('email')

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
        self.fields['birth_date'].widget.format = '%d.%m.%Y'
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
        # check delta for all fields except password_again (not exist in DB)
        for field_name in self.changed_data:
            if field_name in ['password_again']:
                continue

            original_value = getattr(self.instance, field_name)
            if not original_value:
                original_len = 0
            else:
                original_len = len(original_value)

            updated_value = cleaned_data[field_name]
            if not updated_value:
                updated_len = 0
            else:
                updated_len = len(str(updated_value))

            delta += updated_len - original_len

        if self.instance.get_size() + delta > MAX_PAGE_SIZE:
            raise forms.ValidationError(_(ERR_EXCEED_LIMIT), code='oversize')

        return cleaned_data
