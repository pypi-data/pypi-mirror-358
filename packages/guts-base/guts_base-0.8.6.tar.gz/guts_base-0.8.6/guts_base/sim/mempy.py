import pathlib
from typing import Dict, Optional, Literal
import re

import numpy as np
import pandas as pd
import xarray as xr
from pymob import SimulationBase
from pymob.sim.config import Config, DataVariable, Datastructure
from pymob.sim.parameters import Param
from guts_base.sim import GutsBase
from mempy.model import (
    Model, 
    RED_IT, 
    RED_SD,
    RED_IT_DA,
    RED_SD_DA,
    RED_IT_IA,
    RED_SD_IA,
    BufferGUTS_IT,
    BufferGUTS_IT_CA,
    BufferGUTS_IT_DA
)

__all__ = [
    "PymobSimulator",
]

class PymobSimulator(GutsBase):

    @classmethod
    def from_mempy(
        cls,
        exposure_data: Dict,
        survival_data: Dict,
        model: Model,
        info_dict: Dict = {},
        pymob_config: Optional[Config] = None,
        output_directory: str|pathlib.Path = pathlib.Path("output/pymob"),
        default_prior: Literal["uniform", "lognorm"] = "lognorm",
    ) -> SimulationBase:
        """Construct a PymobSimulator from the 
        """

        if pymob_config is None:
            cfg = Config()
            # Configure: The configuration can be overridden in a subclass to override the 
            # configuration
            cls.configure(config=cfg)
        else:
            cfg = pymob_config

        if isinstance(output_directory, str):
            output_directory = pathlib.Path(output_directory)

        cfg.case_study.output = str(output_directory)

        # parse observations
        # obs can be simply subset by selection obs.sel(substance="Exposure-Dime")
        observations = xr.combine_by_coords([
            cls._exposure_data_to_xarray(exposure_data, dim=model.extra_dim),
            cls._survival_data_to_xarray(survival_data)
        ])

        # configure model and likelihood function
        cfg.simulation.model = type(model).__name__
        cfg.inference_numpyro.user_defined_error_model = str(model._likelihood_func_jax.__name__)

        # derive data structure and params from the model instance
        cls._set_data_structure(config=cfg, model=model)
        cls._set_params(config=cfg, model=model, default_prior=default_prior)

        # configure starting values and input
        cfg.simulation.x_in = ["exposure=exposure"]
        cfg.simulation.y0 = [f"{k}={v['y0']}" for k, v in model.state_variables.items() if "y0" in v]

        # create a simulation object
        sim = cls(config=cfg)
        sim.config.create_directory(directory="results", force=True)

        # initialize
        sim.load_modules()
        sim.set_logger()

        sim.initialize(input={"observations": observations, "model": model})
        
        sim.validate()
        sim.dispatch_constructor()


        return sim

    def initialize(self, input=None):
        self.model = input["model"]._rhs_jax
        self.solver_post_processing = input["model"]._solver_post_processing

        super().initialize(input=input)


    @classmethod
    def configure(cls, config: Config):
        """This is normally set in the configuration file passed to a SimulationBase class.
        Since the mempy to pymob converter initializes pymob.SimulationBase from scratch
        (without using a config file), the necessary settings have to be specified here.
        """
        config.case_study.output = "results"

        config.simulation.x_dimension = "time"
        config.simulation.batch_dimension = "id"
        config.simulation.solver_post_processing = None
        config.simulation.unit_time = "day"
        config.simulation.n_reindexed_x = 100
        config.simulation.forward_interpolate_exposure_data = True
        
        config.inference.extra_vars = ["eps", "survivors_before_t"]
        config.inference.n_predictions = 100

        config.jaxsolver.diffrax_solver = "Tsit5"
        config.jaxsolver.rtol = 1e-10
        config.jaxsolver.atol = 1e-12
        config.jaxsolver.throw_exception = True
        config.jaxsolver.pcoeff = 0.3
        config.jaxsolver.icoeff = 0.3
        config.jaxsolver.dcoeff = 0.0
        config.jaxsolver.max_steps = 1000000
        config.jaxsolver.throw_exception = True


        config.inference_numpyro.gaussian_base_distribution = True
        config.inference_numpyro.kernel = "svi"
        config.inference_numpyro.init_strategy = "init_to_median"
        config.inference_numpyro.svi_iterations = 10_000
        config.inference_numpyro.svi_learning_rate = 0.001

    @staticmethod
    def _exposure_data_to_xarray(exposure_data: Dict[str, pd.DataFrame], dim: str):
        """
        TODO: Currently no rect interpolation
        """
        arrays = {}
        for key, df in exposure_data.items():
            # this override is necessary to make all dimensions work out
            df.index.name = "time"
            arrays.update({
                key: df.to_xarray().to_dataarray(dim="id", name=key)
            }) 

        exposure_array = xr.Dataset(arrays).to_array(dim=dim, name="exposure")
        exposure_array = exposure_array.transpose("id", "time", ...)
        return xr.Dataset({"exposure": exposure_array})

    @staticmethod
    def _survival_data_to_xarray(survival_data: pd.DataFrame):
        # TODO: survival name is currently not kept because the raw data is not transferred from the survival
        survival_data.index.name = "time"
        
        survival_array = survival_data.to_xarray().to_dataarray(dim="id", name="survival")
        survival_array = survival_array.transpose("id", "time", ...)
        arrays = {"survival": survival_array}
        return xr.Dataset(arrays)

    @classmethod
    def _set_data_structure(cls, config: Config, model: Model):
        """Takes a dictionary that is specified in the model and uses only keys that
        are fields of the DataVariable config-model"""
        
        state_dict = model.state_variables

        config.data_structure = Datastructure(**{
            key: DataVariable(**{
                k: v for k, v in state_info.items()
                if k in DataVariable.model_fields
            })
            for key, state_info in state_dict.items()
        })


    @classmethod
    def _set_params(cls, config: Config, model: Model, default_prior: str):
        params_info = model.params_info

        if isinstance(model, (
            RED_IT, RED_IT_DA, RED_IT_IA, 
            BufferGUTS_IT, BufferGUTS_IT_CA, BufferGUTS_IT_DA
        )):
            eps = config.jaxsolver.atol * 10
            params_info["eps"] = {'name':'eps', 'initial':eps, 'vary':False}


        for par, param_dict in params_info.items():
            for k, v in model._params_info_defaults.items():
                if k not in param_dict:
                    param_dict.update({k:v})

        param_df = pd.DataFrame(params_info).T
        param_df["param_index"] = param_df.name.apply(lambda x: re.findall(r"\d+", x))
        param_df["param_index"] = param_df.param_index.apply(lambda x: int(x[0])-1 if len(x) == 1 else None)
        param_df["name"] = param_df.name.apply(lambda x: re.sub(r"\d+", "", x).strip("_"))

        for (param_name, ), group in param_df.groupby(["name"]):

            dims = list(dict.fromkeys(group["dims"]))
            dims = tuple([]) if dims == [None] else tuple(dims)

            prior = list(dict.fromkeys(group["prior"]))
            prior = prior[0] if len(prior) == 1 else prior
            
            _min = np.min(np.ma.masked_invalid(group["min"].values.astype(float)))
            _max = np.max(np.ma.masked_invalid(group["max"].values.astype(float)))
            _init = group["initial"].values.astype(float)
            _free = group["vary"].values

            # TODO: allow for parsing one N-D prior from multiple priors
            # TODO: Another choice would be to parse vary=False priors as deterministic
            #       and use a composite prior from a deterministic and a free prior as
            #       the input into the model

            if prior is None:
                if default_prior == "uniform":
                    _loc = _init * np.logical_not(_free) + _min * _free - config.jaxsolver.atol * 10 * np.logical_not(_free)
                    _scale = _init * np.logical_not(_free) + _max * _free + config.jaxsolver.atol * 10 * np.logical_not(_free)
                    _loc = _loc[0] if len(_loc) == 1 else _loc
                    _scale = _scale[0] if len(_scale) == 1 else _scale
                    prior = f"uniform(loc={_loc},scale={_scale})"
                elif default_prior == "lognorm":
                    _s = 3 * _free + config.jaxsolver.atol * 10 * np.logical_not(_free)
                    _init = _init[0] if len(_init) == 1 else _init
                    _s = _s[0] if len(_s) == 1 else _s

                    prior = f"lognorm(scale={_init},s={_s})"
                else:
                    raise ValueError(
                        f"Default prior: '{default_prior}' is not implemented. "+
                        "Use one of 'uniform', 'lognorm' or specify priors for each "+
                        "parameter directly with: "+
                        f"`model.params_dict['prior'] = {default_prior}(...)`"
                    )

                prior = prior.replace(" ", ",")

            # if isinstance(value,float):
            param = Param(
                value=_init,
                free=np.max(_free),
                min=_min,
                max=_max,
                prior=prior,
                dims=dims
            )

            setattr(config.model_parameters, param_name, param)

