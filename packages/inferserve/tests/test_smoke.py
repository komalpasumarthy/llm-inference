from importlib.metadata import version


def test_inferserve_is_installed() -> None:
    assert version("inferserve")


def test_infercalc_is_available_to_inferserve() -> None:
    # Imported inside the test so a broken workspace link shows up as one clear
    # test failure instead of an error that stops pytest from collecting the file.
    import infercalc

    assert infercalc.__name__ == "infercalc"
