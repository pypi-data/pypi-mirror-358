"""Function to estimate growth rate."""

import concurrent.futures
import os

import numpy as np

import omniplate.admin as admin
import omniplate.clogger as clogger
import omniplate.omplot as omplot
import omniplate.sunder as sunder
from omniplate.omfitderiv import runfitderiv


@clogger.log
def getstats(
    self,
    dtype="OD",
    noprocessors=1,
    figs=True,
    options=None,
    experiments="all",
    experimentincludes=False,
    experimentexcludes=False,
    conditions="all",
    conditionincludes=False,
    conditionexcludes=False,
    strains="all",
    strainincludes=False,
    strainexcludes=False,
):
    """
    Smooth data, find its derivatives, and calculate summary statistics.

    The first and second time derivatives are found, typically of OD,
    using a Gaussian process (Swain et al., 2016).

    The derivatives are stored in the .s dataframe;
    summary statistics are stored in the .sc dataframe.

    Parameters
    ----------
    dtype: string, optional
        The type of data - 'OD', 'GFP', 'cGFPperOD', or 'cGFP' - for
        which the derivatives are to be found. The data must exist in the
        .r or .s dataframes.
    noprocessors: int
        Default is 1.
    figs: boolean, optional
        If True, plot both the fits and inferred derivative.
    options: None or dict
        The possible keys are:
            bd: dict
                The bounds on the hyperparameters for the Gaussian process.
                For example, bd= {1: [-2,0])} fixes the bounds on the
                hyperparameter controlling flexibility to be 1e-2 and 1e0.
                The default for a Matern covariance function
                is {0: (-5,5), 1: (-4,4), 2: (-5,2)},
                where the first element controls amplitude, the second controls
                flexibility, and the third determines the magnitude of the
                measurement error.
            cvfn: string
                The covariance function used in the Gaussian process, either
                'matern' or 'sqexp' or 'nn'.
            empirical_errors: boolean
                If True, measurement errors are empirically estimated from the
                variance across replicates at each time point and so vary with
                time.
                If False, the magnitude of the measurement error is fit from
                the data assuming that this magnitude is the same at all time
                points.
            noruns: integer
                The number of attempts made for each fit. Each attempt is made
                with random initial estimates of the hyperparameters within
                their bounds.
            exitearly: boolean
                If True, stop at the first successful fit.
                If False, use the best fit from all successful fits.
            noinits: integer
                The number of random attempts to find a good initial condition
                before running the optimization.
            nosamples: integer
                The number of samples used to calculate errors in statistics by
                bootstrapping.
            logs: boolean
                If True, find the derivative of the log of the data and should be
                True to determine the specific growth rate when dtype= 'OD'.
            findareas: boolean
                If True, find the area under the plot of gr vs OD and the area
                under the plot of OD vs time. Setting to True can make getstats
                slow.
            plotlocalmax: boolean
                If True, mark the highest local maxima found, which is used to
                calculate statistics, on any plots.
            printpeakproperties: boolean
                If True, show properties of any local peaks that have found by
                scipy's find_peaks. Additional properties can be specified as
                kwargs and are passed to find_peaks.
            maxdatapts: integer
                If set, sufficiently large data sets with multiple replicates
                will be subsampled at each time point, randomly picking a
                smaller number of replicates, to reduce the number of data
                points and so run times.
            Parameters for scipy's find_peaks can be include too.
    experiments: string or list of strings
        The experiments to include.
    conditions: string or list of strings
        The conditions to include.
    strains: string or list of strings
        The strains to include.
    experimentincludes: string, optional
        Selects only experiments that include the specified string in their
        name.
    experimentexcludes: string, optional
        Ignores experiments that include the specified string in their
        name.
    conditionincludes: string, optional
        Selects only conditions that include the specified string in their
        name.
    conditionexcludes: string, optional
        Ignores conditions that include the specified string in their name.
    strainincludes: string, optional
        Selects only strains that include the specified string in their
        name.
    strainexcludes: string, optional
        Ignores strains that include the specified string in their name.

    Examples
    --------
    >>> p.getstats()
    >>> p.getstats(conditionincludes= "Gal", noprocessors=8)
    >>> p.getstats(options = {"noruns": 10, "exitearly": False})

    If the fits are poor, often changing the bounds on the hyperparameter
    for the measurement error helps:

    >>> p.getstats(options = {"bd": {2: (-3,0)}})

    References
    ----------
    PS Swain, K Stevenson, A Leary, LF Montano-Gutierrez, IB Clark,
    J Vogel, T Pilizota. (2016). Inferring time derivatives including cell
    growth rates using Gaussian processes. Nat Commun, 7, 1-8.
    """
    default_options = {
        "bd": None,
        "cvfn": "matern",
        "empirical_errors": False,
        "noruns": 10,
        "exitearly": True,
        "noinits": 100,
        "nosamples": 100,
        "logs": True,
        "findareas": False,
        "plotlocalmax": True,
        "printpeakproperties": False,
        "maxdatapts": None,
        "linalgmax": 5,
    }
    if options is None:
        options = default_options
    else:
        options = default_options | options
    # variable to be fit
    if options["logs"]:
        fitvar = f"log_{dtype}"
    else:
        fitvar = dtype
    # name of derivative of fit variable
    if fitvar == "log_OD":
        derivname = "gr"
    else:
        derivname = f"d/dt_{fitvar}"
    exps, cons, strs = sunder.getall(
        self,
        experiments,
        experimentincludes,
        experimentexcludes,
        conditions,
        conditionincludes,
        conditionexcludes,
        strains,
        strainincludes,
        strainexcludes,
        nonull=True,
    )
    getstats_many(
        self,
        noprocessors,
        figs,
        exps,
        cons,
        strs,
        dtype,
        fitvar,
        derivname,
        options,
    )


