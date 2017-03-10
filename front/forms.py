from django.contrib.auth.models import User
from django.forms import ModelForm

class UserForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
    class Meta:
        model = User
        fields = ('username', 'email', 'password','first_name','last_name')