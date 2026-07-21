import asyncio
import pytest
from core.execution.v2.dag.engine import DAGEngine
from core.execution.v2.dispatcher.engine import DispatcherEngine

@pytest.mark.asyncio
async def test_integration():
    engine = DAGEngine()
    dispatcher = DispatcherEngine()
    
    # Test propagation
    decision = {"action": "test", "data": {"value": 42}}
    result = await dispatcher.dispatch(decision)
    
    assert result is not None
    assert result["status"] == "dispatched"
    assert result["args"] == (decision,)
    
    print("✅ Test passed")
