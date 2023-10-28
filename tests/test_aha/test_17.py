import pytest
from numpy.typing import NDArray

from src.aha import aha


@pytest.fixture
def strain_dict(segments_17: list[int], exp_strain_data_17: list[int]) -> dict[str, int]:
    return {k: v for (k, v) in zip(segments_17, exp_strain_data_17)}


@pytest.fixture
def rand_strain_dict(segments_17: list[int], rand_strain_data_17: NDArray) -> dict[str, int]:
    return {k: v for (k, v) in zip(segments_17, rand_strain_data_17)}


@pytest.fixture
def mw_dict(segments_17: list[int], exp_mw_data_17: list[int]) -> dict[str, int]:
    return {k: v for (k, v) in zip(segments_17, exp_mw_data_17)}


@pytest.fixture
def rand_mw_dict(segments_17: list[int], rand_mw_data_17: NDArray) -> dict[str, int]:
    return {k: v for (k, v) in zip(segments_17, rand_mw_data_17)}


@pytest.mark.mpl_image_compare(
    baseline_dir="../baseline",
)
def test_strain_plotting_17(strain_dict: dict[str, int]) -> None:
    strain_plot = aha.AHA(strain_dict, "Strain")
    fig = strain_plot.bullseye_smooth(True)
    return fig


@pytest.mark.mpl_image_compare(
    baseline_dir="../baseline",
)
def test_mw_plotting_17(mw_dict: dict[str, int]) -> None:
    mw_plot = aha.AHA(mw_dict, "MyocardialWork")
    fig = mw_plot.bullseye_smooth(True)
    return fig


def test_rand_strain_plotting_17(rand_strain_dict: dict[str, int]) -> None:
    strain_plot = aha.AHA(rand_strain_dict, "Strain")
    strain_plot.bullseye_smooth(True)


def test_rand_mw_plotting_17(rand_mw_dict: dict[str, int]) -> None:
    mw_plot = aha.AHA(rand_mw_dict, "MyocardialWork")
    mw_plot.bullseye_smooth(True)
