import numpy as np

from py_cce.base.annotations import PanelDataLikeType
from py_cce.base.exceptions import PanelDataError


def compute_annihilator_matrix(
    observables: np.ndarray, n_obs: int, method: str = "SVD"
) -> np.ndarray:
    """Computes annihilator matrix.

    Parameters
    ----------
    observables : np.ndarray
        Numpy array containing cross-sectional averages.

    Returns:
    -------
    np.ndarray
        Numpy array containing annihilator matrix.
    """
    if method == "qr":
        q, _ = np.linalg.qr(observables)
        p_obs = q @ q.T
    else:
        p_obs = observables @ np.linalg.pinv(observables)

    return np.eye(n_obs) - p_obs


def include_observed_common_factors(
    observables: np.ndarray, obs_fac: PanelDataLikeType
) -> np.ndarray:
    """Include observed common factors in the observables matrix.

    Parameters
    ----------
    observables : np.ndarray
        Numpy array containing depedent variables and regressors (observables).
    obs_fac : PanelDataLikeType
        Observed common factors to be included in the observables matrix.

    Returns:
    -------
    np.ndarray
        Numpy array containing observables matrix including the common observed factors

    Raises:
    ------
    PanelDataError
        When the time dimension of the common observed factors does not match the time dimension of the observables.
    """
    if obs_fac is None or obs_fac.size == 0:
        return observables

    dt = np.asarray(obs_fac)
    if dt.shape[0] != observables.shape[0]:
        raise PanelDataError(
            f"Mismatch in time dimension: CSA has {observables.shape[0]} time periods, "
            f"but observed_common_factors has {dt.shape[0]}."
        )

    if dt.ndim != 2:
        raise PanelDataError(
            f"Observed common factors must be of shape (n_obs, n), but got {dt.shape}."
        )

    observables = np.hstack([dt, observables])
    return observables
