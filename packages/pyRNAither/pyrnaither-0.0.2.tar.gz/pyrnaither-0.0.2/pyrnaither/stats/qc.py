# quality_control.R goes here
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from typing import List, Any, Tuple, Callable, Sequence
from statsmodels.robust.scale import mad
from numpy.typing import ArrayLike, NDArray
import matplotlib.pyplot as plt
from scipy import stats
from ..utils.utilities import generate_replicate_matrix_no_filter
from .qc_todo import PdfPages, generate_replicate_matrix, summarize_reps_no_filtering



import itertools


def z_prime(pos_controls: ArrayLike, neg_controls: ArrayLike) -> float:
    """
    Calculate the Z'-factor between positive and negative controls.

    Z' = 1 - 3 * (MAD_pos + MAD_neg) / |median_pos - median_neg|

    Args:
        pos_controls: Array of positive control measurements.
        neg_controls: Array of negative control measurements.

    Returns:
        Z'-factor as a float.
    """
    # Convert to numpy arrays, handle NaNs
    pos = np.asarray(pos_controls, dtype=float)
    neg = np.asarray(neg_controls, dtype=float)

    # Compute medians
    med_pos = np.nanmedian(pos)
    med_neg = np.nanmedian(neg)

    # Compute MADs: median(|x - median|)
    mad_pos = np.nanmedian(np.abs(pos - med_pos))
    mad_neg = np.nanmedian(np.abs(neg - med_neg))

    # Difference of medians absolute
    diff = np.abs(med_pos - med_neg)
    if diff == 0 or np.isnan(diff):
        raise ValueError("Difference of medians is zero or NaN; Z'-factor undefined.")

    z_prime_val = 1 - 3 * (mad_pos + mad_neg) / diff
    return z_prime_val

def discard_labtek(
    data: pd.DataFrame,
    screen_nr: int,
    labtek_nr: int
) -> pd.DataFrame:
    """
    Mark all wells on the specified labtek plate in a given screen as controls (SpotType = -1).

    Args:
        data: DataFrame containing at least columns ['ScreenNb', 'LabtekNb', 'SpotType'].
        screen_nr: Screen number.
        labtek_nr: Labtek number.

    Returns:
        DataFrame with updated SpotType values.
    """
    df = data.copy()
    # mask for the given screen and plate
    mask = (df['ScreenNb'] == screen_nr) & (df['LabtekNb'] == labtek_nr)
    df.loc[mask, 'SpotType'] = -1
    return df

def discard_wells(
    data: pd.DataFrame,
    screen_nr: int,
    labtek_nr: int,
    positions: Sequence[int]
) -> pd.DataFrame:
    """
    Mark specific well positions on a plate as controls (SpotType = -1).

    Args:
        data: DataFrame containing at least columns ['ScreenNb', 'LabtekNb', 'SpotType', 'index'].
        screen_nr: Screen number.
        labtek_nr: Labtek number.
        positions: 0-based indices within the subset of rows for the given screen and plate.

    Returns:
        DataFrame with updated SpotType values. 
    """
    df = data.copy()
    # identify subset indices
    mask_plate = (df['ScreenNb'] == screen_nr) & (df['LabtekNb'] == labtek_nr)
    subset = df[mask_plate].copy().reset_index()
    # iterate positions
    for pos in positions:
        if 0 <= pos < len(subset):
            orig_idx = subset.at[pos, 'index']
            df.at[orig_idx, 'SpotType'] = -1
    return df

def dynamic_range(
    dataset: pd.DataFrame,
    channel: str
) -> np.ndarray:
    """
    Compute the dynamic range per plate across all screens.

    For each plate (LabtekNb) in each screen (ScreenNb), the dynamic range is:
        mean(intensity of negatives) / mean(intensity of positives)
    Spots with SpotType == -1 are excluded.

    Args:
        dataset: DataFrame containing at least columns ['ScreenNb', 'LabtekNb', 'SpotType', channel].
        channel: Name of the intensity column to use.

    Returns:
        A NumPy array of dynamic range values, in order of (screen, plate) sorted by screen then plate.
    """
    # Exclude control spots
    df = dataset.loc[dataset['SpotType'] != -1].copy()

    # Prepare list to collect dynamic range values
    dr_values = []

    # Sort screens and plates for reproducible ordering
    screens = sorted(df['ScreenNb'].dropna().unique().astype(int))
    for screen in screens:
        subset_screen = df[df['ScreenNb'] == screen]
        plates = sorted(subset_screen['LabtekNb'].dropna().unique().astype(int))
        for plate in plates:
            sub = subset_screen[subset_screen['LabtekNb'] == plate]
            # compute means for SpotType 0 (negative) and 1 (positive)
            mean_neg = sub.loc[sub['SpotType'] == 0, channel].mean(skipna=True)
            mean_pos = sub.loc[sub['SpotType'] == 1, channel].mean(skipna=True)
            # handle division by zero or missing
            if mean_pos == 0 or np.isnan(mean_neg) or np.isnan(mean_pos):
                dr_values.append(np.nan)
            else:
                dr_values.append(mean_neg / mean_pos)

    return np.array(dr_values)

def read_dataset_with_header(
    file_path: str,
    nb_header: int,
    sep: str = '\t'
) -> Tuple[List[str], pd.DataFrame]:
    """
    Read a dataset file with a given number of header lines.

    Args:
        file_path: Path to the dataset file.
        nb_header: Number of header lines.
        sep: Separator used in the dataset file.

    Returns:
        A tuple containing the header lines and a DataFrame.
    """
    header = []
    with open(file_path, 'r') as f:
        for _ in range(nb_header):
            header.append(f.readline().rstrip('\n'))
    df = pd.read_csv(
        file_path,
        sep=sep,
        skiprows=nb_header,
        dtype={'SpotType': int},
        low_memory=False
    )
    return header, df


