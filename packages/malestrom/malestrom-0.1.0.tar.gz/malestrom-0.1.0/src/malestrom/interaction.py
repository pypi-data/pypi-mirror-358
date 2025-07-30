import numpy as np
import pandas as pd
from scipy.spatial import KDTree
import astropy.units as u
from typing import Literal
from annotated_types import Annotated, Ge


def close_distance(
    iso_positions: np.ndarray,
    gmc_positions: np.ndarray,
    timesteps: Annotated[int, Ge(1)],
    include_gmcs: bool = False,
    num_distances: Annotated[int, Ge(1)] = 1,
    upper_bound: Annotated[float, Ge(1)] = 1,
    multiprocessing: bool = True,
):
    """
    :param iso_positions:
    :param gmc_positions:
    """
    if iso_positions.shape[1] != 3:
        raise Exception("Did not provide iso position list with shape (,3)")
    if gmc_positions.shape[1] != 3:
        raise Exception("Did not provide gmc position list with shape (,3)")
    n = int(gmc_positions.shape[0] / timesteps)
    dds = list()
    iis = list()
    for i in range(timesteps):
        tree = KDTree(gmc_positions[i * n : (i + 1) * n])
        dd, ii = tree.query(
            iso_positions[i * n : (i + 1) * n],
            num_distances,
            distance_upper_bound=upper_bound,
            workers=-1 if multiprocessing else 1,
        )
        dds.append(dd)
        iis.append(ii)
    if include_gmcs:
        return np.array(dds).flat(), np.array(iis).flat()
    else:
        return np.array(dds)


def close_passage(
    distances: np.ndarray,
    cutoff: float,
    output: Literal["percentage", "counts"] = "percentage",
):
    """
    :param distances:
    :param cutoff:
    :param output:
    """
    res = distances[distances < cutoff]
    match output:
        case "percentage":
            len(res) / len(distances)
        case "counts":
            len(res)
