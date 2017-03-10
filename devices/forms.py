from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


   
class TestMessageForm(forms.Form):
    
    topic = forms.CharField(label='topic', max_length=100)
    message = forms.CharField(label='message', max_length=200)
    

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TestMessageForm, self).__init__(*args, **kwargs)

    def clean_topic(self):
        topic = self.cleaned_data.get('topic')
        try:
            split= topic.split(".")
            account= split[0]
            device = split[1]
            channel= split[3]
            msgformat= split[2]
            
            
        
            
        except:
            raise forms.ValidationError(_('%(string)s is not of at least 4 elements separated by .'),
                  params={'string': topic},
                  )   
        
                   
        if not str(self.user.id) == account:
                raise forms.ValidationError(_('%(string)s does not start with your accountID .'),
                  params={'string': topic},
                  )
        
       
        return topic
        
        