def num_cell_qual_control(
    # dataset_file: str,
    # nb_lines_header: int,
    df:pd.DataFrame,
    header:List[str],
    plot_title: str,
    show_plot: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Quality control by number of cells per well.

    Args:
        df: DataFrame containing at least columns ['NbCells', 'SpotType', 'index'].
        header: Header lines of the dataset.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.

    Returns:
        A tuple containing the updated DataFrame and histogram filename.
    """
    #header, df = read_dataset_with_header(dataset_file, nb_lines_header)
    data = df.copy()
    nb = data['NbCells']
    mean_nb = nb.mean(skipna=True)
    sd_nb = nb.std(skipna=True)
    thresh_lo = mean_nb - 3*sd_nb
    thresh_hi = mean_nb + 3*sd_nb

    # Identify indices
    under_idx = data.index[nb < thresh_lo]
    over_idx = data.index[nb > thresh_hi]

    print(f"Number of cells per well; Data for wells under lower threshold: {thresh_lo}")
    # Histogram
    fig, ax = plt.subplots()
    counts, bins, _ = ax.hist(nb.dropna(), bins=20)
    ax.axvline(thresh_lo, color='red')
    ax.axvline(thresh_hi, color='red')
    ax.set_xlabel('Number of cells per well')
    ax.set_title('Distribution of the number of cells')
    if show_plot:
        plt.show()

    # Discard under-threshold wells
    data.loc[under_idx, 'SpotType'] = -1
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    low_file = f"{base}_numCellQualControl_discarded_lower.txt"
    data.loc[under_idx].to_csv(low_file, sep='\t', index=True)

    print(f"Number of cells per well; Data for wells over upper threshold: {thresh_hi}")
    # Discard over-threshold wells
    data.loc[over_idx, 'SpotType'] = -1
    high_file = f"{base}_numCellQualControl_discarded_higher.txt"
    data.loc[over_idx].to_csv(high_file, sep='\t', index=True)

    # Save histogram
    histo_file = f"{base}_{plot_title}.pdf"
    fig.savefig(histo_file, bbox_inches='tight')
    plt.close(fig)

    # Optionally save updated file
    # data.to_csv(dataset_file, sep='\t', index=False)

    return data, histo_file


def perc_cell_qual_control(
    # dataset_file: str,
    # nb_lines_header: int,
    df:pd.DataFrame,
    header:List[str],
    plot_title: str,
    show_plot: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Quality control by percentage of cells per well.
    Similar to num_cell_qual_control but using 'PercCells'.

    Args:
        df: DataFrame containing at least columns ['PercCells', 'SpotType', 'index'].
        header: Header lines of the dataset.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.

    Returns:
        A tuple containing the updated DataFrame and histogram filename.
    """
    #header, df = read_dataset_with_header(dataset_file, nb_lines_header)
    data = df.copy()
    pc = data['PercCells']
    mean_pc = pc.mean(skipna=True)
    sd_pc = pc.std(skipna=True)
    thresh_lo = mean_pc - 3*sd_pc
    thresh_hi = mean_pc + 3*sd_pc

    under_idx = data.index[pc < thresh_lo]
    over_idx = data.index[pc > thresh_hi]

    print(f"Percentage of cells per well; Data for wells under lower threshold: {thresh_lo}")
    fig, ax = plt.subplots()
    counts, bins, _ = ax.hist(pc.dropna(), bins=20)
    ax.axvline(thresh_lo, color='red')
    ax.set_xlabel('Percentage of cells per well')
    ax.set_title('Distribution of the percentage of cells')
    if show_plot:
        plt.show()

    data.loc[under_idx, 'SpotType'] = -1
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    low_file = f"{base}_percCellQualControl_discarded_lower.txt"
    data.loc[under_idx].to_csv(low_file, sep='\t', index=True)

    print(f"Percentage of cells per well; Data for wells over upper threshold: {thresh_hi}")
    data.loc[over_idx, 'SpotType'] = -1
    high_file = f"{base}_percCellQualControl_discarded_higher.txt"
    data.loc[over_idx].to_csv(high_file, sep='\t', index=True)

    histo_file = f"{base}_{plot_title}.pdf"
    fig.savefig(histo_file, bbox_inches='tight')
    plt.close(fig)

    return data, histo_file


def zprime_qual_control(
    header: List[str],
    data: pd.DataFrame,
    channel: str,
    plot_title: str,
    show_plot: bool = False
) -> Tuple[str, pd.DataFrame]:
    """
    Compute Z'-factor per plate and experiment; save table and plot.    

    Args:
        header: Header lines of the dataset.
        data: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb'].
        channel: Channel to use for Z'-factor calculation.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.

    Returns:
        A tuple containing the Z'-factor table filename and updated DataFrame.
    """
    df = data[data['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    results = []
    labels = []
    for screen in screens:
        subset = df[df['ScreenNb'] == screen]
        plates = sorted(subset['LabtekNb'].unique())
        for plate in plates:
            sub = subset[subset['LabtekNb'] == plate]
            pos = sub.loc[sub['SpotType'] == 1, channel]
            neg = sub.loc[sub['SpotType'] == 0, channel]
            zf = z_prime(pos, neg)
            results.append(zf)
            labels.append(f"{screen}_{plate}")
            if show_plot:
                print(f"The Z' for Experiment {screen} Plate {plate} is {zf}")
    out_df = pd.DataFrame({
        'Experiment': [int(lbl.split('_')[0]) for lbl in labels],
        'Plate': [int(lbl.split('_')[1]) for lbl in labels],
        'Z_Prime_Score': results
    })
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    table_file = f"{base}_Z'Scores.txt"
    out_df.to_csv(table_file, sep='\t', index=False)

    plot_name = f"{base}_{plot_title}"
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(results, marker='o', linestyle='-')
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=90, fontsize=6)
    ax.set_title(plot_title)
    ax.set_ylabel("Z'-factor")
    fig.tight_layout()
    if show_plot:
        plt.show()
    for ext in ('pdf','png'):
        fig.savefig(f"{plot_name}.{ext}")
    plt.close(fig)
    return plot_name, out_df


def snr_qual_control(
    # dataset_file: str,
    # nb_lines_header: int,
    df:pd.DataFrame,
    header:List[str],
    channel: str,
    noise: str,
    plot_title: str,
    show_plot: bool = False
) -> None:
    """
    Compute signal-to-noise ratio (SNR = channel/noise) and plot histograms.

    Args:
        df: DataFrame containing at least columns ['SpotType', channel, noise].
        header: Header lines of the dataset.
        channel: Channel to use for SNR calculation.
        noise: Noise to use for SNR calculation.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.

    Returns:
        None
    """
    # header, df = read_dataset_with_header(dataset_file, nb_lines_header)
    data = df[df['SpotType'] != -1]
    snr = data[channel] / data[noise]

    # overall histogram
    fig, ax = plt.subplots()
    ax.hist(snr.dropna(), bins=20)
    ax.set_xlabel('SNR per well')
    ax.set_title(plot_title)
    if show_plot:
        plt.show()
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    for ext in ('pdf','png'):
        fig.savefig(f"{base}_{plot_title}.{ext}")
    plt.close(fig)

    # per experiment
    screens = sorted(data['ScreenNb'].unique())
    n_screens = len(screens)
    cols = int(np.ceil(np.sqrt(n_screens)))
    rows = int(np.ceil(n_screens/cols))
    fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
    axes = axes.flatten()
    for ax, screen in zip(axes, screens):
        subset = snr[data['ScreenNb'] == screen]
        ax.hist(subset.dropna(), bins=20)
        ax.set_title(f"Exp {screen}")
    fig.tight_layout()
    if show_plot:
        plt.show()
    fig.savefig(f"{base}_{plot_title}_PerExp.pdf")
    plt.close(fig)

    # per plate within each experiment
    for screen in screens:
        subset_df = data[data['ScreenNb'] == screen]
        plates = sorted(subset_df['LabtekNb'].unique())
        n_plates = len(plates)
        cols = int(np.ceil(np.sqrt(n_plates)))
        rows = int(np.ceil(n_plates/cols))
        fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
        axes = axes.flatten()
        for ax, plate in zip(axes, plates):
            sub_snr = snr[(data['ScreenNb'] == screen) & (data['LabtekNb'] == plate)]
            ax.hist(sub_snr.dropna(), bins=20)
            ax.set_title(f"Exp {screen} Plate {plate}")
        fig.tight_layout()
        fig.savefig(f"{base}_{plot_title}_PerPlate_Exp{screen}.pdf")
        plt.close(fig)


def dr_qual_control(
    header: List[str],
    data: pd.DataFrame,
    channel: str,
    plot_title: str,
    show_plot: bool = False
) -> Tuple[str, pd.DataFrame]:
    """
    Dynamic range quality control: compute DR and plot.

    Args:
        header: Header lines of the dataset.
        data: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for DR calculation.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.

    Returns:
        A tuple containing the DR table filename and updated DataFrame.
    """
    df = data[data['SpotType'] != -1]
    dr = dynamic_range(df, channel)
    # build labels
    screens = sorted(df['ScreenNb'].unique())
    labels = []
    for screen in screens:
        subset = df[df['ScreenNb'] == screen]
        for plate in sorted(subset['LabtekNb'].unique()):
            labels.append(f"{screen}_{plate}")
    out_df = pd.DataFrame({
        'Exp_Plate': labels,
        'DR': dr
    })
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    table_file = f"{base}_DR.txt"
    out_df.to_csv(table_file, sep='\t', index=False)

    plot_name = f"{base}_{plot_title}"
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(dr, marker='o', linestyle='-')
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=90, fontsize=6)
    ax.set_title(plot_title)
    ax.set_ylabel('Dynamic Range')
    fig.tight_layout()
    if show_plot:
        plt.show()
    for ext in ('pdf','png'):
        fig.savefig(f"{plot_name}.{ext}")
    plt.close(fig)
    return plot_name, out_df


def plot_control_histo(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    show_plot: bool = False
) -> Figure:
    """
    Plot histogram of controls vs data for a given channel.

    Args:
        header: list of header lines
        dataset: DataFrame containing 'SpotType' and channel columns
        channel: column name to plot
        plot_title: title for the plot
        show_plot: if True, display interactively

    Returns:
        fig: matplotlib Figure
    """
    # Filter out NAs
    all_vals = dataset.loc[dataset['SpotType'] != -1, channel].dropna()
    neg = dataset.loc[dataset['SpotType'] == 0, channel].dropna()
    pos = dataset.loc[dataset['SpotType'] == 1, channel].dropna()
    other = dataset.loc[dataset['SpotType'] == 2, channel].dropna()

    if all_vals.empty:
        raise ValueError("Cannot plot histogram (only NAs in dataset)")

    # Compute breaks
    rng = all_vals.max() - all_vals.min()
    n_bins = 20
    if round((rng + 1) / n_bins) != 0:
        a = all_vals.min()
        b = all_vals.max() + round((rng + 1) / n_bins)
        d = int(np.ceil((b - a) / round((rng + 1) / n_bins)))
        bins = np.linspace(a, b, d)
    else:
        a = all_vals.min()
        b = all_vals.max() + abs(a + 0.5)
        d = int(np.ceil((b - a) / ((rng + 1) / n_bins)))
        bins = np.linspace(a, b, d)

    # Plot
    fig, ax = plt.subplots()
    ax.hist(other, bins=bins, alpha=0.5, label='Data')
    ax.hist(pos, bins=bins, histtype='stepfilled', alpha=0.5, label='Positive Controls')
    ax.hist(neg, bins=bins, histtype='step', linestyle='--', label='Negative Controls')
    ax.set_title(plot_title)
    ax.set_xlabel(channel)
    ax.legend()
    fig.tight_layout()
    if show_plot:
        plt.show()
    return fig


def plot_control_histo_per_plate(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    plot_design: int = 1,
    show_plot: bool = False
) -> None:
    """
    Plot histograms per plate.
    If show_plot or plot_design used to layout subplots, but this function saves to file.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for histogram calculation.
        plot_title: Title for the plot.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.

    Returns:
        None
    """
    df = dataset[dataset['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    for screen in screens:
        subset = df[df['ScreenNb'] == screen]
        plates = sorted(subset['LabtekNb'].unique())
        n = len(plates)
        cols = int(np.ceil(np.sqrt(n))) if plot_design == 1 else 1
        rows = int(np.ceil(n / cols))
        fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
        axes = np.array(axes).reshape(-1)
        for ax, plate in zip(axes, plates):
            sub = subset[subset['LabtekNb'] == plate]
            all_vals = sub.loc[sub['SpotType'] != -1, channel].dropna()
            neg = sub.loc[sub['SpotType'] == 0, channel].dropna()
            pos = sub.loc[sub['SpotType'] == 1, channel].dropna()
            other = sub.loc[sub['SpotType'] == 2, channel].dropna()
            if all_vals.empty:
                ax.text(0.5,0.5,f"Exp{screen} Plate{plate} No data", ha='center')
                ax.axis('off')
            else:
                ax.hist(other, bins=20, alpha=0.5)
                ax.hist(pos, bins=20, histtype='stepfilled', alpha=0.5)
                ax.hist(neg, bins=20, histtype='step', linestyle='--')
                ax.set_title(f"Plate {plate}")
        fig.suptitle(f"{plot_title} for Experiment {screen}")
        fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))
        out_file = f"{base}_{plot_title}_Exp{screen}_PerPlate.png"
        fig.savefig(out_file)
        if show_plot:
            plt.show()
        plt.close(fig)


def plot_histo(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    show_plot: bool = False
) -> Figure:
    """
    Simple histogram of all non-control data in a channel.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for histogram calculation.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.

    Returns:
        The Figure object.
    """
    vals = dataset.loc[dataset['SpotType'] != -1, channel].dropna()
    if vals.empty:
        raise ValueError("Cannot plot histogram (only NAs in dataset)")
    # compute breaks same as Greenwood
    rng = vals.max() - vals.min()
    n_bins = 20
    if round((rng + 1) / n_bins) != 0:
        a = vals.min()
        b = vals.max() + round((rng + 1) / n_bins)
        d = int(np.ceil((b - a) / round((rng + 1) / n_bins)))
        bins = np.linspace(a, b, d)
    else:
        a = vals.min()
        b = vals.max() + abs(a + 0.5)
        d = int(np.ceil((b - a) / ((rng + 1) / n_bins)))
        bins = np.linspace(a, b, d)
    fig, ax = plt.subplots()
    ax.hist(vals, bins=bins)
    ax.set_title(plot_title)
    ax.set_xlabel(channel)
    fig.tight_layout()
    if show_plot:
        plt.show()
    return fig


def plot_histo_per_plate(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    plot_design: int = 1,
    show_plot: bool = False
) -> None:
    """
    Histogram of data per plate (non-controls only).
    Saves one PNG per experiment.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for histogram calculation.
        plot_title: Title for the plot.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.

    Returns:
        None
    """
    df = dataset[dataset['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    for screen in screens:
        subset = df[df['ScreenNb'] == screen]
        plates = sorted(subset['LabtekNb'].unique())
        n = len(plates)
        cols = int(np.ceil(np.sqrt(n))) if plot_design == 1 else 1
        rows = int(np.ceil(n / cols))
        fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
        axes = np.array(axes).reshape(-1)
        for ax, plate in zip(axes, plates):
            sub = subset[subset['LabtekNb'] == plate]
            vals = sub.loc[sub['SpotType'] != -1, channel].dropna()
            if vals.empty:
                ax.text(0.5,0.5,f"Exp{screen} Plate{plate}No data", ha='center')
                ax.axis('off')
            else:
                ax.hist(vals, bins=20)
                ax.set_title(f"Plate {plate}")
        fig.suptitle(f"{plot_title} for Experiment {screen}")
        fig.tight_layout(rect=(0,0,1,0.95))
        out_file = f"{base}_{plot_title}_Exp{screen}_PerPlate.png"
        fig.savefig(out_file)
        if show_plot:
            plt.show()
        plt.close(fig)


def plot_histo_per_screen(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    plot_design: int = 1,
    show_plot: bool = False
) -> None:
    """
    Histogram of data per screen (non-controls only).
    Saves one PNG per screen.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for histogram calculation.
        plot_title: Title for the plot.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.

    Returns:
        None
    """
    df = dataset[dataset['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    n = len(screens)
    cols = int(np.ceil(np.sqrt(n))) if plot_design == 1 else 1
    rows = int(np.ceil(n / cols))
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
    axes = np.array(axes).reshape(-1)
    for ax, screen in zip(axes, screens):
        sub = df[df['ScreenNb'] == screen]
        vals = sub[channel].dropna()
        if vals.empty:
            ax.text(0.5, 0.5, f"Exp{screen}No data", ha='center')
            ax.axis('off')
        else:
            ax.hist(vals, bins=20)
            ax.set_title(f"Exp {screen}")
    fig.suptitle(plot_title)
    fig.tight_layout(rect=(0,0,1,0.95))
    out_file = f"{base}_{plot_title}_PerScreen.png"
    fig.savefig(out_file)
    if show_plot:
        plt.show()
    plt.close(fig)


def plot_qq(
    #header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    show_plot: bool = False
) -> Figure:
    """
    Q-Q plot of data (non-controls only) against a normal distribution.

    Args:
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for Q-Q plot calculation.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.

    Returns:
        The Figure object.
    """
    # filter out controls
    vals = dataset.loc[dataset['SpotType'] != -1, channel].dropna()
    if vals.empty:
        raise ValueError("Cannot plot Q-Q (only NAs in dataset)")

    fig, ax = plt.subplots()
    stats.probplot(vals, dist="norm", plot=ax)
    ax.set_title(plot_title)
    fig.tight_layout()
    if show_plot:
        plt.show()
    return fig


def plot_qq_per_plate(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    plot_design: int = 1,
    show_plot: bool = False
) -> None:
    """
    Per-plate Q-Q plots saved as PNGs per experiment.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for Q-Q plot calculation.
        plot_title: Title for the plot.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.

    Returns:
        None
    """
    df = dataset[dataset['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    for screen in screens:
        subset = df[df['ScreenNb'] == screen]
        plates = sorted(subset['LabtekNb'].unique())
        n = len(plates)
        cols = int(np.ceil(np.sqrt(n))) if plot_design == 1 else 1
        rows = int(np.ceil(n / cols))
        fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
        axes = np.array(axes).reshape(-1)
        for ax, plate in zip(axes, plates):
            sub = subset[subset['LabtekNb'] == plate]
            vals = sub[channel].dropna()
            if vals.empty:
                ax.text(0.5,0.5,f"Exp{screen} Plate{plate}No data", ha='center')
                ax.axis('off')
            else:
                stats.probplot(vals, dist="norm", plot=ax)
                ax.set_title(f"Plate {plate}")
        fig.suptitle(f"{plot_title} for Experiment {screen}")
        fig.tight_layout(rect=(0,0,1,0.95))
        out_file = f"{base}_{plot_title}_Exp{screen}_QqPerPlate.png"
        fig.savefig(out_file)
        if show_plot:
            plt.show()
        plt.close(fig)


def plot_qq_per_screen(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    plot_design: int = 1,
    show_plot: bool = False
) -> None:
    """
    Per-screen Q-Q plots saved as a single PNG.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for Q-Q plot calculation.
        plot_title: Title for the plot.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.

    Returns:
        None
    """
    df = dataset[dataset['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    n = len(screens)
    cols = int(np.ceil(np.sqrt(n))) if plot_design == 1 else 1
    rows = int(np.ceil(n / cols))
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
    axes = np.array(axes).reshape(-1)
    for ax, screen in zip(axes, screens):
        sub = df[df['ScreenNb'] == screen]
        vals = sub[channel].dropna()
        if vals.empty:
            ax.text(0.5,0.5,f"Exp{screen}No data", ha='center')
            ax.axis('off')
        else:
            stats.probplot(vals, dist="norm", plot=ax)
            ax.set_title(f"Exp {screen}")
    fig.suptitle(plot_title)
    fig.tight_layout(rect=(0,0,1,0.95))
    out_file = f"{base}_{plot_title}_QqPerScreen.png"
    fig.savefig(out_file)
    if show_plot:
        plt.show()
    plt.close(fig)


def replicates_spearman_cor(
    header: List[str],
    dataset: pd.DataFrame,
    flag: int,
    col4val: str,
    col4anno: str,
    file_suffix: str
) -> str:
    """
    Compute Spearman correlations between replicates (flag=1) or across experiments (flag=2).
    Saves a TSV file and returns its path.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        flag: Flag to indicate whether to compute Spearman correlations between replicates (flag=1) or across experiments (flag=2).
        col4val: Column name to use for Spearman correlation calculation.
        col4anno: Column name to use for annotation.
        file_suffix: Suffix to add to the output file name.

    Returns:
        The path to the output file.
    """
    import os
    from scipy.stats import spearmanr

    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    if flag == 1:
        screens = sorted(dataset['ScreenNb'].unique())
        fname = f"{base}_{file_suffix}_Spearmancor.txt"
        # write header
        with open(fname, 'w') as f:
            f.write("Exp	Replicate	Replicate	Correlation_coeff")
        for screen in screens:
            subset = dataset[dataset['ScreenNb'] == screen]
            # assume helper: generate_replicate_matrix returns (matrix NxR, pos_idx, neg_idx)
            mat, pos_idx, neg_idx = generate_replicate_matrix_no_filter(subset, n_reps=3, col=col4val, anno=col4anno)
            for i, j in [(0,1), (1,2), (0,2)]:
                col_i = mat[:, i]
                col_j = mat[:, j]
                if np.any(~np.isnan(col_i)) and np.any(~np.isnan(col_j)):
                    coef, _ = spearmanr(col_i, col_j, nan_policy='omit')
                else:
                    coef = np.nan
                with open(fname, 'a') as f:
                    f.write(f"{screen}	{i+1}	{j+1}	{coef}")
        return fname
    elif flag == 2:
        screens = sorted(dataset['ScreenNb'].unique())
        # collect summary per screen
        cols = []
        for screen in screens:
            subset = dataset[dataset['ScreenNb'] == screen]
            # assume helper: summarize_reps_no_filtering returns DataFrame with col4val
            tmp = summarize_reps_no_filtering(subset, col4val, col4anno)
            cols.append(tmp[col4val].values)
        arr = np.column_stack(cols)
        corr_mat, _ = spearmanr(arr, axis=0, nan_policy='omit')
        # corr_mat is square
        corr_df = pd.DataFrame(corr_mat[:len(screens), :len(screens)], index=screens, columns=screens)
        fname = f"{base}_{file_suffix}_Spearmancor_AllExp.txt"
        corr_df.to_csv(fname, sep='	')
        return fname
    else:
        raise ValueError("flag must be 1 or 2")


def replicates_cv(
    header: List[str],
    dataset: pd.DataFrame,
    plot_title: str,
    col4val: str,
    col4anno: str,
    plot_design: int = 1,
    show_plot: bool = False
) -> None:
    """
    Plot coefficient of variation (CV) vs mean intensity per screen.
    Saves PNG per experiment.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        plot_title: Title for the plot.
        col4val: Column name to use for CV calculation.
        col4anno: Column name to use for annotation.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.

    Returns:
        None
    """
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    screens = sorted(dataset['ScreenNb'].unique())
    for screen in screens:
        subset = dataset[dataset['ScreenNb'] == screen]
        # generate replicate matrix and control indices
        mat, pos_idx, neg_idx = generate_replicate_matrix_no_filter(subset, n_reps=3, col=col4val, anno=col4anno)
        means = np.nanmean(mat, axis=1)
        stds = np.nanstd(mat, axis=1)
        cvs = stds / means
        fig, ax = plt.subplots()
        ax.scatter(means, cvs, s=10, label='Data')
        ax.scatter(means[pos_idx], cvs[pos_idx], color='green', s=10, label='Pos controls')
        ax.scatter(means[neg_idx], cvs[neg_idx], color='red', s=10, label='Neg controls')
        ax.set_xlabel('Mean Intensity')
        ax.set_ylabel('CV')
        ax.set_title(f"{plot_title}, Exp {screen}")
        ax.legend()
        fig.tight_layout()
        fname = f"{base}_{plot_title}_Exp{screen}.png"
        fig.savefig(fname)
        if show_plot:
            plt.show()
        plt.close(fig)


def make_boxplot_controls(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    show_plot: bool = False
) -> Figure:
    """
    Make a boxplot of channel values by control type.
    Returns the Figure.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for boxplot calculation.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.

    Returns:
        The Figure object.
    """
    df = dataset[dataset['SpotType'] != -1]
    labels = df['SpotType'].map({0: 'Neg. contr.', 1: 'Pos. contr.', 2: 'Exp. data'})
    data_groups = [df.loc[labels == lab, channel].dropna() for lab in ['Neg. contr.', 'Pos. contr.', 'Exp. data']]
    fig, ax = plt.subplots()
    ax.boxplot(data_groups, labels=['Neg. contr.', 'Pos. contr.', 'Exp. data'])
    ax.set_title(plot_title)
    ax.set_ylabel(channel)
    fig.tight_layout()
    if show_plot:
        plt.show()
    return fig


def make_boxplot_controls_per_plate(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    plot_design: int = 1,
    show_plot: bool = False
) -> Tuple[int, int]:
    """
    Generate boxplots of channel values by SpotType for each plate.

    Saves figures per experiment and plate in both PDF and PNG formats.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for boxplot calculation.
        plot_title: Title for the plot.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.

    Returns:
        (min_screen, max_screen)
    """
    df = dataset[dataset['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    # derive base filename from header
    base = header[0].split(',')[1] if ',' in header[0] else header[0]

    for screen in screens:
        sub_screen = df[df['ScreenNb'] == screen]
        plates = sorted(sub_screen['LabtekNb'].unique())
        # layout
        n = len(plates)
        if plot_design == 1 and n > 0:
            cols = int(np.ceil(np.sqrt(n)))
            rows = int(np.ceil(n / cols))
        else:
            cols, rows = 1, n

        # overall figure for experiment
        fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3), squeeze=False)
        axes_flat = axes.flatten()

        for ax, plate in zip(axes_flat, plates):
            sub = sub_screen[sub_screen['LabtekNb'] == plate]
            # map SpotType to labels
            labels = sub['SpotType'].map({0: 'Neg. controls', 1: 'Pos. controls', 2: 'Exp. data'})
            groups = [sub.loc[labels == lab, channel].dropna() for lab in ['Neg. controls','Pos. controls','Exp. data']]

            if any(len(g) > 0 for g in groups):
                ax.boxplot(groups, labels=['Neg','Pos','Data'])
                ax.set_title(f"Plate {plate}")
            else:
                ax.text(0.5,0.5,f"No data\nExp {screen} Plate {plate}", ha='center')
                ax.axis('off')

        fig.suptitle(f"{plot_title} for Experiment {screen}")
        fig.tight_layout(rect=[0,0,1,0.95])
        # save
        pdf_file = f"{base}_{plot_title}_Exp_{screen}.pdf"
        png_file = f"{base}_{plot_title}_Exp_{screen}.png"
        fig.savefig(pdf_file)
        fig.savefig(png_file)
        if show_plot:
            plt.show()
        plt.close(fig)

    return (min(screens) if screens else 0, max(screens) if screens else 0)


def make_boxplot_controls_per_screen(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    plot_design: int = 1,
    show_plot: bool = False
) -> Tuple[int, int]:
    """
    Generate boxplots of channel values by SpotType for each screen.

    Saves figures per screen in PDF and PNG formats.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for boxplot calculation.
        plot_title: Title for the plot.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.

    Returns:
        (min_screen, max_screen)
    """
    df = dataset[dataset['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    base = header[0].split(',')[1] if ',' in header[0] else header[0]

    n = len(screens)
    if plot_design == 1 and n > 0:
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))
    else:
        cols, rows = 1, n

    fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3), squeeze=False)
    axes_flat = axes.flatten()

    for ax, screen in zip(axes_flat, screens):
        sub = df[df['ScreenNb'] == screen]
        labels = sub['SpotType'].map({0: 'Neg. controls', 1: 'Pos. controls', 2: 'Exp. data'})
        groups = [sub.loc[labels == lab, channel].dropna() for lab in ['Neg. controls','Pos. controls','Exp. data']]
        if any(len(g) > 0 for g in groups):
            ax.boxplot(groups, labels=['Neg','Pos','Data'])
            ax.set_title(f"Exp {screen}")
        else:
            ax.text(0.5,0.5,f"No data\nExp {screen}", ha='center')
            ax.axis('off')

    fig.suptitle(plot_title)
    fig.tight_layout(rect=[0,0,1,0.95])
    pdf_file = f"{base}_{plot_title}.pdf"
    png_file = f"{base}_{plot_title}.png"
    fig.savefig(pdf_file)
    fig.savefig(png_file)
    if show_plot:
        plt.show()
    plt.close(fig)

    return (min(screens) if screens else 0, max(screens) if screens else 0)


def make_boxplot_per_screen(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    show_plot: bool = False
) -> None:
    """
    Boxplot of `channel` by ScreenNb (experiment) for non-control data.
    Saves a PNG and/or displays interactively.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for boxplot calculation.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.

    Returns:
        None
    """
    df = dataset[dataset['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    fig, ax = plt.subplots(figsize=(6,4))
    ax.boxplot(
        [df.loc[df['ScreenNb'] == s, channel].dropna() for s in screens],
        labels=screens
    )
    ax.set_title(plot_title)
    ax.set_xlabel('Exp. ##')
    ax.set_ylabel(channel)
    fig.tight_layout()
    out_file = f"{base}_{plot_title}_PerScreen.png"
    fig.savefig(out_file)
    if show_plot:
        plt.show()
    plt.close(fig)


def make_boxplot_per_plate(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    plot_design: int = 1,
    show_plot: bool = False
) -> None:
    """
    Boxplots of `channel` by LabtekNb (plate) within each ScreenNb (experiment).
    If plot_design==1, lays out all experiments in a grid on one figure; otherwise emits one figure per experiment.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for boxplot calculation.
        plot_title: Title for the plot.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.

    Returns:
        None
    """
    df = dataset[dataset['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    if plot_design == 1:
        n = len(screens)
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n/cols))
        fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
        axes = axes.flatten()
        for ax, screen in zip(axes, screens):
            sub = df[df['ScreenNb'] == screen]
            plates = sorted(sub['LabtekNb'].unique())
            ax.boxplot(
                [sub.loc[sub['LabtekNb'] == p, channel].dropna() for p in plates],
                labels=plates
            )
            ax.set_title(f"{plot_title} for Exp. {screen}")
            ax.set_xlabel('Plate')
            ax.set_ylabel(channel)
        fig.tight_layout()
        out_file = f"{base}_{plot_title}.png"
        fig.savefig(out_file)
        if show_plot:
            plt.show()
        plt.close(fig)
    else:
        for screen in screens:
            sub = df[df['ScreenNb'] == screen]
            plates = sorted(sub['LabtekNb'].unique())
            fig, ax = plt.subplots(figsize=(6,4))
            ax.boxplot(
                [sub.loc[sub['LabtekNb'] == p, channel].dropna() for p in plates],
                labels=plates
            )
            ax.set_title(f"{plot_title} for Exp. {screen}")
            ax.set_xlabel('Plate')
            ax.set_ylabel(channel)
            out_file = f"{base}_{plot_title}(Exp_{screen}).png"
            fig.tight_layout()
            fig.savefig(out_file)
            if show_plot:
                plt.show()
            plt.close(fig)


def make_boxplot_4_plate_type(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    show_plot: bool = False
) -> None:
    """
    Boxplots of `channel` by ScreenNb (experiment) within each LabtekNb (plate type).
    Emits one figure per plate type.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for boxplot calculation.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.

    Returns:
        None
    """
    df = dataset[dataset['SpotType'] != -1]
    plates = sorted(df['LabtekNb'].unique())
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    for plate in plates:
        sub = df[df['LabtekNb'] == plate]
        exps = sorted(sub['ScreenNb'].unique())
        fig, ax = plt.subplots(figsize=(6,4))
        ax.boxplot(
            [sub.loc[sub['ScreenNb'] == e, channel].dropna() for e in exps],
            labels=exps
        )
        ax.set_title(f"{plot_title} for Plate {plate}")
        ax.set_xlabel('Exp. #')
        ax.set_ylabel(channel)
        out_file = f"{base}_{plot_title}_Plate{plate}.png"
        fig.tight_layout()
        fig.savefig(out_file)
        if show_plot:
            plt.show()
        plt.close(fig)


def spatial_distrib(
    header: List[str],
    dataset: pd.DataFrame,
    plot_title: str,
    col4plot: str,
    col4anno: str,
    show_plot: bool = False
) -> Tuple[str, Tuple[int,int], Tuple[int,int]]:
    """
    Generate spatial distribution heatmaps per experiment and plate.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        plot_title: Title for the plot.
        col4plot: Column name to use for boxplot calculation.
        col4anno: Column name to use for annotation.
        show_plot: Whether to display the plot.

    Returns:
        The base plot name, screen range, and plate range.
    """
    df = dataset.copy()
    # mask discarded spots
    df.loc[df['SpotType'] == -1, col4plot] = np.nan

    screens = sorted(df['ScreenNb'].unique())
    min_screen, max_screen = screens[0], screens[-1]
    header_base = header[0].split(',')[1] if ',' in header[0] else header[0]
    base_name = f"{header_base}_{plot_title}"

    min_plate, max_plate = None, None
    for screen in screens:
        sub_scr = df[df['ScreenNb'] == screen]
        if sub_scr.empty:
            continue
        plates = sorted(sub_scr['LabtekNb'].unique())
        if min_plate is None:
            min_plate, max_plate = plates[0], plates[-1]
        for plate in plates:
            sub_plate = sub_scr[sub_scr['LabtekNb'] == plate]
            values = sub_plate.pivot_table(
                index='RowNb', columns='ColNb', values=col4plot
            )
            title = f"{plot_title} plate {plate} Exp {screen}"
            fig, ax = plt.subplots()
            cax = ax.imshow(values, cmap='YlOrBr', origin='lower')
            ax.set_title(title)
            fig.colorbar(cax)
            if show_plot:
                plt.show()
            for ext in ['png','pdf']:
                fname = f"{base_name}_Exp{screen}_Plate{plate}.{ext}"
                fig.savefig(fname, bbox_inches='tight')
            plt.close(fig)
    return base_name, (min_screen, max_screen), (min_plate, max_plate)


def compare_replicates(
    header: List[str],
    dataset: pd.DataFrame,
    plot_title: str,
    col4val: str,
    col4anno: str,
    plot_design: int = 1,
    show_plot: bool = False
) -> Tuple[str, Tuple[int,int], int]:
    """
    Compare replicate measurements pairwise for each experiment.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        plot_title: Title for the plot.
        col4val: Column name to use for boxplot calculation.
        col4anno: Column name to use for annotation.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.

    Returns:
        The base plot name, screen range, and max number of combinations.
    """
    df = dataset[dataset['SpotType'] != -1]
    screens = sorted(df['ScreenNb'].unique())
    header_base = header[0].split(',')[1] if ',' in header[0] else header[0]
    base_name = f"{header_base}_{plot_title}"

    max_comb = 0
    for screen in screens:
        sub = df[df['ScreenNb'] == screen]
        # build replicate matrix indices via helper
        mat, pos_idx, neg_idx = generate_replicate_matrix(sub, min_reps=2, col=col4val, anno=col4anno)
        n_rep = mat.shape[1]
        # determine valid columns
        valid_cols = [i for i in range(n_rep) if np.isnan(mat[:,i]).sum() <= 0.4*mat.shape[0]]
        combos = list(itertools.combinations(valid_cols, 2))
        max_comb = max(max_comb, len(combos))
        # plotting
        if show_plot:
            if plot_design == 1:
                n = len(combos)
                cols = int(np.ceil(np.sqrt(n)))
                rows = int(np.ceil(n/cols))
                fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3))
                axes = axes.flatten()
            for ax, (i,j) in zip(axes if plot_design==1 else [None]*len(combos), combos):
                x = mat[:,i]
                y = mat[:,j]
                lim = (np.nanmin([x,y]), np.nanmax([x,y]))
                if plot_design == 1:
                    axis = ax
                else:
                    fig, axis = plt.subplots()
                axis.scatter(x,y, s=10)
                axis.plot(lim, lim, linestyle='--', color='gray')
                axis.set_xlabel(f"replicate {i+1}")
                axis.set_ylabel(f"replicate {j+1}")
                axis.set_title(f"Exp {screen}")
                if plot_design != 1:
                    if show_plot: plt.show()
                    for ext in ['png','pdf']:
                        plt.savefig(f"{base_name}_Exp{screen}_{i+1}_{j+1}.{ext}", bbox_inches='tight')
                    plt.close(fig)
            if plot_design == 1:
                fig.suptitle(f"{plot_title} Exp {screen}")
                fig.tight_layout(rect=[0,0,1,0.95])
                for ext in ['png','pdf']:
                    fig.savefig(f"{base_name}_Exp{screen}.{ext}", bbox_inches='tight')
                if show_plot: plt.show()
                plt.close(fig)
    return base_name, (screens[0], screens[-1]), max_comb


def compare_replica_plates(
    header: List[str],
    dataset: pd.DataFrame,
    plot_title: str,
    col4val: str,
    show_plot: bool = False
) -> str:
    """
    For each plate, compares its values across all pairs of experiments.
    Saves scatter plots of plate i in exp j vs exp k into a single PDF and optionally displays them.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        plot_title: Title for the plot.
        col4val: Column name to use for boxplot calculation.
        show_plot: Whether to display the plot.

    Returns:
        The PDF filename.
    """
    # prepare
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    out_pdf = f"{base}_{plot_title}.pdf"
    screens = sorted(dataset['ScreenNb'].unique())
    plates = sorted(dataset['LabtekNb'].unique())
    if len(screens) < 2:
        raise ValueError("Comparison not possible - Only one experiment in dataset")
    # mask discarded
    df = dataset.copy()
    df.loc[df['SpotType'] == -1, col4val] = np.nan

    with PdfPages(out_pdf) as pdf:
        for plate in plates:
            for i, j in enumerate(screens[:-1]):
                remaining = screens[i+1:]
                cols = int(np.ceil(np.sqrt(len(remaining))))
                rows = int(np.ceil(len(remaining) / cols))
                fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*4))
                axes = np.array(axes).reshape(-1)
                for ax, k in zip(axes, remaining):
                    sub1 = df[(df['ScreenNb'] == j) & (df['LabtekNb'] == plate)]
                    sub2 = df[(df['ScreenNb'] == k) & (df['LabtekNb'] == plate)]
                    x = sub1[col4val].values
                    y = sub2[col4val].values
                    if x.size > 0 and y.size > 0 and not (np.all(np.isnan(x)) or np.all(np.isnan(y))):
                        mn = np.nanmin(np.concatenate([x, y]))
                        mx = np.nanmax(np.concatenate([x, y]))
                        ax.scatter(x, y, s=5)
                        ax.plot([mn, mx], [mn, mx], '--', color='gray')
                        ax.set_xlabel(f"Plate {plate} Exp {j}")
                        ax.set_ylabel(f"Plate {plate} Exp {k}")
                    ax.set_title(f"Plate {plate}: Exp {j} vs {k}")
                fig.suptitle(f"{plot_title} - plate {plate}")
                fig.tight_layout(rect=[0,0,1,0.96])
                pdf.savefig(fig)
                if show_plot:
                    plt.show()
                plt.close(fig)
    return out_pdf


def compare_replicate_sd(
    header: List[str],
    dataset: pd.DataFrame,
    plot_title: str,
    colname4sd: str,
    col4anno: str,
    show_plot: bool = False
) -> str:
    """
    Computes the per-spot standard deviation across replicates and
    lays them out in a plate-shaped grid heatmap.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        plot_title: Title for the plot.
        colname4sd: Column name to use for standard deviation calculation.
        col4anno: Column name to use for annotation.
        show_plot: Whether to display the plot.

    Returns:
        The base filename (without extension).
    """
    # replicate matrix must return (values, pos_idx, neg_idx)
    mat, pos_idx, neg_idx = generate_replicate_matrix(
        dataset, min_reps=2, col=colname4sd, anno=col4anno
    )
    sd_vec = np.nanstd(mat, axis=1)
    n = len(sd_vec)
    nrow = int(np.ceil(np.sqrt(n)))
    ncol = int(np.ceil(n / nrow))
    # pad to full grid
    if nrow * ncol > n:
        sd_vec = np.concatenate([sd_vec, np.full(nrow*ncol - n, np.nan)])
    grid = sd_vec.reshape(nrow, ncol)

    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    fname = f"{base}_{plot_title}"

    fig, ax = plt.subplots(figsize=(ncol, nrow))
    cax = ax.imshow(grid, cmap='YlOrBr', origin='lower', aspect='equal')
    ax.set_title(plot_title)
    fig.colorbar(cax, ax=ax)
    fig.tight_layout()
    for ext in ('png','pdf'):
        fig.savefig(f"{fname}.{ext}")
    if show_plot:
        plt.show()
    plt.close(fig)
    return fname


def compare_replicate_sd_per_screen(
    header: List[str],
    dataset: pd.DataFrame,
    plot_title: str,
    colname4sd: str,
    col4anno: str,
    show_plot: bool = False
) -> List[str]:
    """
    Same as compare_replicate_sd, but produces one heatmap per experiment.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        plot_title: Title for the plot.
        colname4sd: Column name to use for standard deviation calculation.
        col4anno: Column name to use for annotation.
        show_plot: Whether to display the plot.

    Returns:
        List of base filenames.
    """
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    screens = sorted(dataset['ScreenNb'].unique())
    out_files = []
    for screen in screens:
        sub = dataset[dataset['ScreenNb'] == screen]
        mat, pos_idx, neg_idx = generate_replicate_matrix(
            sub, min_reps=2, col=colname4sd, anno=col4anno
        )
        sd_vec = np.nanstd(mat, axis=1)
        n = len(sd_vec)
        nrow = int(np.ceil(np.sqrt(n)))
        ncol = int(np.ceil(n / nrow))
        if nrow * ncol > n:
            sd_vec = np.concatenate([sd_vec, np.full(nrow*ncol - n, np.nan)])
        grid = sd_vec.reshape(nrow, ncol)

        fname = f"{base}_{plot_title}_Exp{screen}"
        fig, ax = plt.subplots(figsize=(ncol, nrow))
        cax = ax.imshow(grid, cmap='YlOrBr', origin='lower', aspect='equal')
        ax.set_title(f"{plot_title} - Exp {screen}")
        fig.colorbar(cax, ax=ax)
        fig.tight_layout()
        for ext in ('png','pdf'):
            fig.savefig(f"{fname}.{ext}")
        if show_plot:
            plt.show()
        plt.close(fig)
        out_files.append(fname)
    return out_files


def control_density(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    show_plot: bool = False,
    sup_histo: bool = False
) -> str:
    """
    Plots density estimates of positive vs negative controls, optionally
    superimposing histograms, and saves to PDF/PNG.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for boxplot calculation.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.
        sup_histo: Whether to superimpose histograms.

    Returns:
        The base filename (without extension).
    """
    # subsets
    pos = dataset[dataset['SpotType'] == 1][channel].dropna()
    neg = dataset[dataset['SpotType'] == 0][channel].dropna()
    # density estimates
    from scipy.stats import gaussian_kde
    pos_dens = gaussian_kde(pos)
    neg_dens = gaussian_kde(neg)
    xs = np.linspace(min(pos.min(), neg.min()), max(pos.max(), neg.max()), 200)
    ys_pos = pos_dens(xs)
    ys_neg = neg_dens(xs)

    # histogram breaks if requested
    if sup_histo:
        rng = xs.max() - xs.min()
        step = max(rng/20, 1e-6)
        bins = np.arange(xs.min(), xs.max()+step, step)
        hist_pos = np.histogram(pos, bins=bins)
        hist_neg = np.histogram(neg, bins=bins)

    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    fname = f"{base}_{plot_title}"

    fig, ax = plt.subplots()
    ax.plot(xs, ys_pos, color='green', label='Positive Controls')
    ax.plot(xs, ys_neg, color='red', label='Negative Controls')
    if sup_histo:
        ax2 = ax.twinx()
        ax2.bar(hist_pos[1][:-1], hist_pos[0], width=step, alpha=0.3, color='green')
        ax2.bar(hist_neg[1][:-1], hist_neg[0], width=step, alpha=0.3, color='red')
        ax2.set_ylabel('Counts')
    ax.set_title(plot_title)
    ax.set_xlabel(channel)
    ax.legend(loc='upper left')
    fig.tight_layout()
    for ext in ('png','pdf'):
        fig.savefig(f"{fname}.{ext}")
    if show_plot:
        plt.show()
    plt.close(fig)
    return fname


def control_density_per_screen(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    show_plot: bool = False,
    sup_histo: bool = False
) -> List[str]:
    """
    Control density per experiment (screen).

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for boxplot calculation.
        plot_title: Title for the plot.
        show_plot: Whether to display the plot.
        sup_histo: Whether to superimpose histograms.

    Returns:
        List of base filenames.
    """
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    out = []
    for screen in sorted(dataset['ScreenNb'].unique()):
        sub = dataset[dataset['ScreenNb'] == screen]
        fname = f"{base}_{plot_title}_Exp{screen}"
        # reuse control_density logic on subset
        control_density(
            [header[0]], sub, channel, f"{plot_title}_Exp{screen}", show_plot, sup_histo
        )
        out.append(fname)
    return out


def control_density_per_plate(
    header: List[str],
    dataset: pd.DataFrame,
    channel: str,
    plot_title: str,
    plot_design: int = 1,
    show_plot: bool = False,
    sup_histo: bool = False
) -> List[str]:
    """
    Control density per plate within each experiment.

    Args:
        header: Header lines of the dataset.
        dataset: DataFrame containing at least columns ['SpotType', 'ScreenNb', 'LabtekNb', channel].
        channel: Channel to use for boxplot calculation.
        plot_title: Title for the plot.
        plot_design: Layout design for subplots.
        show_plot: Whether to display the plot.
        sup_histo: Whether to superimpose histograms.

    Returns:
        List of base filenames.
    """
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    files = []
    for screen in sorted(dataset['ScreenNb'].unique()):
        sub = dataset[dataset['ScreenNb'] == screen]
        for plate in sorted(sub['LabtekNb'].unique()):
            subp = sub[sub['LabtekNb'] == plate]
            fname = f"{base}_{plot_title}_Exp{screen}_Plate{plate}"
            # compute densities only if enough data
            if subp[subp['SpotType']==1][channel].dropna().size>1 and \
               subp[subp['SpotType']==0][channel].dropna().size>1:
                control_density(
                    [header[0]], subp, channel, f"{plot_title}_Exp{screen}_Plate{plate}", show_plot, sup_histo
                )
            else:
                # skip or create empty placeholder
                pass
            files.append(fname)
    return files



























