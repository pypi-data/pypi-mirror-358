from typing import Tuple
import pytest
import numpy as np
import xarray as xr
from mempy.model import (
    RED_IT, RED_SD, RED_SD_DA, Reduced,
    BufferGUTS_SD, BufferGUTS_IT, BufferGUTS_SD_CA
)
from mempy.input_data import read_exposure_survival
from guts_base import PymobSimulator

from tests.conftest import idfunc

# results are from Bürger and Focks 2025 (https://doi.org/10.1093/etojnl/vgae058) 
# supplementary material (Tab. 5.3)
OPENGUTS_ESTIMATES = dict(
    red_sd = xr.Dataset(dict(kd=0.712, m=2.89, b=0.619, hb=0.008)).to_array().sortby("variable"),
    red_sd_da = None,
    bufferguts_sd_ca = None,
)

def read_data(file):
    data = read_exposure_survival(
        "data/testing", file, 
        survival_name="Survival",
        exposure_name="Exposure",
        visualize=False,
        with_raw_exposure_data=True
    )

    exposure_funcs, survival_data, num_expos, exposure_data = data
    info_dict = {}

    return exposure_funcs, survival_data, num_expos, info_dict, exposure_data


def construct_sim(dataset: Tuple, model: type, output_path="results/testing"):
    """Helper function to construct simulations for debugging"""
    _, survival_data, num_expos, _, exposure_data = read_data(file=dataset)

    if model in (RED_IT, RED_SD, BufferGUTS_SD, BufferGUTS_IT):
        _model = model()
    else:
        _model = model(num_expos=num_expos)

    sim = PymobSimulator.from_mempy(
        exposure_data=exposure_data,
        survival_data=survival_data,
        model=_model,
        output_directory=output_path
    )

    return sim


@pytest.fixture(params=[
    ("ringtest_A_SD.xlsx", RED_SD),
    ("Fit_Data_Cloeon_final.xlsx", RED_SD_DA,),
    ("osmia_multiexpo_synthetic.xlsx", BufferGUTS_SD_CA,),
], ids=idfunc)
def dataset_and_model(request) -> Reduced:
    yield request.param


# Derive simulations for testing from fixtures
@pytest.fixture
def sim(dataset_and_model, tmp_path):
    dataset, model = dataset_and_model
    yield construct_sim(dataset=dataset, model=model, output_path=tmp_path)


# run tests with the Simulation fixtures
def test_setup(sim):
    """Tests the construction method"""
    assert True


def test_simulation(sim):
    """Tests if a forward simulation pass can be computed"""
    # sim.dispatch_constructor()
    evaluator = sim.dispatch()
    evaluator()
    evaluator.results

    assert True

@pytest.mark.slow
@pytest.mark.parametrize("backend", ["numpyro"])
def test_inference(sim: PymobSimulator, backend):
    """Tests if prior predictions can be computed for arbitrary backends"""

    sim.set_inferer(backend)

    sim.prior_predictive_checks()
    sim.inferer.run()

    sim.posterior_predictive_checks()

    sim.config.report.debug_report = True
    sim.report()

    # test if inferer converged on the true estmiates
    pymob_estimates = sim.inferer.idata.posterior.mean(("chain", "draw")).to_array().sortby("variable")
    openguts_estimates = OPENGUTS_ESTIMATES[sim.config.simulation.model.lower()]

    if openguts_estimates is None:
        # this explicitly skips testing the results, since they are not available,
        # but does not fail the test.
        pytest.skip()

    np.testing.assert_allclose(pymob_estimates, openguts_estimates, rtol=0.05, atol=0.1)




if __name__ == "__main__":
    # test_inference(sim=construct_sim("ringtest_A_SD.xlsx", RED_SD), backend="numpyro",)
    test_inference(sim=construct_sim("osmia_multiexpo_synthetic.xlsx", BufferGUTS_SD_CA), backend="numpyro",)
    # test_inference(sim=construct_sim("Fit_Data_Cloeon_final.xlsx", RED_SD_DA), backend="numpyro",)
