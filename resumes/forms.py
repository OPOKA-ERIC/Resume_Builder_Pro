from django import forms
from .models import Resume, Education, Experience, Skill, Project, Certification, Language, Reference


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resume Title'}),
        }


class EducationForm(forms.ModelForm):
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    class Meta:
        model = Education
        fields = ['institution', 'qualification', 'start_date', 'end_date', 'description']
        labels = {
            'description': 'Responsibilities',
        }
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your responsibilities...'}),
        }


class ExperienceForm(forms.ModelForm):
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    class Meta:
        model = Experience
        fields = ['company', 'role', 'start_date', 'end_date', 'description']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'proficiency_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'proficiency_level': forms.Select(attrs={'class': 'form-select'}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'link']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['title', 'issuer', 'date_awarded']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'issuer': forms.TextInput(attrs={'class': 'form-control'}),
            'date_awarded': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ['name', 'proficiency_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'proficiency_level': forms.Select(attrs={'class': 'form-select'}),
        }


class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        fields = ['name', 'relationship', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
