from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, UniversitySubmission, ScholarshipSubmission

_ctrl = 'form-control'
_ctrl_lg = 'form-control form-control-lg'


class SignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': _ctrl_lg, 'placeholder': 'your@email.com', 'autocomplete': 'email'}))
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': _ctrl_lg, 'placeholder': 'John Doe'}))
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': _ctrl_lg, 'placeholder': 'johndoe', 'autocomplete': 'username'}))
    country_of_origin = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': _ctrl_lg, 'placeholder': 'e.g. Nigeria, India, Brazil'}))
    current_country = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': _ctrl_lg, 'placeholder': 'e.g. Germany, Canada, UK'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': _ctrl_lg, 'placeholder': 'Create a strong password', 'autocomplete': 'new-password'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': _ctrl_lg, 'placeholder': 'Repeat your password', 'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ('email', 'full_name', 'username', 'country_of_origin', 'current_country', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.country_of_origin = self.cleaned_data.get('country_of_origin', '')
        user.current_country = self.cleaned_data.get('current_country', '')
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email Address', widget=forms.EmailInput(attrs={'class': _ctrl_lg, 'placeholder': 'your@email.com', 'autofocus': True, 'autocomplete': 'email'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': _ctrl_lg, 'placeholder': 'Your password', 'autocomplete': 'current-password'}))


class EditProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.Select, forms.Textarea)):
                field.widget.attrs.setdefault('class', _ctrl)
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', _ctrl)
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', _ctrl)

    full_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': _ctrl, 'placeholder': 'Your full name'})
    )
    bio = forms.CharField(
        max_length=500, required=False,
        widget=forms.Textarea(attrs={
            'class': _ctrl, 'rows': 4,
            'placeholder': 'Tell other students about yourself, your experience abroad, tips…'
        })
    )

    class Meta:
        model = User
        fields = ['full_name', 'country_of_origin', 'current_country',
                  'university', 'study_level', 'year_of_study', 'field_of_study', 'bio']
        widgets = {
            'country_of_origin': forms.TextInput(attrs={'class': _ctrl, 'placeholder': 'e.g. Nigeria, India, Brazil'}),
            'current_country': forms.TextInput(attrs={'class': _ctrl, 'placeholder': 'e.g. Germany, Canada, UK'}),
            'university': forms.TextInput(attrs={'class': _ctrl, 'placeholder': 'Your university name'}),
            'study_level': forms.Select(attrs={'class': _ctrl}),
            'year_of_study': forms.Select(attrs={'class': _ctrl}),
            'field_of_study': forms.TextInput(attrs={'class': _ctrl, 'placeholder': 'e.g. Computer Science, Law, Medicine'}),
        }


class UniversitySubmissionForm(forms.ModelForm):
    class Meta:
        model = UniversitySubmission
        fields = ['university_name', 'country', 'city', 'description', 'website', 'founded_year', 'photo']
        widgets = {
            'university_name': forms.TextInput(attrs={'class': _ctrl, 'placeholder': 'Full official name of the university'}),
            'country': forms.TextInput(attrs={'class': _ctrl, 'placeholder': 'Country where the university is located'}),
            'city': forms.TextInput(attrs={'class': _ctrl, 'placeholder': 'City'}),
            'description': forms.Textarea(attrs={
                'class': _ctrl, 'rows': 5,
                'placeholder': 'Describe the university — programs, campus life, admission, notable facts, your personal experience…'
            }),
            'website': forms.URLInput(attrs={'class': _ctrl, 'placeholder': 'https://www.university.edu'}),
            'founded_year': forms.NumberInput(attrs={'class': _ctrl, 'placeholder': 'e.g. 1950', 'min': 1000, 'max': 2100}),
            'photo': forms.FileInput(attrs={'class': _ctrl, 'accept': 'image/jpeg,image/png,image/webp', 'id': 'photoInput'}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image must be under 5 MB.')
            if not photo.content_type.startswith('image/'):
                raise forms.ValidationError('Please upload a valid image file.')
        return photo


class ScholarshipSubmissionForm(forms.ModelForm):
    class Meta:
        model = ScholarshipSubmission
        fields = [
            'title', 'university_name', 'scholarship_type', 'coverage',
            'stipend_amount', 'stipend_unknown', 'deadline', 'no_deadline',
            'description', 'link',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': _ctrl, 'placeholder': 'e.g. Excellence Scholarship 2025'}),
            'university_name': forms.TextInput(attrs={'class': _ctrl, 'readonly': True}),
            'scholarship_type': forms.Select(attrs={'class': _ctrl}),
            'coverage': forms.Select(attrs={'class': _ctrl}),
            'stipend_amount': forms.NumberInput(attrs={
                'class': _ctrl, 'placeholder': 'e.g. 5000', 'min': 0, 'step': '0.01'
            }),
            'stipend_unknown': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'stipendUnknown'}),
            'deadline': forms.DateInput(attrs={'class': _ctrl, 'type': 'date'}),
            'no_deadline': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'noDeadline'}),
            'description': forms.Textarea(attrs={
                'class': _ctrl, 'rows': 5,
                'placeholder': 'Describe eligibility criteria, application process, and any other relevant details…'
            }),
            'link': forms.URLInput(attrs={'class': _ctrl, 'placeholder': 'https://scholarship-page.edu/apply'}),
        }

    def clean(self):
        cleaned = super().clean()
        stipend_unknown = cleaned.get('stipend_unknown')
        stipend_amount = cleaned.get('stipend_amount')
        no_deadline = cleaned.get('no_deadline')
        deadline = cleaned.get('deadline')

        if not stipend_unknown and stipend_amount is not None and stipend_amount < 0:
            self.add_error('stipend_amount', 'Stipend amount must be a positive number.')

        if not no_deadline and deadline is None:
            # deadline is optional; only validate format if provided (handled by DateField itself)
            pass

        return cleaned
