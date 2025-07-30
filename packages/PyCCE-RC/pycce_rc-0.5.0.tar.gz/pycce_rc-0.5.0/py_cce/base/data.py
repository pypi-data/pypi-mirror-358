from __future__ import annotations

import warnings

from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from py_cce.base.annotations import PanelDataLikeType
from py_cce.base.annotations import ArrayLikeType, PandasObject
from py_cce.base.exceptions import PanelDataError
from py_cce.utils.csa import compute_csa, normalize_weights
from py_cce.utils.data import compute_annihilator_matrix


class PanelData:
    """This class stores and manages panel data, where observations are indexed by both time and entity."""

    def __init__(
        self,
        frame: pd.DataFrame,
        y_col: str | int = 0,
        csa: np.ndarray | None = None,
        csa_indices: list[int] | None = None,
        obs_facs: PanelDataLikeType | None = None,
        entity_name: str = "entity",
        time_period_name: str = "period",
        weights: PanelDataLikeType | None = None,
    ):
        """Initialise a PanelData object.

        Parameters
        ----------
        data : ArrayLikeType
            Data to be transformed to PanelData object.
        y_col : str or int, optional
            Column name or index indicating the dependent variable. Defaults to 0.
        csa : np.ndarray or None, optional
            Pre-computed CSA to be used in the estimation process.
        csa_indices: np.ndarray or None, optional
            Indices of variables used in pre-computed CSA.
        obs_facs: PanelDataLikeType or None, optional
            Observed common factors to be included in the model.
        entity_name : str, optional
            The name of the entity index. Defaults to "entity".
        time_period_name : str, optional
            The name of the time period index. Defaults to "period".
        weights : np.ndarray | None, optional
            Weights to be used in the computation of the cross-sectional averages.
        """
        self._entity_name = entity_name
        self._time_period_name = time_period_name
        self._y_col = y_col if isinstance(y_col, str) else frame.columns[0]
        self._obs_facs = obs_facs

        self._panel_frame = frame.copy()
        self._is_balanced = self._check_panel_balance()

        self._regressor_data = self._panel_frame.drop(columns=[self._y_col])
        self._dependent_variable_data = self._panel_frame[self._y_col]

        self._time_idx = self._panel_frame.index.get_level_values(
            self._time_period_name
        )
        self._entity_idx = self._panel_frame.index.get_level_values(self._entity_name)

        self._n_vars: int = self._panel_frame.shape[1]
        self._n_obs: int = self._time_idx.nunique()
        self._n_ents: int = self._entity_idx.nunique()

        self._contains_aug_csa = False

        self._weights = (
            normalize_weights(np.asarray(weights), self._n_ents)
            if weights is not None
            else np.full(self._n_ents, 1 / self._n_ents)
        )

        if self._weights is not None and len(self._weights) != self._n_ents:
            raise PanelDataError(
                "The number of weights passed does not equal the number of entities."
            )

        self._time_periods = self._time_idx.unique()
        self._entities = self._entity_idx.unique()

        self._index_containing_nan = self._panel_frame[
            self._panel_frame.isna().any(axis=1)
        ].index

        if len(self._index_containing_nan) / len(self._panel_frame.index) > 0.2:
            raise PanelDataError(
                r"More than 20% of the data contains NaN values, which can lead to numerical instability plus poor regressions."
            )

        if (
            csa is not None
            and csa_indices is None
            or csa is None
            and csa_indices is not None
        ):
            raise PanelDataError(
                "When passing a pre-computed CSA it is required to also provide the indices of the variables used in this CSA."
            )

        if self._obs_facs is not None:
            self._obs_facs_proj_mat = compute_annihilator_matrix(
                observables=self._obs_facs, n_obs=self._n_obs
            )
            self._panel_tensor_orth_obs = self._panel_to_tensor(
                proj_mat=self._obs_facs_proj_mat
            )
            self._csa_orth_obs = (
                self._compute_csa(include_proj=True) if csa is None else csa.copy()
            )

        self._panel_tensor = self._panel_to_tensor()
        self._csa = self._compute_csa() if csa is None else csa.copy()
        self._csa_indices = csa_indices if csa_indices is not None else None

    @classmethod
    def from_input_data(
        cls, dep_var: PanelDataLikeType, regs: PanelDataLikeType | None, **kwargs: Any
    ) -> PanelData:
        """Initialise PanelData object from input data.

        Parameters
        ----------
        dep_var : PanelDataLikeType
            Input data of depedent variable.
        regs : PanelDataLikeType | None
            Input data of regressors.

        Returns:
        -------
        PanelData
            Initialised PanelData object from input data.

        Raises:
        ------
        PanelDataError
            If dependent variable and regressors are not of a similar panel data type.
        """
        if isinstance(dep_var, PandasObject) and isinstance(regs, PandasObject):
            return cls.from_pandas(dep_var=dep_var, regs=regs, **kwargs)

        if isinstance(dep_var, ArrayLikeType) and isinstance(regs, ArrayLikeType):
            return cls.from_array(dep_var=dep_var, regs=regs, **kwargs)

        raise PanelDataError(
            "Depedent variable and regressors should either both be of array like type or both be pandas type"
        )

    @classmethod
    def from_pandas(
        cls,
        dep_var: PandasObject,
        regs: PandasObject | None = None,
        **kwargs: Any,
    ) -> PanelData:
        """Initialises PanelData object from pandas object.

        Parameters
        ----------
        dep_var : PandasObject
            Depedent variable
        regs : PandasObject | None, optional
            Regressors, by default None

        Returns:
        -------
        PanelData
            PanelData object initialised from pandas data
        """
        if len(dep_var.index.levshape) != 2 or not isinstance(
            dep_var.index, pd.MultiIndex
        ):
            raise PanelDataError(
                "Pandas object needs to be provided with 2-dimensional MultiIndex in the form (entities, time periods)"
            )

        if regs is not None:
            if len(regs.index.levshape) != 2 or not isinstance(
                regs.index, pd.MultiIndex
            ):
                raise PanelDataError(
                    "Pandas object needs to be provided with 2-dimensional MultiIndex in the form (entities, time periods)"
                )

            if not dep_var.index.equals(regs.index):
                warnings.warn(
                    "Indices of dependent variable and regressors do not match. "
                    "They will be aligned via outer join, which may introduce NaNs.",
                    stacklevel=2,
                    category=UserWarning,
                )

        if isinstance(dep_var, pd.Series):
            dep_var.name = "y" if dep_var.name is None else dep_var.name
            dep_var = pd.DataFrame(dep_var)

        if isinstance(regs, pd.Series):
            regs.name = "X" if regs.name is None else regs.name
            regs = pd.DataFrame(regs)

        panel_frame = (
            pd.concat([dep_var, regs], axis=1) if regs is not None else dep_var.copy()
        )
        kwargs["entity_name"] = panel_frame.index.names[0]
        kwargs["time_period_name"] = panel_frame.index.names[1]
        kwargs["y_col"] = dep_var.columns[0]

        return cls(frame=panel_frame, **kwargs)

    @classmethod
    def from_array(
        cls,
        dep_var: ArrayLikeType,
        regs: ArrayLikeType | None = None,
        **kwargs: Any,
    ) -> PanelData:
        """Initialises PanelData object from numpy objects.

        Parameters
        ----------
        dep_var : PandasObject
            Depedent variable
        regs : PandasObject | None, optional
            Regressors, by default None

        Returns:
        -------
        PanelData
            PanelData object initialised from numpy data

        Notes:
        -----
        The data provided must be 3-dimensional in the form (n_vars, n_obs, n_ents), where:

        * n_vars : Number of variables, including dependent variable. If a 2-dimensional array is provided, it is assumed that n_vars = 1.
        * n_obs : Number of time observations.
        * n_ents : Number of cross-sectional entities.

        Raises:
        ------
        PanelDataError
            If the position of the depedent variable column is provided as a string, which does not work for numpy arrays.
        """
        y_col = kwargs.get("y_col", 0)
        if isinstance(y_col, str):
            raise PanelDataError(
                "Dependent variable column should be an integer for numpy arrays"
            )

        dep_var = cls._transform_numpy_array_dimensions(dep_var)
        if regs is not None:
            regs = cls._transform_numpy_array_dimensions(regs)

            if dep_var.shape[1:] != regs.shape[1:]:
                raise PanelDataError(
                    "Dependent variable and regressors need to have the same n_obs and n_ents"
                )

        panel_data = (
            np.concatenate((dep_var, regs), axis=0)
            if regs is not None
            else dep_var.copy()
        )

        entity_name = kwargs.get("entity_name", "entity")
        time_period_name = kwargs.get("time_period_name", "period")

        k, t, n = panel_data.shape
        regs_columns = [f"X_{i}" if i > 0 else "y" for i in range(k)]
        regressors_dict = {
            col: panel_data[i].T.flatten() for i, col in enumerate(regs_columns)
        }
        index = pd.MultiIndex.from_product(
            [[f"i_{j}" for j in range(1, n + 1)], [f"t_{j}" for j in range(1, t + 1)]],
            names=[entity_name, time_period_name],
        )

        panel_frame = pd.DataFrame(regressors_dict, index=index)
        kwargs["entity_name"] = panel_frame.index.names[0]
        kwargs["time_period_name"] = panel_frame.index.names[1]
        kwargs["y_col"] = "y"

        return cls(
            frame=panel_frame,
            **kwargs,
        )

    @staticmethod
    def _transform_numpy_array_dimensions(data_array: ArrayLikeType) -> np.ndarray:
        """Checks numpy array dimensions and converts to correct dimensions if necessary.

        Parameters
        ----------
        data_array : np.ndarray
            Input data numpy array.

        Returns:
        -------
        np.ndarray
            Numpy array transformed to correct dimensions.

        Raises:
        ------
        PanelDataError
            If numpy array is not 2 or 3-dimensional
        """
        data_array = np.asarray(data_array)

        if data_array.ndim == 2:
            data_array = data_array[np.newaxis, :, :]
        elif data_array.ndim != 3:
            raise PanelDataError(
                "To convert numpy array to panel data it should either be 2 or 3-dimensional"
            )

        return data_array

    def _set_augmented_csa(self, aug_csa: np.ndarray) -> None:
        """Updates the csa after a succesful augmentation."""
        self._contains_aug_csa = True
        self._csa = aug_csa.copy()

    def _check_panel_balance(self) -> bool:
        """Check whether the panel data is balanced.

        Returns:
        -------
        bool
            True if panel is balanced, False otherwise.
        """
        contains_nan_values = self._panel_frame.isna().any().any()

        return not contains_nan_values

    def _panel_to_tensor(self, proj_mat: np.ndarray | None = None) -> np.ndarray:
        """Transform panel to a 3D array of shape T x (K+1) x N.

        Parameters
        ----------
        proj_mat : np.ndarray | None, optional
            Projection matrix to pre-multiply observables by.

        Returns:
        -------
        np.ndarray
            Numpy array of shape T x (K+1) x N
        """
        entity_data = []
        for entity in self._entities:
            z_i = self._panel_frame.loc[entity].values

            if proj_mat is not None:
                z_i = proj_mat @ z_i
            entity_data.append(z_i[:, :, np.newaxis])

        return np.concatenate(entity_data, axis=2)

    def _compute_csa(
        self,
        include_proj: bool = False,
        weights: PanelDataLikeType | None = None,
    ) -> np.ndarray:
        """Computes CSA for provided data.

        Parameters
        ----------
        proj_mat : np.ndarray | None, optional
            Projection matrix to be used to transform observables, by default None.
        weights : ArrayLikeType | None, optional
            Weights to be used per unit when computing CSA, by default None.

        Returns:
        -------
        np.ndarray
            Numpy array with cross-sectional averages in shape (n_obs, n_vars).
        """
        if weights is not None:
            weights = np.asarray(weights)
        elif self._weights is not None:
            weights = self._weights.copy()
        else:
            weights = None

        observables = (
            self._panel_tensor_orth_obs if include_proj else self._panel_tensor
        )
        return compute_csa(observables=observables, weights=weights)

    def compute_csa(
        self, weights: PanelDataLikeType | None = None, include_proj: bool = False
    ) -> np.ndarray:
        """Exposes internal CSA computation method externally.

        Parameters
        ----------
        weights : ArrayLikeType | None, optional
            Weights to be used per unit when computing CSA, by default None.
        include_proj: bool
            Boolean indicating whether to use the panel where observed factors are projected out.

        Returns:
        -------
        np.ndarray
            Numpy array with cross-sectional averages in shape (n_obs, n_vars).
        """
        return self._compute_csa(weights=weights, include_proj=include_proj)

    @property
    def y_col(self) -> str:
        """Returns the column name or index of the dependent variable.

        Returns:
        -------
        str | int
            Column name or index of the dependent variable.
        """
        return self._y_col

    @property
    def panel_shape(self) -> tuple[int, int, int]:
        """Returns shape of panel in format (n_vars, n_obs, n_ents).

        Returns:
        -------
        tuple[int, int, int]
            Shape of the panel.
        """
        return (
            self._n_vars,
            self._n_obs,
            self._n_ents,
        )

    @property
    def is_balanced(self) -> bool:
        """Indicates whether the panel is balanced.

        Returns:
        -------
        bool
            True if balanced, False otherwise.
        """
        return self._is_balanced

    @property
    def panel_frame(self) -> pd.DataFrame:
        """Returns the internal panel DataFrame.

        Returns:
        -------
        pd.DataFrame
        """
        return self._panel_frame

    @property
    def index_containing_nan(self) -> pd.MultiIndex:
        """Returns the entity-time index pairs that contain NaN values.

        Returns:
        -------
        pd.MultiIndex
        """
        return self._index_containing_nan

    @property
    def columns_containing_nan(self) -> pd.Index:
        """Returns the columns that contain NaN values.

        Returns:
        -------
        pd.Index
        """
        return self._panel_frame.columns[self._panel_frame.isna().any()]

    @property
    def entities(self) -> pd.Index:
        """Returns pandas object containing all unique entities.

        Returns:
        -------
        pd.Index
            Index containing all unique entities.
        """
        return self._entities

    @property
    def time_periods(self) -> pd.Index:
        """Returns pandas object containing all unique time periods.

        Returns:
        -------
        pd.Index
            Index containing all unique time periods.
        """
        return self._time_periods

    @property
    def csa(self) -> np.ndarray:
        """Returns the CSA used in estimation.

        Returns:
        -------
        np.ndarray
            Numpy array containing the CSA.
        """
        return self._csa if self._obs_facs is None else self._csa_orth_obs

    def __str__(self) -> str:
        """Return the string representation of the object.

        Returns:
        -------
        str
        """
        return f"{self.__class__.__name__} \n {self._panel_frame}"

    def __repr__(self) -> str:
        """Return the detailed representation of the object.

        Returns:
        -------
        str
        """
        return f"{str(self)} \n Object ID: {hex(id(self))}"
