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

    '''
    get the first 27 character of last messages, total unread messages, in chat and other needed fields, 
    then return it as list object.
    '''
    
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
            last_message = Chat.objects.values('sender__username', 'reciver__username', 'message', 'timestamp','sender__id','reciver__id','is_read').filter(Q(sender=sender,reciver=item) | Q(sender=item,reciver=sender)).last()
            if last_message != None:
                if len(last_message['message']) > 33:
                    last_message['message'] = last_message['message'][:37]+' ...'
                chatviewlist.append(last_message)
    
    ''' Total unread messages of user '''
    count = 0
    for item in chatviewlist:
        if item['reciver__id'] == request.user.id and item['is_read'] == False:
            count += 1
    counter = 0
    for item in chatviewlist:
        if item['reciver__id'] == request.user.id:
            item['reciver__id'] = item['sender__id']
            item['reciver__username'] = item['sender__username']
            if item['is_read'] == False:
                counter += 1
                item['unread_count'] = counter
        elif item['sender__id'] == request.user.id:
            item['sender__id'] = item['reciver__id']
            item['sender__username'] = item['reciver__username']
    
    chatviewlist = sorted(chatviewlist, key=lambda i: i['timestamp'], reverse=True)

    return chatviewlist, count

def get_chat_detail(request,pk):
    sender = request.user
    reciver = CustomUser.objects.get(id=pk)        
    object = Chat.objects.values("id","reciver__username","sender__username","message", "timestamp","sender__id",'reciver__id', "is_read").filter(Q(sender=sender, reciver=reciver) | Q(sender=reciver, reciver=sender))
    x=0
    
    for item in object:
    
        if len(item['message']) > 37:

            if item['message'][25:32].find(' ') >= 32:
                x = item['message'][32:37].find(' ')
                item['message'] = item['message'][:x] + '\n' + item['message'][x:]
            else:
                item['message'] = item['message'][:32] + '\n' + item['message'][32:]


    for item in object:
        
        if request.user.id == item["reciver__id"]:
            read_chat=Chat.objects.get(id=item['id'])
            read_chat.is_read = True
            read_chat.save()


    return object  


def ChatDetailViewtwo(request,pk):
    '''
    return the list of chat between two participate
    '''
    if not request.POST:
        
        listobject, count = get_chat_list(request,pk)

        context =  { 
        'object' : get_chat_detail(request,pk) ,
        'listobject': listobject,
        'count' : count
        }

        return render(request, 'chat_detailtwo.html',context=context)    

    else:
        sender = request.user
        reciver = CustomUser.objects.get(id=pk)
        message = request.POST.get('message')
        chat_msg = Chat(sender=sender, reciver=reciver, message=message)
        Chat.save(chat_msg)
        
        listobject, count = get_chat_list(request,pk)

        context =  { 
        'object' : get_chat_detail(request,pk),
        "listobject" : listobject,
        "count" : count
        }
        
        return render(request, 'chat_detailtwo.html', context=context)


