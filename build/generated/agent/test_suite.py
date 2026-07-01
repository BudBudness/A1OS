from .core_agent import SovereignAgentCore

def test_agent_subsystem():
    agent = SovereignAgentCore()
    
    # Test built-in ping routine execution
    res = agent.execute_cycle("PING")
    assert res["status"] == "success"
    assert res["result"] == "PONG"
    
    # Test parameter splitting logic sequence
    res_echo = agent.execute_cycle("ECHO msg=SovereignOS")
    assert res_echo["status"] == "success"
    assert res_echo["result"] == "SOVEREIGNOS"
    
    print("✅ Agent Execution Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_agent_subsystem()