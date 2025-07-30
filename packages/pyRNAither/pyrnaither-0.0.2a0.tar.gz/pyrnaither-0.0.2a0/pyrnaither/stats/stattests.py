
import numpy as np
import pandas as pd
from typing import Any, List, Tuple, Callable, Sequence
from scipy.stats import ttest_1samp, ttest_ind, wilcoxon, mannwhitneyu
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from ..utils.utilities import generate_replicate_mat
from ..visualization.visualizer import spatial_distrib
from .stattests_todo import order_gene_ids

def incorporate_pval_vec(
    dataset: pd.DataFrame,
    p_val: pd.Series,
    col4anno: str,
    colname4pval: str
) -> pd.DataFrame:
    """
    Add a new column `colname4pval` to `dataset`, mapping each row’s
    annotation (in col4anno) to the corresponding p-value.

    Args:
        dataset: DataFrame to modify.
        p_val: Series of p-values indexed by annotation labels.
        col4anno: Column name for annotation grouping.
        colname4pval: Column name for p-value.

    Returns:
        DataFrame with new p-value column.
    """
    df = dataset.copy()
    df[colname4pval] = df[col4anno].map(p_val)
    return df


def t_test(
    dataset: pd.DataFrame,
    args: List[Any]
) -> Tuple[pd.Series, pd.DataFrame, str, str]:
    """
    Port of the R Ttest function to Python.

    args = [testType, reference, col4val, col4anno]
    - testType: 'two.sided', 'less', or 'greater'
    - reference: numeric (for one-sample) or string (for two-sample)
    - col4val: column name for intensity values
    - col4anno: column name for annotation grouping

    Returns:
        p_val: Series indexed by annotation labels
        new_dataset: DataFrame with new p-value column
        pval_colname: name of the p-value column
        method: 't test'
    """
    test_type, reference, col4val, col4anno = args

    # Generate replicate matrix (rows: annotation, cols: replicates)
    replica_matrix = generate_replicate_mat(dataset, col4val=col4val, col4anno=col4anno)

    # Initialize p-value Series
    p_val = pd.Series(index=replica_matrix.index, dtype=float)

    # Map R's alt hypotheses to SciPy's
    alt = test_type  # SciPy uses 'two-sided', 'less', 'greater'

    for label, row in replica_matrix.iterrows():
        values = row.dropna()
        if values.var() != 0:
            if not isinstance(reference, str):
                # One-sample t-test
                stat = ttest_1samp(values, popmean=reference, alternative=alt)
            else:
                # Two-sample t-test vs another annotation
                if reference not in replica_matrix.index:
                    raise KeyError(f"Reference '{reference}' not found in annotations")
                ref_values = replica_matrix.loc[reference].dropna()
                stat = ttest_ind(values, ref_values, alternative=alt)
            p_val.at[label] = stat.pvalue
        else:
            p_val.at[label] = float('nan')

    pval_colname = f"pValue.ttest_{test_type}"
    new_dataset = incorporate_pval_vec(dataset, p_val, col4anno, pval_colname)
    return p_val, new_dataset, pval_colname, 't test'


