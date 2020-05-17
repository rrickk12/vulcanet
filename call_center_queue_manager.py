from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver
import json
import queue as Queue



class QueueMananager(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.session_calls=[] # Calls que sao da comunicacao com esse cliente

    # Da hangup em todas as calls desse cliente
    def connectionLost(self, reason):
        for call in self.session_calls:
            self.hangup(call)

    def dataReceived(self, data):
        request = json.loads(data)
        command = request['command']
        id = request['id'].encode('ascii')

        if command=='call':
            response = self.call(id)
            self.respond(response)
        elif command=='answer':
            response= self.answer(id)
            self.respond(response)
        elif command=='reject':
            response = self.reject(id)
            self.respond(response)
        elif command=='hangup':
            response = self.hangup(id)
            self.respond(response)

    # Executa quando uma call eh ignorada por 10 seg
    # tendo execucao semelhante a de quando a call eh
    # rejected, CHAMA RESPOND() DIRETO
    def ignoredCall(self, call_id, operator):
        response = []
        if operator in self.factory.ringingCalls:
            del self.factory.ringingCalls[operator]
            response.append('\nCall ' + call_id + ' ignored by operator ' + operator)
            if self.ring_call(call_id, response):
                self.factory.Operators[operator] = 'available'
                self.respond(self.parseResponse(*response))
                return
            self.ring(operator, call_id, response)
            self.respond(self.parseResponse(*response))

    # Retira a response do vetor e a junta
    # em uma soh com quebra de linhas
    def parseResponse(self, *response):
        index = 0
        parsed_response=''
        while index < len(response)-1:
            parsed_response += response[index] + '\n'
            index+=1
        parsed_response += response[index]
        return parsed_response

    # Responde response para o cliente
    def respond(self, response):
        self.transport.write(response)

    # Chamado para tocar a chamada call_id
    # para o operador operator
    def ring(self, operator, call_id, response):
        self.factory.Operators[operator] = 'ringing'
        self.factory.ringingCalls[operator]=call_id
        response.append('Call ' + call_id + ' ringing for operator ' + operator)
        reactor.callLater(10, self.ignoredCall, call_id, operator)

    # Chamado para verificar, qual operador em
    # self.factory.Operators esta disponivel para
    # responder a call, em seguida chama ring()
    # para tal operador
    def ring_call(self, call_id, response):
        for operator, state in self.factory.Operators.iteritems():
            if state == 'available':
                self.ring(operator, call_id, response)
                return True

    # Remove call de calls_waiting_queue
    def remove_from_queue(self, call):
        auxiliary_queue = Queue.Queue()

        # Vai tirando da calls_waiting_queue e pondo na
        # auxiliary_queue, ate achar a call
        while not self.factory.calls_waiting_queue.empty():
            queue_object = self.factory.calls_waiting_queue.get()
            if queue_object == call:
                # Poe os restantes em auxiliary_queue, deixando call de fora
                while not self.factory.calls_waiting_queue.empty():
                    queue_object = self.factory.calls_waiting_queue.get()
                    auxiliary_queue.put(queue_object)
                # poe tudo de volta em calls_waiting_queue, agora
                # sem o call
                while not auxiliary_queue.empty():
                    queue_object = auxiliary_queue.get()
                    self.factory.calls_waiting_queue.put(queue_object)
                return True
            auxiliary_queue.put(queue_object)

        # Caso nao encontrou so poe de volta tudo na calls_waiting_queue
        while not auxiliary_queue.empty():
            queue_object = auxiliary_queue.get()
            self.factory.calls_waiting_queue.put(queue_object)
            return False

    def call(self, call_id):
        self.session_calls.append(call_id)
        response = []
        response.append('Call ' + call_id + ' received')
        if self.ring_call(call_id,response):
            return self.parseResponse(*response)
        self.factory.calls_waiting_queue.put(call_id)
        response.append('Call ' + call_id + ' waiting in queue')
        return self.parseResponse(*response)

    def answer(self, operator_id):
        response = []
        call_id = self.factory.ringingCalls[operator_id]
        self.factory.Operators[operator_id]='busy'
        self.factory.ongoingCalls[call_id]=operator_id
        del self.factory.ringingCalls[operator_id]
        response.append('Call ' + call_id + ' answered by operator ' + operator_id)
        return self.parseResponse(*response)

    def reject(self, operator_id):
        response = []
        call_id = self.factory.ringingCalls[operator_id]
        del self.factory.ringingCalls[operator_id]
        response.append('Call ' + call_id + ' rejected by operator ' + operator_id)
        if self.ring_call(call_id, response):
            self.factory.Operators[operator_id] = 'available'
            return self.parseResponse(*response)
        self.ring(operator_id, call_id, response)
        return self.parseResponse(*response)

    def hangup(self, call_id):
        for index in range(len(self.session_calls)-1):
            if call_id==self.session_calls[index]:
                del self.session_calls[index]
        response= []
        if call_id in self.factory.ongoingCalls:
            operator = self.factory.ongoingCalls[call_id]
            self.factory.Operators[operator]='available'
            del self.factory.ongoingCalls[call_id]
            response.append('Call ' + call_id + ' finished and operator ' + operator + ' available')
            if not self.factory.calls_waiting_queue.empty():
                 disenqueued_call_id = self.factory.calls_waiting_queue.get()
                 self.ring(operator, disenqueued_call_id, response)
                 return self.parseResponse(*response)
            return self.parseResponse(*response)
        else:
            for operator, respective_call in self.factory.ringingCalls.iteritems():
                if respective_call == call_id:
                    del self.factory.ringingCalls[operator]
                    response.append('Call ' +  call_id + ' missed')
                    self.factory.Operators[operator]='available'
                    if not self.factory.calls_waiting_queue.empty():
                        disenqueued_call_id = self.factory.calls_waiting_queue.get()
                        self.ring(operator, disenqueued_call_id, response)
                    return self.parseResponse(*response)
            if self.remove_from_queue(call_id):
                response.append('Call ' + call_id + ' missed')
                return self.parseResponse(*response)

class QueueMananagerFactory(protocol.Factory):
    def __init__(self):
        self.Operators = {'A':'available', 'B':'available'}  # operator:state
        self.ringingCalls = {}                               # operator:call_id
        self.ongoingCalls = {}                               # call_id:operator
        self.calls_waiting_queue = Queue.Queue()

    def buildProtocol(self, addr):
        return QueueMananager(self)