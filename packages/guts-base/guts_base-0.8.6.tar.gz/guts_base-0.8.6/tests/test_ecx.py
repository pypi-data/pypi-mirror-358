import pytest
import arviz as az

from guts_base import LPxEstimator, GutsBase

from tests.conftest import construct_sim, idfunc


# Derive simulations for testing from fixtures
@pytest.fixture(params=[
    (GutsBase, "red_sd_ia", "ecx/idata_red_sd_ia.nc", "FLUA.5"),
    (GutsBase, "red_it", "ecx/idata_red_it.nc", "T 1"),
], ids=idfunc,)
def lpx_estimator(request, tmp_path):
    simulation_class, scenario, idata, id = request.param
    yield construct_estimator(
        simulation_class=simulation_class,
        scenario=scenario,
        idata=idata, 
        id=id,
        output_path=tmp_path
    )

def construct_estimator(simulation_class, scenario, idata, id, output_path=None):
    sim = construct_sim(
        simulation_class=simulation_class, 
        scenario=scenario,
        output_path=output_path
    )
    sim.set_inferer("numpyro")
    sim.inferer.idata = az.from_netcdf(f"data/testing/{idata}")

    return LPxEstimator(sim=sim, id=id)

@pytest.mark.slow
def test_lp50(lpx_estimator):
    # pytest.skip()

    theta_mean = lpx_estimator.sim.inferer.idata.posterior.mean(("chain", "draw"))
    theta_mean = {k: v["data"] for k, v in theta_mean.to_dict()["data_vars"].items()}

    lpx_estimator._loss(log_factor=0.0, theta=theta_mean)

    lpx_estimator.plot_loss_curve()

    lpx_estimator.estimate(mode="mean")
    lpx_estimator.estimate(mode="manual", parameters=lpx_estimator._posterior_mean())
    lpx_estimator.estimate(mode="draws")

    lpx_estimator.results
    lpx_estimator.results_full

def test_copy(lpx_estimator):
    e = lpx_estimator.sim.dispatch()
    e()
    e.results


if __name__ == "__main__":
    # test_inference(sim=construct_sim("test_scenario_v2", Simulation_v2), backend="numpyro")
    # test_lp50(simulation_class=GutsBase, scenario="red_sd_ia", idata="ecx/idata_red_sd_ia.nc", id="FLUA.5")
    test_copy(construct_estimator(GutsBase, "red_sd_ia", "ecx/idata_red_sd_ia.nc", "FLUA.5"))
