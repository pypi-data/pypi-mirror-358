import numpy as np

from py_cce.base.annotations import PanelDataLikeType
from py_cce.base.data import PanelData
from py_cce.base.results import AugmentationResult
from py_cce.utils.csa import compute_aug_csa
from py_cce.utils.data import (
    compute_annihilator_matrix,
    include_observed_common_factors,
)


def _construct_augmented_set(
    panel: PanelData,
    aug_weights: list[np.ndarray] | None,
    aug_regs: list[np.ndarray] | None,
) -> list[np.ndarray]:
    """Constructs set of candidate CSA based on provided augmentations.

    Parameters
    ----------
    panel : PanelData
        Original panel to be augmented.
    aug_weights : np.ndarray | None
        List of different weight vectors to be considered for augmenting CSAs.
    aug_regs : PanelDataLikeType | None
        List of additional exogenous regressors to be considered for augmentation of the CSA.

    Returns:
    -------
    list[np.ndarray]
        List containing all provided augmentations.
    """
    aug_set = []

    if aug_weights is not None:
        contains_obs_facs = panel._obs_facs is not None
        for w in aug_weights:
            aug_set.append(panel.compute_csa(weights=w, include_proj=contains_obs_facs))

    if aug_regs is not None:
        # For now it is assumed that the additional regressors do not load on the observed factors.
        for reg in aug_regs:
            aug_set.append(compute_aug_csa(aug_regs=reg, weights=panel._weights))

    return aug_set


def _information_criterion(
    obs_facs: PanelDataLikeType,
    obs_mat: np.ndarray,
    aug_csa: np.ndarray,
    panel_shape: tuple[int, int, int],
) -> float:
    """Computes the information criterion value.

    Parameters
    ----------
    obs_facs : PanelDataLikeType
        Observed factors to be projected out of the observables.
    obs_mat : np.ndarray
        Matrix containing all observations in form (n_obs, n_vars, n_ents)
    aug_csa : np.ndarray
        Proposed augmentation for which the IC is computed.
    panel_shape : int
        Shape of panel in format (n_vars, n_obs, n_ents).

    Returns:
    -------
    float
        Value of the information criterion.
    """
    k, t, n = panel_shape
    s = aug_csa.shape[1]

    n_t_min = np.min([t, n])
    g = k * np.log(n_t_min) / n_t_min

    csa_mat = include_observed_common_factors(observables=aug_csa, obs_fac=obs_facs)
    anni_mat = compute_annihilator_matrix(observables=csa_mat, n_obs=t)

    v_j = np.zeros((k, k))
    n_effective = 0

    for i in range(n):
        z_i = obs_mat[:, :, i]

        valid_rows = ~np.isnan(z_i).any(axis=1)

        if valid_rows.sum() < k:
            continue

        z_i_valid = z_i[valid_rows, :]
        anni_valid = anni_mat[np.ix_(valid_rows, valid_rows)]

        contrib = z_i_valid.T @ anni_valid @ z_i_valid
        v_j += contrib
        n_effective += valid_rows.sum()

    if n_effective == 0:
        raise ValueError("No valid data found across entities for IC computation.")

    v_j /= n * t

    sign, logdet = np.linalg.slogdet(v_j)
    if sign <= 0 or not np.isfinite(logdet):
        raise ValueError("Covariance matrix not positive definite or ill-conditioned.")

    return float(logdet + s * g)


def _eval_csa_aug(
    panel: PanelData,
    aug_weights: np.ndarray | None = None,
    aug_regs: np.ndarray | None = None,
) -> AugmentationResult:
    """Evaluate a set of potential augmentation weights and/or additional regressors.

    Parameters
    ----------
    panel : PanelData
        Panel that was used in the estimation of the model.
    aug_weights : np.ndarray | None
        Set of different weight combinations to be considered in augmenting the CSA.
    aug_regs : np.ndarray | None
        List of additional exogenous regressors to add to the model, in the form (n_vars, n_obs, n_ents).
    obs_Facs : PanelDataLikeType
        Observed factors that were used in the original model.


    Returns:
    -------
    AugmentationResult
        Dataclass containing information of the augmentation.

    Raises:
    ------
    ValueError
        Raises value error if no augmentations provided.
    """
    if aug_weights is None and aug_regs is None:
        raise ValueError(
            "Both augmentation options are None, can't augment CSA without augmentation information."
        )
    panel_shape = panel.panel_shape
    init_csa = panel._csa
    obs_mat = (
        panel._panel_tensor_orth_obs
        if panel._obs_facs is not None
        else panel._panel_tensor
    )

    ic_zero = _information_criterion(
        obs_facs=panel._obs_facs,
        obs_mat=obs_mat,
        aug_csa=init_csa,
        panel_shape=panel_shape,
    )
    augmented_set = _construct_augmented_set(
        panel=panel,
        aug_weights=aug_weights,
        aug_regs=aug_regs,
    )
    aug_ic = []
    for aug_csa in augmented_set:
        aug_ic.append(
            _information_criterion(
                obs_facs=panel._obs_facs,
                obs_mat=obs_mat,
                aug_csa=aug_csa,
                panel_shape=panel_shape,
            )
        )

    j_hat = list(np.where(aug_ic == np.min(aug_ic))[0])
    augs = []

    for j in j_hat:
        if aug_ic[j] <= ic_zero:
            augs.append(augmented_set[j])

    found_lower_ic = len(augs) > 0
    j_hat = j_hat if found_lower_ic else []
    aug_csa = np.hstack(augs) if found_lower_ic else None

    return AugmentationResult(
        found_lower_ic=found_lower_ic,
        selected_indices=j_hat,
        aug_csa=aug_csa,
        orig_csa=init_csa,
    )
