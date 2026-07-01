import json

class A1OSPlugin:
    def process_event(self, event_type, data):
        raise NotImplementedError

class ResourceMonitor(A1OSPlugin):
    def process_event(self, event_type, data):
        if event_type == "RESOURCE_UPDATE":
            entropy = (data['threshold'] - data['state_value']) / data['threshold']
            return {"action": "MAINTENANCE" if entropy > 0.5 else "STABLE", "entity": data['entity_id']}

class MarketIntelligence(A1OSPlugin):
    def process_event(self, event_type, data):
        if event_type == "MARKET_SIGNAL":
            return {"action": "UPDATE_DASHBOARD", "analysis": "ACTIONABLE" if data['value'] > 0 else "NOISE"}

PLUGIN_REGISTRY = {
    "RESOURCE_UPDATE": ResourceMonitor(),
    "MARKET_SIGNAL": MarketIntelligence()
}

def execute_engine(event_type, json_data):
    data = json.loads(json_data)
    plugin = PLUGIN_REGISTRY.get(event_type)
    if plugin:
        return plugin.process_event(event_type, data)
    return None

if __name__ == "__main__":
    res = execute_engine("RESOURCE_UPDATE", '{"entity_id": "ASSET_01", "state_value": 20.0, "threshold": 100.0}')
    mkt = execute_engine("MARKET_SIGNAL", '{"source": "API_ALPHA", "signal_type": "PRICE_SWING", "value": 1.5, "timestamp": 1719856200}')
    print(json.dumps({"resource_result": res, "market_result": mkt}))