def mann_whitney(
    dataset: pd.DataFrame,
    args: List[Any]
) -> Tuple[pd.Series, pd.DataFrame, str, str]:
    """
    Port of the R MannWhitney function to Python.

    args = [testType, reference, col4val, col4anno]
    - testType: 'two.sided', 'less', or 'greater'
    - reference: numeric (for one-sample) or string (for two-sample)
    - col4val: column name for intensity values
    - col4anno: column name for annotation grouping

    Returns:
        p_val: Series indexed by annotation labels
        new_dataset: DataFrame with new p-value column
        pval_colname: name of the p-value column
        method: 'Mann-Whitney test'
    """
    test_type, reference, col4val, col4anno = args

    # Generate replicate matrix
    replica_matrix = generate_replicate_mat(dataset, col4val, col4anno)

    # Initialize p-value Series
    p_val = pd.Series(index=replica_matrix.index, dtype=float)

    alt = test_type

    for label, row in replica_matrix.iterrows():
        values = row.dropna()
        if values.var() != 0:
            if not isinstance(reference, str):
                # One-sample Wilcoxon signed-rank test
                stat = wilcoxon(values - reference, alternative=alt)
            else:
                # Two-sample Mann-Whitney U test vs another annotation
                if reference not in replica_matrix.index:
                    raise KeyError(f"Reference '{reference}' not found in annotations")
                ref_values = replica_matrix.loc[reference].dropna()
                stat = mannwhitneyu(values, ref_values, alternative=alt)
            p_val.at[label] = stat.pvalue
        else:
            p_val.at[label] = float('nan')

    pval_colname = f"pValue.mannwhitney_{test_type}"
    new_dataset = incorporate_pval_vec(dataset, p_val, col4anno, pval_colname)
    return p_val, new_dataset, pval_colname, 'Mann-Whitney test'


def rank_product(
    dataset: pd.DataFrame,
    args: List[Any]
) -> Tuple[pd.Series, pd.DataFrame, str, str]:
    """
    Port of the R RankProduct function to Python via permutation-based test.

    args = [permutations, flag, col4val, col4anno]
    - permutations: number of random permutations
    - flag: 1 for 'l' (lower), else 'g' (greater)
    - col4val: column name for intensity values
    - col4anno: column name for annotation grouping

    Returns:
        p_val: Series indexed by annotation labels (estimated pfp)
        new_dataset: DataFrame with new p-value column
        pval_colname: name of the p-value column
        method: 'Rank product test'
    """
    num_perm, flag, col4val, col4anno = args
    test_type = 'l' if flag == 1 else 'g'

    replica_matrix = generate_replicate_mat(dataset, col4val, col4anno)
    mat = replica_matrix.values.astype(float)
    G, R = mat.shape

    # Rank data per replicate
    ranks = np.zeros_like(mat)
    for j in range(R):
        col = mat[:, j]
        if test_type == 'l':
            order = np.argsort(col, kind='mergesort')
        else:
            order = np.argsort(-col, kind='mergesort')
        col_ranks = np.empty_like(col)
        col_ranks[order] = np.arange(1, G + 1)
        ranks[:, j] = col_ranks

    # Observed rank products (geometric mean)
    rp_obs = np.prod(ranks, axis=1) ** (1.0 / R)

    # Permutation null distribution
    null_rps = []
    for _ in range(num_perm):
        perm_ranks = np.zeros_like(ranks)
        for j in range(R):
            perm_ranks[:, j] = np.random.permutation(ranks[:, j])
        rp_perm = np.prod(perm_ranks, axis=1) ** (1.0 / R)
        null_rps.append(rp_perm)
    null_rps = np.concatenate(null_rps)

    # Empirical pfp: proportion of null <= observed
    p_val = pd.Series(index=replica_matrix.index, dtype=float)
    for idx, rp_val in enumerate(rp_obs):
        p_val.iloc[idx] = np.mean(null_rps <= rp_val)

    pval_colname = f"pValue.rankproduct_{test_type}"
    new_dataset = incorporate_pval_vec(dataset, p_val, col4anno, pval_colname)
    return p_val, new_dataset, pval_colname, 'Rank product test'


def mult_test_adjust(
    p_val_vec: pd.Series,
    adjust_method: str
) -> pd.Series:
    """
    Adjust p-values for multiple testing.

    Args:
        p_val_vec: Series of p-values indexed by feature/annotation.
        adjust_method: correction method, e.g., 'bonferroni', 'fdr_bh', etc.

    Returns:
        Series of adjusted p-values (same index).
    """
    corrected, p_corrected, _, _ = multipletests(
        p_val_vec.values,
        method=adjust_method
    )
    return pd.Series(p_corrected, index=p_val_vec.index)



