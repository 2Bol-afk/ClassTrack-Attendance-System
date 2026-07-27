from django import forms

from .models import Course, Subject, SubjectOffering


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. BSED',
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Bachelor of Secondary Education',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        duplicate = Course.objects.filter(name__iexact=name)
        if self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise forms.ValidationError('A course with this name already exists.')
        return name

    def clean_description(self):
        return self.cleaned_data['description'].strip()


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['course', 'subject_code', 'name', 'semester_number', 'year_level']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'semester_number': forms.Select(attrs={'class': 'form-control'}),
            'year_level': forms.Select(attrs={'class': 'form-control'}),
        }


class AssignSubjectForm(forms.ModelForm):
    """
    Used mainly to render consistent widgets on the assignment pages.
    """

    class Meta:
        model = SubjectOffering
        fields = ['subject', 'teacher', 'year', 'section', 'school_year']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}),
            'school_year': forms.TextInput(attrs={'class': 'form-control'}),
        }
