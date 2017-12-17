from django import forms
from models import Room, Message
from django.contrib.auth import get_user_model
from example.models import get_online_users


User = get_user_model()

class RoomCreateForm(forms.ModelForm):
    
    class Meta:
        model = Room
        fields = ('label',)
        
        
class RoomInviteUserForm(forms.ModelForm):
    online_users = get_online_users()
    
    users = forms.ModelMultipleChoiceField(queryset=online_users)
    class Meta:
        model = Room
        fields = ('users',)

class ChatRoomForm(forms.ModelForm):
    
    class Meta:
        model = Message
        fields = ('message', )
        
        
