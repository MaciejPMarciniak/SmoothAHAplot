import pytest

from src.aha import aha


@pytest.fixture
def exp_strain_data() -> list[int]:
    return [
        -13,
        -14,
        -16,
        -20,
        -19,
        -18,
        -19,
        -23,
        -19,
        -21,
        -20,
        -20,
        -23,
        -22,
        -28,
        -25,
        -26,
    ]


@pytest.fixture
def exp_mw_data() -> list[int]:
    return [
        1926,
        1525,
        1673,
        2048,
        2325,
        2200,
        2197,
        2014,
        1982,
        2199,
        2431,
        2409,
        2554,
        2961,
        2328,
        2329,
        2288,
    ]


@pytest.fixture
def segments_17() -> list[str]:
    return [
        "Basal Anterior",
        "Basal Anteroseptal",
        "Basal Inferoseptal",
        "Basal Inferior",
        "Basal Inferolateral",
        "Basal Anterolateral",
        "Mid Anterior",
        "Mid Anteroseptal",
        "Mid Inferoseptal",
        "Mid Inferior",
        "Mid Inferolateral",
        "Mid Anterolateral",
        "Apical Anterior",
        "Apical Septal",
        "Apical Inferior",
        "Apical Lateral",
        "Apex",
    ]


@pytest.fixture
def strain_dict(segments_17: list[int], exp_strain_data: list[int]) -> dict[str, int]:
    return {k: v for (k, v) in zip(segments_17, exp_strain_data)}


@pytest.fixture
def mw_dict(segments_17: list[int], exp_mw_data: list[int]) -> dict[str, int]:
    return {k: v for (k, v) in zip(segments_17, exp_mw_data)}


def test_strain_plotting(strain_dict: dict[str, int]) -> None:
    strain_plot = aha.AHA(strain_dict, "Strain")
    strain_plot.bullseye_smooth(True)


def test_mw_plotting(mw_dict: dict[str, int]) -> None:
    mw_plot = aha.AHA(mw_dict, "MyocardialWork")
    mw_plot.bullseye_smooth(True)
