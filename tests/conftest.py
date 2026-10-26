def pytest_addoption(parser) -> None:
    parser.addoption(
        "--test-mode",
        action="store",
        choices=["unit", "integration"],
        default="unit",
        help="Select test mode: unit or integration",
    )


def pytest_configure(config) -> None:
    mode: str = config.getoption("--test-mode")

    modules: list = [
        f"tests.{mode}.fixtures.common",
        f"tests.{mode}.fixtures.flavour",
        f"tests.{mode}.fixtures.image",
        f"tests.{mode}.fixtures.security_group",
    ]

    if mode == "unit":
        modules.append("tests.unit.fixtures.kubernetes")

    for module in modules:
        config.pluginmanager.import_plugin(module)
