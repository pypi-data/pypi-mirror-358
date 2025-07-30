from typing import Any

import numpy as np

from py_cce.base.annotations import ArrayLikeType, PanelDataLikeType
from py_cce.base.model import CCEBaseModel
from py_cce.base.results import AugmentationResult, CCEAggregateResult
from py_cce.models.cce_individual import CCEIndividualSpecificModel


class CCEMeanGroupModel(CCEBaseModel):
    """Class for the mean group CCE estimator."""

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
        """Initialise the mean group CCE estimator.

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
        kwargs["weights"] = weights
        self._indiv_specific_model = self._init_indiv_model(**kwargs)

    def _init_indiv_model(self, **kwargs: Any) -> CCEIndividualSpecificModel:
        """Factory method to instantiate the individual-specific model."""
        return CCEIndividualSpecificModel(
            dep_var=self._dep_var,
            regs=self._regs,
            obs_facs=self._obs_facs,
            **kwargs,
        )

    def _compute_cov_mat(self, beta_i: np.ndarray, beta_mg: np.ndarray) -> np.ndarray:
        n_ents = self._panel._n_ents

        centered = beta_i - beta_mg
        sigma_mg = (centered.T @ centered) / (n_ents - 1)
        return sigma_mg / n_ents

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
        """Fits mean group CCE estimator using OLS.

        Parameters
        ----------
        method : str, optional
            String determining which method to use in computing OLS, by default "SVD"

        Returns:
        -------
        _type_
            _description_.
        """
        model_indiv = self._indiv_specific_model._fit(method=method, aug_res=aug_res)
        beta_i = model_indiv.beta_i
        beta_mg = np.mean(beta_i, axis=0)
        cov_mat = self._compute_cov_mat(beta_i=beta_i, beta_mg=beta_mg)
        rc_res = self._eval_rc() if aug_res is None else aug_res.aug_rc_res

        if rc_res is None:
            raise ValueError(
                "rc_res must not be None when constructing CCEIndividualResult"
            )

        self._beta_i = beta_i
        self._beta = beta_mg.flatten()

        return CCEAggregateResult(
            name="CCE Mean Group estimator",
            beta=beta_mg,
            indiv_results=model_indiv,
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
