import os
import itertools as it
from typing import List
import pandas as pd

from pymob import SimulationBase
from pymob.sim.report import Report, reporting

from guts_base.plot import plot_survival_multipanel
from guts_base.sim.ecx import ECxEstimator

class GutsReport(Report):
    ecx_estimates_times: List = [1, 2, 4, 10]
    ecx_estimates_x: List = [0.1, 0.25, 0.5, 0.75, 0.9]

    def additional_reports(self, sim: "SimulationBase"):
        super().additional_reports(sim=sim)
        self.model_fits(sim)
        self.LCx_estimates(sim)

    @reporting
    def model_fits(self, sim: SimulationBase):
        self._write("### Survival model fits")
        
        out_mp = plot_survival_multipanel(
            sim=sim,
            results=sim.inferer.idata.posterior_model_fits,
            ncols=6,
        )

        lab = self._label.format(placeholder='survival_fits')
        self._write(f"![Surival model fits.\label{{{lab}}}]({os.path.basename(out_mp)})")

        return out_mp


    @reporting
    def LCx_estimates(self, sim):
        X = self.ecx_estimates_x
        T = self.ecx_estimates_times
        P = sim.predefined_scenarios()

        estimates = pd.DataFrame(
            it.product(X, T, P.keys()), 
            columns=["x", "time", "scenario"]
        )

        ecx = []

        for i, row in estimates.iterrows():
            ecx_estimator = ECxEstimator(
                sim=sim,
                effect="survival", 
                x=row.x,
                id=None, 
                time=row.time, 
                x_in=P[row.scenario], 
            )
            
            ecx_estimator.estimate(
                mode=sim.ecx_mode,
                draws=250,
                show_plot=False
            )

            ecx.append(ecx_estimator.results)

        results = pd.DataFrame(ecx)
        estimates[results.columns] = results

        out = self._write_table(tab=estimates, label_insert="$LC_x$ estimates")
        
        return out
