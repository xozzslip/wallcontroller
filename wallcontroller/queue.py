from queue import Queue
from wallcontroller.models import VkApp


tokens_queue = Queue()
for vkapp in VkApp.objects.all():
    tokens_queue.put(vkapp.access_token)
