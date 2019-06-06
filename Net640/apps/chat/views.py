import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from Net640.apps.chat.models import Message

User = get_user_model()


@login_required
def chat_room(request, person_id):
    # group name for chat
    user_to_chat = get_object_or_404(User, pk=person_id)
    id_list = [request.user.pk, int(person_id)]
    id_list.sort()
    room_name = "room_"+str(id_list[0])+"_with_"+str(id_list[1])

    messages = Message.objects.filter(chat_room=room_name)

    return render(request, 'chat/room.html', {
        # 'room_name': mark_safe(json.dumps(room_name)),
        'room_name': room_name,
        'user_to_chat': user_to_chat,
        'user': request.user,
        'messages': messages
    })
