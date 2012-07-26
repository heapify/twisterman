from os import environ
from twisted.internet import protocol
from twisted.application import service
from twisted.python import log
from datetime import datetime
import sys
from wrappers import Procfile
from twisted.internet import reactor as _reactor
from twisted.internet import defer
from twisted.python import log

class ProcessProtocol(service.Service, protocol.ProcessProtocol):

    def __init__(self, name, commandline, reactor=_reactor):
        self.reactor = reactor
        self.setName(name)
        self.commandline = commandline
        self.outbuffer = ""
        self.errbuffer = ""
        self.running = False
    
    def connectionMade(self):
        self.printLine("started with pid %s" % str(self.transport.pid))
        self.running = True

    def processExited(self, status):
        self.running = False
        if self.errbuffer:
            self.printLine(self.errbuffer)
            self.errbuffer = ""
        if self.outbuffer:
            self.printLine(self.outbuffer)
            self.outbuffer = ""
        self.printLine("process terminated")
        self.parent.stopService()

    def outReceived(self, data):
        self.outbuffer += data
        while True:
            line, _, remainder = self.outbuffer.partition("\n")
            if not remainder:
                break
            else:
                self.outbuffer = remainder
                self.printLine(line)

    def errReceived(self, data):
        self.errbuffer += data
        while True:
            line, _, remainder = self.errbuffer.partition("\n")
            if not remainder:
                break
            else:
                self.errbuffer = remainder
                self.printLine(line)
                                                                                    

    def printLine(self, message):
        message = message.rstrip()
        log.msg(message, system=self.name)

    def startService(self):
        self.reactor.spawnProcess(self, "sh", args=('sh', '-c', self.commandline), env=environ)


    def stopService(self):
        if self.running:
            self.transport.signalProcess('KILL')

class ProcessManager(service.MultiService, service.Service):
    def __init__(self, reactor=_reactor, procfile="Procfile"):
        service.MultiService.__init__(self)
        self.reactor = reactor
        self.procfile = Procfile(procfile)
        self.running = False

    def startService(self):
        if self.running:
            return
        self.running = True
        for name, commandline in self.procfile.iteritems():
            protocol = ProcessProtocol(name, commandline)
            protocol.setServiceParent(self)


    def stopService(self):
        if not self.running:
            return
        self.running = False
        log.msg("sending SIGTERM to all processes")
        deferreds = []
        for child in self:
            deferreds.append(defer.maybeDeferred(child.stopService))
        d = defer.DeferredList(deferreds)
        d.addErrback(lambda failure: log.err(failure.value))
        d.addBoth(lambda ignored: self.reactor.stop())
        return d
