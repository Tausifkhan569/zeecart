from django import forms
from django.core.exceptions import ValidationError
from django.db.models import fields
from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):                        #class Registraionform(formds module.classModelForm)
    password=forms.CharField(widget=forms.PasswordInput(attrs={ #password var will 
        'placeholder':'Enter Password',
        'class':'form-control',
    }))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'confirm Password',
        'class':'form-control',
        
    }))
    def clean(self):
        cleaned_data=super(RegistrationForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')
        if password!= confirm_password:
            raise ValidationError(
                "Password does not match "
            )    
    
    def __init__ (self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder']="Enter First Name"
        self.fields['last_name'].widget.attrs['placeholder']="Enter Last Name"
        self.fields['email'].widget.attrs['placeholder']="Enter Email Address"
        self.fields['phone_number'].widget.attrs['placeholder']="Enter Phone Number"
        
    
    class Meta:
        model=Account
        fields=['first_name','last_name','phone_number','email','password']
        
class UserForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=['first_name','last_name','phone_number']
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model=UserProfile
        fields=['address_line_1','address_line_2','city','state','country','profile_picture']