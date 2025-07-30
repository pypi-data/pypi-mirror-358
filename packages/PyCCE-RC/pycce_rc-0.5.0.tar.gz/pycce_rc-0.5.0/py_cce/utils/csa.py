import numpy as np

from py_cce.base.annotations import ArrayLikeType


def normalize_weights(weights: np.ndarray, n_ents: int) -> np.ndarray:
    """Normalizes weights to ensure they sum up to 1.

    Parameters
    ----------
    weights : np.ndarray
        Numpy array containing weights.

    Returns:
    -------
    np.ndarray
        Numpy array containing normalized weights.

    Raises:
    ------
    ValueError
        Raised when the number of dimensions is not 1 or lenght of weight array is not equal to number of entities.
    ValueError
        Raised when the condition provided in Pesaran (2006) may be violated.
    """
    if weights.ndim != 1 or weights.shape[0] != n_ents:
        raise ValueError(
            "Weights must be a 1-dimensional array with length equal to the number of entities"
        )

    weights_norm = (
        weights / weights.sum()
        if not np.isclose(weights.sum(), 1.0)
        else weights.copy()
    )

    if np.sum(np.abs(weights_norm)) > 10_000:
        raise ValueError(
            "Weights total variation is too large, may violate Pesaran (2006)"
        )

    return weights_norm


def compute_aug_csa(
    aug_regs: ArrayLikeType,
    weights: ArrayLikeType | None,
) -> np.ndarray:
    """Computes CSA for internal use only.

    Parameters
    ----------
    aug_regs : np.ndarray
        Additional exogenous regressors to add to the model, in the form (n_vars, n_obs, n_ents).
    weights : ArrayLikeType | None
        Weights to be used per unit when computing CSA, by default None.

    Returns:
    -------
    np.ndarray
        Numpy array with cross-sectional averages in shape (n_obs, n_vars).
    """
    aug_regs = aug_regs.transpose(1, 0, 2)

    weights = np.asarray(weights) if weights is not None else None

    return compute_csa(observables=aug_regs, weights=weights)


def compute_csa(
    observables: np.ndarray, weights: np.ndarray | None = None
) -> np.ndarray:
    """Computes CSA of the provided observables.

    Parameters
    ----------
    observables : np.ndarray
        Observables that CSA is computed for, has to be provided in form (n_obs, n_vars, n_ents).
    weights : np.ndarray | None
        Weights to be used per unit when computing CSA.

    Returns:
    -------
    np.ndarray
        Numpy array with cross-sectional averages in shape (n_obs, n_vars).
    """
    n_ents = observables.shape[2]

    if weights is None:
        weights = np.full(n_ents, 1 / n_ents)
    else:
        weights = normalize_weights(weights=weights, n_ents=n_ents)

    observables = np.nan_to_num(observables)

    return np.tensordot(observables, weights, axes=([2], [0]))
