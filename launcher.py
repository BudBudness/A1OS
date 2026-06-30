import logging
from control_plane.control_plane import ControlPlane
from control_plane.runtime_adapter import RuntimeAdapter
from control_plane.event_bus import EventBus
from control_plane.secret_vault import SecretVault
from control_plane.lifecycle_manager import LifecycleManager
from control_plane.capability_contract import CapabilityContract
from control_plane.persistence_manager import PersistenceManager
from control_plane.watchdog import Watchdog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A1OS-Launcher")

# 1. Initialize Infrastructure with Persistence
bus = EventBus()
vault = SecretVault()
pm = PersistenceManager()

# 2. Setup Security with Persistent State
# The contract will automatically bootstrap grants from the database
contracts = CapabilityContract(persistence_manager=pm)

# 3. Setup Kernel Core
cp = ControlPlane(None, bus, vault, contracts)
adapter = RuntimeAdapter(cp)
cp.set_runtime_adapter(adapter)

# 4. Lifecycle & Supervision
lifecycle = LifecycleManager(cp)
lifecycle.scan_and_load("plugins")

watchdog = Watchdog(lifecycle)
watchdog.start()

logger.info("=== A1OS Production Kernel Online: Persistent Security Enabled ===")
