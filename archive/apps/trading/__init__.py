from apps.base import BaseApp

class TradingEngine(BaseApp):
    def run(self, *args, **kwargs):
        pass
    def health_check(self) -> bool:
        return True
