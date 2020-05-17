from twisted.application import internet, service
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from call_center_queue_manager import QueueMananagerFactory

application = service.Application("queue_manager")
queue_managerService = internet.TCPServer(5678, QueueMananagerFactory())
queue_managerService.setServiceParent(application)