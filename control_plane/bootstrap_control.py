from control_plane.control_plane import ControlPlane

def init_control():
    cp = ControlPlane("~/A1OS")

    modules = [
        "generators.modules.api_gen",
        "generators.modules.memory_gen",
        "generators.modules.agent_gen",
        "generators.modules.workflow_gen",
        "generators.modules.security_gen",
        "generators.modules.consensus_gen",
        "generators.modules.events_gen"
    ]

    for m in modules:
        cp.register(m.split(".")[-1], m)

    cp.start()
    return cp
