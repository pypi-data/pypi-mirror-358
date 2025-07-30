import os
import glob
from functools import partial
from copy import deepcopy
import warnings
import numpy as np
import xarray as xr
from diffrax import Dopri5
from typing import Literal, Optional, List, Dict
import tempfile
import pandas as pd

from pymob import SimulationBase
from pymob.sim.config import DataVariable, Param, string_to_list

from pymob.solvers import JaxSolver
from pymob.solvers.base import rect_interpolation
from pymob.sim.config import ParameterDict
from expyDB.intervention_model import (
    Treatment, Timeseries, select, from_expydb
)

from guts_base import mod
from guts_base.data import (
    to_dataset, reduce_multiindex_to_flat_index, create_artificial_data, 
    create_database_and_import_data_main, design_exposure_scenario
)
from guts_base.sim.report import GutsReport

class GutsBase(SimulationBase):
    """
    Initializes GUTS models from a variety of data sources 

    Initialization follows a couple of steps
    1. check if necessary entries are made in the configuration, otherwise add defaults
    2. read data or take from input
    3. process data (add dimensions, or add indices)
    """
    solver = JaxSolver
    Report = GutsReport

    def initialize(self, input: Dict = None):
        self.ecx_mode: Literal["mean", "draws"] = "mean"

        self.unit_time: Literal["day", "hour", "minute", "second"] = "day"
        if hasattr(self.config.simulation, "unit_time"):
            self.unit_time = self.config.simulation.unit_time  # type: ignore

        self.results_interpolation: Optional[List[float|int]] = [np.nan, np.nan, 100]
        if hasattr(self.config.simulation, "results_interpolation"):
            self.results_interpolation = string_to_list(self.config.simulation.results_interpolation)
            self.results_interpolation[0] = float(self.results_interpolation[0])
            self.results_interpolation[1] = float(self.results_interpolation[1])
            self.results_interpolation[2] = int(self.results_interpolation[2])

        if "observations" in input:
            self.observations = input["observations"]
        else:
            self.observations = self.read_data()
            self.process_data()

        # define tolerance based on the sovler tolerance
        self.observations = self.observations.assign_coords(eps=self.config.jaxsolver.atol * 10)

        self._reindex_time_dim()

        if "survival" in self.observations:
            if "subject_count" not in self.observations.coords:
                self.observations = self.observations.assign_coords(
                    subject_count=("id", self.observations["survival"].isel(time=0).values, )
                )
            self.observations = self._data.prepare_survival_data_for_conditional_binomial(
                observations=self.observations
            )

        if "exposure" in self.observations:
            self.config.data_structure.exposure.observed=False

        # prepare y0 and x_in
        x_in = self.parse_input(input="x_in", reference_data=self.observations, drop_dims=[])
        y0 = self.parse_input(input="y0", reference_data=self.observations, drop_dims=["time"])
        
        # add model components
        if self.config.simulation.forward_interpolate_exposure_data: # type: ignore
            self.model_parameters["x_in"] = rect_interpolation(x_in)
        else:
            self.model_parameters["x_in"] = x_in

        self.model_parameters["y0"] = y0
        self.model_parameters["parameters"] = self.config.model_parameters.value_dict

    def construct_database_statement_from_config(self):
        """returns a statement to be used on a database"""
        substance = self.config.simulation.substance # type:ignore
        exposure_path = self.config.simulation.exposure_path # type:ignore
        return (
            select(Timeseries, Treatment)
            .join(Timeseries)
        ).where(
            Timeseries.variable.in_([substance]),  # type: ignore
            Timeseries.name == {exposure_path}
        )

    def read_data(self):
        # TODO: Update to new INTERVENTION MODEL
        dataset = str(self.config.case_study.observations)
        
        # read from a directory
        if os.path.isdir(os.path.join(self.config.case_study.data_path, dataset)):
            # This looks for xlsx files in the folder and imports them as a database and
            # then proceeds as normal
            files = glob.glob(os.path.join(
                self.config.case_study.data_path, 
                dataset, "*.xlsx"
            ))

            tempdir = tempfile.TemporaryDirectory()
            dataset = self.read_data_from_xlsx(data=files, tempdir=tempdir)

        ext = dataset.split(".")[-1]
        
        if not os.path.exists(dataset):
            dataset = os.path.join(self.data_path, dataset)
            
        if ext == "db":
            statement = self.construct_database_statement_from_config()
            observations = self.read_data_from_expydb(dataset, statement)
            
            # TODO: Integrate interventions in observations dataset

        elif ext == "nc":
            observations = xr.load_dataset(dataset)

        else:
            raise NotImplementedError(
                f"Dataset extension '.{ext}' is not recognized. "+
                "Please use one of '.db' (mysql), '.nc' (netcdf)."
            )
        
        return observations
        
    def read_data_from_xlsx(self, data, tempdir):
        database = os.path.join(tempdir.name, "import.db")

        if hasattr(self.config.simulation, "data_preprocessing"):
            preprocessing = self.config.simulation.data_preprocessing
        else:
            preprocessing = None

        create_database_and_import_data_main(
            datasets_path=data, 
            database_path=database, 
            preprocessing=preprocessing,
            preprocessing_out=os.path.join(tempdir.name, "processed_{filename}")
        )

        return database    


    def read_data_from_expydb(self, database, statement) -> xr.Dataset:

        observations_idata, interventions_idata = from_expydb(
            database=f"sqlite:///{database}",
            statement=statement
        )

        dataset = to_dataset(
            observations_idata, 
            interventions_idata,
            unit_time=self.unit_time
        )
        dataset = reduce_multiindex_to_flat_index(dataset)

        # "Continue here. I want to return multidimensional datasets for data coming "+
        # "from the database. The method can be implemented in any class. Currently I'm looking "+
        # "at guts base"

        filtered_dataset = self.filter_dataset(dataset)

        return filtered_dataset

    def process_data(self):
        """
        Currently these methods, change datasets, indices, etc. in-place.
        This is convenient, but more difficult to re-arragen with other methods
        TODO: Make these methods static if possible

        """
        self._create_indices()
        self._indices_to_dimensions()

    def _create_indices(self):
        """Use if indices should be added to sim.indices and sim.observations"""
        pass

    def _indices_to_dimensions(self):
        pass

    def filter_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        return dataset

    def _reindex_time_dim(self):
        if self.config.simulation.model is not None:
            if "_it" in self.config.simulation.model.lower():
                self.logger.info(msg=(
                    "Redindexing time vector to increase resolution, because model has "+
                    "'_it' (individual tolerance) in it's name"
                ))
                if not hasattr(self.config.simulation, "n_reindexed_x"): 
                    self.config.simulation.n_reindexed_x = 100

                new_time_index = np.unique(np.concatenate([
                    self.coordinates["time"],
                    np.linspace(
                        0, np.max(self.coordinates["time"]), 
                        int(self.config.simulation.n_reindexed_x) # type: ignore
                    )
                ]))
                self.observations = self.observations.reindex(time = new_time_index)
                return

        self.logger.info(msg=(
            "No redindexing of time vector to, because model name did not contain "+
            "'_it' (individual tolerance), or model was not given by name. If an IT model "
            "is calculated without a dense time resolution, the estimates can be biased!"
        ))



    def recompute_posterior(self):
        """This function interpolates the posterior with a given resolution
        posterior_predictions calculate proper survival predictions for the
        posterior.

        It also makes sure that the new interpolation does not include fewer values
        than the original dataset
        """

        if np.isnan(self.results_interpolation[0]):
            self.results_interpolation[0] = float(self.observations["time"].min())
        
        if np.isnan(self.results_interpolation[1]):
            self.results_interpolation[1] = float(self.observations["time"].max())

        # generate high resolution posterior predictions
        if self.results_interpolation is not None:
            time_interpolate = np.linspace(
                start=self.results_interpolation[0],
                stop=self.results_interpolation[1],
                num=self.results_interpolation[2] 
            )

            # combine original coordinates and interpolation. This 
            # a) helps error checking during posterior predictions.
            # b) makes sure that the original time vector is retained, which may be
            #    relevant for the simulation success (e.g. IT model)
            self.observations = self.observations.reindex(
                time=np.unique(np.concatenate(
                    [time_interpolate, self.observations["time"]]
                ))
            )
            
        self.dispatch_constructor()
        _ = self._prob.posterior_predictions(self, self.inferer.idata) # type: ignore
        self.inferer.store_results(output=f"{self.output_path}/numpyro_posterior_interp.nc") # type: ignore
        self.logger.info("Recomputed posterior and storing in `numpyro_posterior_interp.nc`")


    def prior_predictive_checks(self):
        super().prior_predictive_checks()

        self._plot.plot_prior_predictions(self, data_vars=["survival"])

    def posterior_predictive_checks(self):
        super().posterior_predictive_checks()

        self.recompute_posterior()
        # TODO: Include posterior_predictive group once the survival predictions are correctly working
        self._plot.plot_posterior_predictions(self, data_vars=["survival"], groups=["posterior_model_fits"])


    def plot(self, results):
        self._plot.plot_survival(self, results)

    def copy(self):
        with warnings.catch_warnings(action="ignore"):
            sim_copy = type(self)(self.config.copy(deep=True))
            sim_copy.observations = self.observations.copy(deep=True)
            
            # must copy individual parts of the dict due to the on_update method
            model_parameters = {k: deepcopy(v) for k, v in self.model_parameters.items()}
            
            # TODO: Refactor this once the parameterize method is removed.
            sim_copy.parameterize = partial(sim_copy.parameterize, model_parameters=model_parameters)
            sim_copy._model_parameters = ParameterDict(model_parameters, callback=sim_copy._on_params_updated)

            sim_copy.load_modules()
            if hasattr(self, "inferer"):
                sim_copy.inferer = type(self.inferer)(sim_copy)
                # idata uses deepcopy by default
                sim_copy.inferer.idata = self.inferer.idata.copy()
            sim_copy.model = self.model
            sim_copy.solver_post_processing = self.solver_post_processing

        return sim_copy
    
    def predefined_scenarios(self):
        """
        TODO: Fix timescale to observations
        TODO: Incorporate extra exposure patterns (constant, pulse_1day, pulse_2day)
        """
        # get the maximum possible time to provide exposure scenarios that are definitely
        # long enough
        time_max = max(
            self.observations[self.config.simulation.x_dimension].max(), 
            *self.Report.ecx_estimates_times
        )

        # this produces a exposure x_in dataset with only the dimensions ID and TIME
        standard_dimensions = (
            self.config.simulation.batch_dimension,
            self.config.simulation.x_dimension, 
        )

        # get dimensions different from standard dimensions
        exposure_dimension = [
            d for d in self.observations.exposure.dims if d not in 
            standard_dimensions
        ]

        # raise an error if the number of extra dimensions is larger than 1
        if len(exposure_dimension) > 1:
            raise ValueError(
                f"{type(self).__name__} can currently handle one additional dimension for "+
                f"the exposure beside {standard_dimensions}. You provided an exposure "+ 
                f"array with the dimensions: {self.observations.exposure.dims}"
            )
        else:
            exposure_dimension = exposure_dimension[0]

        # iterate over the coordinates of the exposure dimensions to 
        exposure_coordinates = self.observations.exposure[exposure_dimension].values

        scenarios = {}
        for coord in exposure_coordinates:
            concentrations = np.where(coord == exposure_coordinates, 1, 0)

            exposure_dict = {
                coord: dict(start=0.0, end=1.0, concentration=conc)
                for coord, conc in zip(exposure_coordinates, concentrations)
            }

            scenario = design_exposure_scenario(
                exposures=exposure_dict,
                t_max=time_max,
                dt=1/24,
                exposure_dimension=exposure_dimension
            )

            scenarios.update({
                f"1day_exposure_{coord}": scenario
            })

        return scenarios

    def expand_batch_like_coordinate_to_new_dimension(self, coordinate, variables):
        """This method will take an existing coordinate of a dataset that has the same
        coordinate has the batch dimension. It will then re-express the coordinate as a
        separate dimension for the given variables, by duplicating the N-Dimensional array
        times the amount of unique names in the specified coordinate to create an 
        N+1-dimensional array. This array will be filled with zeros along the batch dimension
        where the specified coordinate along the ID dimension coincides with the new (unique)
        coordinate of the new dimension. 

        This process is entirely reversible
        """
        old_coords = self.observations[coordinate]
        batch_dim = self.config.simulation.batch_dimension

        # old coordinate before turning it into a dimension
        obs = self.observations.drop(coordinate)

        # create unique coordinates of the new dimension, preserving the order of the
        # old coordinate
        _, index = np.unique(old_coords, return_index=True)
        coords_new_dim = tuple(np.array(old_coords)[sorted(index)])

        for v in variables:
            # take data variable and extract dimension order
            data_var = obs[v]
            dim_order = data_var.dims

            # expand the dimensionality, then transpose for new dim to be last
            data_var = data_var.expand_dims(coordinate).transpose(..., batch_dim, coordinate)

            # create a dummy dimension to broadcast the new array 
            # dummy_3d = np.ones((1, len(coords_new_dim)))
            dummy_categorical = pd.get_dummies(old_coords).astype(int).values

            # apply automatic broadcasting to increase the size of the new dimension
            # data_var_np1_d = data_var * dummy_3d
            data_var_np1_d = data_var * dummy_categorical

            # annotate coordinates of the new dimension
            data_var_np1_d = data_var_np1_d.assign_coords({
                coordinate: list(coords_new_dim)
            })

            # transpose back to original dimension order with new dim as last dim
            data_var_np1_d = data_var_np1_d.transpose(*dim_order, coordinate)
            obs[v] = data_var_np1_d

        return obs


    def reduce_dimension_to_batch_like_coordinate(self, dimension, variables):
        """This method takes an existing dimension from a N-D array and reduces it to an
        (N-1)-D array, by writing a new coordinate from the reducible dimension in the way
        that the new batch-like coordinate takes the coordinate of the dimension, where
        the data of the N-D array was not zero. After it has been asserted that there is
        only a unique candidate for the each coordinate along the batch dimension 
        (i.e. only one value is non-zero for a given batch-coordinate), the dimension will
        be reduced by summing over the given dimension.

        The method is contingent on having no overlap in batch dimension in the dataset
        """
        pass

    def initialize_from_script(self):
        pass

