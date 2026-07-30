from django import forms


class JobAnalysisForm(forms.Form):
    SOURCE_CHOICES = (
        ('existing', 'Select an existing resume'),
        ('upload', 'Upload a resume file'),
    )

    JD_SOURCE_CHOICES = (
        ('url', 'AI Fetch — Auto-extract from URL'),
        ('manual', 'Manual — Paste description'),
        ('autosearch', 'Auto-Search — AI finds matching jobs'),
    )

    source = forms.ChoiceField(
        choices=SOURCE_CHOICES, initial='upload',
        widget=forms.RadioSelect(attrs={'class': 'btn-check source-radio'}),
    )
    resume = forms.ChoiceField(
        label='Select Resume', required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    resume_file = forms.FileField(
        label='Upload Resume', required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control', 'accept': '.pdf,.docx,.txt,.md',
        }),
    )

    jd_source = forms.ChoiceField(
        choices=JD_SOURCE_CHOICES, initial='autosearch',
        widget=forms.RadioSelect(attrs={'class': 'btn-check jd-source-radio'}),
    )
    job_url = forms.URLField(
        label='Job Posting URL',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control', 'placeholder': 'https://linkedin.com/jobs/view/...',
        }),
    )
    job_title = forms.CharField(
        label='Job Title', max_length=200, required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Auto-detected by AI',
        }),
    )
    company = forms.CharField(
        label='Company', max_length=200, required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Auto-detected by AI',
        }),
    )
    job_description = forms.CharField(
        label='Job Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 10,
            'placeholder': 'Paste the job description, or use AI Fetch from URL above...',
        }),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            resumes = user.resumes.all()
            choices = [(r.id, f"{r.title} ({r.template.name if r.template else 'No template'})")
                       for r in resumes]
            if not choices:
                choices = [('', '-- No resumes yet --')]
            self.fields['resume'].choices = choices

    def clean(self):
        cleaned = super().clean()
        source = cleaned.get('source')
        jd_source = cleaned.get('jd_source')

        if source == 'existing' and not cleaned.get('resume'):
            raise forms.ValidationError('Please select a resume or switch to file upload.')
        if source == 'upload' and not cleaned.get('resume_file'):
            raise forms.ValidationError('Please upload a resume file or switch to selecting an existing one.')
        if jd_source == 'url' and not cleaned.get('job_url'):
            raise forms.ValidationError('Please enter a job posting URL for AI to fetch.')
        if jd_source == 'manual' and not cleaned.get('job_description'):
            raise forms.ValidationError('Please paste a job description.')
        return cleaned
