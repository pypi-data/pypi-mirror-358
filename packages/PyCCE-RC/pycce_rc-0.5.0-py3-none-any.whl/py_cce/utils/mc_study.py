import pickle
import time
import warnings

from collections import Counter
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np

from joblib import Parallel, delayed

from py_cce.models.cce_pooled import CCEPooledModel
from py_cce.utils.sample import generate_panel


class MonteCarloStudy:
    correct_estimates = {
        "exp_1": {
            "phi": 2,
            "m": 2,
        },
        "exp_2": {
            "phi": 1,
            "m": 2,
        },
        "exp_3": {
            "phi": 0,
            "m": 2,
        },
    }

    def __init__(
        self,
        experiment: int,
        num_sims: int,
        gen_sample_params: dict[str, Any],
        rng: np.random.Generator,
    ):
        self._rng = rng
        self._experiment = experiment
        self._num_sims = num_sims
        self._gen_sample_kwargs = gen_sample_params
        self._correct_vals = self.correct_estimates[f"exp_{self._experiment}"]

    def _generate_valid_weights(self, big_n: int) -> np.ndarray:

        raw_weights = self._rng.uniform(0, 1, size=big_n)
        weights = raw_weights / raw_weights.sum()

        return weights

    def run_study(self) -> dict[str, Any]:
        correct_phi = self._correct_vals["phi"]
        correct_m = self._correct_vals["m"]
        real_phi = 2

        phi_counter: Counter = Counter()
        m_counter: Counter = Counter()
        num_rc_holds = 0

        aug_phi_counter = Counter()
        aug_m_counter = Counter()
        num_restored_rc = 0

        selects_correct_restorer = 0

        index_counter = Counter()

        beta_res = []
        conf_int_res = []
        standard_errors = []

        beta_res_aug = []
        conf_int_res_aug = []
        standard_errors_aug = []
        tau_list = []
        crit_val_list = []

        c = self._gen_sample_kwargs.pop("c")
        for i in range(self._num_sims):
            dep_var, regs, dt, aug_data, aug_data_2 = generate_panel(
                **self._gen_sample_kwargs
            )

            if not self._gen_sample_kwargs["include_d"] and dt is not None:
                raise ValueError("Observed factors are not None but include_d is False")

            if self._gen_sample_kwargs["include_d"] and dt is None:
                raise ValueError("Observed factors are None but include_d is True")

            pooled_model = CCEPooledModel(dep_var=dep_var, regs=regs, obs_facs=dt)
            rc_res = pooled_model.eval_rc(m_max=10, c=c)
            fit_model = pooled_model.fit()
            beta_res.append(fit_model.beta)
            conf_int_res.append(fit_model.conf_int)
            standard_errors.append(fit_model.se_beta)

            tau_list.append(rc_res.tau_list)
            crit_val_list.append(rc_res.crit_val_list)

            m_counter[self.compare(rc_res.m_estim, correct_m)] += 1
            phi_counter[self.compare(rc_res.phi_estim, correct_phi)] += 1

            if rc_res.rc_holds:
                num_rc_holds += 1

            if self._experiment != 1:
                if self._experiment == 3:
                    right_index = 0

                big_n = self._gen_sample_kwargs["N"]
                n_1 = big_n / 10
                aug_weights = np.repeat(1 / n_1, n_1)
                aug_weights = np.pad(
                    aug_weights, (0, big_n - len(aug_weights)), constant_values=0
                )
                aug_weights_2 = self._generate_valid_weights(big_n)

                if self._experiment == 2:
                    right_index = 2

                aug_res = pooled_model.eval_csa_aug(
                    aug_regs=[aug_data, aug_data_2],
                    aug_weights=[aug_weights, aug_weights_2],
                )

                if aug_res.aug_cce is not None:
                    beta_res_aug.append(aug_res.aug_cce.beta)
                    conf_int_res_aug.append(aug_res.aug_cce.conf_int)
                    standard_errors_aug.append(aug_res.aug_cce.se_beta)

                index_counter[tuple(aug_res.selected_indices)] += 1
                if (
                    len(aug_res.selected_indices) == 1
                    and aug_res.selected_indices[0] == right_index
                ):
                    selects_correct_restorer += 1

                if aug_res.aug_rc_res is not None:
                    aug_rc = aug_res.aug_rc_res
                    aug_m_counter[self.compare(aug_rc.m_estim, correct_m)] += 1
                    aug_phi_counter[self.compare(aug_rc.phi_estim, real_phi)] += 1
                    if aug_rc.rc_holds:
                        num_restored_rc += 1

        return {
            "m_results": m_counter,
            "phi_results": phi_counter,
            "orig_rc_holds": num_rc_holds,
            "aug_m_results": aug_m_counter,
            "aug_phi_results": aug_phi_counter,
            "restored_rc_holds": num_restored_rc,
            "selects_correct_restorer": selects_correct_restorer,
            "selected_idx": index_counter,
            "beta": beta_res,
            "conf_intervals": conf_int_res,
            "standard_errors": standard_errors,
            "beta_aug": beta_res_aug,
            "conf_int_res_aug": conf_int_res_aug,
            "standard_errors_aug": standard_errors_aug,
            "tau_list": tau_list,
            "crit_val_list": crit_val_list,
        }

    @staticmethod
    def compare(est, true_val):
        if est < true_val:
            return "lower"
        elif est == true_val:
            return "equal"
        else:
            return "higher"


def run_single_experiment(args):
    warnings.filterwarnings("ignore")
    exp, t, n, c, kwargs = args
    start = time.time()

    file_path = save_path / f"exp_{exp}_{n}_{t}_{c}.pkl"
    if file_path.exists():
        print(f"⚠️ Skipping exp={exp}, N={n}, T={t} (already exists)")
        return

    kwargs.update(
        {
            "T": t,
            "N": n,
            "experiment": exp,
            "c": c,
        }
    )

    mc_study = MonteCarloStudy(
        experiment=exp, num_sims=1_000, gen_sample_params=kwargs, rng=rng
    )
    results = mc_study.run_study()

    with open(file_path, "wb") as f:
        pickle.dump(results, f)

    elapsed = time.time() - start
    print(f"⏱️ Time for exp={exp}, N={n}, T={t}: {timedelta(seconds=round(elapsed))}")


if __name__ == "__main__":
    save_path = Path("results/exp_3/test_sign_lev")
    save_path.mkdir(exist_ok=True)

    # Variables that change
    # experiments = [1, 2, 3]
    experiments = [1]
    c_list = [20, 40]
    num_periods = [20, 50, 100, 200]
    num_entities = [20, 50, 100, 200]
    include_d = True

    # Constant variables used
    rho = 0.8
    k = 2
    rng = np.random.default_rng(42)
    beta = np.array([[2], [3]])
    homogeneous = True
    all_results = {}

    total_experiments = len(experiments) * len(num_periods) * len(num_entities)
    current_experiment = 0

    start_total = time.time()

    kwargs = {
        "include_d": include_d,
        "k": k,
        "rho": rho,
        "homogeneous": homogeneous,
        "perc_missing": None,
        "beta": beta,
        "rng": rng,
    }
    all_combinations = [
        (exp, t, n, c, kwargs)
        for exp in experiments
        for t in num_periods
        for n in num_entities
        for c in c_list
    ]

    Parallel(n_jobs=-1)(
        delayed(run_single_experiment)(args) for args in all_combinations
    )

    total_elapsed = time.time() - start_total
    print(
        f"\n✅ All experiments finished in: {timedelta(seconds=round(total_elapsed))}"
    )
