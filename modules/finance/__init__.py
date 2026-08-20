try:
    from .engine import FinanceEngine
except ImportError as exc:
    if exc.name != "finance.engine":
        raise
    FinanceEngine = None

Finance = FinanceEngine
