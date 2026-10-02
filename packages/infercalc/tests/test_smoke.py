from importlib.metadata import version


def test_infercalc_is_installed() -> None:
    # Reads the version from the installed package metadata, not from the source
    # folder, so this only passes if the workspace actually installed infercalc.
    assert version("infercalc")
