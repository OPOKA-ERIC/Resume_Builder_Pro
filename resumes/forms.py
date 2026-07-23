import re
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Resume, Education, Experience, Skill, Project, Certification, Language, Reference

CURRENT_YEAR = 2026


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resume Title'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Resume title is required.')
        if len(title) < 2:
            raise forms.ValidationError('Resume title must be at least 2 characters.')
        return title


class EducationForm(forms.ModelForm):
    start_year = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(1950), MaxValueValidator(CURRENT_YEAR + 10)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2020', 'min': 1950, 'max': CURRENT_YEAR + 10}),
    )
    end_year = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1950), MaxValueValidator(CURRENT_YEAR + 10)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if ongoing', 'min': 1950, 'max': CURRENT_YEAR + 10}),
    )

    class Meta:
        model = Education
        fields = ['institution', 'qualification', 'start_year', 'end_year', 'description']
        labels = {
            'description': 'Description',
        }
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Stanford University'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B.S. Computer Science'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your achievements, coursework, or responsibilities...'}),
        }

    def clean_institution(self):
        val = self.cleaned_data.get('institution', '').strip()
        if not val:
            raise forms.ValidationError('Institution name is required.')
        if len(val) < 2:
            raise forms.ValidationError('Institution name must be at least 2 characters.')
        return val

    def clean_qualification(self):
        val = self.cleaned_data.get('qualification', '').strip()
        if not val:
            raise forms.ValidationError('Qualification is required.')
        return val

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_year')
        end = cleaned_data.get('end_year')
        if start and end and end < start:
            raise forms.ValidationError('End year cannot be before start year.')
        return cleaned_data


class ExperienceForm(forms.ModelForm):
    start_year = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(1950), MaxValueValidator(CURRENT_YEAR + 10)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2022', 'min': 1950, 'max': CURRENT_YEAR + 10}),
    )
    end_year = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1950), MaxValueValidator(CURRENT_YEAR + 10)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if current', 'min': 1950, 'max': CURRENT_YEAR + 10}),
    )

    class Meta:
        model = Experience
        fields = ['company', 'role', 'start_year', 'end_year', 'description']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Google'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Engineer'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your responsibilities and achievements...'}),
        }

    def clean_company(self):
        val = self.cleaned_data.get('company', '').strip()
        if not val:
            raise forms.ValidationError('Company name is required.')
        return val

    def clean_role(self):
        val = self.cleaned_data.get('role', '').strip()
        if not val:
            raise forms.ValidationError('Job title/role is required.')
        return val

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_year')
        end = cleaned_data.get('end_year')
        if start and end and end < start:
            raise forms.ValidationError('End year cannot be before start year.')
        return cleaned_data


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'proficiency_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python'}),
            'proficiency_level': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_name(self):
        val = self.cleaned_data.get('name', '').strip()
        if not val:
            raise forms.ValidationError('Skill name is required.')
        if len(val) > 100:
            raise forms.ValidationError('Skill name must be 100 characters or fewer.')
        return val


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'link']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. E-commerce Platform'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the project, technologies used, and your role...'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

    def clean_name(self):
        val = self.cleaned_data.get('name', '').strip()
        if not val:
            raise forms.ValidationError('Project name is required.')
        return val

    def clean_link(self):
        link = self.cleaned_data.get('link', '').strip()
        if link and not link.startswith(('http://', 'https://')):
            raise forms.ValidationError('Enter a valid URL starting with http:// or https://.')
        return link


class CertificationForm(forms.ModelForm):
    year_awarded = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(1950), MaxValueValidator(CURRENT_YEAR + 5)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2023', 'min': 1950, 'max': CURRENT_YEAR + 5}),
    )

    class Meta:
        model = Certification
        fields = ['title', 'issuer', 'year_awarded']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AWS Solutions Architect'}),
            'issuer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Amazon Web Services'}),
        }

    def clean_title(self):
        val = self.cleaned_data.get('title', '').strip()
        if not val:
            raise forms.ValidationError('Certification title is required.')
        return val

    def clean_issuer(self):
        val = self.cleaned_data.get('issuer', '').strip()
        if not val:
            raise forms.ValidationError('Issuer name is required.')
        return val


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ['name', 'proficiency_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. English'}),
            'proficiency_level': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_name(self):
        val = self.cleaned_data.get('name', '').strip()
        if not val:
            raise forms.ValidationError('Language name is required.')
        return val


class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        fields = ['name', 'relationship', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Professor, Stanford University'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. email@example.com or +1 555 123 4567'}),
        }

    def clean_name(self):
        val = self.cleaned_data.get('name', '').strip()
        if not val:
            raise forms.ValidationError('Reference name is required.')
        return val

    def clean_relationship(self):
        val = self.cleaned_data.get('relationship', '').strip()
        if not val:
            raise forms.ValidationError('Relationship/title is required.')
        return val

    def clean_contact(self):
        val = self.cleaned_data.get('contact', '').strip()
        if not val:
            raise forms.ValidationError('Contact information is required.')
        if len(val) < 5:
            raise forms.ValidationError('Contact info seems too short. Please provide a valid email or phone number.')
        return val
