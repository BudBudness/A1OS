from system.loader import PluginLoader
from executive.ceo import CEO
from applications.audit_dashboard import AuditDashboard
import os

# 1. Initialize
PluginLoader.load_plugins(os.path.expanduser("~/A1OS/plugins/"))
ceo = CEO("A1")

# 2. Perform Actions
ceo.delegate('Marketing', 'Launch Summer Campaign')

# 3. View Dashboard
dashboard = AuditDashboard()
dashboard.run()
