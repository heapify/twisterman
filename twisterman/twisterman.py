
from twisted.internet import protocol
from twisted.application import service
from twisted.python import log
from datetime import datetime
import sys
from wrappers import Procfile
from twisted.internet import reactor as _reactor


class ProcessProtocol(service.Service, protocol.ProcessProtocol):

    def __init__(self, name, commandline, reactor=_reactor):
        self.reactor = reactor
        self.setName(name)
        self.commandline = commandline
    
    def connectionMade(self):
        self.printLine("started with pid %s" % str(self.transport.pid))

    def processEnded(self, status):
        self.printLine("process terminated")

    def printLine(self, message):
        print "%s %s    | %s" % (datetime.now().strftime("%H:%M:%S"), self.name,
                                 message)

    def startService(self):
        self.reactor.spawnProcess(self, "sh", args=('-c', self.commandline))


    def stopService(self):
        self.transport.signalProcess('KILL')


class ProcessManager(service.MultiService, service.Service):
    def __init__(self, reactor=_reactor, procfile="Procfile"):
        self.reactor = reactor
        self.procfile = Procfile(procfile)

    def startService(self):
        for name, commandline in self.procfile.iteritems():
            protocol = ProcessProtocol(name, commandline)
            protocol.setServiceParent(self)
            protocol.startService()



