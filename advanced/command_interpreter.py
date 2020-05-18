import sys
from cmd import Cmd
from twisted.python import log
from twisted.internet import reactor, stdio
from twisted.internet.protocol import ServerFactory, Factory, Protocol
from twisted.protocols.basic import LineReceiver
from os import linesep

class Command(Cmd):
    #create the cmd functions to be passed by stdin
    #this functions parse the input data and deliver the message as a json format
    #call <id> {"command": "call", "id": "<id>"}
    def do_call(self, arg):
        call_id = arg.split()[0]
        request = ('{"command": "call", "id": '+call_id+'}')
        reactor.callFromThread(connect,request)
    #answer <id> {"command": "answer", "id": "<id>"}
    def do_answer(self, arg):
        operator = arg.split()[0]
        request = ('{"command": "answer", "id": '+'"'+operator+'"'+'}')
        reactor.callFromThread(connect,request)
    #reject <id> {"command": "reject", "id": "<id>"}
    def do_reject(self, arg):
        operator = arg.split()[0]
        request = ('{"command": "reject", "id": '+'"'+operator+'"'+'}')
        reactor.callFromThread(connect,request)
    #hangup <id> {"command": "hangup", "id": "<id>"}
    def do_hangup(self, arg):
        call=arg.split()[0]
        request = ('{"command": "hangup", "id": '+call+'}')
        reactor.callFromThread(connect,request)

#this function is the client protocol that connects to te server and send the data over via TCP protocol
class ClientProtocol(Protocol):
    #built in variable
    def __init__(self, dataJSON = None):
        self.dataJSON = dataJSON

    def dataReceived(self, data):
        
#        log.msg('Data received {}'.format(data))
        print(data.decode())
        self.transport.loseConnection()

    def connectionMade(self):
#        log.msg('Data sent {}'.format(self))
        data = self.dataJSON
        self.transport.write(data.encode())
#        log.msg('Data sent {}'.format(data))

    def connectionLost(self, reason):
        pass
#        log.msg('Lost connection because {}'.format(reason))

#This function is the factory that spawns the client process
class ClientFactory(Factory):
    protocol = ClientProtocol
    #built in variable
    def __init__ (self, dataJSON=None):
        self.dataJSON = dataJSON

    def startedConnecting(self, connector):
        #log.msg('Started to connect.')
        pass

    #build the client that will connect to the server
    def buildProtocol(self, addr):
        #log.msg('Connected {}'.format(self.dataJSON))
		
        return ClientProtocol(self.dataJSON)

    def clientConnectionLost(self, connector, reason):
        pass
        #log.msg('Lost connection. Reason: {}'.format(reason))

    def clientConnectionFailed(self, connector, reason):
        pass
        #log.msg('Lost failed. Reason: {}'.format(reason))

#this function recives the data parsed by the cmd and create the tcp connection between the client and server
def connect(data):
	reactor.connectTCP('localhost', 5678, ClientFactory(data))

def main():

    #log.startLogging(sys.stdout)
    #log.msg('Start your engines...')
    #the cmd.loop and reactor.run is a blocking instruction we run cmd in another thread
    reactor.callInThread(Command().cmdloop)
    reactor.run()


if __name__ == '__main__':
    main()
