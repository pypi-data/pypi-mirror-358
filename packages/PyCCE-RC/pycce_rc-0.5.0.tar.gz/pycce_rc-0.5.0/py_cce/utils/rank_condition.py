import warnings

import numpy as np

from py_cce.base.results import RankConditionTestResult


def _sort_eig(
    eig_vals: np.ndarray, eig_vecs: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Sorts eigenvalues in descending order, ensures that corresponding eigenvectors map to the same index of corresponding eigenvalue after sorting.

    Parameters
    ----------
    eig_vals : np.ndarray
        Eigen values
    eig_vecs : np.ndarray
        Eigen vectors

    Returns:
    -------
    tuple[np.ndarray, np.ndarray]
        Sorted eigenvalues and eigenvectors, still with the correct link of indices.
    """
    idx = np.argsort(eig_vals)[::-1]
    return eig_vals[idx], eig_vecs[:, idx]


def _compute_omega_hat(
    csa: np.ndarray, obs_mat: np.ndarray, psi: np.ndarray, n_ents: int
) -> np.ndarray:
    """Computes the asymptotic variance Omega hat.

    Parameters
    ----------
    csa : np.ndarray
        Numpy array containing cross-sectional averages (T x (k + 1)).
    obs_mat : np.ndarray
        Numpy array containig observables. (T x (k+1) x N)
    psi : np.ndarray
        Dimensionality reduction matrix ((k + 1) x T).
    n_ents : int
        Number of entities.

    Returns:
    -------
    np.ndarray
        Asymptotic variance Omega hat.
    """
    _, k = csa.shape
    omega_hat = np.zeros(shape=(k**2, k**2))

    for i in range(n_ents):
        z_i = obs_mat[:, :, i]

        valid_rows = ~np.isnan(z_i).any(axis=1)

        if valid_rows.sum() == 0:
            continue

        z_i_valid = z_i[valid_rows]
        csa_valid = csa[valid_rows]
        psi_valid = psi[:, valid_rows]

        psi_z_i = psi_valid @ z_i_valid
        psi_z_bar = psi_valid @ csa_valid

        diff = psi_z_i - psi_z_bar
        omega_hat += np.outer(diff.flatten("F"), diff.flatten("F"))

    return omega_hat


def _determine_crit_vals_weighted_chi_squared_distribution(
    weights: np.ndarray,
    n_ents: int,
    rng: np.random.Generator,
    n_sim: int = 10_000,
    c: int = 20,
    alpha: float = 0.05,
) -> float:
    """Determines the critical value to be used in factor loading rank test.

    Parameters
    ----------
    weights : np.ndarray
        Array containing weights for the distribution.
    n_ents : int, optional
        Number of entities.
    rng : np.random.Generator
        Random numpy generator.
    n_samples : int, optional
        Number of samples, by default 10_000.
    c : int, optional
        Multiplier of the significance level
    alpha : float, optional
        List of additional exogenous regressors to be considered for augmentation of the CSA, in the form (n_vars, n_obs, n_ents).


    Returns:
    -------
    float
        Critical value to be used for hypothesis test.
    """
    alpha = c * alpha / n_ents
    n_sample = len(weights)
    chi_samples = rng.chisquare(df=1, size=(n_sim, n_sample))
    weighted_sum = chi_samples @ weights
    return float(np.percentile(weighted_sum, 1 - alpha))


def is_symmetric(matrix: np.ndarray, tol: float = 1e-8) -> bool:
    """Determines if matrix is symmetric.

    Parameters
    ----------
    matrix : _type_
        Matrix to check
    tol : _type_, optional
        tolerance used, by default 1e-8

    Returns:
    -------
    _type_
        Boolean indicating whether matrix is symmetric.
    """
    return bool(np.allclose(matrix, matrix.T, atol=tol))


def estimate_rank_factor_loadings(
    csa: np.ndarray,
    obs_mat: np.ndarray,
    rand_state: int | None = None,
    c: int = 20,
    alpha: float = 0.05,
) -> tuple[int, list[float], list[float]]:
    """Estimate the rank of the factor loading matrix.

    Parameters
    ----------
    csa : np.ndarray
        Numpy array containing cross-sectional averages (T x (k + 1)).
    obs_mat : np.ndarray
        Numpy array containig observables. (T x (k+1) x N)
    c : int, optional
        Multiplier of the significance level
    alpha : float, optional
        List of additional exogenous regressors to be considered for augmentation of the CSA, in the form (n_vars, n_obs, n_ents).

    Returns:
    -------
    np.intp
        Estimated rank of factor loadings
    """
    rand_state = rand_state if rand_state is not None else 42
    rng = np.random.default_rng(seed=rand_state)
    n_periods, n_vars, n_ents = obs_mat.shape

    dim_red_mat = rng.standard_normal(size=(n_vars, n_periods))
    dim_red_mat = 1 / np.sqrt(n_periods) * dim_red_mat

    mat_a = dim_red_mat @ csa @ csa.T @ dim_red_mat.T
    mat_b = csa.T @ dim_red_mat.T @ dim_red_mat @ csa

    if is_symmetric(mat_a) and is_symmetric(mat_b):
        eig_mat_a = np.linalg.eigh(mat_a)
        eig_mat_b = np.linalg.eigh(mat_b)
    else:
        raise ValueError("Matrices not symmetric")

    eig_vals_a, eig_vecs_a = _sort_eig(
        eig_vals=eig_mat_a.eigenvalues, eig_vecs=eig_mat_a.eigenvectors
    )
    _, eig_vecs_b = _sort_eig(
        eig_vals=eig_mat_b.eigenvalues, eig_vecs=eig_mat_b.eigenvectors
    )

    omega_hat = _compute_omega_hat(
        csa=csa, obs_mat=obs_mat, psi=dim_red_mat, n_ents=n_ents
    )
    tau_list = []
    crit_val_list = []
    for i in range(n_vars):
        tau = n_ents * np.sum(eig_vals_a[i:])
        tau_list.append(tau)
        r = n_vars - i

        r_phi = eig_vecs_a[:, i:]
        d_phi = eig_vecs_b[:, i:]

        kron_prod = np.kron(d_phi, r_phi)
        kron_prod_trans = np.kron(d_phi.T, r_phi.T)
        kron_mat = kron_prod_trans @ omega_hat @ kron_prod

        if is_symmetric(kron_mat):
            weights = np.linalg.eigvalsh(kron_mat)
        else:
            raise ValueError("Matrix not symmetric")

        weights[::-1].sort()
        r_weights = weights[: r**2]
        crit_val = _determine_crit_vals_weighted_chi_squared_distribution(
            weights=r_weights,
            n_ents=n_ents,
            rng=rng,
            alpha=alpha,
            c=c,
        )
        crit_val_list.append(crit_val)

        if tau <= crit_val:
            return i, tau_list, crit_val_list

    return int(n_vars), tau_list, crit_val_list


def growth_ratio_factor_test(obs_mat: np.ndarray, m_max: int | None = None) -> int:
    """Estimate the number of common factors using the Growth Ratio (GR) criterion.

    Parameters:
    -----------
    obs_mat : np.ndarray
        Numpy array containig observables (T x (k + 1) x N).
    m_max : int, optional
        The maximum number of factors to consider. Defaults to min(T, N) // 2.

    Returns:
    --------
    m_hat : int
        The estimated number of factors.
    """
    t, _, n = obs_mat.shape
    m = min(t, n)
    m_max = m // 2 if m_max is None or m_max > t else m_max

    reshaped_obs = obs_mat.reshape(t, -1)

    obs_zero = np.nan_to_num(reshaped_obs, nan=0.0)

    valid_mask = ~np.isnan(reshaped_obs)
    eff_count = np.maximum(valid_mask.sum(axis=1, keepdims=True), 1)

    trans_mat = (obs_zero @ obs_zero.T) / eff_count.mean()

    eig_vals = np.linalg.eigvalsh(trans_mat)[::-1]

    v_k = np.array([np.sum(eig_vals[j : m + 1]) for j in range(m_max)])

    agg_gr = []
    for k in range(1, m_max - 1):
        num = np.log(v_k[k - 1] / v_k[k]) if v_k[k] > 0 and v_k[k - 1] > 0 else -np.inf
        den = np.log(v_k[k] / v_k[k + 1]) if v_k[k + 1] > 0 and v_k[k] > 0 else -np.inf
        gr_k = num / den if den != 0 else -np.inf
        agg_gr.append(gr_k)

    m_hat = np.argmax(agg_gr) + 1
    return int(m_hat)


def _evaluate_rank_condition(
    obs_mat: np.ndarray,
    csa: np.ndarray,
    m_max: int | None = None,
    aug_obs: np.ndarray | None = None,
    aug_csa: np.ndarray | None = None,
    c: int = 20,
    alpha: float = 0.05,
) -> RankConditionTestResult:
    """Evaluate the rank condition by comparing number of factors and rank of factor loadings.

    Parameters
    ----------
    obs_mat : np.ndarray
        Numpy array containig observables.
    csa : np.ndarray
        Numpy array containing cross-sectional averages.
    m_max : int
        The maximum number of factors to consider for the rank condition test.
    c : int, optional
        Multiplier of the significance level
    alpha : float, optional
        List of additional exogenous regressors to be considered for augmentation of the CSA, in the form (n_vars, n_obs, n_ents).


    Returns:
    -------
    tuple[bool, int, int]
        Boolean indicating whether the RC holds and the two estimated ranks.
    """
    warnings.warn(
        "There are still some instabilities in testing the RC, these will be fixed in future versions",
        stacklevel=2,
        category=UserWarning,
    )

    m_hat = growth_ratio_factor_test(obs_mat=obs_mat, m_max=m_max)
    num_vars = obs_mat.shape[1]

    if (
        aug_obs is None
        and aug_csa is not None
        or aug_obs is not None
        and aug_csa is None
    ):
        raise ValueError(
            "Both aug_obs and aug_csa must be provided together or not at all."
        )

    csa = aug_csa.copy() if aug_csa is not None else csa
    obs_mat = aug_obs.copy() if aug_obs is not None else obs_mat

    phi_hat, tau_list, crit_val_list = estimate_rank_factor_loadings(
        obs_mat=obs_mat, csa=csa, c=c, alpha=alpha
    )

    sufficient_loading_rank = not bool(phi_hat < m_hat)
    sufficient_num_vars = m_hat <= num_vars
    rc_holds = sufficient_loading_rank and sufficient_num_vars

    return RankConditionTestResult(
        rc_holds=rc_holds,
        phi_estim=phi_hat,
        m_estim=m_hat,
        tau_list=tau_list,
        crit_val_list=crit_val_list,
    )
