class RuntimeKernelContract:
    REQUIRED_ASYNC = (
        "run",
        "emit",
        "register_worker",
    )

    REQUIRED_SYNC = (
        "stop",
        "subscribe",
    )

    @classmethod
    def validate(cls, runtime):
        import inspect

        for name in cls.REQUIRED_ASYNC:
            if not inspect.iscoroutinefunction(getattr(runtime, name)):
                raise TypeError(f"{name} must be async")

        for name in cls.REQUIRED_SYNC:
            if not callable(getattr(runtime, name)):
                raise TypeError(f"{name} must be callable")

        return True
