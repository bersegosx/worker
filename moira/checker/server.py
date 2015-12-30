import multiprocessing
from sys import executable
from os import environ
from twisted.application import service
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ProcessProtocol
from moira.checker.subscriber import SubscriberService
from moira.graphite import datalib
from moira.db import Db
import os


CHECKER_PATH = os.path.abspath(
    os.path.join(
        os.path.abspath(
            os.path.dirname(__file__)), 'check.py'))


class CheckerProcessProtocol(ProcessProtocol):

    def connectionMade(self):
        log.msg("Run checker - %s" % self.transport.pid)

    def processEnded(self, reason):
        log.msg("Checker process ended with reason: %s" % reason)
        if reactor.running:
            reactor.stop()


class TopService(service.MultiService):

    checkers = []

    def startService(self):
        service.MultiService.startService(self)
        for i in range(max(1, multiprocessing.cpu_count() - 1)):
            checker = reactor.spawnProcess(
                CheckerProcessProtocol(), executable, [
                    'moira-checker', CHECKER_PATH, str(i)], childFDs={
                    0: 'w', 1: 1, 2: 2}, env=environ)
            self.checkers.append(checker)

    def stopService(self):
        for process in self.checkers:
            process.signalProcess('INT')

topService = TopService()

db = Db()
datalib.db = db
db.setServiceParent(topService)

subService = SubscriberService(db)
subService.setServiceParent(topService)

application = service.Application("moira-worker-subscriber")
topService.setServiceParent(application)
