import numpy as np


def generate_common_factors(
    rng: np.random.Generator, T: int, rho: float, m: int, n: int
) -> tuple[np.ndarray, np.ndarray]:
    sigma_fac = np.sqrt(1 - rho**2)
    error_f = rng.normal(loc=0.0, scale=sigma_fac, size=(T, m))
    error_d = rng.normal(loc=0.0, scale=sigma_fac, size=(T, n))

    unobs_facs = np.zeros((T, m))
    obs_facs = np.zeros((T, n))

    for t in range(1, T):
        if t == 0:
            unobs_facs[t] = error_f[t]
            obs_facs[t] = error_d[t]
        else:
            unobs_facs[t] = rho * unobs_facs[t - 1] + error_f[t]
            obs_facs[t] = rho * obs_facs[t - 1] + error_d[t]

    return obs_facs, unobs_facs


def generate_loadings(
    rng: np.random.Generator,
    N: int,
    m: int,
    k: int,
    experiment: int,
) -> tuple[np.ndarray, np.ndarray]:
    # Goed checken, volgens mij zijn resultaten verkeerd gedraaid aangezien ik zelfde loadings gebruik voor observed als unobserved
    # Kan even checken of de factors alsnog uniquely identifiable zijn

    # loadings_no_zero = np.concatenate([np.arange(-5, 0), np.arange(1, 6)])
    # big_gamma_avg = rng.choice(loadings_no_zero, size=(m, k))
    # small_gamma_avg = rng.choice(loadings_no_zero, size=(m, 1))

    small_gamma_avg = np.array([[3], [2]])

    shift_1 = np.array([[-2], [0]])
    shift_2 = np.array([[0], [-1]])

    if experiment == 2:
        small_gamma_avg[0, :] = 0

    big_gamma = np.zeros((N, m, k))
    small_gamma = np.zeros((N, m, 1))
    for i in range(N):
        small_gamma[i] = small_gamma_avg + rng.normal(size=(m, 1))

        if experiment == 2:
            for j in range(k):
                big_gamma[i] = np.repeat(small_gamma[i], k, axis=1)
        elif experiment == 3:
            if i >= N / 10:
                small_gamma[i] = np.zeros((m, 1)) + rng.normal(size=(m, 1))
                big_gamma[i] = np.zeros((m, k)) + rng.normal(size=(m, k))
            else:
                small_gamma[i] = small_gamma_avg + rng.normal(size=(m, 1))
                big_gamma[i, :, 0] = (small_gamma[i] + shift_1).flatten()
                big_gamma[i, :, 1] = (small_gamma[i] + shift_2).flatten()
        else:
            big_gamma[i, :, 0] = (small_gamma[i] + shift_1).flatten()
            big_gamma[i, :, 1] = (small_gamma[i] + shift_2).flatten()

    return big_gamma, small_gamma


def generate_errors(
    rng: np.random.Generator, N: int, T: int, k: int, rho: float
) -> tuple[np.ndarray, np.ndarray]:
    sigma_eps = np.sqrt((1 - rho**2) / 2)
    epsilon = np.zeros((N, T, 1))
    v = np.zeros((N, T, k))

    eps_err = rng.normal(loc=0.0, scale=sigma_eps, size=(N, T))
    v_err = rng.normal(loc=0.0, scale=sigma_eps, size=(N, T, k))

    for i in range(N):
        for t in range(T):
            if t == 0:
                epsilon[i, t] = eps_err[i, t]
                v[i, t] = v_err[i, t]
            else:
                epsilon[i, t] = rho * epsilon[i, t - 1] + eps_err[i, t]
                v[i, t] = rho * v[i, t - 1] + v_err[i, t]

    return epsilon, v


def generate_candidate_observations(
    N: int, unobs_facs: np.ndarray, rho: float, rng: np.random.Generator
) -> np.ndarray:
    # Only to be used for m = 2 and k = 2
    z_2_mat = []
    base_c = np.array([[2.5, 1.0], [1.0, 2.5]])
    _, epsilon = generate_errors(rng, N, unobs_facs.shape[0], 2, rho)

    for i in range(N):
        c_2 = base_c + rng.normal(size=(2, 2))
        z_2_mat.append(unobs_facs @ c_2 + epsilon[i])

    return np.transpose(z_2_mat, (2, 1, 0))


def generate_panel(
    T: int,
    N: int,
    k: int,
    rho: float,
    include_d: bool,
    homogeneous: bool,
    rng: np.random.Generator,
    beta: np.ndarray,
    perc_missing: float | None = None,
    experiment: int = 1,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray, np.ndarray]:
    m = 2
    n = 2

    obs_facs, unobs_facs = generate_common_factors(rng, T, rho, m, n)
    big_gamma, small_gamma = generate_loadings(rng, N, m, k, experiment=experiment)
    # big_a, alpha = generate_loadings(rng, N, n, k, experiment=1)
    epsilon, v = generate_errors(rng, N, T, k, rho)
    z_list = []

    for i in range(N):
        if not homogeneous:
            beta_i = beta + rng.normal(size=(k, 1))
        else:
            beta_i = beta

        C_i = np.hstack([small_gamma[i] + big_gamma[i] @ beta_i, big_gamma[i]])

        U_i = np.hstack([epsilon[i] + v[i] @ beta_i, v[i]])

        if include_d:
            # obs_facsit is traag, nog verbeteren
            alpha_i = np.array([[1], [3]]) + rng.normal(size=(2, 1))
            big_a_i = np.array([[1, 2], [2, 1]]) + rng.normal(size=(2, 2))
            B_i = np.hstack([alpha_i + big_a_i @ beta_i, big_a_i])

        if include_d:
            obs_i = obs_facs @ B_i + unobs_facs @ C_i + U_i
        else:
            obs_i = unobs_facs @ C_i + U_i

        z_list.append(obs_i)

    data_reordered = np.transpose(z_list, (2, 1, 0))

    if perc_missing is not None:
        n_total_positions = T * N
        n_missing = int(perc_missing * n_total_positions)

        all_tn_indices = [(t, n) for t in range(T) for n in range(N)]
        selected_tn = rng.choice(len(all_tn_indices), size=n_missing, replace=False)

        for idx in selected_tn:
            t, n = all_tn_indices[idx]
            var_idx = rng.integers(0, k + 1)
            data_reordered[var_idx, t, n] = np.nan

    regs = data_reordered[1:, :, :]
    dep_var = data_reordered[0, :, :]

    aug_data = generate_candidate_observations(N, unobs_facs, rho, rng)
    _, unobs_facs_2 = generate_common_factors(rng, T, rho, m, n)
    aug_data_2 = generate_candidate_observations(N, unobs_facs_2, rho, rng)

    if not include_d:
        obs_facs = None

    return dep_var, regs, obs_facs, aug_data, aug_data_2
