from functools import partial
import numpy as np
import jax
import jax.numpy as jnp
import numpyro
from numpyro.infer import Predictive
from typing import Literal


maximum = jnp.frompyfunc(jnp.maximum, nin=2, nout=1, identity=None) # type: ignore


@jax.jit
def ffill_na(x, mask):
    """Forward-fill nan values in x. If a mask is provided, assume 

    Parameters
    ----------
    x : _type_
        _description_
    mask : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if mask is None:
        mask = jnp.logical_not(jnp.isnan(x))
    idx = jnp.where(mask,jnp.arange(mask.shape[1]),0)
    idx_ = maximum.accumulate(jnp.array(idx), axis=1).astype(int)
    return x[jnp.arange(idx.shape[0])[:,None], idx_]


def conditional_survival_from_hazard(x, mask):
    """Calculates the conditional survival from cumulative hazard values. 
    This equation is used when survival is repeatedly observed over time and

    Parameters
    ----------
    x : np.ndarray[I,T, float]
        A 2-dimensional I x T array of cumulative hazards defined as H = -ln(S).
        I is the batch dimension and T is the time dimension

    mask : np.ndarray[I,T, bool]
        A 2-dimensional array of the same shape as x, taking True if the survival
        was observed for the given index (i,t) and taking False if survival was
        not observed for the given index (i,t).
    
    Returns
    -------
    out : np.ndarray[I,T, float]
        A matrix with conditional probabilities and nans in place where the 
        mask has nans. Output has the same shape as input.

    Example
    -------
    Calculation example from survival probabilities to conditional survival
    probabilities given some masked values.
    
    >>> S_i = np.array([
    >>>     [1.  , 0.75, 0.1 , 0.05, 0.01, 0.  ],
    >>>     [1.  , 0.75, 0.1 , 0.05, 0.01, 0.  ],
    >>>     [1.  , 0.75, 0.1 , 0.05, 0.01, 0.  ],
    >>>     [1.  , 0.75, 0.1 , 0.05, 0.01, 0.  ],
    >>>     [1.  , 0.75, 0.1 , 0.05, 0.01, 0.  ],
    >>> ])

    >>> mask_obs = np.array([
    >>>     [ True,  True,  True,  True,  True,  True],
    >>>     [ True, False,  True,  True,  True,  True],
    >>>     [ True, False, False,  True,  True,  True],
    >>>     [ True,  True, False,  True,  True,  True],
    >>>     [ True, False,  True, False,  True,  True],
    >>> ])

    >>> conditional_survival_from_hazard(-jnp.log(S_i), mask_obs)
    array([
       [1.0  0.75  0.133  0.5     0.2  0.0]
       [1.0   nan  0.1    0.5     0.2  0.0]
       [1.0   nan  nan    0.05    0.2  0.0]
       [1.0  0.75  nan    0.0667  0.2  0.0]
       [1.0   nan  0.1    nan     0.1  0.0]
    ])
    """

    # Append zeros (hazard) to the beginning of the array (this aligns with the
    # safe assumption that before the zeroth observation S(t=-1) = 1.0)
    x_ = jnp.column_stack([jnp.zeros_like(x[:, 0]), x])

    # also mask needs to be expanded accordingly
    mask_ = jnp.column_stack([jnp.ones_like(mask[:, 0]), mask])

    # fill NaNs with forward
    x_filled = ffill_na(x_, mask_)

    # calculate the conditional survival.
    conditional_survival = jnp.exp(x_filled[:, :-1] - (x_[:, 1:]))

    # add nans and return
    return jnp.where(
        mask, conditional_survival, jnp.nan
    )


def conditional_survival_hazard_error_model(theta, simulation_results, observations, indices, masks, make_predictions):
    """Computes the likelihood of observing K survivors at time t given that
    N survivors were alive at the previous observation t-1

    This is achieved by using the Cumulative hazard directly in the calculation
    of the conditional survival probability. Note that this equation can easily
    be adapted to compute the conditional lethality probability.

    $$\\Pr(t < T~|~t_0 < T) = \\frac{e^{-H(t)}}{e^{-H(t_0)}} = e^{-H(t) - (- H(t_0))} = e^{-H(t) + H(t_0)} = e^{-(H(t) - H(t_0))} = e^{H(t_0) - H(t)}$$

    Example
    -------

                          t0    t1   t2     t3  tinf 
    observations          10     8    5      2     0
    Pr(T > t)            1.0   0.8  0.5    0.2   0.0
    Pr(T > t | T > t-1) (1.0)  0.8  0.625  0.4   0.0


    If the experiment ends before the last organism has died, these information
    have to be included in he computation of the likelihood. For multinomial
    distributions this is done by computing the remaining (ubobserved) lethality
    until the end of the experiment, whihc is just the inverse of the number of
    survivors at the end of the experiment. Therefore, for conditional survival 
    the information about the number of alive organisms
    at the end of the experiment is contained in the last observation.      

    We compute an additional interval until the start of the experiment in order
    to align the results with the observations (which include t=0). Otherwise
    we would only compute T-1 intervals if we have T observations (including t=0).
    """

    H = simulation_results["H"]
    n_surv = observations["survivors_before_t"]
    S_mask = masks["survival"]
    obs_survival = observations["survival"]
    S_conditional = conditional_survival_from_hazard(H, S_mask)

    if make_predictions:
        obs_survival = None

    ID, T = S_mask.shape

    with numpyro.plate("time", size=T):
        with numpyro.plate("id", size=ID):
            numpyro.sample(
                "survival_obs", numpyro.distributions.Binomial(
                    probs=S_conditional, 
                    total_count=n_surv
                ).mask(S_mask), 
                obs=obs_survival
            )


def conditional_survival_error_model(theta, simulation_results, observations, indices, masks, make_predictions):
    """Note that the conditional survival error model will not work to generate
    posterior predictions for observational uncertainty out of the box
    
    This model can be used for SD and IT models, but for SD models, the 
    conditional_survival_hazard_model is preferrable.
    """
    # error model
    EPS = observations["eps"]
    S = jnp.clip(simulation_results["survival"], EPS, 1 - EPS) 

    S_mask = masks["survival"]
    n_surv = observations["survivors_before_t"]
    obs_survival = observations["survival"]
    
    S_ = ffill_na(S, S_mask)
    S_cond_na = S_[:, 1:] / S_[:, :-1]
    S_cond_na_ = jnp.column_stack([jnp.ones_like(S[:,[0]]), S_cond_na])
    S_cond_na__ = jnp.clip(S_cond_na_, EPS, 1 - EPS) 

    if make_predictions:
        obs_survival = None

    ID, T = S_mask.shape

    with numpyro.plate("time", size=T):
        with numpyro.plate("id", size=ID):
            numpyro.sample(
                "survival_obs", numpyro.distributions.Binomial(
                    probs=S_cond_na__, 
                    total_count=n_surv
                ).mask(S_mask), 
                obs=obs_survival
            )


def conditional_lethality_error_model(theta, simulation_results, observations, indices, masks, make_predictions):
    raise NotImplementedError(
        "Conditional lethality error model needs to forward fill survival " +
        "probabilities for missing (observation) values"
        ""
    )

    # error model
    EPS = observations["eps"]
    S = jnp.clip(simulation_results["S"], EPS, 1 - EPS) 

    # TODO work on this
    # Conditional survival may be wrong, but also maybe the data generation
    # fct may be wrong
    # a test showed that it looks preddy darn good. I guess this is because
    # it is the conditional probability to survive. Not the conditional
    # probability to die.
    S_cond = (S[:, :-1] - S[:, 1:]) / S[:, :-1]
    S_cond_ = jnp.column_stack([jnp.zeros_like(S[:,[0]]), S_cond])
    S_cond__ = jnp.clip(S_cond_, EPS, 1 - EPS) 
    
    n_surv = observations["survivors_before_t"]
    L_mask = masks["L"]
    L = observations["L"]

    if make_predictions:
        L = None

    numpyro.sample(
        "L_obs", numpyro.distributions.Binomial(
            probs=S_cond__, 
            total_count=n_surv
        ).mask(L_mask), 
        obs=L
    )


def multinomial_error_model(theta, simulation_results, observations, indices, masks, make_predictions):
    raise NotImplementedError(
        "Multinomial error model needs to forward fill survival " +
        "probabilities for missing (observation) values"
        ""
    )
    # error model
    EPS = observations["eps"]
    # TODO This should not be done before calculating the difference
    S = jnp.clip(simulation_results["S"], EPS, 1 - EPS) 

    # TODO work on this
    # This is not working with replicates
    s_probs = S[:, :-1] - S[:, 1:]
    s_probs_ = jnp.column_stack([jnp.zeros_like(S[:,[0]]), s_probs])
    
    L_mask = masks["L"]
    L = observations["L"]
    N = observations["n_subjects"]
    # N_ = jnp.broadcast_to(jnp.expand_dims(N, 1), L.shape)

    if make_predictions:
        L = None

    ID, T = L_mask.shape

    with numpyro.plate("id", ID):
        numpyro.sample(
            "L_obs", numpyro.distributions.Multinomial(
                probs=s_probs_, 
                total_count=N
            ).mask(L_mask), 
            obs=L
        )

def survival_predictions(
    probs, n_trials, 
    eps: float = 0.0,
    seed=1, 
    mode: Literal["survival", "lethality", "deaths"] = "survival"
):
    """Generate predictions for survival based on a multinomial survival distribution

    Parameters
    ----------
    probs : ArrayLike
        2D Array denoting the multinomial probabilities of deaths for each time interval 
        per experiment 
        dims=(experiment, time)
    n_trials : ArrayLike
        1D Array denoting the number of organisms at the beginning in each experiment
        dims = (experiment,)
    seed : int, optional
        Seed for the random number generator, by default 1
    mode : str, optional
        How should the random draws be returned? 
        - survival: Decreasing from n_trials to 0
        - lethality: Increasing from 0 to n_trials
        - deaths: Between 0 and n_trials in each interval. Summing to n_trials
    """

    def survival_to_death_probs(pr_survival):
        # truncate here, because numeric errors below the solver tolerance can
        # lead to negative values in the difference. This needs to be cured here
        pr_survival_ = np.trunc(pr_survival / eps) * eps
        pr_death = pr_survival_[:-1] - pr_survival_[1:]

        pr_death = np.concatenate([
            # concatenate a zero at the beginning in order to "simulate" no
            # deaths at T = 0
            jnp.zeros((1,)),
            # Delta S
            pr_death,
            # The remaining mortility as T -> infinity 
            jnp.ones((1,))-pr_death.sum()
        ])

        # make sure the vector is not zero or 1 (this is always problematic for 
        # probabilities) and make sure the vector sums to 1
        pr_death = np.clip(pr_death, eps, 1-eps)
        pr_death = pr_death / pr_death.sum()
        return pr_death

    rng = np.random.default_rng(seed)
    deaths = jnp.array(list(map(
        lambda n, pr_survival: rng.multinomial(
            n=n, pvals=survival_to_death_probs(pr_survival)
        ), 
        n_trials, 
        probs
    )))

    # remove the last observations to trim off the simulated unobserved mortality
    deaths = deaths[:, :-1]

    if mode == "deaths":
        return deaths
    elif mode == "lethality":
        return deaths.cumsum(axis=1)
    elif mode == "survival":
        return np.expand_dims(n_trials, axis=1) - deaths.cumsum(axis=1)
    else:
        raise NotImplementedError(
            f"Mode {mode} is not implemented."+
            "Use one of 'survival', 'lethality', or 'deaths'."
        )
    
def posterior_predictions(sim, idata, seed=None):
    """Make posterior predictions for survival data"""
    if seed is None:
        seed = sim.config.simulation.seed

    n = idata.posterior.dims["draw"]
    c = idata.posterior.dims["chain"]

    key = jax.random.PRNGKey(seed)

    obs, masks = sim.inferer.observation_parser()

    model_kwargs = sim.inferer.preprocessing(obs=obs, masks=masks)

    # prepare model
    model = partial(
        sim.inferer.inference_model, 
        solver=sim.inferer.evaluator, 
        **model_kwargs
    )    

    posterior_samples = {
        k: np.array(v["data"]) for k, v 
        in idata.unconstrained_posterior.to_dict()["data_vars"].items()
    }

    predictive = Predictive(
        model, posterior_samples=posterior_samples,
        num_samples=n, batch_ndims=2
    )

    samples = predictive(key)

    chains = []
    for i in range(c):
        # TODO: Switch to vmap and jit, but it did not work, so if you do it TEST IT!!!!!!!
        predictions = list(map(
            partial(
                survival_predictions,
                n_trials=obs["survival"][:, 0].astype(int),
                eps=obs["eps"],
                seed=seed,
                mode="survival",
            ),
            samples["survival"][i]
        ))
        chains.append(predictions)

    new_idata = sim.inferer.to_arviz_idata(
        posterior=samples,
        posterior_predictive={"survival_obs": np.array(chains)},
        n_draws=n,
        n_chains=c
    )

    # update chain names in case they were subselected (clustering)
    # new_idata = new_idata.assign_coords({"chain": idata.posterior.chain.values})
    new_idata = new_idata.assign_coords({"chain": idata.posterior.chain.values})

    # assert the new posterior matches the old posterior
    tol = sim.config.jaxsolver.atol * 100
    abs_diff_posterior = np.abs(idata.posterior - new_idata.posterior)
    np.testing.assert_array_less(abs_diff_posterior.mean().to_array(), tol)

    fit_tol = tol * sim.coordinates["time"].max()
    abs_diff_fits = np.abs(new_idata.posterior_model_fits - idata.posterior_model_fits)
    np.testing.assert_array_less(abs_diff_fits.mean().to_array(), fit_tol)

    idata.posterior_model_fits = new_idata.posterior_model_fits
    idata.posterior_predictive = new_idata.posterior_predictive

    return idata