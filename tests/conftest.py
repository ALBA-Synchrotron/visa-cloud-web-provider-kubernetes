def pytest_addoption(parser):
    parser.addoption(
        "--test-mode",
        action="store",
        choices=["unit", "integration"],
        default="unit",
        help="Select test mode: unit or integration",
    )


def pytest_configure(config):
    mode = config.getoption("--test-mode")

    if mode == "unit":

        modules = [
            f"tests.unit.fixtures.common",
            f"tests.unit.fixtures.kubernetes",
            f"tests.unit.fixtures.flavour",
            f"tests.unit.fixtures.image",
            f"tests.unit.fixtures.security_group",
        ]

        for module in modules:
            config.pluginmanager.import_plugin(module)
