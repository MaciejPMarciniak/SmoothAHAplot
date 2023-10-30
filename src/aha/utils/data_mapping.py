import pandas as pd


def case_to_dict(data: pd.DataFrame, case_id: str | pd.Index) -> dict[str, int | float]:
    case_dict = {}
    for column in data.columns:
        case_dict[column] = data.loc[case_id, column]

    return case_dict
