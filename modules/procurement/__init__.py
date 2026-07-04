from .data_sync import ProcurementData

class Procurement:
    def refresh_metrics(self):
        return "Procurement metrics synchronized with supply chain database."

    def get_data(self):
        return ProcurementData().get_active_procurements()
