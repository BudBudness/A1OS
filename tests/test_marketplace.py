from workflow.marketplace import Marketplace

# Test dynamic loading of finance_app
app = Marketplace.load_app("finance_app")
if app:
    print(f"App loaded: {app.__name__}")
    # Verify the app contains the expected class
    if hasattr(app, "FinanceApp"):
        print("Verification: FinanceApp class identified.")
else:
    print("Marketplace failed to load app.")
