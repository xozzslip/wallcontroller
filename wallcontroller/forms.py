from django import forms
from wallcontroller.models import Community


class AddCommunityForm(forms.Form):
    url = forms.CharField(max_length=300)

    def domen_name_from_url(self):
        url = self.cleaned_data["url"]
        domen_name = url.split("://")[1].split("/")[1]
        if "public" in url:
            domen_name = domen_name.split("public")[1]
        return domen_name


class ChangeCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['end_count']