class GutsSimulationConstantExposure(GutsBase):
    t_max = 10
    def initialize_from_script(self):
        self.config.data_structure.B = DataVariable(dimensions=["time"], observed=False)
        self.config.data_structure.D = DataVariable(dimensions=["time"], observed=False)
        self.config.data_structure.H = DataVariable(dimensions=["time"], observed=False)
        self.config.data_structure.survival = DataVariable(dimensions=["time"], observed=False)

        # y0
        self.config.simulation.y0 = ["D=Array([0])", "H=Array([0])", "survival=Array([1])"]
        self.model_parameters["y0"] = self.parse_input(input="y0", drop_dims=["time"])

        # parameters
        self.config.model_parameters.C_0 = Param(value=10.0, free=False)
        self.config.model_parameters.k_d = Param(value=0.9, free=True)
        self.config.model_parameters.h_b = Param(value=0.00005, free=True)
        self.config.model_parameters.b = Param(value=5.0, free=True)
        self.config.model_parameters.z = Param(value=0.2, free=True)

        self.model_parameters["parameters"] = self.config.model_parameters.value_dict
        self.config.simulation.model = "guts_jax"

        self.coordinates["time"] = np.linspace(0,self.t_max)

    def use_jax_solver(self):
        # =======================
        # Define model and solver
        # =======================

        self.coordinates["time"] = np.array([0,self.t_max])
        self.config.simulation.model = "guts_jax"

        self.solver = JaxSolver

        self.dispatch_constructor(diffrax_solver=Dopri5)

    def use_symbolic_solver(self):
        # =======================
        # Define model and solver
        # =======================

        self.coordinates["time"] = np.array([0,self.t_max])
        self.config.simulation.model = "guts_sympy"

        self.solver = mod.PiecewiseSymbolicSolver

        self.dispatch_constructor(diffrax_solver=Dopri5)


