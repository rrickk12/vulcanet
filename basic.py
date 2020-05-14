import cmd

#This basic application accept commads via cmd module to simulate actions performed by a real device
#It handles commands typed in stdin and reports threir results by printing messages to stdout.

#this class holds the call iunformation and functions
class Call():
    def __init__(self,id):
        self.id = id
        self.state = "new"
        self.operator = None
  
    def set_state(self,state):
        self.state = state

    def set_operator(self,operator):
        self.operator = operator

#this function delvier a call to the first operator avaliable
def deliver_call(call):
    operator = operatorStack.pop()
    call.set_operator(operator)
    operatorDict[operator]= "ringing"
    call.set_state("ringing")
    callDict[operator] = call
    print("Call "+str(call.id)+" ringing for operator "+str(operator))


class Cmd(cmd.Cmd):
    
    #makes application receive a call whose id is <id>.
    def do_call(self,arg):
        param = arg.split()
        call = Call(param[0])
        calls[call.id]=call
        print("Call "+str(call.id)+" recieved")
        #if there is no operator available
        if not len(operatorStack):
            print("Call "+str(call.id)+" wainting in queue")
            call.set_state("waiting")
            callQueue.append(call)
        else:
            deliver_call(call)

    def do_answer(self,arg):
        param = arg.split()
        operator = param[0]
        operatorDict[operator]="busy"
        call = callDict[operator]
        call.set_state("awnsered")
        print("Call "+str(call.id)+" answered by operator "+str(operator))
        
    def do_reject(self,arg):
        param = arg.split()
        operator = param[0]
        call = callDict[operator]
        operatorDict[operator]="available"
        operatorStack.append(operator)
        call.set_state("rejected")
        print("Call "+str(call.id)+" rejected by operator "+str(operator))
        if not operatorStack == []:
            deliver_call(call)
        
    def do_hangup(self,arg):
        param = arg.split()
        call=calls[param[0]]
        operator=call.operator
        if call.state == "ringing" or call.state == "waiting":
            if call.state == "waiting":
                callQueue.remove(call)
            if call.state == "ringing":
                operatorDict[operator]= "available"
                operatorStack.append(operator)
            print("Call "+str(call.id)+" missed")
        else:
            print("Call "+str(call.id)+" finished and operator "+str(operator)+" available")
            operatorDict[operator]="available"
            operatorStack.append(operator)
            calls[call.id] = None
        if not callQueue == []:
            call = callQueue[0]
            callQueue.remove(call)
            deliver_call(call)


operatorDict = {"A": "available", "B": "available"}
callDict = {}
calls = {}
callQueue = []
operatorStack = []
operatorStack.append("B")
operatorStack.append("A")

Cmd=Cmd()
Cmd.prompt = ''
Cmd.cmdloop()