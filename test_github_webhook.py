import asyncio
from launcher_core import A1OSKernel
from generators.modules.github_eng.github_plugin import GitHubPlugin

async def main():
    kernel = A1OSKernel()
    plugin = GitHubPlugin(kernel)
    
    # 1. Simulate a GitHub 'opened' action
    mock_payload = {"action": "opened", "repository": "A1OS", "sender": "Eddie"}
    
    print("🚀 [TEST] Simulating GitHub Webhook arrival...")
    await plugin.handle_webhook(mock_payload, "mock_signature")

if __name__ == "__main__":
    asyncio.run(main())
