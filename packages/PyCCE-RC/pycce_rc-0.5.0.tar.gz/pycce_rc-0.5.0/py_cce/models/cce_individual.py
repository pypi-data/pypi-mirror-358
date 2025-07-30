from typing import Any

import numpy as np

from py_cce.base.annotations import ArrayLikeType, PanelDataLikeType
from py_cce.base.model import CCEBaseModel
from py_cce.base.results import AugmentationResult, CCEIndividualResult
from py_cce.utils.data import (
    compute_annihilator_matrix,
    include_observed_common_factors,
)


class CCEIndividualSpecificModel(CCEBaseModel):
    """Class for the individual-specific CCE estimator."""

    def __init__(
        self,
        dep_var: PanelDataLikeType,
        regs: PanelDataLikeType | None = None,
        *,
        obs_facs: PanelDataLikeType | None = None,
        weights: ArrayLikeType | None = None,
        csa: np.ndarray | None = None,
        csa_indices: list[int] | None = None,
        internal_use: bool = False,
        **kwargs: Any,
    ):
        """Initialise the individual-specific CCE estimator.

        Parameters
        ----------
        dep_var : ArrayLikeType
            Data containing the dependent variable.
        regs : ArrayLikeType
            Data containing the regressors.
        weights : ArrayLikeType or None, optional
            Weights to be used in computing cross-sectional averages (CSA). Defaults to None.
        csa: np.ndarray or None, optional
            Pre-computed CSA to be used in the estimation process.
        csa_indices: np.ndarray or None, optional
            Indices of variables used in pre-computed CSA.
        internal_use : bool
            Boolean indicating whether instance is for internal use.
        **kwargs: Any
            Additional variables used to initialise the PanelData object.
        """
        super().__init__(
            dep_var=dep_var,
            regs=regs,
            obs_facs=obs_facs,
            weights=weights,
            csa=csa,
            csa_indices=csa_indices,
            **kwargs,
        )
        self._internal_use = internal_use

    def _compute_cov_mat(
        self, x_tilde: np.ndarray, y_tilde: np.ndarray, beta_i: np.ndarray
    ) -> np.ndarray:
        """Compute the Newey-West HAC-robust variance estimator for individual-specific CCE estimator.

        Parameters
        ----------
        x_tilde : np.ndarray
            Regressors transformed by the annihilator matrix in fitting model.
        y_tilde : np.ndarray
            Dependent variable transformed by the annihilator matrix in fitting model.
        beta_i : np.ndarray
            Estimated beta vector of entity i.

        Returns:
        -------
        np.ndarray
            Newey-West HAC-robust (k+1) x (k+1) matrix.
        """
        n_obs = x_tilde.shape[0]
        k = x_tilde.shape[1]
        lags = int(np.floor(n_obs ** (1 / 4)))

        e_hat = y_tilde - x_tilde @ beta_i

        s_hat = np.zeros((k, k))
        for lag in range(lags + 1):
            weight = 1.0 if lag == 0 else 1 - lag / (lags + 1)
            for t in range(lag, n_obs):
                x_t = x_tilde[t].reshape(-1, 1)
                x_lag = x_tilde[t - lag].reshape(-1, 1)
                contrib = e_hat[t] * e_hat[t - lag] * (x_t @ x_lag.T)
                if lag == 0:
                    s_hat += contrib
                else:
                    s_hat += weight * (contrib + contrib.T)
        s_hat /= n_obs

        x_t_x_inv = np.linalg.pinv((x_tilde.T @ x_tilde) / n_obs)
        return x_t_x_inv @ s_hat @ x_t_x_inv

    def fit(self, method: str = "SVD") -> CCEIndividualResult:
        """Fits individual-specific CCE estimator using OLS.

        Parameters
        ----------
        method : str, optional
            String determining which method to use in computing annihilator matrix, by default "SVD"

        Returns:
        -------
        CCEIndividualResult
            Object with the fitted model stored.
        """
        return self._fit(method=method)

    def _fit(
        self,
        method: str = "SVD",
        aug_res: AugmentationResult | None = None,
    ) -> CCEIndividualResult | np.ndarray:
        """Fits individual-specific CCE estimator using OLS.

        Parameters
        ----------
        method : str
            String determining which method to use in computing annihilator matrix, by default "SVD"

        Returns:
        -------
        _type_
            _description_.
        """
        k = self._panel._n_vars - 1
        t = self._panel._n_obs
        n = self._panel._n_ents

        unit_betas = np.empty((n, k))
        unit_vars = np.empty((n, k, k))

        z_bar = self._panel._csa

        observables = include_observed_common_factors(
            observables=z_bar, obs_fac=self._obs_facs
        )
        anni_mat = compute_annihilator_matrix(
            observables=observables, n_obs=t, method=method
        )

        x = self._panel._regressor_data
        y = self._panel._dependent_variable_data

        entities = self._panel.entities

        for j, entity in enumerate(entities):
            x_i = x.loc[entity].to_numpy()
            y_i = y.loc[entity].to_numpy().reshape(t, 1)

            data_i = np.hstack([x_i, y_i])
            valid_rows = ~np.isnan(data_i).any(axis=1)

            if valid_rows.sum() < x_i.shape[1]:
                unit_betas[j] = np.full((k,), np.nan)
                unit_vars[j] = np.full((k, k), np.nan)
                continue

            anni_valid = anni_mat[np.ix_(valid_rows, valid_rows)]

            x_i_valid = x_i[valid_rows]
            y_i_valid = y_i[valid_rows]

            x_aug = anni_valid @ x_i_valid
            y_aug = anni_valid @ y_i_valid

            beta_i, *_ = np.linalg.lstsq(x_aug, y_aug, rcond=None)
            unit_betas[j] = beta_i.flatten()

            if not self._internal_use:
                var_i = self._compute_cov_mat(
                    x_tilde=x_aug, y_tilde=y_aug, beta_i=beta_i
                )
                unit_vars[j] = var_i / t

        self._beta_i = unit_betas
        if self._internal_use:
            return unit_betas

        rc_res = self._eval_rc() if aug_res is None else aug_res.aug_rc_res

        if rc_res is None:
            raise ValueError(
                "rc_res must not be None when constructing CCEIndividualResult"
            )

        return CCEIndividualResult(
            beta_i=unit_betas,
            var_beta_i=unit_vars,
            rc_res=rc_res,
            panel=self._panel,
        )

    def predict(self, regs: np.ndarray) -> np.ndarray:
        """Predicts values based on the fitted model.

        Parameters
        ----------
        regs : np.ndarray
            The regressors for which predictions are to be made, in shape (T, K, N).

        Returns:
        -------
        np.ndarray
            The predicted values based on the fitted model.
        """
        if regs.ndim != 3:
            raise ValueError("regs must be a 3-dimensional array (T, K, N).")

        if not hasattr(self, "_beta_i"):
            raise ValueError(
                "Model must be fitted before making predictions, use .fit() method."
            )

        return np.einsum("tkn,nk->tn", regs, self._beta_i)
