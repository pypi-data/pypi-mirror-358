import pandas as pd
import numpy as np
from scipy.stats import trim_mean
from typing import List, Union, Tuple, Callable, Optional

def create_subset(dataset: pd.DataFrame, list_ids: pd.Series, equal_to: str) -> pd.DataFrame:
    """
    Creates a subset of the dataset where the list_ids column matches the equal_to value.

    Args:
        dataset: DataFrame to subset.
        list_ids: Series of IDs to match.
        equal_to: Value to match in list_ids.

    Returns:
        Subset of the dataset where list_ids matches equal_to.
    """
    return dataset[list_ids == equal_to].copy()

def index_subset(list_ids: pd.Series, equal_to: str) -> List[int]:
    """
    Returns the indices of the list_ids where the value matches equal_to.

    Args:
        list_ids: Series of IDs to search.
        equal_to: Value to match in list_ids.

    Returns:
        List of indices where list_ids matches equal_to.
    """
    return list_ids[list_ids == equal_to].index.tolist()

def find_replicates(dataset: pd.DataFrame, which_col: str, replicate_id: str) -> List[int]:
    """
    Returns the indices of the dataset where the which_col column matches the replicate_id value.

    Args:
        dataset: DataFrame to search.
        which_col: Column name to match.
        replicate_id: Value to match in which_col.

    Returns:
        List of indices where which_col matches replicate_id.
    """
    return dataset.index[dataset[which_col] == replicate_id].tolist()

def order_gene_ids(dataset: pd.DataFrame, id_col: str) -> pd.DataFrame:
    """
    Orders the dataset by the id_col column and returns a new DataFrame with the indices reset.

    Args:
        dataset: DataFrame to order.
        id_col: Column name to order by.

    Returns:
        New DataFrame with the indices reset after ordering by id_col.
    """
    return dataset.sort_values(by=id_col).reset_index(drop=True)

def rms(vec: Union[List[float], np.ndarray]) -> float:
    """
    Returns the root mean square of the input vector.

    Args:
        vec: Input vector.

    Returns:
        Root mean square of the input vector.
    """
    vec = np.array(vec)
    vec = vec[~np.isnan(vec)]
    return np.sqrt(np.sum(vec ** 2) / len(vec))

def trim_avg(vec: Union[List[float], np.ndarray]) -> float:
    """
    Returns the trimmed mean of the input vector.

    Args:
        vec: Input vector.

    Returns:
        Trimmed mean of the input vector.
    """
    return trim_mean(vec, 0.05)

def closest_to_zero(vec: Union[List[float], np.ndarray]) -> float:
    """
    Returns the value in the input vector that is closest to zero.

    Args:
        vec: Input vector.

    Returns:
        Value in the input vector that is closest to zero.
    """
    vec = np.array(vec)
    return vec[np.nanargmin(np.abs(vec))]

def furthest_from_zero(vec: Union[List[float], np.ndarray]) -> float:
    """
    Returns the value in the input vector that is furthest from zero.

    Args:
        vec: Input vector.

    Returns:
        Value in the input vector that is furthest from zero.
    """
    vec = np.array(vec)
    return vec[np.nanargmax(np.abs(vec))]

def divide_channels(ch1: np.ndarray, ch2: np.ndarray) -> np.ndarray:
    """
    Returns the element-wise division of ch1 by ch2.

    Args:
        ch1: First channel.
        ch2: Second channel.

    Returns:
        Element-wise division of ch1 by ch2.
    """
    return np.divide(ch1, ch2)

def erase_dataset_column(dataset: pd.DataFrame, colname: str) -> pd.DataFrame:
    """
    Erases the column with the given name from the dataset.

    Args:
        dataset: DataFrame to erase column from.
        colname: Name of the column to erase.

    Returns:
        DataFrame with the column erased.
    """
    if colname not in dataset.columns:
        return dataset
    return dataset.drop(columns=[colname])

