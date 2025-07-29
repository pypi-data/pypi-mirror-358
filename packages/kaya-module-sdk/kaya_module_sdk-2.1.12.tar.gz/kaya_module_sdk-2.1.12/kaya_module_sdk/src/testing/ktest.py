def setup_kit_framework(legacy: bool = False) -> type:
    if legacy:
        from kaya_module_sdk.src.testing.kit_harness import KIT
    else:
        from kaya_module_sdk.src.testing.kit_code import KIT  # type: ignore
    return KIT