class GutsSimulationVariableExposure(GutsSimulationConstantExposure):
    t_max = 10
    def initialize_from_script(self):
        super().initialize_from_script()
        del self.coordinates["time"]
        exposure = create_artificial_data(
            t_max=self.t_max, dt=1, 
            exposure_paths=["topical"]
        ).squeeze()
        self.observations = exposure

        self.config.data_structure.exposure = DataVariable(dimensions=["time"], observed=True)

        self.config.simulation.x_in = ["exposure=exposure"]
        x_in = self.parse_input(input="x_in", reference_data=exposure, drop_dims=[])
        x_in = rect_interpolation(x_in=x_in, x_dim="time")
        self.model_parameters["x_in"] = x_in

        # parameters
        self.config.model_parameters.remove("C_0")

        self.model_parameters["parameters"] = self.config.model_parameters.value_dict
        self.config.simulation.solver_post_processing = "post_exposure"
        self.config.simulation.model = "guts_variable_exposure"


    def use_jax_solver(self):
        # =======================
        # Define model and solver
        # =======================

        self.model = self._mod.guts_variable_exposure
        self.solver = JaxSolver

        self.dispatch_constructor(diffrax_solver=Dopri5)

    def use_symbolic_solver(self, do_compile=True):
        # =======================
        # Define model and solver
        # =======================

        self.model = self._mod.guts_sympy
        self.solver = self._mod.PiecewiseSymbolicSolver

        self.dispatch_constructor(do_compile=do_compile, output_path=self.output_path)

