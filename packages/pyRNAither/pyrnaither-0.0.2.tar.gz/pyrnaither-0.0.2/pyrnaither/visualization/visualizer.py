import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import cm, patches
import colorsys
import numpy as np
import matplotlib as mpl
from typing import List, Tuple
import pandas as pd



# Function to get the complementary color
def get_complementary_color(color):
    """
    Returns the complementary color of the given color.

    Args:
        color: The color to get the complementary color of.

    Returns:
        The complementary color of the given color.
    """
    # Convert the color from RGB to HLS
    r, g, b = mcolors.to_rgb(color)  # Normalize the RGB values to [0, 1]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    
    # Shift the hue by 0.5 (equivalent to 180 degrees) to get the complementary color
    h_complementary = (h + 0.5) % 1.0
    
    # Convert it back to RGB
    r_complementary, g_complementary, b_complementary = colorsys.hls_to_rgb(h_complementary, l, s)
    
    # Return the complementary color in a format that matplotlib can use
    return (r_complementary, g_complementary, b_complementary)

# Function to plot 96-well plate with color-coded intensity
def plot_96_well_plate_with_intensity(data, meta=None, title="", scale=1.5, cbar_label=None, ):
    """
    Plots a 96-well plate with color-coded intensity.

    Args:
        data: The data to plot.
        meta: The metadata to use for annotation.
        title: The title of the plot.
        scale: The scale of the plot.
        cbar_label: The label for the colorbar.

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(12.5/scale, 8/scale))

    # 96 well plate dimensions: 8 rows (A-H) and 12 columns (1-12)
    rowsn = list("ABCDEFGH")[::-1]
    cols = list(range(1, 13))  # Corrected to have 12 columns (1 to 12)

    # Normalize the intensity data for color mapping
    intensities = np.array(list([i for i in data.values() if not isinstance(i, str)]))
    norm = mpl.colors.Normalize(vmin=np.min(intensities), vmax=np.max(intensities))
    cmap = cm.get_cmap('YlOrBr')  # You can use other colormaps like 'plasma', 'coolwarm', etc.

    # Create grid
    for i, row in enumerate(rowsn):
        for j, col in enumerate(cols):
            well_key = f"{row}{col}"
            intensity = data.get(well_key, np.nan)  # Get intensity or NaN if well is empty

            if not np.isnan(intensity):
                color = cmap(norm(intensity))  # Get color based on intensity
                # Plot a circle for each well
                circle = patches.Circle((j+1, i+1), 0.4, color=color, ec='black', lw=1)
                ax.add_patch(circle)
            else:
                color = 'white'  # No data wells will be white
                circle = patches.Circle((j+1, i+1), 0.4, color=color, ec='gray', lw=0.5, alpha=0.5)
                ax.add_patch(circle)
                ax.scatter(j+1, i+1, s=400, c='gray', marker='x', clip_on=False, alpha=0.5) # type: ignore
            

            # Add intensity value to the well
            if not np.isnan(intensity):
                if (1-intensity) > 0.33 and (1-intensity) < 0.66:
                    color = cmap(1)
                else:
                    color = cmap(1-intensity)
                    
                alt = meta.get(well_key, None) if meta is not None else None
                if alt:
                    circle = patches.Circle((j+1, i+1), 0.4, color=cmap(intensity), ec=cmap(0.5), lw=2)
                    ax.add_patch(circle)
                    ax.text(j+1, i+1.12, f"{alt}",
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=10,
                        color=color)
                    ax.text(j+1, i+0.85, f"{intensity:.2f}",
                            horizontalalignment='center',
                            verticalalignment='center',
                            fontsize=8,
                            color=color)

                else:
                    ax.text(j+1, i+1, f"{intensity:.2f}",
                            horizontalalignment='center',
                            verticalalignment='center',
                            fontsize=8,
                            color=color)

    # Set axis limits to ensure all 12 columns are visible
    ax.set_xlim(0.5, 12.5)  # Adjusted to show all 12 columns
    ax.set_ylim(0.5, 8.5)

    # Set labels and ticks
    ax.set_xticks(range(1, 13))  # Ensuring 12 ticks
    ax.set_xticklabels(list(range(1, 13)) )
    ax.set_yticks(range(8, 0, -1))
    ax.set_yticklabels(rowsn[::-1])

    # Set title and hide axis lines
    ax.set_title(title)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Turn off the ticks (both major and minor ticks)
    ax.tick_params(left=False, bottom=False)

    # Optionally, you can remove the grid if you don't want it
    ax.grid(False)

    # Add colorbar
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5, fraction=0.01)
    cbar.set_label(cbar_label)

    # Show the plot
    plt.show()

def spatial_distrib(
    header: List[str],
    dataset: pd.DataFrame,
    plot_title: str,
    col4plot: str,
    col4anno: str,
    show_plot: bool
) -> Tuple[str, Tuple[int,int], Tuple[int,int]]:
    """
    Plot spatial distribution of values per plate and experiment.

     Args:
        header: The header of the dataset.
        dataset: The dataset to plot.
        plot_title: The title of the plot.
        col4plot: The column to plot.
        col4anno: The column to group replicates by.
        show_plot: Whether to show the plot.

    Returns:
        (basic_plot_name, (min_screen, max_screen), (min_plate, max_plate)).
    """
    df = dataset.copy()
    # mask controls
    df.loc[df['SpotType'] == -1, col4plot] = np.nan

    screens = sorted(df['ScreenNb'].dropna().unique().astype(int))
    # derive base plot name
    base = header[0].split(',')[1] if ',' in header[0] else header[0]
    basic_plot_name = f"{base}_{plot_title}"

    all_plates = []
    for screen in screens:
        subset = df[df['ScreenNb'] == screen]
        plates = sorted(subset['LabtekNb'].dropna().unique().astype(int))
        all_plates.extend(plates)
        for plate in plates:
            sub = subset[subset['LabtekNb'] == plate]
            # check data
            if sub[col4plot].notna().any():
                # build matrix
                nrows = int(sub['RowNb'].max())
                ncols = int(sub['ColNb'].max())
                mat = np.full((nrows, ncols), np.nan)
                for _, row in sub.iterrows():
                    r = int(row['RowNb']) - 1
                    c = int(row['ColNb']) - 1
                    mat[r, c] = row[col4plot]
                # plot
                fig, ax = plt.subplots()
                cax = ax.imshow(mat, origin='upper', aspect='auto')
                title = f"{plot_title} plate {plate} Exp. {screen}"
                ax.set_title(title)
                # annotate N/P
                for _, row in sub.iterrows():
                    if row['SpotType'] in (0, 1):
                        r = int(row['RowNb']) - 1
                        c = int(row['ColNb']) - 1
                        label = 'P' if row['SpotType'] == 1 else 'N'
                        ax.text(c, r, label, ha='center', va='center', fontsize=8)
                fig.colorbar(cax)
                if show_plot:
                    plt.show()
                # save PNG
                fname_png = f"{basic_plot_name}_Exp{screen}_Plate{plate}.png"
                fig.savefig(fname_png)
                plt.close(fig)
                # write simple HTML
                html_file = f"{basic_plot_name}_Exp{screen}_Plate{plate}.html"
                with open(html_file, 'w') as f:
                    f.write(f"<html><body><h1>{title}</h1><img src='{fname_png}'/></body></html>")
            else:
                # blank plot for no data
                fig, ax = plt.subplots()
                ax.text(0.5, 0.75, f"Cannot plot plate {plate} Exp {screen}", ha='center')
                ax.text(0.5, 0.25, "Only NAs available", ha='center')
                ax.axis('off')
                fname_png = f"{basic_plot_name}_Exp{screen}_Plate{plate}.png"
                fig.savefig(fname_png)
                plt.close(fig)
    # determine ranges
    min_screen, max_screen = (min(screens), max(screens)) if screens else (0, 0)
    min_plate, max_plate = (min(all_plates), max(all_plates)) if all_plates else (0, 0)
    return basic_plot_name, (min_screen, max_screen), (min_plate, max_plate)