def generate_replicate_mat(data: pd.DataFrame, min_nb_reps: int, index_or_int: str,
                            col4val: str, col4anno: str) -> Tuple[np.ndarray, List[int], List[int]]:
    """
    Generates a replicate matrix from the given data.

    Args:
        data: DataFrame containing at least columns [col4val, col4anno].
        min_nb_reps: Minimum number of replicates required to keep an ID.
        index_or_int: "Index" to return row indices, "Intensities" to return values.
        col4val: name of the intensity column to fetch when index_or_int="Intensities".
        col4anno: name of the annotation column grouping replicates.

    Returns:
        replicate_matrix: 2D numpy array of shape (n_items, max_replicates), filled with
                          indices or values, using np.nan where missing.
        index_pos_controls: list of row indices in replicate_matrix corresponding to positive controls.
        index_neg_controls: list of row indices in replicate_matrix corresponding to negative controls.
    """
    workdata = data.copy()
    workdata.loc[workdata["SpotType"] == -1, col4val] = np.nan

    max_num_rep = 0
    ids = workdata[col4anno].unique()
    new_ids = []
    for id_ in ids:
        rep_index = find_replicates(workdata, col4anno, id_)
        if len(rep_index) > max_num_rep:
            max_num_rep = len(rep_index)
        if min_nb_reps == 2 and len(rep_index) < 2:
            continue
        new_ids.append(id_)

    cv_matrix = np.full((len(new_ids), max_num_rep), np.nan)
    index_pos_controls = []
    index_neg_controls = []

    for i, id_ in enumerate(new_ids):
        rep_index = find_replicates(workdata, col4anno, id_)

        if index_or_int == "Intensities":
            values = workdata.loc[rep_index, col4val].dropna().values
            cv_matrix[i, :len(values)] = values

        elif index_or_int == "Index":
            valid_indices = [ix for ix in rep_index if not pd.isna(workdata.at[ix, col4val])]
            cv_matrix[i, :len(valid_indices)] = valid_indices

        if workdata.at[rep_index[0], "SpotType"] == 1:
            index_pos_controls.append(i)
        elif workdata.at[rep_index[0], "SpotType"] == 0:
            index_neg_controls.append(i)

    # Remove rows with only NaNs
    valid_rows = ~np.isnan(cv_matrix).all(axis=1)
    cv_matrix = cv_matrix[valid_rows]

    index_pos_controls = [i for i in index_pos_controls if valid_rows[i]]
    index_neg_controls = [i for i in index_neg_controls if valid_rows[i]]

    return cv_matrix, index_pos_controls, index_neg_controls

def summarize_reps(data: pd.DataFrame, fun_sum: Callable, col4val: List[str],
                   col4anno: str, cols2del: List[str]) -> pd.DataFrame:
    """
    Summarizes the replicates in the given data.

    Args:
        data: DataFrame containing at least columns [col4val, col4anno].
        fun_sum: Function to use for summarization.
        col4val: name of the column to summarize.
        col4anno: name of the annotation column grouping replicates.
        cols2del: list of columns to delete from the data.

    Returns:
        DataFrame with the replicates summarized.
    """
    for col in cols2del:
        data = erase_dataset_column(data, col)

    data = data[data["SpotType"] != -1].copy()
    cv_matrix, *_ = generate_replicate_mat(data, 1, "Index", col4val[0], col4anno)

    summarized = {
        "Spotnumber": [], "Internal_GeneID": [], "GeneName": [], "SpotType": [],
        "LabtekNb": [], "RowNb": [], "ColNb": [], "ScreenNb": []
    }
    flex_data = {col: [] for col in col4val}

    for row_indices in cv_matrix.astype(int):
        row_indices = row_indices[~np.isnan(row_indices)].astype(int)

        summarized["Spotnumber"].append(",".join(map(str, data.loc[row_indices, "Spotnumber"])))
        summarized["LabtekNb"].append(",".join(map(str, data.loc[row_indices, "LabtekNb"])))
        summarized["RowNb"].append(",".join(map(str, data.loc[row_indices, "RowNb"])))
        summarized["ColNb"].append(",".join(map(str, data.loc[row_indices, "ColNb"])))
        summarized["ScreenNb"].append(",".join(map(str, data.loc[row_indices, "ScreenNb"])))

        first_index = row_indices[0]
        summarized["SpotType"].append(data.at[first_index, "SpotType"])
        summarized["Internal_GeneID"].append(str(data.at[first_index, "Internal_GeneID"]))
        summarized["GeneName"].append(str(data.at[first_index, "GeneName"]))

        for col in col4val:
            values = data.loc[row_indices, col].dropna()
            if not values.empty:
                flex_data[col].append(fun_sum(values))
            else:
                flex_data[col].append(np.nan)

    summarized_df = pd.DataFrame(summarized)
    for col in col4val:
        summarized_df[col] = flex_data[col]

    return summarized_df

