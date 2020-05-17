import sys
from cmd import Cmd
from twisted.python import log
from twisted.internet import reactor, stdio
from twisted.internet.protocol import ServerFactory, Factory, Protocol
from twisted.protocols.basic import LineReceiver
from os import linesep

class Command(Cmd):

    def do_test(self, arg):
        call_id = arg.split()[0]
        reactor.callFromThread(on_main_thread,call_id)
        

    def do_call(self, arg):
        call_id = arg.split()[0]
        request = ("{'command': 'call', 'id': "+call_id+"}")
        reactor.callFromThread(on_main_thread,request)

    def do_answer(self, arg):
        operator = arg.split()[0]
        request = ("{'command': 'answer', 'id': "+operator+"}")
        reactor.callFromThread(on_main_thread,request)

    def do_reject(self, arg):
        operator = arg.split()[0]
        request = ("{'command': 'reject', 'id': "+operator+"}")
        reactor.callFromThread(on_main_thread,request)

    def do_hangup(self, arg):
        call=arg.split()[0]
        request = ("{'command': 'hangup', 'id': "+call+"}")
        reactor.callFromThread(on_main_thread,request)

class EchoClientProtocol(Protocol):

    def __init__(self, dataJSON = None):
        self.dataJSON = dataJSON

    def dataReceived(self, data):
        log.msg('Data received {}'.format(data))
        self.transport.loseConnection()

    def connectionMade(self):
        log.msg('Data sent {}'.format(self))
        data = self.dataJSON
        self.transport.write(data.encode())
        log.msg('Data sent {}'.format(data))

    def connectionLost(self, reason):
        log.msg('Lost connection because {}'.format(reason))



class EchoClientFactory(Factory):
    protocol = EchoClientProtocol

    def __init__ (self, dataJSON=None):
        self.dataJSON = dataJSON

    def startedConnecting(self, connector):
        log.msg('Started to connect.')

    def buildProtocol(self, addr):
        log.msg('Connected {}'.format(self.dataJSON))
		
        return EchoClientProtocol(self.dataJSON)

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection. Reason: {}'.format(reason))

    def clientConnectionFailed(self, connector, reason):
        log.msg('Lost failed. Reason: {}'.format(reason))

def on_main_thread(data):
	reactor.connectTCP('localhost', 5678, EchoClientFactory(data))

def main():

    log.startLogging(sys.stdout)
    log.msg('Start your engines...')
    reactor.callInThread(Command().cmdloop)
    reactor.run()


if __name__ == '__main__':
    main()
