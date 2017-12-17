from django.conf.urls import url
from example.views import (log_in, log_out, sign_up, user_list,
                           RoomInviteUserView, RoomCreateView, ChatRoomView,)
from django.conf.urls.static import static
from django.conf import settings
 
##static

urlpatterns = [
    url(r'^log_in/$', log_in, name='log_in'),
    url(r'^log_out/$', log_out, name='log_out'),
    url(r'^sign_up/$', sign_up, name='sign_up'),
    url(r'^room/chat/(?P<label>\w+)/$', ChatRoomView.as_view(), name='chatroom'),
    url(r'^room/create$', RoomCreateView.as_view(), name='createroom'),
    url(r'^room/invite/(?P<pk>\d+)/$', RoomInviteUserView.as_view(), name='inviteuser'),
    url(r'^$', user_list, name='user_list')
]

"""
urlpatterns = urlpatterns + static(settings.MEDIA_URL, 
                                   document_root=settings.MEDIA_ROOT)
"""