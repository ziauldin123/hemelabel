from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from labeller.models import CellFeature

from .models import Project, Region, Cell, Slide

class RegionForm(forms.ModelForm):
	class Meta:
		model = Region
		fields = ['rid', 'slide', 'image']
		labels = {'rid': '', 'slide': '', 'image': ''}

# Form for cell upload
class CellForm(forms.ModelForm):
  class Meta:
    model = Cell
    fields = {'image'}

# Form for creating a new project
class ProjectForm(forms.ModelForm):
  class Meta:
    model = Project
    fields = {'name'}


# Create user sign up form
class UserForm(UserCreationForm):
  first_name = forms.CharField()
  last_name  = forms.CharField()
  email      = forms.EmailField()

  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

# https://medium.com/swlh/django-forms-for-many-to-many-fields-d977dec4b024
# https://medium.com/analytics-vidhya/django-how-to-pass-the-user-object-into-form-classes-ee322f02948c
class CellFeatureForm(forms.ModelForm): 
  
  class Meta:
    model = Cell
    fields = ['name','cellFeatures']

  cellFeatures = forms.ModelMultipleChoiceField(
      queryset=CellFeature.objects.all(),
      widget=forms.CheckboxSelectMultiple
  )    


class DiagnosisForm(forms.Form):
    name = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Diagnosis"
        })
    )
    abbreviation = forms.CharField(
        max_length=8,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Dx"
        })
    )
