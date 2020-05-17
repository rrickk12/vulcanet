import sys, cmd
from twisted.python import log
from twisted.internet import reactor, stdio
from twisted.internet.protocol import ServerFactory, ClientFactory, Protocol
from twisted.protocols.basic import LineReceiver
from os import linesep

class Cmd(cmd.Cmd):

    def do_call(self, arg):
        call_id = arg.split()[0]
        request = json.dumps({'command': 'call', 'id': call_id})
        return request

    def do_answer(self, arg):
        operator = arg.split()[0]
        request =  json.dumps({'command': 'answer', 'id': operator})
        return request

    def do_reject(self, arg):
        operator = arg.split()[0]
        request = json.dumps({'command': 'reject', 'id': operator})
        return request

    def do_hangup(self, arg):
        call=arg.split()[0]
        request = json.dumps({'command': 'hangup', 'id': call})
        return request

class Echo(LineReceiver):

    delimiter = linesep.encode("ascii")

    def connectionMade(self):
        self.transport.write(b'>>> ')

    def lineReceived(self, line):
        self.sendLine(b'Echo: ' + line)
        self.transport.write(b'>>> ')

class EchoClientProtocol(Protocol):
    def dataReceived(self, data):
        log.msg('Data received {}'.format(data))
        self.transport.loseConnection()

    def connectionMade(self):
        data = 'Hello, Server!'
        self.transport.write(data.encode())
        log.msg('Data sent {}'.format(data))

    def connectionLost(self, reason):
        log.msg('Lost connection because {}'.format(reason))



class EchoClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        log.msg('Started to connect.')

    def buildProtocol(self, addr):
        log.msg('Connected.')
        return EchoClientProtocol()

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection. Reason: {}'.format(reason))

    def clientConnectionFailed(self, connector, reason):
        log.msg('Lost failed. Reason: {}'.format(reason))


def main():
    log.startLogging(sys.stdout)
    log.msg('Start your engines...')
    stdio.StandardIO(Echo())
    reactor.connectTCP('localhost', 5678, EchoClientFactory())
    reactor.run()


if __name__ == '__main__':
    main()