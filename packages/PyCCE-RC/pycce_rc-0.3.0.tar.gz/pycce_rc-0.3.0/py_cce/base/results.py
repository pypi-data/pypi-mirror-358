from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
import pandas as pd

from py_cce.base.data import PanelData


@dataclass
class RankConditionTestResult:
    """Class to hold the results of the rank condition test."""

    rc_holds: bool
    m_estim: int
    phi_estim: int
    tau_list: list[float]
    crit_val_list: list[float]

    def summary(self, max_width: int = 80) -> None:
        """Prints the summary of the rank condition test results with dynamic width."""
        rank_data = {
            "RC holds": self.rc_holds,
            "Estimated number of common factors (m)": self.m_estim,
            "Estimated rank of factor loadings": self.phi_estim,
        }

        # Compute dynamic key padding based on longest label
        key_width = max(len(key) for key in rank_data)
        rank_summary_lines = [
            f"{key:<{key_width}} : {value}" for key, value in rank_data.items()
        ]

        # Determine the actual width needed (title or longest line, whichever is longer)
        rank_title_core = " Rank Condition Test Summary "
        longest_line_len = max(
            len(rank_title_core), *(len(line) for line in rank_summary_lines)
        )
        dynamic_width = max(max_width, longest_line_len)

        # Center the title based on dynamic width
        rank_title_line = rank_title_core.center(dynamic_width, " ")

        # Print summary
        print(f"{rank_title_line}")
        print("=" * dynamic_width)
        for line in rank_summary_lines:
            print(line)
        print("=" * dynamic_width + "\n")

    def __repr__(self) -> str:
        """Method to implement the representation of this object.

        Returns:
        -------
        str
            Representation of object in string format.
        """
        return (
            f"RankConditionResult("
            f"rc_holds={self.rc_holds}, "
            f"m_estim={self.m_estim}, "
            f"phi_estim={self.phi_estim})"
        )


class CCEBaseResult(ABC):
    """Marker base class for all CCE result objects."""

    @abstractmethod
    def summary(self, decimals: int = 4) -> None:
        """Return a summary of the results."""
        pass


@dataclass
class AugmentationResult:
    """Class to hold the results of augmentation algorithm."""

    found_lower_ic: bool
    aug_csa: np.ndarray
    orig_csa: np.ndarray
    selected_indices: list[int]
    aug_rc_res: RankConditionTestResult | None = None
    aug_cce: CCEBaseResult | None = None

    def __repr__(self) -> str:
        """Method to implement the representation of this object.

        Returns:
        -------
        str
            Representation of object in string format.
        """
        aug_shape = (
            self.aug_csa.shape
            if self.found_lower_ic
            else "No improving augmentation found"
        )
        orig_shape = self.orig_csa.shape
        num_selected = len(self.selected_indices)

        rc_info = self.aug_rc_res if self.aug_rc_res is not None else "None"
        cce_info = (
            f"{self.aug_cce.__class__.__name__}(...)"
            if self.aug_cce is not None
            else "None"
        )

        return (
            f"{self.__class__.__name__} object at: {id(self)}\n"
            f"AugmentationResult(\n"
            f"  found_lower_ic={self.found_lower_ic},\n"
            f"  selected_indices={self.selected_indices}  # {num_selected} selected,\n"
            f"  aug_csa.shape={aug_shape},\n"
            f"  original_csa.shape={orig_shape},\n"
            f"  aug_rc={rc_info},\n"
            f"  aug_cce={cce_info},\n"
            f")"
        )

    def summary(self, decimals: int = 4) -> None:
        """Summarize the augmentation result and CCE summary if available.

        Parameters
        ----------
        decimals : int, optional
            Number of decimals to show in numerical output, by default 4.
        """
        aug_shape = self.aug_csa.shape if self.found_lower_ic else "N/A"
        orig_shape = self.orig_csa.shape
        num_selected = len(self.selected_indices)
        rc_status = (
            f"Holds (m={self.aug_rc_res.m_estim}, φ={self.aug_rc_res.phi_estim})"
            if self.aug_rc_res and self.aug_rc_res.rc_holds
            else (
                "Fails"
                if self.aug_rc_res
                else "Not evaluated since no improving augmentations found"
            )
        )

        lines = [
            ("Improved IC found", str(self.found_lower_ic)),
            ("Original CSA shape", str(orig_shape)),
            ("Selected CSA augmentation shape", str(aug_shape)),
            ("No. selected augmentations", str(num_selected)),
            ("Selected indices", str(self.selected_indices)),
            ("Rank condition after aug.", rc_status),
        ]

        # Dynamically determine the necessary padding
        label_pad = max(len(label) for label, _ in lines)
        value_pad = max(len(value) for _, value in lines)
        gap = 4
        line_width = label_pad + gap + value_pad
        title_core = " Augmentation Summary "
        title_line = title_core.center(line_width, " ")

        # Print summary
        print(f"\n{title_line}")
        print("=" * line_width)

        for label, value in lines:
            print(f"{label:<{label_pad}}{' ' * gap}{value:<{value_pad}}")

        print("=" * line_width)

        if self.aug_cce is not None:
            self.aug_cce.summary(decimals=decimals)
        else:
            print("No CCE results available for augmented data.")
            print("=" * line_width)


