import numpy as np
import pytest
from numpy.typing import NDArray


@pytest.fixture
def exp_strain_data_17() -> list[int]:
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
def rand_strain_data_17() -> NDArray:
    rand_strain = np.random.randint(-30, 10, 17)
    return rand_strain


@pytest.fixture
def exp_mw_data_17() -> list[int]:
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
def rand_mw_data_17() -> NDArray:
    rand_mw = np.random.randint(1000, 3000, 17)
    return rand_mw


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
def exp_strain_data_18() -> list[int]:
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
        -18,
    ]


@pytest.fixture
def rand_strain_data_18() -> NDArray:
    rand_strain = np.random.randint(-30, 10, 18)
    return rand_strain


@pytest.fixture
def exp_mw_data_18() -> list[int]:
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
        1800,
    ]


@pytest.fixture
def rand_mw_data_18() -> NDArray:
    rand_mw = np.random.randint(1000, 3000, 18)
    return rand_mw


@pytest.fixture
def segments_18() -> list[str]:
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
        "Apical Anteroseptal",
        "Apical Inferoseptal",
        "Apical Inferior",
        "Apical Inferolateral",
        "Apical Anterolateral",
    ]
