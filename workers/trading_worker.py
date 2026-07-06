from twisted.internet import reactor
from ctrader_open_api import Client

class TradingWorker:
    def __init__(self, config):
        self.config = config
    def start(self):
        print('Worker initialized and started.')
