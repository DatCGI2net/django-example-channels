from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView
from example.forms import RoomCreateForm, RoomInviteUserForm, ChatRoomForm
from django.urls.base import reverse_lazy
from django.utils.decorators import method_decorator
from example.models import Message, Room


User = get_user_model()

login_required_decorators = (login_required(login_url='/log_in/'), )

APP_NAME = 'example'

class RoomOwnerMixins(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        print('form.instance:', form.instance)
        return super(RoomOwnerMixins, self).form_valid(form)
    
    def form_invalid(self, form):
        print('form invalid:', form)
        return super(RoomOwnerMixins, self).form_invalid(form)
    
    def get_success_url(self):
        if self.object and self.object.label:
            label = self.object.label
        else:
            label = kwargs=self.request.POST.get('label')
            
        return reverse('{0}:chatroom'.format(APP_NAME), kwargs={'label':label} )
        
    
@method_decorator(login_required_decorators, name='dispatch') 
class RoomCreateView(RoomOwnerMixins, CreateView):
    form_class = RoomCreateForm
    #success_url = reverse_lazy('example:chatroom')
    template_name = '{0}/createroom.html'.format(APP_NAME)
    
    
        
    
    
@method_decorator(login_required_decorators, name='dispatch') 
class RoomInviteUserView(RoomOwnerMixins, UpdateView):
    model = Room
    fields = ('users', )
    
    
@method_decorator(login_required_decorators, name='dispatch')    
class ChatRoomView(RoomOwnerMixins, CreateView):
    form_class =ChatRoomForm
    ##success_url = reverse_lazy('example:chatroom')
    template_name = '{0}/chatroom.html'.format(APP_NAME)
    
    
    def get_context_data(self, **kwargs):
        ctx = super(ChatRoomView, self).get_context_data(**kwargs)
        
        label = self.kwargs.get('label')
        print 'label:', label
        room = Room.objects.get(label=label)
        ctx['room'] = room
        ctx['messages'] = Message.top_messages(room)
        
        return ctx
    
    

@login_required(login_url='/log_in/')
def user_list(request):
    """
    NOTE: This is fine for demonstration purposes, but this should be
    refactored before we deploy this app to production.
    Imagine how 100,000 users logging in and out of our app would affect
    the performance of this code!
    """
    users = User.objects.select_related('logged_in_user')
    for user in users:
        user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
    return render(request, 'example/user_list.html', {'users': users})


def log_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('example:user_list'))
        else:
            print(form.errors)
    return render(request, 'example/log_in.html', {'form': form})


@login_required(login_url='/log_in/')
def log_out(request):
    logout(request)
    return redirect(reverse('example:log_in'))


def sign_up(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('example:log_in'))
        else:
            print(form.errors)
    return render(request, 'example/sign_up.html', {'form': form})
