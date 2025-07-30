import pytest

from guts_base import GutsBase

from tests.conftest import construct_sim, idfunc

# List test scenarios and simulations
@pytest.fixture(params=[
    (GutsBase, "red_sd"),
    (GutsBase, "red_it"),
    (GutsBase, "red_sd_ia"),
], ids=idfunc)
def sim_and_scenario(request):
    return request.param


# Derive simulations for testing from fixtures
@pytest.fixture
def sim(sim_and_scenario, tmp_path):
    simulation_class, scenario = sim_and_scenario
    yield construct_sim(
        scenario=scenario, 
        simulation_class=simulation_class, 
        output_path=tmp_path
    )


# run tests with the Simulation fixtures
def test_setup(sim):
    """Tests the construction method"""
    assert True


def test_simulation(sim):
    """Tests if a forward simulation pass can be computed"""
    sim.dispatch_constructor()
    evaluator = sim.dispatch()
    evaluator()
    evaluator.results

    assert True
            
def test_copy(sim):
    sim.dispatch_constructor()
    e_orig = sim.dispatch()
    e_orig()
    e_orig.results

    sim_copy = sim.copy()
    
    sim_copy.dispatch_constructor()
    e_copy = sim_copy.dispatch()
    e_copy()

    assert (e_copy.results == e_orig.results).all().to_array().all().values


@pytest.mark.slow
@pytest.mark.parametrize("backend", ["numpyro"])
def test_inference(sim: GutsBase, backend):
    """Tests if prior predictions can be computed for arbitrary backends"""
    sim.dispatch_constructor()
    sim.set_inferer(backend)

    sim.config.inference.n_predictions = 2
    sim.prior_predictive_checks()
    
    sim.config.inference_numpyro.kernel = "svi"
    sim.config.inference_numpyro.svi_iterations = 10
    sim.config.inference_numpyro.svi_learning_rate = 0.05
    sim.config.inference_numpyro.draws = 10
    sim.config.inference.n_predictions = 10

    sim.inferer.run()

    sim.inferer.idata
    sim.inferer.store_results()

    sim.posterior_predictive_checks()

    sim.inferer.load_results()
    sim.config.report.debug_report = True
    sim.report()


if __name__ == "__main__":
    test_inference(sim=construct_sim("red_sd", GutsBase), backend="numpyro")