@dataclass
class CCEIndividualResult(CCEBaseResult):
    """Class that holds the results of the individual-specific CCE estimator. All results are per entity, thus has dimensions N x (k+1)."""

    beta_i: np.ndarray
    var_beta_i: np.ndarray
    rc_res: RankConditionTestResult
    panel: PanelData
    cov_type: str = "Newey-West HAC Robust"
    name: str = "Individual-specific CCE estimator"
    se_i: np.ndarray = field(init=False)
    t_stats_i: np.ndarray = field(init=False)
    entity_names: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Method called after initialization of dataclass."""
        self.se_i = np.sqrt(np.stack([np.diag(var_i) for var_i in self.var_beta_i]))
        self.t_stats_i = self.beta_i / self.se_i
        self.entity_names = self.panel.entities.to_list()

        lower = self.beta_i - 1.96 * self.se_i
        upper = self.beta_i + 1.96 * self.se_i
        self.conf_int_i = np.stack((lower, upper), axis=-1)

    def summary(self, decimals: int = 4) -> None:
        """Summarizes results of the CCE regression."""
        n_vars, n_obs, n_ents = self.panel.panel_shape
        k = n_vars - 1
        dep_var_name = self.panel.y_col
        now = datetime.now()

        df_summary = pd.DataFrame(
            {
                "Std": self.beta_i.std(axis=0),
                "Min": self.beta_i.min(axis=0),
                "Max": self.beta_i.max(axis=0),
                "5th %": np.percentile(self.beta_i, 5, axis=0),
                "95th %": np.percentile(self.beta_i, 95, axis=0),
                "|t| > 1.96 %": (np.abs(self.t_stats_i) > 1.96).mean(axis=0) * 100,
                "Avg CI Width": (
                    self.conf_int_i[:, :, 1] - self.conf_int_i[:, :, 0]
                ).mean(axis=0),
            },
            index=[f"b{j+1}" for j in range(k)],
        )
        df_str = df_summary.round(decimals).to_string()

        left_col = [
            ("Dep. Variable:", dep_var_name),
            ("Model:", "Panel interactive effects"),
            ("Method:", "CCE-Individual"),
            ("Date:", now.strftime("%a, %d %b %Y")),
            ("Covariance Type:", self.cov_type),
        ]

        right_col = [
            ("No. Observations:", str(n_obs)),
            ("No. Entities:", str(n_ents)),
            ("No. Regressors:", str(k)),
            ("Time:", now.strftime("%H:%M:%S")),
            ("Balanced panel:", str(self.panel.is_balanced)),
        ]

        label_pad = max(len(label) for label, _ in left_col + right_col)
        value_pad = max(len(value) for _, value in left_col + right_col)
        gap = 4
        line_width = 2 * (label_pad + value_pad) + gap

        title_core = " CCE Individual Estimator Summary "
        title_line = title_core.center(line_width, " ")

        summary_lines = [
            f"{l_label:<{label_pad}} {l_value:<{value_pad}}{' ' * gap}"
            f"{r_label:<{label_pad}} {r_value:<{value_pad}}"
            for (l_label, l_value), (r_label, r_value) in zip(
                left_col, right_col, strict=False
            )
        ]

        print(f"\n{title_line}")
        print("=" * line_width)

        for line in summary_lines:
            print(line)

        print("=" * line_width)
        print(df_str)
        print("=" * line_width)
        print(
            f"Note: the statistics are computed across entities (N={len(self.entity_names)})."
        )
        print(
            "NOte: use the 'get_entity_result' method to get entity specific results\n"
        )
        self.rc_res.summary(line_width)

    def top_entities(self, coeff_idx: int = 0, top: int = 5) -> pd.DataFrame:
        """Return top entities by estimated coefficient β_j."""
        sorted_idx = np.argsort(-self.beta_i[:, coeff_idx])
        rows = sorted_idx[:top]
        return pd.DataFrame(
            {
                "Entity": [self.entity_names[i] for i in rows],
                f"β{coeff_idx+1}": self.beta_i[rows, coeff_idx],
                "t-stat": (
                    self.t_stats_i[rows, coeff_idx]
                    if not np.isnan(self.t_stats_i).all()
                    else None
                ),
            }
        )

    def get_entity_result(self, i: int | str) -> pd.DataFrame:
        """Get β and t-stats for one entity (by index or name)."""
        idx = self.entity_names.index(i) if isinstance(i, str) else i
        k = self.beta_i.shape[1]
        data = {
            "Coefficient": [f"β{j+1}" for j in range(k)],
            "Estimate": [self.beta_i[idx, j] for j in range(k)],
            "Std. Error": [self.se_i[idx, j] for j in range(k)],
            "t-Statistic": [self.t_stats_i[idx, j] for j in range(k)],
            "95% CI": [
                f"[{self.conf_int_i[idx, j, 0]:.4f}, {self.conf_int_i[idx, j, 1]:.4f}]"
                for j in range(k)
            ],
        }
        return pd.DataFrame(data)

    def __repr__(self) -> str:
        """Method to implement the representation of this object.

        Returns:
        -------
        str
            Representation of object in string format.
        """
        return (
            f"\n{self.__class__.__name__} object at: {id(self)}\n"
            f"{self.name}\n"
            f"Number of entities: {len(self.entity_names)}\n"
            f"Number of coefficients: {self.beta_i.shape[1]}\n"
            f"Covariance type: {self.cov_type}\n"
            f"(Use `.summary()` or `.get_entity_result(idx)` to inspect results.)\n"
        )


@dataclass
class CCEAggregateResult(CCEBaseResult):
    """Class to hold the results of the CCE estimator regression."""

    name: str
    beta: np.ndarray
    var_beta: np.ndarray
    rc_res: RankConditionTestResult
    panel: PanelData
    cov_type: str = "Nonparametric"
    indiv_results: CCEIndividualResult | None = None

    se_beta: np.ndarray = field(init=False)
    t_stats: np.ndarray = field(init=False)
    conf_int: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        """Method called after initialization of dataclass."""
        self.se_beta = np.sqrt(np.diag(self.var_beta))
        self.t_stats = self.beta / self.se_beta
        self.conf_int = np.column_stack(
            [self.beta - 1.96 * self.se_beta, self.beta + 1.96 * self.se_beta]
        )

    def summary(self, decimals: int = 4) -> None:
        """Summarizes results of the CCE regression.

        Parameters
        ----------
        decimals : int, optional
            Number of decimals to be shown in results summary, by default 4.
        """
        n_vars, n_obs, n_ents = self.panel.panel_shape
        k = n_vars - 1
        dep_var_name = self.panel.y_col
        now = datetime.now()
        df = pd.DataFrame(
            {
                "Estimate": self.beta,
                "Std. Error": self.se_beta,
                "t-Statistic": self.t_stats,
                "95% CI": [
                    f"[{low:.{decimals}f}, {high:.{decimals}f}]"
                    for low, high in zip(
                        self.conf_int[:, 0], self.conf_int[:, 1], strict=False
                    )
                ],
            }
        )
        df.index = [f"β{j+1}" for j in range(len(self.beta))]

        df_str = df.round(decimals).to_string()

        method = "CCE-pooled" if self.indiv_results is None else "CCE-MG"

        left_col = [
            ("Dep. Variable:", dep_var_name),
            ("Model:", "Panel interactive effects"),
            ("Method:", method),
            ("Date:", now.strftime("%a, %d %b %Y")),
            ("Covariance Type:", self.cov_type),
        ]

        right_col = [
            ("No. Observations:", str(n_obs)),
            ("No. Entities:", str(n_ents)),
            ("No. Regressors:", str(k)),
            ("Time:", now.strftime("%H:%M:%S")),
            ("Balanced panel:", str(self.panel.is_balanced)),
        ]

        label_pad = max(len(label) for label, _ in left_col + right_col)
        value_pad = max(len(value) for _, value in left_col + right_col)
        gap = 4
        line_width = 2 * (label_pad + value_pad) + gap

        title_core = f" {self.name} Summary "
        title_line = title_core.center(line_width, " ")

        summary_lines = [
            f"{l_label:<{label_pad}} {l_value:<{value_pad}}{' ' * gap}"
            f"{r_label:<{label_pad}} {r_value:<{value_pad}}"
            for (l_label, l_value), (r_label, r_value) in zip(
                left_col, right_col, strict=False
            )
        ]

        print(f"\n{title_line}")
        print("=" * line_width)

        for line in summary_lines:
            print(line)

        print("=" * line_width)
        print(df_str)
        print("=" * line_width)
        self.rc_res.summary(line_width)

    def __repr__(self) -> str:
        """Method to implement the representation of this object.

        Returns:
        -------
        str
            Representation of object in string format.
        """
        return (
            f"{self.__class__.__name__} object at: {hex(id(self))}\n"
            f"{self.name}\n"
            f"Rank condition holds: {self.rc_res.rc_holds}\n"
            f"Estimated number of common factors (m): {self.rc_res.m_estim}\n"
            f"Estimated rank of factor loadings: {self.rc_res.phi_estim}\n"
            f"Number of coefficients: {self.beta.shape[0]}\n"
            f"Covariance type: {self.cov_type}\n"
            f"(Use `.summary()` to inspect results.)"
        )
