from core.kernel import Kernel
def handle_request(payload):
    k = Kernel()
    return k.process_input(payload)
