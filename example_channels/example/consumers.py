import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
import re
import logging
from channels.sessions import channel_session
from .models import Room

log = logging.getLogger(__name__)

def send_user_login(group, message, is_logged_in):
    ##print 'message:', message.__dict__
    
    group.send({
        'text': json.dumps({
            'username': message.user.username,
            'is_logged_in': is_logged_in
        })
    })


@channel_session_user_from_http
def ws_connect(message):
    # Extract the room from the message. This expects message.path to be of the
    # form /room/chat/{label}/, and finds a Room if the message path is applicable,
    # and if the Room exists. Otherwise, bails (meaning this is a some othersort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    try:
        prefixroom, prefix, label = message['path'].decode('ascii').strip('/').split('/')
        if prefix != 'chat':
            log.debug('invalid ws path=%s', message['path'])
            return
        room = Room.objects.get(label=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return

    log.debug('chat connect room=%s client=%s:%s', 
        room.label, message['client'][0], message['client'][1])
    
    # Need to be explicit about the channel layer so that testability works
    # This may be a FIXME?
    group = Group('chat-'+label, channel_layer=message.channel_layer)
    group.add(message.reply_channel)
    send_user_login(group, message, True)
    
    message.channel_session['room'] = room.label


@channel_session_user
def ws_receive(message):
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
    except KeyError:
        log.debug('no room in channel_session')
        return
    except Room.DoesNotExist:
        log.debug('recieved message, buy room does not exist label=%s', label)
        return

    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
        data['owner'] = message.user
        data['room'] = room
        
        print 'Got data:', data
    except ValueError:
        log.debug("ws message isn't json text=%s", message)
        return
    
    if set(data.keys()) != set(('owner', 'message', 'room')):
        log.debug("ws message unexpected format data=%s", data)
        return

    if data:
        log.debug('chat message room=%s handle=%s message=%s', 
            room.label, data['owner'], data['message'])
        try:
            m = room.messages.create(**data)
            print('message created', m.id)
        except Exception as err:
            print "Could not create message. Reason:", err
            

        # See above for the note about Group
        Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(m.as_dict())})

@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
        group = Group('chat-'+label, channel_layer=message.channel_layer)
        group.discard(message.reply_channel)
        send_user_login(group, message, False)
    except (KeyError, Room.DoesNotExist):
        pass
