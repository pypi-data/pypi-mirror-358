from typing import Any

import numpy as np

from py_cce.base.annotations import ArrayLikeType, PanelDataLikeType
from py_cce.base.model import CCEBaseModel
from py_cce.base.results import AugmentationResult, CCEAggregateResult
from py_cce.models.cce_individual import CCEIndividualSpecificModel
from py_cce.utils.data import (
    compute_annihilator_matrix,
    include_observed_common_factors,
)


class CCEPooledModel(CCEBaseModel):
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
        csa : np.ndarray or None, optional
            Pre-computed CSA to be used in the estimation process.
        csa_indices: np.ndarray or None, optional
            Indices of variables used in pre-computed CSA.
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

    def _get_centered_individual_coef(self) -> np.ndarray:
        """Computes centered individual coefficients to be used in covariance estimator.

        Returns:
        -------
        np.ndarray
            Array containing individual coefficients centered around mean group estimates.
        """
        beta_i = CCEIndividualSpecificModel(
            self._panel._dependent_variable_data,
            self._panel._regressor_data,
            obs_facs=self._obs_facs,
            weights=self._panel._weights,
            internal_use=True,
        ).fit()
        beta_mg = np.mean(beta_i, axis=0)
        return beta_i - beta_mg

    def _compute_r_hat(
        self,
        anni_mat: np.ndarray,
        regs_wide: np.ndarray,
    ) -> np.ndarray:
        """Compute the R hat matrix, to be used in covariance matrix estimator.

        Parameters
        ----------
        anni_mat : np.ndarray
            Annihilator matrix to project out influence of (un)observed factors.
        regs_wide : np.ndarray
            Matrix containing only the regressors in shape T x k x N

        Returns:
        -------
        np.ndarray
            R hat matrix.
        """
        n_vars, n_obs, n_ents = self._panel.panel_shape
        k = n_vars - 1

        r_hat = np.zeros((k, k))
        beta_center = self._get_centered_individual_coef()
        w_tilde = self._panel._weights / np.sqrt(
            1 / n_ents * np.sum(self._panel._weights**2)
        )

        for i in range(n_ents):
            x_i = regs_wide[:, :, i]
            valid_rows = ~np.isnan(x_i).any(axis=1)
            if valid_rows.sum() < k:
                continue

            x_i_valid = x_i[valid_rows]
            anni_valid = anni_mat[np.ix_(valid_rows, valid_rows)]

            proj_x_i = (x_i_valid.T @ anni_valid @ x_i_valid) / valid_rows.sum()
            b_i_centered = beta_center[i][:, np.newaxis]

            proj_x_i = (x_i.T @ anni_mat @ x_i) / n_obs
            r_hat += w_tilde[i] ** 2 * (
                proj_x_i @ b_i_centered @ b_i_centered.T @ proj_x_i
            )

        r_hat /= n_ents - 1

        return r_hat

    def _compute_psi_hat(
        self,
        anni_mat: np.ndarray,
        regs_wide: np.ndarray,
    ) -> np.ndarray:
        """Compute the Psi hat matrix, to be used in covariance matrix estimator.

        Parameters
        ----------
        anni_mat : np.ndarray
            Annihilator matrix to project out influence of (un)observed factors.
        regs_wide : np.ndarray
            Matrix containing only the regressors in shape T x k x N

        Returns:
        -------
        np.ndarray
            Psi hat matrix.
        """
        weights = self._panel._weights
        n_vars, _, n_ents = self._panel.panel_shape
        k = n_vars - 1

        psi_hat = np.zeros((k, k))
        for i in range(n_ents):
            x_i = regs_wide[:, :, i]
            valid_rows = ~np.isnan(x_i).any(axis=1)

            if valid_rows.sum() < k:
                continue

            x_i_valid = x_i[valid_rows, :]
            anni_valid = anni_mat[np.ix_(valid_rows, valid_rows)]

            psi_i = (x_i_valid.T @ anni_valid @ x_i_valid) / valid_rows.sum()
            psi_hat += weights[i] * psi_i

        return psi_hat

    def _compute_cov_mat(
        self,
        anni_mat: np.ndarray,
        cov_type: str = "Nonparametric",
    ) -> np.ndarray:
        """Computes covariance matrix.

        Parameters
        ----------
        cov_type : str
            Type of covariance estimator that will be computed.
        anni_mat : np.ndarray
            Annihilator matrix to project out influence of (un)observed factors.

        Returns:
        -------
        np.ndarray
            Estimated covariance matrix.
        """
        regs_wide_panel = self._panel._panel_tensor[:, 1:, :]
        psi_hat = self._compute_psi_hat(anni_mat=anni_mat, regs_wide=regs_wide_panel)

        if cov_type == "Nonparametric":
            r_hat = self._compute_r_hat(anni_mat=anni_mat, regs_wide=regs_wide_panel)
            inv_psi = np.linalg.pinv(psi_hat)
            cov_mat = np.sum(self._panel._weights**2) * (inv_psi @ r_hat @ inv_psi)
        else:
            # Not implemented yet, but a different covariance matrix estimator is given in Pesaran
            # If conditions of theorem 4 hold.
            pass

        return cov_mat

    def fit(self, method: str = "SVD") -> CCEAggregateResult:
        """Fits individual-specific CCE estimator using OLS.

        Parameters
        ----------
        method : str, optional
            String determining which method to use in computing annihilator matrix, by default "SVD"

        Returns:
        -------
        CCEAggregateResult
            Object with the fitted model stored.
        """
        return self._fit(method=method)

    def _fit(
        self,
        method: str = "SVD",
        aug_res: AugmentationResult | None = None,
    ) -> CCEAggregateResult:
        """Fits the pooled CCE estimator using OLS.

        Parameters
        ----------
        method : str
            Method to compute the annihilator matrix, by default "SVD".
        cov_type : str
            Method used to compute the covariance matrix, by default "Nonparametric".
        aug_res : AugmentationResult | None, optional
            Augmentation result containing additional information, by default None.

        Returns:
        -------
        np.ndarray
            Estimated pooled beta vector.
        """
        k = self._panel._n_vars - 1
        t = self._panel._n_obs

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

        x_mx_sum = np.zeros((k, k))
        x_my_sum = np.zeros((k, 1))

        for entity in entities:
            x_i = x.loc[entity].to_numpy()
            y_i = y.loc[entity].to_numpy().reshape(t, 1)

            data_i = np.hstack([x_i, y_i])
            valid_rows = ~np.isnan(data_i).any(axis=1)

            if valid_rows.sum() < x_i.shape[1]:
                continue

            anni_valid = anni_mat[np.ix_(valid_rows, valid_rows)]

            x_i_valid = x_i[valid_rows]
            y_i_valid = y_i[valid_rows]

            x_aug = anni_valid @ x_i_valid
            y_aug = anni_valid @ y_i_valid

            x_mx_sum += x_aug.T @ x_aug
            x_my_sum += x_aug.T @ y_aug

        beta_pooled = np.linalg.solve(x_mx_sum, x_my_sum)
        cov_mat = self._compute_cov_mat(anni_mat=anni_mat)
        rc_res = self._eval_rc() if aug_res is None else aug_res.aug_rc_res

        if rc_res is None:
            raise ValueError(
                "rc_res must not be None when constructing CCEIndividualResult"
            )

        self._beta = beta_pooled.flatten()

        return CCEAggregateResult(
            name="CCE Pooled estimator",
            beta=self._beta,
            var_beta=cov_mat,
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

        if not hasattr(self, "_beta"):
            raise ValueError(
                "Model must be fitted before making predictions, use .fit() method."
            )

        return np.einsum("tkn,k->tn", regs, self._beta)
