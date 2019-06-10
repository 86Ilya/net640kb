from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from Net640.apps.images.models import Image
from Net640.settings import MAX_PAGE_SIZE


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('description', 'image')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['description'].widget.attrs.update({
            'placeholder': 'Image description', 'class': 'form-control mb-3'
        })
        self.fields['description'].help_text = ''
        self.fields['description'].label = ''
        self.fields['description'].required = True

        self.fields['image'].widget.attrs.update({'class': 'form-control mb-3'})
        self.fields['image'].help_text = ''
        self.fields['image'].label = ''
        self.fields['image'].required = True

    def clean(self):
        cleaned_data = super().clean()
        validation_errors = list()

        # without user we can't calculate page size.
        if not self.user:
            raise forms.ValidationError(_('Anonymous posts are not allowed'))

        # Calculate form size
        # use latest id as reference
        try:
            form_size = len(str(Image.objects.latest('id').id))
        except ObjectDoesNotExist:
            form_size = 1

        form_size += len(cleaned_data['description']) + cleaned_data['image'].size
        if self.user.get_size() + form_size > MAX_PAGE_SIZE:
            validation_errors.append(forms.ValidationError(_('Not enough space!'), code='oversize'))
        if validation_errors:
            raise forms.ValidationError(validation_errors)

        return cleaned_data
