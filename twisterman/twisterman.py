from twisted.internet import protocol
from twisted.python import log
from datetime import datetime
import sys

class ProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, name):
        self.name = name
    
    def connectionMade(self):
        self.printLine("started with pid %s" % str(self.transport.pid))

    def processEnded(self, status):
        self.printLine("process terminated")
        reactor.stop()

    def printLine(self, message):
        print "%s %s    | %s" % (datetime.now().strftime("%H:%M:%S"), self.name,
                                 message)

from twisted.internet import reactor
reactor.spawnProcess(ProcessProtocol("ls"), "/bin/ls")
reactor.run()
