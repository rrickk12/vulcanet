import sys, json
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, ClientFactory, Protocol

class Call():
    def __init__(self,id):
        self.id = id
        self.state = "new"
        self.operator = None
  
    def set_state(self,state):
        self.state = state

    def set_operator(self,operator):
        self.operator = operator

class ServerProtocol(Protocol):
    
	
    def deliver_call(self,call):
        response = {}
        operator = operatorStack.pop()
        call.set_operator(operator)
        operatorDict[operator]= "ringing"
        call.set_state("ringing")
        callDict[operator] = call
        #log.msg("Call "+str(call.id)+" ringing for operator "+str(operator))
        response["response"]=("Call "+str(call.id)+" ringing for operator "+str(operator))
        self.transport.write(json.dumps(response).encode())

    def dataReceived(self, data):
        response = {}
        #log.msg('Data received {}'.format(data))
        dataJSON = json.loads(data.decode())
        if dataJSON["command"] == 'call':
            call = Call(int(dataJSON['id']))
            calls[call.id]=call
            #log.msg("Call "+str(call.id)+" recieved")
            response["response"]=("Call "+str(call.id)+" recieved")
            self.transport.write(json.dumps(response).encode())
            #if there is no operator available
            if not len(operatorStack):
                #log.msg("Call "+str(call.id)+" wainting in queue")
                response["response"]=("Call "+str(call.id)+" wainting in queue")
                self.transport.write(json.dumps(response).encode())
                call.set_state("waiting")
                callQueue.append(call)
            else:
                self.deliver_call(call)
        elif dataJSON["command"] == 'answer':
            operator = dataJSON['id']
            operatorDict[operator]="busy"
            call = callDict[operator]
            call.set_state("awnsered")
            #log.msg("Call "+str(call.id)+" answered by operator "+str(operator))
            response["response"]=("Call "+str(call.id)+" answered by operator "+str(operator))
            self.transport.write(json.dumps(response).encode())
            
        elif dataJSON["command"] == 'reject':
            operator = dataJSON['id']
            call = callDict[operator]
            operatorDict[operator]="available"
            operatorStack.append(operator)
            call.set_state("rejected")
            #log.msg("Call "+str(call.id)+" rejected by operator "+str(operator))
            response["response"]=("Call "+str(call.id)+" answered by operator "+str(operator))
            self.transport.write(json.dumps(response).encode())
            if not operatorStack == []:
                self.deliver_call(call)

        elif dataJSON["command"] == 'hangup':
            call=calls[dataJSON['id']]
            operator=call.operator
            if call.state == "ringing" or call.state == "waiting":
                if call.state == "waiting":
                    callQueue.remove(call)
                if call.state == "ringing":
                    operatorDict[operator]= "available"
                    operatorStack.append(operator)
                #log.msg("Call "+str(call.id)+" missed")
                response["response"]=("Call "+str(call.id)+" missed")
                self.transport.write(json.dumps(response).encode())
            else:
                #log.msg("Call "+str(call.id)+" finished and operator "+str(operator)+" available")
                operatorDict[operator]="available"
                operatorStack.append(operator)
                calls[call.id] = None
                response["response"]=("Call "+str(call.id)+" finished and operator "+str(operator)+" available")
                self.transport.write(json.dumps(response).encode())
            if not callQueue == []:
                call = callQueue[0]
                callQueue.remove(call)
                self.deliver_call(call)

    #def connectionMade(self):
    #    log.msg('Client connection from {}'.format(self.transport.getPeer()))

    #def connectionLost(self, reason):
    #    log.msg('Lost connection because {}'.format(reason))


class ServerFactory(ServerFactory):
    def buildProtocol(self, addr):
        return ServerProtocol()


operatorDict = {
"A": "available",
"B": "available"}
callDict = {}
calls = {}
callQueue = []
operatorStack = []
operatorStack.append("B")
operatorStack.append("A")
log.startLogging(sys.stdout)
log.msg('Start your engines...')
reactor.listenTCP(5678, ServerFactory())
reactor.run()