def hit_selection_pval(
    dataset: pd.DataFrame,
    p_val_vec: pd.Series,
    col4val: str,
    col4sel: str,
    thresh: float,
    col4anno: str,
    file4hits: str
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, float]:
    """
    Select hits based on p-value threshold.

    Args:
        dataset: DataFrame containing at least columns [col4val, col4anno].
        p_val_vec: Series of p-values indexed by feature/annotation.
        col4val: Column name for intensity values.
        col4sel: Column name for selection.
        thresh: P-value threshold for selection.
        col4anno: Column name for annotation.
        file4hits: File name for hits output.

    Returns:
        Tuple of (dataset, hit_vector, replica_matrix, used_threshold)
    """
    # replicate matrix
    replica_matrix = generate_replicate_mat(dataset, col4val, col4anno)
    # boolean index
    idx = p_val_vec < thresh
    # adjust threshold if no hits
    if not idx.any():
        thresh = p_val_vec.min(skipna=True) + 1e-5
        print(f"No p-values under threshold. Threshold increased to {thresh}.")
        idx = p_val_vec < thresh
    # hit vector
    hit_vector = pd.Series(0, index=replica_matrix.index)
    hit_vector[idx] = 1
    # incorporate into dataset
    dataset = incorporate_pval_vec(dataset, hit_vector, col4anno, col4sel)
    # reset controls
    if 'SpotType' in dataset:
        dataset.loc[dataset['SpotType'] == -1, col4sel] = 0
    # export hits
    hits = replica_matrix.loc[hit_vector == 1]
    # build output
    if hits.shape[0] == 1:
        vals = hits.values.flatten()
        median_val = np.nanmedian(vals)
        output = pd.DataFrame([
            np.concatenate(([p_val_vec[idx].iloc[0]], [median_val], vals))
        ], index=[hits.index[0]])
        cols = ["pvalue", "median"] + [col4val]*len(vals)
        output.columns = cols
    else:
        medians = hits.median(axis=1)
        output = hits.copy()
        output.insert(0, 'median', medians)
        output.insert(0, 'pvalue', p_val_vec.loc[hits.index])
        output = output.sort_values('pvalue')
    output.to_csv(file4hits, sep='\t')
    return dataset, hit_vector, replica_matrix, thresh


