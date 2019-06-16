from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from Net640.apps.chat.models import Message

User = get_user_model()


@login_required
@require_GET
def chat_room(request, person_id):
    """
    Prepare variables for creating chat room.
    Render chat room from template.
    """
    # Group name for chat. It's uniq.
    user_to_chat = get_object_or_404(User, pk=person_id)
    id_list = [request.user.pk, int(person_id)]
    id_list.sort()
    room_name = "room_" + str(id_list[0]) + "_with_" + str(id_list[1])

    # show messages stored id DB to user
    messages = Message.objects.filter(chat_room=room_name)

    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'user_to_chat': user_to_chat,
        'user': request.user,
        'messages': messages
    })


@login_required
@require_POST
def user_message_action(request):
    """
    Process any action on user messages.
    For example - remove message.
    """
    context = {}
    user = request.user
    message_id = request.POST.get('message_id', None)
    message = get_object_or_404(Message, id=message_id)
    action = request.POST.get('action', None)

    if action == 'remove':
        if user == message.author:
            message.delete()
            context.update({"result": True})
    return JsonResponse(context)
