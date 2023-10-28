from pathlib import Path

import pandas as pd
from loguru import logger


def read_data(filename: str) -> pd.DataFrame:
    datafile = Path(filename).stem
    biomarker, n_segments = datafile.split("_")
    data = pd.read_csv(filename, index_col=0)
    logger.info(
        f"\nNumber of cases: {len(data)}\n"
        f"Biomarker: {biomarker}\n"
        f"Number of segments: {n_segments}\n"
    )
    return data