def hit_selection_zscore(
    dataset: pd.DataFrame,
    col4zscore: str,
    col4sel: str,
    thresh: int,
    flag: int,
    flag2: int,
    col4anno: str,
    sum_func: Callable[..., float],
    file4hits: str
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Select hits based on Z-score ranking or threshold.

    Args:
        dataset: DataFrame containing at least columns [col4zscore, col4anno].
        col4zscore: Column name for Z-score.
        col4sel: Column name for selection.
        thresh: Z-score threshold for selection.
        flag: 1 for 'l' (lower), else 'g' (greater).
        flag2: 1 for 'l' (lower), else 'g' (greater).
        col4anno: Column name for annotation.
        sum_func: Function to calculate sum of replicates.
        file4hits: File name for hits output.

    Returns:
        Tuple of (dataset, hit_vector)
    """
    df = dataset.copy()
    hit_vector = pd.Series(0, index=df.index)
    # Option 1: direct ordering by gene IDs
    if flag == 1 and flag2 == 1:
        df_ord = order_gene_ids(df, col4zscore)
        valid = df_ord[col4zscore].notna() & (df_ord['SpotType'] != -1)
        count = abs(thresh)
        if 2*count > valid.sum():
            print(f"Threshold too large; only {valid.sum()} values available.")
            df_ord.to_csv(file4hits, sep='\t', index=False)
            return df, hit_vector
        if thresh > 0:
            sel = df_ord[valid].head(count).index
        elif thresh < 0:
            sel = df_ord[valid].tail(count).index
        else:
            sel = df_ord.index
        hit_vector.loc[sel] = 1
        df[col4sel] = hit_vector
        #df[col4sel].iloc[df['SpotType']==-1] = 0
        df.loc[df['SpotType']==-1, col4sel] = 0
        df.loc[hit_vector==1].to_csv(file4hits, sep='\t', index=False)
        return df, hit_vector
    # Option 2 & 3: simple cutoff on z-score
    if flag == 1 and flag2 in (-2, 2):
        if flag2 == -2:
            idx = df[col4zscore] < thresh
        else:
            idx = df[col4zscore] > thresh
        if not idx.any():
            if flag2 == -2:
                new_thresh = df[col4zscore].min(skipna=True) + 1e-6
                print(f"No Z-scores under threshold; increased to {new_thresh}.")
                idx = df[col4zscore] < new_thresh
            else:
                new_thresh = df[col4zscore].max(skipna=True) - 1e-6
                print(f"No Z-scores over threshold; decreased to {new_thresh}.")
                idx = df[col4zscore] > new_thresh
        hit_vector[idx] = 1
        hit_vector[df['SpotType']==-1] = 0
        df[col4sel] = hit_vector
        df_ord = order_gene_ids(df, col4zscore)
        df_ord[df_ord[col4sel]==1].to_csv(file4hits, sep='\t', index=False)
        return df, hit_vector
    # Option 4: summarized Z-scores
    if flag == 2:
        replica_matrix = generate_replicate_mat(df, col4zscore, col4anno)
        summed = replica_matrix.apply(lambda row: sum_func(row.values, skipna=True), axis=1)
        order_idx = summed.sort_values(ascending=(thresh>=0)).index
        count = abs(thresh)
        if 2*count > len(order_idx):
            print(f"Threshold too large; only {len(order_idx)} features available.")
            pd.DataFrame({'summedZScore': summed}).to_csv(file4hits, sep='\t')
            return df, hit_vector
        if thresh > 0:
            sel = order_idx[:count]
        elif thresh < 0:
            sel = order_idx[-count:]
        else:
            sel = order_idx
        hit_vector = pd.Series(0, index=replica_matrix.index)
        hit_vector.loc[sel] = 1
        df = incorporate_pval_vec(df, hit_vector, col4anno, col4sel)
        df.loc[df['SpotType']==-1, col4sel] = 0
        hits = replica_matrix.loc[sel]
        # export
        if len(sel)==1:
            vals = hits.values.flatten(); out = pd.DataFrame([np.concatenate(([summed[sel[0]]], vals))], index=[sel[0]])
            out.columns = ['summarizedZScore'] + [col4zscore]*len(vals)
            out.to_csv(file4hits, sep='\t')
        else:
            out = hits.copy(); out.insert(0, 'summarizedZScore', summed)
            out.to_csv(file4hits, sep='\t')
        return df, hit_vector
    return df, hit_vector


def hit_selection_zscore_pval(
    dataset: pd.DataFrame,
    p_val_vec: pd.Series,
    col4zscore: str,
    col4sel: str,
    thresh: float,
    thresh2: float,
    flag2: int,
    col4anno: str,
    sum_func: Callable[..., float],
    file4hits: str
) -> Tuple[pd.DataFrame, pd.Series, float, float]:
    """
    Combined Z-score and p-value hit selection.
    Returns (dataset, hit_vector, used_thresh_z, used_thresh_p).

    Args:
        dataset: DataFrame containing at least columns [col4zscore, col4anno].
        p_val_vec: Series of p-values indexed by feature/annotation.
        col4zscore: Column name for Z-score.
        col4sel: Column name for selection.
        thresh: Z-score threshold for selection.
        thresh2: P-value threshold for selection.
        flag2: 1 for 'l' (lower), else 'g' (greater).
        col4anno: Column name for annotation.
        sum_func: Function to calculate sum of replicates.
        file4hits: File name for hits output.

    Returns:
        Tuple of (dataset, hit_vector, used_thresh_z, used_thresh_p).
    """
    # build replicate matrix and summed scores
    replica_matrix = generate_replicate_mat(dataset, col4zscore, col4anno)
    summed = replica_matrix.apply(lambda row: sum_func(row.values, skipna=True), axis=1)
    # logical indices
    if flag2 == -2:
        idx_z = summed < thresh
    else:
        idx_z = summed > thresh
    idx_p = p_val_vec < thresh2
    if not idx_z.any():
        thresh = summed[idx_p].min(skipna=True) + 1e-5
        print(f"No Z-scores under threshold; increased to {thresh}.")
        idx_z = summed < thresh if flag2==-2 else summed > thresh
    if not idx_p.any():
        thresh2 = p_val_vec.min(skipna=True) + 1e-5
        print(f"No p-values under threshold; increased to {thresh2}.")
        idx_p = p_val_vec < thresh2
    hit = idx_z & idx_p
    hit_vector = hit.astype(int)
    # incorporate
    df = incorporate_pval_vec(dataset, pd.Series(hit_vector, index=replica_matrix.index), col4anno, col4sel)
    df.loc[df['SpotType']==-1, col4sel] = 0
    # export
    hits = replica_matrix.loc[hit]
    if hits.shape[0] == 1:
        vals = hits.values.flatten()
        out = pd.DataFrame([np.concatenate(([summed[hit.idxmax()]], [p_val_vec[hit.idxmax()]], vals))], index=[hits.index[0]])
        out.columns = ['summarizedZScore', 'p-value'] + [col4zscore]*len(vals)
        out.to_csv(file4hits, sep='\t')
    else:
        out = hits.copy()
        out.insert(0, 'p-value', p_val_vec)
        out.insert(0, 'summarizedZScore', summed)
        out.to_csv(file4hits, sep='\t')
    return df, pd.Series(hit_vector, index=replica_matrix.index), thresh, thresh2


def spatial_distrib_hits(
    header: List[str],
    dataset: pd.DataFrame,
    plot_title: str,
    col4hits: str,
    col4anno: str,
    show_plot: bool
) -> None:
    """
    Wrapper for spatial distribution plotting of hits.
    Assumes a function spatial_distrib is defined elsewhere.

    Args:
        header: List of column names.
        dataset: DataFrame containing at least columns [col4hits, col4anno].
        plot_title: Title for the plot.
        col4hits: Column name for hits.
        col4anno: Column name for annotation.
        show_plot: Whether to show the plot interactively.
    """
    spatial_distrib(header, dataset, plot_title, col4hits, col4anno, show_plot)

def volcano_plot(
    header: List[str],
    dataset: pd.DataFrame,
    col4plotx: str,
    col4ploty: str,
    col4anno: str,
    plot_title: str,
    sig_level: Sequence[float],
    show_plot: bool
) -> str:
    """
    Generates a volcano plot and saves PDF/PNG.
    Returns the base plot name.

    Args:
        header: List of column names.
        dataset: DataFrame containing at least columns [col4plotx, col4ploty, col4anno].
        col4plotx: Column name for x-axis.
        col4ploty: Column name for y-axis.
        col4anno: Column name for annotation.
        plot_title: Title for the plot.
        sig_level: Significance level for the plot.
        show_plot: Whether to show the plot interactively.

    Returns:
        Base plot name.
    """
    # filter controls
    df = dataset[dataset.get('SpotType', -1) != -1]
    x = df[col4plotx]
    y = df[col4ploty]
    neglogy = -np.log10(y)

    # interactive display
    if show_plot:
        plt.figure()
        plt.scatter(x, neglogy)
        plt.title(plot_title)
        plt.xlabel(col4plotx)
        plt.ylabel(f"-log10({col4ploty})")
        if len(sig_level) >= 1:
            plt.axhline(-np.log10(sig_level[0]), color='green')
        if len(sig_level) >= 2:
            plt.axvline(sig_level[1], color='red')
        if len(sig_level) >= 3:
            plt.axvline(sig_level[2], color='red')
        plt.show()

    # derive plot name
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    plot_name = f"{base}_{plot_title}"

    # save to files
    for ext in ('pdf', 'png'):
        plt.figure()
        plt.scatter(x, neglogy)
        plt.title(plot_title)
        plt.xlabel(col4plotx)
        plt.ylabel(f"-log10({col4ploty})")
        if len(sig_level) >= 1:
            plt.axhline(-np.log10(sig_level[0]), color='green')
        if len(sig_level) >= 2:
            plt.axvline(sig_level[1], color='red')
        if len(sig_level) >= 3:
            plt.axvline(sig_level[2], color='red')
        plt.savefig(f"{plot_name}.{ext}")
        plt.close()

    return plot_name


def venn_diag(
    header: List[str],
    list_of_cols: List[Sequence[int]],
    list_of_names: List[str],
    plot_title: str,
    show_plot: bool
) -> str:
    """
    Creates and saves a Venn diagram for 2 or 3 hit sets.
    Returns the base plot name.

    Args:
        header: List of column names.
        list_of_cols: List of columns for the hit sets.
        list_of_names: List of names for the hit sets.
        plot_title: Title for the plot.
        show_plot: Whether to show the plot interactively.

    Returns:
        Base plot name.
    """
    n = len(list_of_cols)
    if n not in (2, 3):
        raise ValueError("venn_diag supports only 2 or 3 sets")

    sets = [set(np.where(col)[0]) for col in list_of_cols]
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    plot_name = f"{base}_{plot_title}"

    # optional interactive
    if show_plot:
        plt.figure()
        if n == 2:
            venn2(subsets=sets, set_labels=list_of_names)
        else:
            venn3(subsets=sets, set_labels=list_of_names)
        plt.title(plot_title)
        plt.show()

    # save files
    for ext in ('pdf', 'png'):
        plt.figure()
        if n == 2:
            venn2(subsets=sets, set_labels=list_of_names)
        else:
            venn3(subsets=sets, set_labels=list_of_names)
        plt.title(plot_title)
        plt.savefig(f"{plot_name}.{ext}")
        plt.close()

    return plot_name


def compare_hits(
    hit_vec1: Sequence[int],
    hit_vec2: Sequence[int],
    names1: Sequence[str],
    names2: Sequence[str]
) -> List[str]:
    """
    Returns the list of annotation names where both hit vectors agree on a hit (1).
    Raises if inputs are mismatched.

    Args:
        hit_vec1: First hit vector.
        hit_vec2: Second hit vector.
        names1: First set of annotation names.
        names2: Second set of annotation names.

    Returns:
        List of annotation names where both hit vectors agree on a hit (1).
    """
    if len(hit_vec1) != len(hit_vec2):
        raise ValueError(f"Hit vectors have different lengths: {len(hit_vec1)} vs {len(hit_vec2)}")
    if len(hit_vec1) != len(names1) or len(hit_vec2) != len(names2):
        raise ValueError("Hit vectors and annotation names must have the same lengths")

    # create DataFrame for alignment
    df1 = pd.DataFrame({'name': names1, 'hit': hit_vec1})
    df2 = pd.DataFrame({'name': names2, 'hit': hit_vec2})
    df1_sorted = df1.sort_values('name').reset_index(drop=True)
    df2_sorted = df2.sort_values('name').reset_index(drop=True)

    if not all(df1_sorted['name'] == df2_sorted['name']):
        diff = pd.DataFrame({
            'names1': df1_sorted['name'],
            'names2': df2_sorted['name']
        })
        raise ValueError(f"Annotation vectors differ:\n{diff}")

    # filter where both hits == 1
    mask = (df1_sorted['hit'] == 1) & (df2_sorted['hit'] == 1)
    return list(df1_sorted.loc[mask, 'name'])
