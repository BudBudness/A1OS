try:
    from .engine import FinanceEngine
except ImportError:
    FinanceEngine = None

Finance = FinanceEngine
