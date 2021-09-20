from article.views import CommentCreateView
from django.core.checks import messages
from django.shortcuts import render
from ChatApp.models import Chat
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.conf import settings
from accounts.models import CustomUser
from django.db.models import Q
# Create your views here.

class ChatCreateView(LoginRequiredMixin , CreateView):

    model = Chat
    fields = ('message')
    template_name = 'chat_create.html'

    def form_valid(self, form, pk):
        form.instance.sender = self.request.user
        #print (self.request.POST['reciver'])
        form.instance.reciver = CustomUser.objects.get(id=pk)#int(self.request.POST['reciver']))
        form.instance.message = self.request.POST.get('message')
        return super().form_valid(form)

class ChatDetailView(ListView):
    model = Chat
    template_name = 'chat_detail.html'

def get_chat_list(request,pk):
    sender = request.user
    reciver = CustomUser.objects.get(id=pk)
    objectview = Chat.objects.values("reciver__id","sender__id","message", "timestamp").filter(Q(sender=sender) | Q(reciver=sender))        
    listobject = []
    for item in objectview:
        listobject.append(item['reciver__id'])
        listobject.append(item['sender__id'])
        
    final_chat_list = []
    for item in listobject:
        if item not in final_chat_list:
            final_chat_list.append(item)
            
    chatviewlist=[]
    for item in final_chat_list:
        if item != request.user:
            last_message = Chat.objects.values('sender__username', 'reciver__username', 'message', 'timestamp','sender__id','reciver__id').filter(Q(sender=sender,reciver=item) | Q(sender=item,reciver=sender)).last()
            if last_message != None:
                chatviewlist.append(last_message)
    for item in chatviewlist:
        if item['reciver__id'] == request.user.id:
            item['reciver__id'] = item['sender__id']
            item['reciver__username'] = item['sender__username']
        elif item['sender__id'] == request.user.id:
            item['sender__id'] = item['reciver__id']
            item['sender__username'] = item['reciver__username']

    return chatviewlist


def ChatDetailViewtwo(request,pk):
    '''
    return the list of chat between two participate
    '''
    if not request.POST:
        sender = request.user
        reciver = CustomUser.objects.get(id=pk)        
        object = Chat.objects.values("reciver__username","sender__username","message", "timestamp","sender__id").filter(Q(sender=sender, reciver=reciver) | Q(sender=reciver, reciver=sender))
               
        context =  { 
        'object' : object ,
        'listobject': get_chat_list(request,pk)
        }

        return render(request, 'chat_detailtwo.html',context=context)    

    else:
        sender = request.user
        reciver = CustomUser.objects.get(id=pk)
        message = request.POST.get('message')
        chat_msg = Chat(sender=sender, reciver=reciver, message=message)
        Chat.save(chat_msg)
        object = Chat.objects.values("reciver__username","sender__username","message", "timestamp", 'sender__id', 'reciver__id').filter(Q(sender=sender , reciver=reciver) | Q(reciver=sender , sender=reciver))
        
        context =  { 
        'object' : object,
        "listobject" : get_chat_list(request,pk)
        }
        
        return render(request, 'chat_detailtwo.html', context=context)

class ChatListView(ListView):
    model = Chat

