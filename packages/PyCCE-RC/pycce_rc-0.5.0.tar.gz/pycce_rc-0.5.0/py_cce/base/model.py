from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from py_cce.base.annotations import ArrayLikeType, PanelDataLikeType
from py_cce.base.data import PanelData
from py_cce.base.results import (
    AugmentationResult,
    CCEBaseResult,
    RankConditionTestResult,
)
from py_cce.utils.augmentation import _eval_csa_aug
from py_cce.utils.rank_condition import _evaluate_rank_condition


class CCEBaseModel(ABC):
    """Base class for the estimators, for internal use only."""

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
        """Initialise the base CCE model.

        Parameters
        ----------
        dep_var : PanelDataLikeType
            Data containing the dependent variable.
        regs : PanelDataLikeType
            Data containing the regressors.
        obs_facs: PanelDataLikeType or None, optional
            Observed common factors to be included in the model.
        weights : ArrayLikeType or None, optional
            Weights to be used in computing cross-sectional averages (CSA).
        csa : np.ndarray or None, optional
            Pre-computed CSA to be used in the estimation process.
        csa_indices: np.ndarray or None, optional
            Indices of variables used in pre-computed CSA.
        **kwargs: Any
            Additional variables used to initialise the PanelData object.
        """
        kwargs["weights"] = weights
        kwargs["obs_facs"] = obs_facs
        kwargs["csa"] = csa
        kwargs["csa_indices"] = csa_indices

        self._panel = PanelData.from_input_data(dep_var=dep_var, regs=regs, **kwargs)

        self._dep_var = dep_var
        self._regs = regs
        self._obs_facs = obs_facs

    @abstractmethod
    def _fit(
        self, method: str = "SVD", aug_res: AugmentationResult | None = None
    ) -> CCEBaseResult:
        """Abstract fitting method, to be implemented by all estimators.

        This method is for internal usage only.
        """
        pass

    @abstractmethod
    def fit(self, method: str = "SVD") -> CCEBaseResult:
        """Abstract fitting method, to be implemented by all estimators.

        This method should compute the estimator-specific coefficients and store results internally.
        """
        pass

    @abstractmethod
    def predict(self, regs: np.ndarray) -> np.ndarray:
        """Abstract prediction method, to be implemented by all estimators.

        Parameters
        ----------
        regs : np.ndarray
            The regressors for which predictions are to be made, in shape (T, K, N).

        Returns:
        -------
        np.ndarray
            The predicted values based on the fitted model.
        """
        pass

    def eval_rc(
        self,
        m_max: int | None = None,
        c: int = 20,
        alpha: float = 0.05,
    ) -> RankConditionTestResult:
        """Exposes the internal rank condition evaluation method.

        m_max : int
            The maximum number of factors to consider in the rank condition test.
        c : int, optional
            Multiplier of the significance level
        alpha : float, optional
            List of additional exogenous regressors to be considered for augmentation of the CSA, in the form (n_vars, n_obs, n_ents).


        Returns:
        -------
        RankConditionTestResult
            Result of the rank condition test.
        """
        return self._eval_rc(m_max=m_max, alpha=alpha, c=c)

    def _eval_rc(
        self,
        aug_obs: np.ndarray | None = None,
        aug_csa: np.ndarray | None = None,
        m_max: int | None = None,
        c: int = 20,
        alpha: float = 0.05,
    ) -> RankConditionTestResult:
        """Evaluates rank condition, transforms data if observed factors are present, otherwise regular data used.

        Parameters
        ----------
        m_max : int
            The maximum number of factors to consider in the rank condition test.
        c : int, optional
            Multiplier of the significance level
        alpha : float, optional
            List of additional exogenous regressors to be considered for augmentation of the CSA, in the form (n_vars, n_obs, n_ents).

        Returns:
        -------
        bool
            Result of the rank condition test.
        """
        if self._obs_facs is not None:
            z_mat = self._panel._panel_tensor_orth_obs
            csa = self._panel._csa_orth_obs
        else:
            z_mat = self._panel._panel_tensor
            csa = self._panel._csa

        if self._panel._csa_indices is not None:
            z_mat = z_mat[:, self._panel._csa_indices, :]

        return _evaluate_rank_condition(
            obs_mat=z_mat,
            csa=csa,
            m_max=m_max,
            aug_obs=aug_obs,
            aug_csa=aug_csa,
            c=c,
            alpha=alpha,
        )

    def eval_csa_aug(
        self,
        aug_weights: list[ArrayLikeType] | None = None,
        aug_regs: list[PanelDataLikeType] | None = None,
        m_max: int | None = None,
        c: int = 20,
        alpha: float = 0.05,
    ) -> AugmentationResult:
        """Evaluates the CSA augmentation for the model.

        Parameters
        ----------
        aug_weights : list[ArrayLikeType] | None, optional
            List of different weight vectors to be considered for augmenting CSAs.
        aug_regs : PanelDataLikeType | None, optional
            List of additional exogenous regressors to be considered for augmentation of the CSA, in the form (n_vars, n_obs, n_ents).
        m_max : int | None, optional
            The maximum number of factors to consider in the rank condition test.
        c : int, optional
            Multiplier of the significance level
        alpha : float, optional
            List of additional exogenous regressors to be considered for augmentation of the CSA, in the form (n_vars, n_obs, n_ents).

        Returns:
        -------
        CCEBaseResult
            Result object containing the evaluation of the CSA augmentation.
        """
        aug_res = _eval_csa_aug(self._panel, aug_weights, aug_regs)
        if aug_res.found_lower_ic:
            vars = (
                self._panel._panel_tensor
                if self._obs_facs is None
                else self._panel._panel_tensor_orth_obs
            )
            add_weights = []
            add_vars = []

            for j in aug_res.selected_indices:
                if aug_weights is not None and j < len(aug_weights):
                    add_weights.append(aug_weights[j])
                    continue

                if aug_regs is not None:
                    if aug_weights is None:
                        idx = j
                    elif aug_regs is not None and j >= len(aug_weights):
                        idx = j - len(aug_weights)

                    add_vars.append(aug_regs[idx].transpose(1, 0, 2))

            aug_vars = np.concatenate(
                [vars] * (len(add_weights) + 1) + add_vars, axis=1
            )

            aug_csa = np.hstack([aug_res.orig_csa, aug_res.aug_csa])
            aug_res.aug_rc_res = self._eval_rc(
                m_max=m_max, aug_obs=aug_vars, aug_csa=aug_csa, c=c, alpha=alpha
            )

            if aug_res.aug_rc_res.rc_holds:
                self._panel._set_augmented_csa(aug_csa)
                aug_res.aug_cce = self._fit(aug_res=aug_res)

        return aug_res

    @property
    def panel(self) -> PanelData:
        """Returns panel data.

        Returns:
        -------
        PanelData
            The panel representation of the input data.
        """
        return self._panel
