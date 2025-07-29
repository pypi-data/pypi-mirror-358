import pytest
import numpy as np
import itertools
from causal_falsify.utils.simulate_data import simulate_data
from causal_falsify.mint import MINT
from causal_falsify.transport import TransportabilityTest


@pytest.mark.parametrize(
    "method_class",
    [
        MINT(feature_representation="linear"),
        MINT(feature_representation="poly"),
        TransportabilityTest(cond_indep_test="fisherz"),
        TransportabilityTest(cond_indep_test="kcit_rbf"),
    ],
)
def test_method_grid(method_class):
    method = method_class
    iterations = 10
    seed = 42
    alpha = 0.05
    n_samples_list = [50, 100]
    degree_list = [1]
    n_envs_list = [25, 100]
    transportability_violation_list = [0.0]
    n_observed_confounders_list = [1, 5]

    config_grid = list(
        itertools.product(
            n_samples_list,
            degree_list,
            n_envs_list,
            transportability_violation_list,
            n_observed_confounders_list,
        )
    )

    for (
        n_samples,
        degree,
        n_envs,
        transportability_violation,
        n_observed_confounders,
    ) in config_grid:

        def run_test(conf_strength):
            rejections = []
            for _ in range(iterations):
                data = simulate_data(
                    n_samples=n_samples,
                    degree=degree,
                    conf_strength=conf_strength,
                    transportability_violation=transportability_violation,
                    n_envs=n_envs,
                    n_observed_confounders=n_observed_confounders,
                    seed=seed,
                )
                covariates = [f"X_{i}" for i in range(n_observed_confounders)]
                result = method.test(
                    data,
                    covariate_vars=covariates,
                    treatment_var="A",
                    outcome_var="Y",
                    source_var="S",
                )
                rejections.append(result < alpha)
            return rejections

        rejections_null_true = run_test(conf_strength=0.0)
        rejections_null_false = run_test(conf_strength=1.0)

        type_1_error = np.mean(rejections_null_true)
        type_2_error = 1 - np.mean(rejections_null_false)

        print(
            f"\nMethod: {method_class.__name__} | Config: n={n_samples}, deg={degree}, envs={n_envs}, "
            f"violation={transportability_violation}, confs={n_observed_confounders}"
        )
        print(f"Type 1 error: {type_1_error:.4f}")
        print(f"Type 2 error: {type_2_error:.4f}")

        assert (
            type_1_error < alpha
        ), f"❌ Type 1 Error check failed for {method_class.__name__}"
        assert (
            type_2_error < 0.2
        ), f"❌ Type 2 Error check failed for {method_class.__name__}"
