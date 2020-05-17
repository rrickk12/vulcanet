from twisted.internet import reactor, protocol
from twisted.internet import stdio
from twisted.protocols import basic
from os import linesep
from cmd import Cmd
import json , sys



class CommandProcessor(Cmd):
	def do_send(self,inp):
		payload = {'task': inp}
		m = MyClientProtocol()
		reactor.callFromThread(m.sendTask,payload)

class MyClientProtocol()
	def onConnect(self, response):
		self.factory.connectedProtocol = self

reactor.callInThread(CommandProcessor().cmdloop)
reactor.run()

