from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from Net640.apps.user_posts.models import Post
from Net640.settings import MAX_PAGE_SIZE


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content', 'image')

    content = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['content'].widget.attrs.update({
            'placeholder': 'Your post', 'class': 'form-control w-100 mb-3', 'rows': 3,
        })
        self.fields['content'].help_text = ''
        self.fields['content'].label = ''
        self.fields['content'].required = True

        self.fields['image'].widget.attrs.update({
            'class': 'form-control',
        })
        self.fields['image'].help_text = ''
        self.fields['image'].label = ''
        self.fields['image'].required = False

    def clean(self):
        cleaned_data = super().clean()
        validation_errors = list()

        # without user we can't calculate page size.
        if not self.user:
            raise forms.ValidationError(_('Anonymous posts are not allowed'))

        # Calculate form size
        # use latest id as reference
        try:
            form_size = len(str(Post.objects.latest('id').id))
        except ObjectDoesNotExist:
            form_size = 1
        form_size += len(str(cleaned_data['content'])) + len(str(self.instance.date)) + len(str(self.user.id))
        if cleaned_data['image']:
            form_size += cleaned_data['image'].size

        if self.user.get_size() + form_size > MAX_PAGE_SIZE:
            validation_errors.append(forms.ValidationError(_('Not enough space!'), code='oversize'))
        if validation_errors:
            raise forms.ValidationError(validation_errors)

        return cleaned_data
