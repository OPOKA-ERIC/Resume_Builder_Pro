import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.validators import RegexValidator
from .models import UserProfile


def _career_lines(value):
    return [line.strip() for line in (value or '').splitlines() if line.strip()]


def _career_parts(line, count):
    parts = [p.strip() for p in line.split('|')]
    parts += [''] * (count - len(parts))
    return parts[:count]


def _to_year(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


CAREER_SPECS = [
    ('career_experience', 'experience',
     ('role', 'company', 'start_year', 'end_year', 'description'),
     ('role', 'company', 'start_year')),
    ('career_education', 'education',
     ('qualification', 'institution', 'start_year', 'end_year', 'description'),
     ('qualification', 'institution', 'start_year')),
    ('career_projects', 'projects',
     ('name', 'link', 'description'),
     ('name',)),
    ('career_certifications', 'certifications',
     ('title', 'issuer', 'year_awarded'),
     ('title', 'issuer', 'year_awarded')),
    ('career_languages', 'languages',
     ('name', 'proficiency_level'),
     ('name',)),
]


def serialize_career(cleaned):
    data = {}
    for field, key, cols, required in CAREER_SPECS:
        items = []
        for line in _career_lines(cleaned.get(field)):
            values = _career_parts(line, len(cols))
            item = dict(zip(cols, values))
            if 'start_year' in item:
                item['start_year'] = _to_year(item['start_year'])
            if 'end_year' in item:
                item['end_year'] = _to_year(item['end_year']) or None
            if 'year_awarded' in item:
                item['year_awarded'] = _to_year(item['year_awarded'])
            if key == 'languages' and not item.get('proficiency_level'):
                item['proficiency_level'] = 'fluent'
            if all(item.get(r) for r in required):
                items.append(item)
        data[key] = items
    return data


def career_initial_from_data(career_data):
    out = {}
    for field, key, cols, _required in CAREER_SPECS:
        lines = []
        for item in (career_data or {}).get(key, []):
            lines.append(' | '.join(str(item.get(c, '') or '') for c in cols))
        out[field] = '\n'.join(lines)
    return out


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        })
    )
    username = forms.CharField(
        min_length=3,
        max_length=30,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Username may only contain letters, digits, and @/./+/-/_ characters.',
            ),
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email',
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
        })
    )
    skills = forms.CharField(
        required=False,
        help_text='Comma-separated skills added to every new job resume.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Python, Django, Project Management, Excel',
        })
    )

    career_experience = forms.CharField(
        required=False,
        help_text='One entry per line. Columns separated by | : Role | Company | Start Year | End Year | Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Role | Company | Start Year | End Year | Description',
        })
    )
    career_education = forms.CharField(
        required=False,
        help_text='One entry per line: Qualification | Institution | Start Year | End Year | Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Qualification | Institution | Start Year | End Year | Description',
        })
    )
    career_projects = forms.CharField(
        required=False,
        help_text='One entry per line: Name | Link | Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Name | Link | Description',
        })
    )
    career_certifications = forms.CharField(
        required=False,
        help_text='One entry per line: Title | Issuer | Year Awarded',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Title | Issuer | Year Awarded',
        })
    )
    career_languages = forms.CharField(
        required=False,
        help_text='One entry per line: Name | Proficiency Level (basic, conversational, fluent, native)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Name | Proficiency Level (basic, conversational, fluent, native)',
        })
    )

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'photo', 'website', 'city', 'skills']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+256 700 000000',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Your address',
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Kampala, Uganda',
                'id': 'id_city',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
        if self.instance and not self.is_bound:
            for field, value in career_initial_from_data(self.instance.career_data).items():
                self.fields[field].initial = value

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if not re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone):
                raise forms.ValidationError('Enter a valid phone number (7-20 digits).')
        return phone

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })
