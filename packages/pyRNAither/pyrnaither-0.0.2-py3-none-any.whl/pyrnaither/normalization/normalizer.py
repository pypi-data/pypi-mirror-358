import numpy as np
import pandas as pd
from typing import List, Any, Tuple, Callable
from statsmodels.robust.scale import mad
from statsmodels.nonparametric.smoothers_lowess import lowess
from sklearn.preprocessing import quantile_transform
from typing import Dict, cast, List
from numpy import ndarray, ones, zeros, abs, median  # type: ignore
from numpy.typing import NDArray

# adapted from https://github.com/Palpatineli/median_polish/blob/master/median_polish/main.py
def median_polish(data: ndarray, n_iter: int = 10) -> Dict[str, float | NDArray[float]]:
    """Performs median polish on a 2-D array
    Args:
        data: input 2-D array
    Returns:
        a dict, with:
            ave: μ
            col: column effect
            row: row effect
            r: cell residue
    """
    assert data.ndim == 2, "Input must be 2D array"
    ndim = 2
    data = data.copy()
    grand_effect = cast(float, median(data))
    data -= grand_effect
    median_margins: List[float] = [0] * ndim
    margins = [zeros(shape=data.shape[idx]) for idx in range(2)]
    dim_mask = ones(ndim, dtype=int)

    for _ in range(n_iter):
        for dim_id in range(ndim):
            rest_dim = 1 - dim_id
            temp_median = cast(NDArray[float], median(data, rest_dim))
            margins[dim_id] += temp_median
            median_margins[rest_dim] = cast(float, median(margins[rest_dim]))
            margins[rest_dim] -= median_margins[rest_dim]
            dim_mask[dim_id] = -1
            data -= temp_median.reshape(dim_mask)
            dim_mask[dim_id] = 1
        grand_effect += sum(median_margins)
    return {'ave': grand_effect, 'row': margins[1], 'column': margins[0], 'r': data}


def med_abs_dev(data: ndarray) -> float:
    """Median absolute deviation.
    MAD = median(|X_i - median(X)|)
    """
    return cast(float, median(abs(data - median(data))))

def save_old_intensity_columns(dataset: pd.DataFrame, col4val: str) -> pd.DataFrame:

    """
    Save the old intensity columns in the dataset.

    Args:
        dataset: The dataset to save the old intensity columns in.
        col4val: The column name to save the old intensity columns in.

    Returns:
        The dataset with the old intensity columns saved.
    """

    existing = [c for c in dataset.columns if c.startswith(col4val)]
    new_col = f"{col4val}.old{len(existing)}" if existing else f"{col4val}.old"
    dataset[new_col] = dataset[col4val]
    return dataset


def save_dataset(header: List[str], data: pd.DataFrame, data_set_file: str) -> None:

    """
    Save the dataset to a file.

    Args:
        header: The header of the dataset.
        data: The dataset to save.
        data_set_file: The file to save the dataset to.
    """

    with open(data_set_file, 'w') as f:
        for line in header:
            f.write(f"{line}\n")
    data.to_csv(data_set_file, sep='\t', index=False, mode='a')


def var_adjust(header: List[str], dataset: pd.DataFrame, args: List[Any]) -> Tuple[List[str], pd.DataFrame]:

    """
    Perform variance adjustment on the dataset.

    Args:
        header: The header of the dataset.
        dataset: The dataset to perform variance adjustment on.
        args: The arguments for the variance adjustment.

    Returns:
        A tuple containing the updated header and dataset.
    """

    flag, col4val, excl = args
    dataset = save_old_intensity_columns(dataset, col4val)
    for screen in sorted(dataset['ScreenNb'].unique()):
        mask = dataset['ScreenNb'] == screen
        subset = dataset.loc[mask].copy()
        idx = subset.index
        special = subset[subset['SpotType'] != -1]
        if excl == 1:
            special = special[special['SpotType'] == 2]
        scale = mad(special[col4val].dropna())
        if scale == 0 or np.isnan(scale):
            continue
        subset.loc[:, col4val] = subset[col4val] / scale
        dataset.loc[idx, col4val] = subset[col4val]
    header[2] = header[2].replace("NA", "")
    header[2] += f"VarAdjust {col4val},"
    return header, dataset


def div_norm(header: List[str], dataset: pd.DataFrame, args: List[Any]) -> Tuple[List[str], pd.DataFrame]:

    """
    Perform division normalization on the dataset.

    Args:
        header: The header of the dataset.
        dataset: The dataset to perform division normalization on.
        args: The arguments for the division normalization.

    Returns:
        A tuple containing the updated header and dataset.
    """

    func, flag, mode, col4val, excl = args
    dataset = save_old_intensity_columns(dataset, col4val)
    for screen in sorted(dataset['ScreenNb'].unique()):
        mask = dataset['ScreenNb'] == screen
        subset = dataset.loc[mask].copy()
        idx = subset.index
        special = subset[subset['SpotType'] != -1]
        if excl == 1:
            special = special[special['SpotType'] == 2]
        val = func(special[col4val].dropna()) if len(special) else np.nan
        if np.isnan(val):
            continue
        if mode == 1:
            subset[col4val] = subset[col4val] / val
        else:
            subset[col4val] = subset[col4val] - val
        dataset.loc[idx, col4val] = subset[col4val]
    header[2] = header[2].replace("NA", "")
    header[2] += f"divNorm {col4val},"
    return header, dataset


def quantile_normalization(header: List[str], dataset: pd.DataFrame, args: List[Any]) -> Tuple[List[str], pd.DataFrame]:

    """
    Perform quantile normalization on the dataset.

    Args:
        header: The header of the dataset.
        dataset: The dataset to perform quantile normalization on.
        args: The arguments for the quantile normalization.

    Returns:
        A tuple containing the updated header and dataset.
    """

    flag, col4val = args
    dataset = save_old_intensity_columns(dataset, col4val)
    df = dataset.copy()
    df.loc[df['SpotType'] == -1, col4val] = np.nan
    if flag == 1:
        screens = sorted(df['ScreenNb'].unique())
        mat = []
        for s in screens:
            vals = df[df['ScreenNb']==s][col4val].values
            mat.append(vals)
        arr = np.column_stack([np.pad(v, (0, max(map(len, mat))-len(v)), constant_values=np.nan) for v in mat])
        norm = quantile_transform(arr, axis=0, copy=True, n_quantiles=100, output_distribution='uniform')
        # flatten back
        flat = norm[~np.isnan(arr)]
        it = iter(flat)
        for s in screens:
            idx = df['ScreenNb']==s
            count = idx.sum()
            df.loc[idx, col4val] = [next(it) for _ in range(count)]
    header[2] = header[2].replace("NA", "")
    header[2] += f"quantileNormalization {col4val},"
    return header, df


def b_score(header: list, dataset: pd.DataFrame, args: list) -> Tuple[list, pd.DataFrame]:

    """
    Perform B-score normalization on the dataset.

    Args:
        header: The header of the dataset.
        dataset: The dataset to perform B-score normalization on.
        args: The arguments for the B-score normalization.

    Returns:
        A tuple containing the updated header and dataset.
    """

    col, excl = args
    dataset = save_old_intensity_columns(dataset, col)
    dataset.loc[dataset['SpotType']==-1, col] = np.nan
    for screen in sorted(dataset['ScreenNb'].unique()):
        plates = sorted(dataset.loc[dataset['ScreenNb']==screen, 'LabtekNb'].unique())
        for plate in plates:
            mask = (dataset['ScreenNb']==screen) & (dataset['LabtekNb']==plate)
            sub = dataset.loc[mask].copy()
            if sub.empty:
                continue
            max_row = int(sub['RowNb'].max())
            max_col = int(sub['ColNb'].max())
            mat = np.full((max_row, max_col), np.nan)
            for idx, row in sub.iterrows():
                r, c = int(row['RowNb'])-1, int(row['ColNb'])-1
                mat[r, c] = row[col]
            res = median_polish(mat, n_iter=10)
            resid = res['r']
            scale = mad(resid, center=0.0)
            if scale == 0 or np.isnan(scale):
                continue
            bs = resid / scale
            for idx, row in sub.iterrows():
                r, c = int(row['RowNb'])-1, int(row['ColNb'])-1
                if isinstance(bs, np.ndarray) and bs.ndim == 2:
                    dataset.at[idx, col] = bs[r, c]
                else:
                    dataset.at[idx, col] = bs
    header[2] = header[2].replace("NA", "") + f"BScore {col},"
    return header, dataset


