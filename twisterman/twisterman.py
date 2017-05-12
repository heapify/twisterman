from twisted.internet import protocol
from twisted.application import service
import sys
from wrappers import Procfile, EnvFile
from twisted.internet import reactor as _reactor
from twisted.internet import defer, error
from twisted.python import log
import signal

class ProcessProtocol(service.Service, protocol.ProcessProtocol):

    def __init__(self, name, commandline, reactor=_reactor):
        self.reactor = reactor
        self.setName(name)
        self.commandline = commandline
        self.outbuffer = ""
        self.errbuffer = ""
        self.running = False
        self.kill_switch = None
        self.process_wait = None
    
    def connectionMade(self):
        self.printLine("started with pid %s" % str(self.transport.pid))
        self.running = True

    def processExited(self, status):
        self.running = False
        self.kill_switch, kill_switch = None, self.kill_switch
        self.process_wait, process_wait = None, self.process_wait
        if kill_switch is not None:
            try:
                kill_switch.cancel()
            except error.AlreadyCalled:
                pass
        if process_wait is not None:
            process_wait.callback(None)
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
        self.reactor.spawnProcess(self, "sh",
                                  args=('sh', '-c', self.commandline),
                                  env=self.parent.envfile)
        self.process_wait = defer.Deferred()

    def forceTerminate(self):
        log.msg("Sending SIGKILL to process that didn't exit")
        self.transport.signalProcess('KILL')
        
    def stopService(self):
        if self.running:
            self.transport.signalProcess('TERM')
            self.kill_switch = self.reactor.callLater(30, self.forceTerminate)
        return self.process_wait

class ProcessManager(service.MultiService, service.Service):
    def __init__(self, reactor=_reactor, procfile="Procfile", envfile=".env"):
        service.MultiService.__init__(self)
        self.reactor = reactor
        self.procfile = Procfile(procfile)
        self.envfile = EnvFile(envfile)
        self.stop_count = 0
        self.running = False
        signal.signal(signal.SIGINT, self._signalHandler)

    def startService(self):
        if self.running:
            return
        self.running = True
        for name, commandline in self.procfile.iteritems():
            protocol = ProcessProtocol(name, commandline)
            protocol.setServiceParent(self)

    def _signalHandler(self, signal, _):
        log.msg("Received signal %s" % signal)
        self.stopService()
        self.stop_count += 1

    def stopService(self):
        if not self.running:
            return
        if self.stop_count > 0:
            for child in self:
                if child.running:
                    child.forceTerminate()
        else:
            log.msg("sending SIGTERM to all processes")
            deferreds = []
            for child in self:
                deferreds.append(child.stopService())
            d = defer.DeferredList(deferreds)
            d.addErrback(lambda failure: log.err(failure.value))
            d.addBoth(self._safeTerminateReactor)

    def _safeTerminateReactor(self, _):
        try:
            self.running = False
            self.reactor.stop()
        except error.ReactorNotRunning:
            pass

def main():
    log.startLogging(sys.stdout)
    application = service.Application("twisterman")
    ProcessManager().setServiceParent(application)
    service.IService(application).startService()
    _reactor.run()
