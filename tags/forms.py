from django import forms

from tags.models import Tag
from utils import formfield_extra_kwargs


class CreateTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = (
            "user",
            "name",
        )


class UpdateTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ("name",)
        formfield_callback = formfield_extra_kwargs(
            name=dict(required=False),
        )


class DeleteTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ()


class OrderTagForm(forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = Tag
        fields = ("id", "user", "name")