def z_score(header: List[str], dataset: pd.DataFrame, args: List[Any]) -> Tuple[List[str], pd.DataFrame]:

    """
    Perform Z-score normalization on the dataset.

    Args:
        header: The header of the dataset.
        dataset: The dataset to perform Z-score normalization on.
        args: The arguments for the Z-score normalization.

    Returns:
        A tuple containing the updated header and dataset.
    """

    col4val, excl = args
    dataset = save_old_intensity_columns(dataset, col4val)
    for screen in sorted(dataset['ScreenNb'].unique()):
        mask = dataset['ScreenNb']==screen
        sub = dataset[mask].copy()
        special = sub[sub['SpotType']!=-1]
        if excl==1:
            special = special[special['SpotType']==2]
        med = special[col4val].median(skipna=True)
        scale = mad(special[col4val].dropna())
        if scale==0:
            continue
        dataset.loc[mask, col4val] = (dataset.loc[mask, col4val] - med)/scale
    header[2] = header[2].replace("NA", "")
    header[2] += f"ZScore {col4val},"
    return header, dataset


def z_score_per_screen(header: List[str], dataset: pd.DataFrame, args: List[Any]) -> Tuple[List[str], pd.DataFrame]:
    """
    Perform Z-score normalization per screen on the dataset.

    Args:
        header: The header of the dataset.
        dataset: The dataset to perform Z-score normalization per screen on.
        args: The arguments for the Z-score normalization per screen.

    Returns:
        A tuple containing the updated header and dataset.
    """

    return z_score(header, dataset, args)


def subtract_background(header: List[str], dataset: pd.DataFrame, args: List[Any]) -> Tuple[List[str], pd.DataFrame]:
    """
    Perform background subtraction on the dataset.

    Args:
        header: The header of the dataset.
        dataset: The dataset to perform background subtraction on.
        args: The arguments for the background subtraction.

    Returns:
        A tuple containing the updated header and dataset.
    """

    col4val, col4bg = args
    dataset = save_old_intensity_columns(dataset, col4val)
    dataset[col4val] = dataset[col4val] - dataset[col4bg]
    header[2] = header[2].replace("NA", "") + f" subtractBackground {col4val},"
    return header, dataset


def lowess_norm(header: List[str], dataset: pd.DataFrame, args: List[Any]) -> Tuple[List[str], pd.DataFrame]:
    """
    Perform lowess normalization on the dataset.

    Args:
        header: The header of the dataset.
        dataset: The dataset to perform lowess normalization on.
        args: The arguments for the lowess normalization.

    Returns:
        A tuple containing the updated header and dataset.
    """
    ch1, ch2, frac = args[0], args[1], args[2] if len(args)>2 else 2/3
    dataset = save_old_intensity_columns(dataset, ch1)
    dataset = save_old_intensity_columns(dataset, ch2)
    for screen in sorted(dataset['ScreenNb'].unique()):
        for plate in sorted(dataset['LabtekNb'].unique()):
            mask = (dataset['ScreenNb']==screen)&(dataset['LabtekNb']==plate)
            sub = dataset[mask].copy()
            x = sub[ch1].values
            y = sub[ch2].values
            use = ~np.isnan(x)&~np.isnan(y)
            if use.sum()>0:
                fitted = lowess(y[use], x[use], frac=frac, return_sorted=False)
                res = y.copy()
                res[use] = y[use] - fitted
                dataset.loc[mask, ch2] = res
    header[2] = header[2].replace("NA", "") + f" lowessNorm {ch1},{ch2},"
    return header, dataset


def control_norm(header: List[str], dataset: pd.DataFrame, args: List[Any]) -> Tuple[List[str], pd.DataFrame]:
    """
    Perform control normalization on the dataset.

    Args:
        header: The header of the dataset.
        dataset: The dataset to perform control normalization on.
        args: The arguments for the control normalization.

    Returns:
        A tuple containing the updated header and dataset.
    """
    flag, flag2, col4val, flag3 = args
    dataset = save_old_intensity_columns(dataset, col4val)
    for screen in sorted(dataset['ScreenNb'].unique()):
        mask = dataset['ScreenNb']==screen
        sub = dataset[mask].copy()
        if flag2 in (0,1):
            norm_subset = sub[sub['SpotType']==flag2]
        else:
            norm_subset = sub[sub['GeneName']==flag2]
        med = norm_subset[col4val].median(skipna=True)
        if flag3==1:
            sub[col4val] = sub[col4val]/med
        else:
            sub[col4val] = sub[col4val]-med
        dataset.loc[mask, col4val] = sub[col4val]
    header[2] = header[2].replace("NA", "") + f" controlNorm {col4val},"
    return header, dataset
