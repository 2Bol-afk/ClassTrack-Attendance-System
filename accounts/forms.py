from django import forms
from .models import TeacherProfile,CustomUser,StudentProfile,ParentProfile
from academics.models import CourseMajor, Subject, Semester
class TeacherUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.role = 'teacher'
        if commit:
            user.save()
        return user

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['first_name','middle_name','last_name']
        widgets = {
            'first_name':forms.TextInput(attrs={'class':'form-control'}),
            'middle_name':forms.TextInput(attrs={'class':'form-control'}),
            'last_name':forms.TextInput(attrs={'class':'form-control'}),
        }

class StudentUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    def save(self,commit = True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.role = 'student'
        if commit:
            user.save()
        return user



class StudentProfileForm(forms.ModelForm):
    semester = forms.ChoiceField(
        choices=[('1st', '1st Semester'), ('2nd', '2nd Semester')],
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = StudentProfile
        fields = [
            'student_ID','first_name','middle_name','last_name',
            'course','major','year','section','is_regular','subjects'
        ]
        widgets = {
            'student_ID': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class':'form-control','id':'id_course'}),
            'major': forms.Select(attrs={'class':'form-control','id':'id_major'}),
            'year': forms.Select(attrs={'class':'form-control','id':'id_year'}),
            'section': forms.Select(attrs={'class':'form-control'}),
            'is_regular': forms.Select(attrs={'class':'form-control'}),
            'subjects': forms.CheckboxSelectMultiple(),
        }

    # ✅ THIS MUST BE OUTSIDE Meta
    def __init__(self, *args, **kwargs):
        # Get semester from view or default to 1st
        semester = kwargs.pop('semester', '1st')
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)

        course_id = self.data.get('course') if self.is_bound else course
        if not course_id and getattr(self.instance, 'course_id', None):
            course_id = self.instance.course_id

        # Filter subjects by semester
        subjects_qs = Subject.objects.filter(semester_number=semester)
        if course_id:
            subjects_qs = subjects_qs.filter(course_id=course_id)

        self.fields['subjects'].queryset = subjects_qs
        self.fields['major'].queryset = CourseMajor.objects.none()
        self.fields['major'].required = False
        self.fields['major'].empty_label = 'No major / specialization'

        if course_id:
            try:
                self.fields['major'].queryset = CourseMajor.objects.filter(
                    course_id=int(course_id)
                )
            except (TypeError, ValueError):
                pass

        # Pre-check all subjects if student is regular
        if (self.initial.get('is_regular') == 'Regular') or (getattr(self.instance, 'is_regular', None) == 'Regular'):
            self.fields['subjects'].initial = list(subjects_qs.values_list('id', flat=True))

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        major = cleaned_data.get('major')
        if major and major.course_id != getattr(course, 'id', None):
            self.add_error('major', 'Select a major that belongs to the chosen course.')
        return cleaned_data

class parentUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email']
        widgets = {
            'email':forms.EmailInput(attrs={'class': 'form-control'})
        }
    def save(self,commit = True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.role = 'parent'
        if commit:
            user.save()
        return user
    
class parentProfileForm(forms.ModelForm):
    class Meta:
        model  = ParentProfile
        fields = ['first_name','middle_name','last_name','contact_number']
        widgets = {
            'first_name':forms.TextInput(attrs={'class':'form-control'}),
            'middle_name':forms.TextInput(attrs={'class':'form-control'}),
            'last_name':forms.TextInput(attrs={'class':'form-control'}),
            'contact_number':forms.TextInput(attrs={'class':'form-control'})
        }
