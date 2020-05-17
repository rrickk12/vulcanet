import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, ClientFactory, Protocol


class EchoServerProtocol(Protocol):
    def dataReceived(self, data):
        log.msg('Data received {}'.format(data))
        self.transport.write(data)

    def connectionMade(self):
        log.msg('Client connection from {}'.format(self.transport.getPeer()))

    def connectionLost(self, reason):
        log.msg('Lost connection because {}'.format(reason))


class EchoServerFactory(ServerFactory):
    def buildProtocol(self, addr):
        return EchoServerProtocol()

def main():
    log.startLogging(sys.stdout)
    log.msg('Start your engines...')
    reactor.listenTCP(5678, EchoServerFactory())
    reactor.run()


if __name__ == '__main__':
    main()