def sum_channels(header: List[str], dataset: pd.DataFrame, fun_name: Callable,
                         colname4ch1: str, colname4ch2: str) -> Tuple[List[str], pd.DataFrame]:
    """
    Sums the values of two channels in the dataset.

    Args:
        header: The header of the dataset.
        dataset: The dataset to perform the sum on.
        fun_name: The function to use for the sum.
        colname4ch1: The name of the first channel.
        colname4ch2: The name of the second channel.

    Returns:
        A tuple containing the updated header and dataset.
    """
    dataset[f"old_{colname4ch1}"] = dataset[colname4ch1]
    dataset[f"old_{colname4ch2}"] = dataset[colname4ch2]

    dataset[colname4ch1] = fun_name(dataset[colname4ch1], dataset[colname4ch2])
    dataset = erase_dataset_column(dataset, colname4ch2)

    new_colname = f"{colname4ch1}_{colname4ch2}"
    dataset.rename(columns={colname4ch1: new_colname}, inplace=True)

    header[2] = header[2].replace("NA", "")
    header[2] += f"Summarization of channel {colname4ch1} and {colname4ch2},"

    return header, dataset

def generate_replicate_matrix_no_filter(
    data: pd.DataFrame,
    min_nb_reps: int,
    index_or_int: str,
    col4val: str,
    col4anno: str
) -> Tuple[np.ndarray, List[int], List[int]]:
    """
    Build a replicate matrix without filtering.

    Args:
        data: DataFrame containing at least columns for annotation (col4anno),
              SpotType, and intensity column (col4val).
        min_nb_reps: minimum number of replicates required to keep an ID.
        index_or_int: "Index" to return row indices, "Intensities" to return values.
        col4val: name of the intensity column to fetch when index_or_int="Intensities".
        col4anno: name of the annotation column grouping replicates.

    Returns:
        replicate_matrix: 2D numpy array of shape (n_items, max_replicates), filled with
                          indices or values, using np.nan where missing.
        index_pos_controls: list of row indices in replicate_matrix corresponding to positive controls.
        index_neg_controls: list of row indices in replicate_matrix corresponding to negative controls.
    """
    # Find all unique IDs and group their row indices
    ids = data[col4anno].unique()
    rep_indices = {id_: data.index[data[col4anno] == id_].tolist() for id_ in ids}

    # Determine maximum replicates across IDs
    max_rep = max((len(idxs) for idxs in rep_indices.values()), default=0)

    # Filter IDs by minimum replicates
    if min_nb_reps > 1:
        new_ids = [id_ for id_, idxs in rep_indices.items() if len(idxs) >= min_nb_reps]
    else:
        new_ids = list(rep_indices.keys())

    n = len(new_ids)
    # Initialize matrix
    replicate_matrix = np.full((n, max_rep), np.nan)

    index_pos_controls: List[int] = []
    index_neg_controls: List[int] = []

    for i, id_ in enumerate(new_ids):
        idxs = rep_indices[id_]
        # fill row
        for j, idx in enumerate(idxs):
            if index_or_int == "Index":
                replicate_matrix[i, j] = idx
            elif index_or_int == "Intensities":
                replicate_matrix[i, j] = data.at[idx, col4val]
            else:
                raise ValueError("index_or_int must be 'Index' or 'Intensities'")
        # classify control by first replicate's SpotType
        if idxs:
            first = idxs[0]
            spot_type = data.at[first, 'SpotType']
            if spot_type == 1:
                index_pos_controls.append(i)
            elif spot_type == 0:
                index_neg_controls.append(i)

    return replicate_matrix, index_pos_controls, index_neg_controls
