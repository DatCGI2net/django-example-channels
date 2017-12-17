from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.decorators import classonlymethod

##User = get_user_model()

def get_online_users():
    User = get_user_model()
    users = User.objects.exclude(logged_in_user__user__isnull=True)
    return users

class LoggedInUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='logged_in_user')

        

## from https://github.com/ddollar/foreman
class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, 
                              related_name='rooms')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    
    def __unicode__(self):
        return self.label
    

    

class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages')
    ##handle = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, 
                              related_name='owner_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __unicode__(self):
        return '[{timestamp}] {room}: {message}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p')
    
    def as_dict(self):
        return {'owner': self.owner.username, 'room': self.room.label, 'message': self.message, 
                'timestamp': self.formatted_timestamp}
        
        
    class Meta:
        ordering = ('-timestamp', )
        
    @classonlymethod
    def top_messages(self, room):
        return self.objects.filter(room=room).all()[:10]     
    