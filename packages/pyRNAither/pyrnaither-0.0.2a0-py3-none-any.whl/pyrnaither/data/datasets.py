import pandas as pd
import numpy as np
from typing import List, Union

def generate_dataset_file(
    external_experiment_name: str,
    type_of_data: str,
    comments: str,
    output_file: str,
    plate_layout_internal: pd.DataFrame,
    plate_layout_ncbi: pd.DataFrame,
    nb_rows_per_plate: int,
    nb_cols_per_plate: int,
    screen_nb_pre: int,
    empty_wells: List[List[int]],
    poor_wells: List[List[int]],
    control_coords_output: List[List[List[int]]],
    background_val_output: List[np.ndarray],
    mean_signal_output: List[np.ndarray],
    sd_mean_signal: List[np.ndarray],
    obj_num_output: List[np.ndarray],
    cell_num_output: List[np.ndarray]
) -> None:

    """
    Generate a dataset file from the given data.

    Args:
        external_experiment_name: Name of the external experiment.
        type_of_data: Type of data.
        comments: Comments.
        output_file: Output file.
        plate_layout_internal: Plate layout internal.
        plate_layout_ncbi: Plate layout NCBI.
        nb_rows_per_plate: Number of rows per plate.
        nb_cols_per_plate: Number of columns per plate.
        screen_nb_pre: Screen number pre.
        empty_wells: Empty wells.
        poor_wells: Poor wells.
        control_coords_output: Control coordinates output.
        background_val_output: Background value output.
        mean_signal_output: Mean signal output.
        sd_mean_signal: SD mean signal.
        obj_num_output: Object number output.
        cell_num_output: Cell number output.

    Returns:
        None
    """


    nb_spots_per_plate = nb_rows_per_plate * nb_cols_per_plate
    total_number_of_spots = nb_spots_per_plate * len(control_coords_output)

    Spotnumber = np.zeros(total_number_of_spots, dtype=int)
    SpotType = np.zeros(total_number_of_spots, dtype=int)
    Internal_GeneID = np.full(total_number_of_spots, 'NA', dtype=object)
    GeneName = np.full(total_number_of_spots, 'NA', dtype=object)
    SigIntensity = np.zeros(total_number_of_spots)
    SDSIntensity = np.zeros(total_number_of_spots)
    Background = np.zeros(total_number_of_spots)
    LabtekNb = np.zeros(total_number_of_spots, dtype=int)
    RowNb = np.zeros(total_number_of_spots, dtype=int)
    ColNb = np.zeros(total_number_of_spots, dtype=int)
    ScreenNb = np.zeros(total_number_of_spots, dtype=int)
    NbCells = np.zeros(total_number_of_spots)
    PercCells = np.zeros(total_number_of_spots)

    for i, coords in enumerate(control_coords_output):
        pos_coords, neg_coords = coords
        num_obj = obj_num_output[i] if len(obj_num_output) > 1 else (
            obj_num_output[0] if any(pd.notna(obj_num_output)) else np.full(nb_spots_per_plate, np.nan))
        num_cells = cell_num_output[i] if len(cell_num_output) > 1 else (
            cell_num_output[0] if any(pd.notna(cell_num_output)) else np.full(nb_spots_per_plate, np.nan))

        mean_cyto_signal = mean_signal_output[i]
        spot_type_pre = np.full(nb_spots_per_plate, 2)

        if pd.notna(pos_coords[0]):
            spot_type_pre[pos_coords] = 1
        if pd.notna(neg_coords[0]):
            spot_type_pre[neg_coords] = 0
        if pd.notna(empty_wells[i]):
            spot_type_pre[empty_wells[i]] = -1
        if pd.notna(poor_wells[i]):
            spot_type_pre[poor_wells[i]] = -1

        row_nb_pre = np.repeat(np.arange(1, nb_rows_per_plate + 1), nb_cols_per_plate)
        col_nb_pre = np.tile(np.arange(1, nb_cols_per_plate + 1), nb_rows_per_plate)

        perc_cells_pre = np.divide(num_cells, num_obj, out=np.full_like(num_cells, np.nan), where=num_obj!=0)

        start = i * nb_spots_per_plate
        end = (i + 1) * nb_spots_per_plate
        Spotnumber[start:end] = np.arange(1, nb_spots_per_plate + 1)
        Internal_GeneID[start:end] = plate_layout_internal.iloc[:, i].values
        GeneName[start:end] = plate_layout_ncbi.iloc[:, i].values
        SpotType[start:end] = spot_type_pre
        SigIntensity[start:end] = mean_cyto_signal

        if i < len(sd_mean_signal) and len(sd_mean_signal[i]) == nb_spots_per_plate:
            SDSIntensity[start:end] = sd_mean_signal[i]
        else:
            SDSIntensity[start:end] = np.nan

        if i < len(background_val_output) and len(background_val_output[i]) == nb_spots_per_plate:
            Background[start:end] = background_val_output[i]
        else:
            Background[start:end] = np.nan

        LabtekNb[start:end] = i + 1
        RowNb[start:end] = row_nb_pre
        ColNb[start:end] = col_nb_pre
        ScreenNb[start:end] = screen_nb_pre
        NbCells[start:end] = num_cells
        PercCells[start:end] = perc_cells_pre

    df = pd.DataFrame({
        "Spotnumber": Spotnumber,
        "Internal_GeneID": Internal_GeneID,
        "GeneName": GeneName,
        "SpotType": pd.Categorical(SpotType, categories=[-1, 0, 1, 2]),
        "SigIntensity": SigIntensity,
        "SDSIntensity": SDSIntensity,
        "Background": Background,
        "LabtekNb": LabtekNb,
        "RowNb": RowNb,
        "ColNb": ColNb,
        "ScreenNb": ScreenNb,
        "NbCells": NbCells,
        "PercCells": PercCells
    })

    with open(output_file, 'w') as f:
        f.write(f"external_experiment_name,{external_experiment_name}\n")
        f.write(f"type_of_data,{type_of_data}\n")
        f.write(f"comments,{comments}\n")
        df.to_csv(f, sep='\t', index=False)