def getstats_many(
    self,
    noprocessors,
    figs,
    exps,
    cons,
    strs,
    dtype,
    fitvar,
    derivname,
    options,
):
    """Parallelize getstats."""
    params = {
        "fitvar": fitvar,
        "derivname": derivname,
        "fitderiv_params": options,
    }
    if noprocessors > 1:
        # multiple processors
        max_workers = np.min([os.cpu_count() - 1, noprocessors])
        print(f"Using {max_workers} processors out of {os.cpu_count()}.")
        results = run_many(self, exps, cons, strs, dtype, params, max_workers)
        # process results
        print("---")
        for e, c, s, f_fitderiv in results:
            print(f"Results for {e}: {s} in {c}")
            process_results_from_fitderiv(
                self, f_fitderiv, params, figs, e, c, s
            )

    else:
        # single processor
        for e in exps:
            for c in cons:
                for s in strs:
                    res = getdata_one(self, dtype, e, c, s)
                    if res is not None:
                        t, d = res
                        f_fitderiv = getstats_one(e, c, s, t, d, params)[-1]
                        process_results_from_fitderiv(
                            self, f_fitderiv, params, figs, e, c, s
                        )
        # print information on GP's hyperparameters
    f_fitderiv.gp.info


def run_many(self, exps, cons, strs, dtype, params, max_workers):
    """Submit getstats_one to multiple processors and return results."""
    results = []
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=max_workers
    ) as executor:
        # create and submit all tasks
        futures = []
        for e in exps:
            for c in cons:
                for s in strs:
                    res = getdata_one(self, dtype, e, c, s)
                    if res is not None:
                        t, d = res
                        futures.append(
                            executor.submit(
                                getstats_one, e, c, s, t, d, params
                            )
                        )
        # collect results as they complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result is not None:
                    results.append(result)
            except Exception as exc:
                print(f"One processor generated an exception: {exc}")
    return results


def process_results_from_fitderiv(self, f_fitderiv, params, figs, e, c, s):
    """Add results from fitderiv to dataframes and plot."""
    # add time series to s dataframe
    admin.add_to_s(self, params["derivname"], f_fitderiv.df_for_s)
    # create or add summary stats to sc dataframe
    admin.add_dict_to_sc(self, f_fitderiv.dict_for_sc)
    if figs:
        f_fitderiv.plotfit(
            experiment=e,
            condition=c,
            strain=s,
            fitvar=params["fitvar"],
            derivname=params["derivname"],
            logs=params["fitderiv_params"]["logs"],
        )
    f_fitderiv.gp.results()
    print("---")


def getdata_one(self, dtype, e, c, s):
    """Get data for one condition and strain."""
    if f"{s} in {c}" not in self.allstrainsconditions[e]:
        return
    esc_name = f"{e}: {s} in {c}"
    if dtype in self.r.columns:
        # raw data
        t, d = sunder.extractwells(self.r, self.s, e, c, s, dtype)
    elif dtype in self.s.columns:
        # processed data
        df = self.s.query(
            "experiment == @e and condition == @c and strain == @s"
        )
        # add columns plus and minus err
        df = omplot.augmentdf(df, dtype)[[dtype, "augtype", "time"]]
        piv_df = df.pivot(index="time", columns="augtype", values=dtype)
        # convert to array for fitderiv
        d = piv_df.values
        t = piv_df.index.to_numpy()
        numberofnans = np.count_nonzero(np.isnan(d))
        if np.any(numberofnans):
            print(f"\nWarning: {numberofnans} NaNs in data")
    else:
        print(f"\n-> {dtype} not recognised for {esc_name}.\n")
        return
    # check data exists
    if d.size == 0:
        if esc_name.split(":")[1].strip() in self.allstrainsconditions[e]:
            print(f"\n-> No data found for {dtype} for {esc_name}.\n")
        return
    return t, d


def getstats_one(e, c, s, t, d, params):
    """Process a single getstats by running fitderiv."""
    f_fitderiv = runfitderiv(
        t=t,
        d=d,
        fitvar=params["fitvar"],
        derivname=params["derivname"],
        experiment=e,
        condition=c,
        strain=s,
        **params["fitderiv_params"],
    )
    return (e, c, s, f_fitderiv)
