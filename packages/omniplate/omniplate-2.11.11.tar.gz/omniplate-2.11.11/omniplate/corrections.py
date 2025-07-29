"""
Functions for performing corrections.

For non-linearity in the OD, for the fluorescence of the media,
and for autofluorescence.
"""

import importlib.resources as import_files
import re

import gaussianprocessderivatives as gp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from nunchaku import Nunchaku
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar
from statsmodels.nonparametric.smoothers_lowess import lowess

import omniplate.admin as admin
import omniplate.clogger as clogger
import omniplate.omerrors as errors
import omniplate.omgenutils as gu
import omniplate.sunder as sunder
from omniplate.correctauto_bayesian import correctauto_bayesian
from omniplate.omfitderiv import preprocess_data, runfitderiv


@clogger.log
def correctOD(
    self,
    figs=True,
    bd=None,
    gp_results=False,
    ODfname=None,
    odmatch_min=0.1,
    max_nunchaku_segments=4,
    correctformedia=True,
    frac=0.33,
    null_dict=None,
    experiments="all",
    experimentincludes=False,
    experimentexcludes=False,
    conditions="all",
    conditionincludes=False,
    conditionexcludes=False,
):
    """
    Correct for the non-linear relationship between OD and cell number.

    Requires a set of dilution data set, with the default being haploid
    yeast growing in glucose.

    An alternative can be loaded from a file - a txt file of two columns
    with OD specified in the first column and the dilution factor specified
    in the second.

    Parameters
    ---------
    figs: boolean, optional
        If True, a plot of the fit to the dilution data is produced.
    bd: dictionary, optional
        Specifies the limits on the hyperparameters for the Gaussian
        process.
        For example, bd= {0: [-1, 4], 2: [2, 6]})
        sets confines the first hyperparameter to be between 1e-1 and 1e^4
        and confines the third hyperparameter between 1e2 and 1e6.
    gp_results: boolean, optional
        If True, show the results of fitting the Gaussian process
    ODfname: string, optional
        The name of the file with the dilution data used to correct OD for
        its non-linear dependence on numbers of cells. If unspecified, data
        for haploid budding yeast growing in glucose is used.
    odmatch_min: float, optional
        An expected minimal value of the OD up to which there is a linear
        scaling of the OD with cell numbers.
    max_nunchaku_segments: int, optional
        The number of segments used by nunchaku when finding the inital
        region where the relationship between the dilution factor and OD
        is linear.
    correctformedia: boolean, optional
        If True (default), correct OD for background levels from media.
    frac: float
        The fraction of the data used for smoothing the media OD via lowess.
        Used to correct OD for the background OD of the media.
    null_dict: dict[str, list[str]], optional
        A dictionary specifying which Null conditions should be used to correct
        other conditions.
        For example:
            null_dict= {"2% glu": ["all"]}
        means that all conditions should be corrected using "Null in 2% glu";
            null_dict= {"2% glu": ["2% glu 0.1 mg/ml", "2% glu 0.2 mg/ml"],
                        "2% gal": ["2% gal 0.1 mg/ml"]}
        means that "2% glu 0.1 mg/ml" and "2% glu 0.2 mg/ml" should be
        corrected with "Null in 2% glu" and that "2% gal 0.1 mg/ml" should
        be corrected with "Null in 2% gal".
    experiments: string or list of strings
        The experiments to include.
    conditions: string or list of strings
        The conditions to include.
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

    Examples
    -------
    >>> p.correctOD()
    >>> p.correctOD(figs= False)
    """
    exps = sunder.getset(
        self,
        experiments,
        experimentincludes,
        experimentexcludes,
        "experiment",
        nonull=True,
    )
    cons = sunder.getset(
        self,
        conditions,
        conditionincludes,
        conditionexcludes,
        "condition",
        nonull=True,
        nomedia=False,
    )
    # fit dilution data
    gc, odmatch = findODcorrection(
        datadirpath=self.datadirpath,
        ODfname=ODfname,
        figs=figs,
        bd=bd,
        gp_results=gp_results,
        odmatch_min=odmatch_min,
        max_nunchaku_segments=max_nunchaku_segments,
    )
    print()
    # correct ODs
    for e in exps:
        for c in cons:
            if correctformedia:
                correctODformedia(
                    self,
                    figs=figs,
                    frac=frac,
                    experiments=e,
                    conditions=c,
                    null_dict=null_dict,
                )
            # correct all wells
            r_data = self.r.query(
                "experiment == @e and condition == @c"
            ).OD.to_numpy()
            gc.batchpredict(r_data)
            # leave small ODs unchanged
            new_r = gc.f
            new_r[r_data < odmatch] = r_data[r_data < odmatch]
            # update r data frame
            self.r.loc[
                (self.r.experiment == e) & (self.r.condition == c),
                "OD",
            ] = new_r
    if self.progress["negativevalues"][e]:
        print(
            "Warning: correcting OD for media has created "
            f"negative values in {e} for"
        )
        # ignore final newline
        print(self.progress["negativevalues"][e][:-1])
    # update s dataframe
    admin.update_s(self)


def findODcorrection(
    datadirpath,
    ODfname,
    figs,
    bd,
    gp_results,
    odmatch_min,
    max_nunchaku_segments,
):
    """
    Determine a function to correct OD.

    Use a Gaussian process to fit serial dilution data to correct for
    non-linearities in the relationship between OD and cell density.

    The data are either loaded from file ODfname or the default
    data for haploid yeast growing in glucose are used.
    """
    print("Fitting dilution data for OD correction for non-linearities.")
    if ODfname is not None:
        try:
            od_df = pd.read_csv(
                str(datadirpath / ODfname),
                sep=None,
                engine="python",
                header=None,
            )
            print(f"Using {ODfname}")
            od_data = od_df.to_numpy()
            od, dilfac = od_data[:, 0], od_data[:, 1]
        except (FileNotFoundError, OSError):
            raise errors.FileNotFound(str(datadirpath / ODfname))
    else:
        print("Using default data.")
        fname = "dilution_data_xiao.tsv"
        od, dilfac = read_default_dilution_data(fname)
    od, dilfac = arrange_into_replicates(od, dilfac)
    # run nunchaku
    X = np.mean(dilfac, 1)
    nc = Nunchaku(X, od.T, estimate_err=True, prior=[-5, 5])
    num_regions, _ = nc.get_number(max_nunchaku_segments)
    bds, _ = nc.get_iboundaries(num_regions)
    # find linear region, which starts from origin
    odmatch_pts = np.mean(od, 1)[bds]
    # pick end point with OD at least equal to odmatch_min
    ipick = np.where(odmatch_pts > odmatch_min)[0][0]
    odmatch = odmatch_pts[ipick]
    dilfacmatch = X[bds[ipick]]
    # process data
    dilfac = dilfac.flatten()[np.argsort(od.flatten())]
    od = np.sort(od.flatten())
    # rescale so that OD and dilfac match
    y = dilfac / dilfacmatch * odmatch
    # set up Gaussian process
    bds = {0: (-4, 4), 1: (-4, 4), 2: (-3, -1)}
    # find bounds
    if bd is not None:
        bds = gu.mergedicts(original=bds, update=bd)
    gc = gp.maternGP(bds, od, y)
    # run Gaussian process
    gc.findhyperparameters(noruns=5, exitearly=True, quiet=True)
    if gp_results:
        gc.results()
    gc.predict(od)
    if figs:
        plt.figure()
        gc.sketch(".")
        plt.plot(odmatch, odmatch, "bs")
        plt.grid(True)
        plt.xlabel("OD")
        plt.ylabel("corrected OD (relative cell numbers)")
        if ODfname:
            plt.title("Fitting " + ODfname)
        else:
            plt.title("for haploid budding yeast in glucose")
        plt.show(block=False)
    return gc, odmatch


def read_default_dilution_data(fname):
    """Import default dilution data."""
    d = import_files.read_text("omniplate", fname)
    res = np.array(re.split(r"\n|\t", d)[:-1]).astype(float)
    od, dilfac = res[::2], res[1::2]
    if fname == "dilution_data_xiao.tsv":
        # missing replicate - use mean of existing ones
        dilfac = np.insert(dilfac, 0, dilfac[0])
        od = np.insert(od, 0, np.mean(od[:2]))
    else:
        raise ValueError("Dilution data unrecognised.")
    return od, dilfac


def arrange_into_replicates(od, dilfac):
    """Rearrange so that data from each replicate is in a column."""
    udilfac, indices, counts = np.unique(
        dilfac, return_inverse=True, return_counts=True
    )
    ucounts = np.unique(counts)
    if len(ucounts) == 1:
        noreps = np.unique(counts)[0]
        dilfac_reps = np.tile(np.atleast_2d(udilfac).T, noreps)
        od_reps = np.array(
            [od[indices == i] for i in range(udilfac.size)]
        ).reshape((udilfac.size, noreps))
        return od_reps, dilfac_reps
    else:
        raise ValueError(
            "There are inconsistent numbers of replicates"
            " in the OD correction data."
        )


@clogger.log
def correctODformedia(
    self,
    figs=False,
    frac=0.33,
    null_dict=None,
    experiments="all",
    experimentincludes=False,
    experimentexcludes=False,
    conditions="all",
    conditionincludes=False,
    conditionexcludes=False,
):
    """
    Correct OD or fluorescence for that of the media.

    Use data from wells marked Null.

    Use lowess to smooth measurements from all Null wells and subtract
    this smoothed time series from the raw data.
    """
    exps = sunder.getset(
        self,
        experiments,
        experimentincludes,
        experimentexcludes,
        "experiment",
        nonull=True,
    )
    cons = sunder.getset(
        self,
        conditions,
        conditionincludes,
        conditionexcludes,
        "condition",
        nonull=True,
        nomedia=False,
    )
    for e in exps:
        for c in cons:
            if c in self.allconditions[e]:
                print(f"{e} - {c}: Correcting OD for the OD of the medium.")
                negvalues = find_Null_and_correct(
                    self,
                    df=self.r,
                    dtype="OD",
                    e=e,
                    c=c,
                    figs=figs,
                    frac=frac,
                    null_dict=null_dict,
                )
                if negvalues is not None:
                    if not self.progress["negativevalues"][e]:
                        self.progress["negativevalues"][e] = negvalues
                    else:
                        self.progress["negativevalues"][e] += negvalues
    # update s dataframe
    admin.update_s(self)


def find_Null_and_correct(self, df, dtype, e, c, figs, frac, null_dict):
    """Find data for Null strain and pass df to perform_media_correction."""
    null_e, null_c = e, c
    if null_dict:
        for medium, conditions in null_dict.items():
            if conditions == ["all"] or null_c in conditions:
                null_c = medium
                break
    null_df = self.r[
        (self.r.experiment == null_e)
        & (self.r.condition == null_c)
        & (self.r.strain == "Null")
    ]
    if null_df.empty:
        print(f"{e}: No Null strain found for {c}.")
    else:
        negvalues = perform_media_correction(
            null_df=null_df,
            df=df,
            dtype=dtype,
            experiment=e,
            condition=c,
            figs=figs,
            frac=frac,
        )
        return negvalues


def perform_media_correction(
    null_df, df, dtype, experiment, condition, figs, frac
):
    """
    Correct data of type dtype for any signal from the media.

    Data for the Null strain is in null_df; data to be ovewritten
    is in df.

    Use lowess to smooth over time the media data from the Null
    wells and subtract the smoothed values from the data.
    """
    t, null_data = null_df["time"].to_numpy(), null_df[dtype].to_numpy()
    if ~np.any(null_data[~np.isnan(null_data)]):
        # all data is NaN
        return
    # find correction
    res = lowess(null_data, t, frac=frac)
    correctionfn = interp1d(
        res[:, 0],
        res[:, 1],
        fill_value=(res[0, 1], res[-1, 1]),
        bounds_error=False,
    )
    if figs:
        plt.figure()
        plt.plot(t, null_data, "ro", res[:, 0], res[:, 1], "b-")
        plt.xlabel("time (hours)")
        plt.title(
            f"{experiment}: media correction for {dtype} in {condition}."
        )
        plt.show(block=False)
    # perform correction to data in df
    choose = (df.experiment == experiment) & (df.condition == condition)
    df.loc[choose, dtype] = df[choose][dtype] - correctionfn(
        df[choose]["time"]
    )
    # check for any negative values
    negvalues = ""
    for s in np.unique(df[choose]["strain"][df[choose][dtype] < 0]):
        if s != "Null":
            wstr = f"\t{dtype}: {s} in {condition} for wells "
            for well in np.unique(
                df[choose][df[choose].strain == s]["well"][
                    df[choose][dtype] < 0
                ]
            ):
                wstr += f"{well}, "
            wstr = wstr[:-2] + "\n"
            negvalues += wstr
    return negvalues


@clogger.log
def correctauto(
    self,
    f="GFP",
    refstrain="WT",
    noprocessors=1,
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
    Correct fluorescence for autofluorescence.

    The correction is made using the fluorescence of an untagged
    reference strain.

    Arguments
    --
    f: string
        The fluorescence measurements, typically either 'mCherry' or
        'GFP'.
    refstrain: string
        The reference strain used to estimate autofluorescence.
    noprocessors: int (default: 1)
        The number of processors to use. Numpy has built-in parallelisation
        and using one processor may be fastest.
    options: None or Dict
       The keys of options are:
            bd: dict (default: None)
                Specifies the bounds on the hyperparameters for the
                Gaussian process applied to the logarithm of the inferred
                fluorescence.
                e.g. {2: (-2, 0)}.
            figs: boolean (default: True)
                If True, use omplot.inspect to show raw data and inferred
                fluorescence per cell.
            noboots: int (default: 10)
                The number of bootstrapped data sets to fit. Larger numbers
                give better estimates of errors.
            flcvfn: str (default: "matern")
                The covariance function to use for the Gaussian process
                that smooths the inferred fluorescence.
            nosamples: int (default: 1000)
                The number of samples taken to estimate errors from the
                Gaussian process used to smooth the inferred fluorescence.
            maxdatapts: int or None (default: None)
                The maximum number of data points to allow in the Gaussian
                process smoothing before subsampling.
            fitderiv_figs: boolean (default: False)
                If True, show the results of the Gaussian process smoothing.
    experiments: string or list of strings
        The experiments to include.
    conditions: string or list of strings
        The conditions to include.
    strains: string or list of strings
        The strains to include.
    experimentincludes: string, optional
        Selects only experiments that include the specified string in
        their name.
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
    >>> p.correctauto('GFP', options = {"figs": False, "bd": {2: (-1,3)}})
    >>> p.correctauto('mCherry', refstrain= 'BY4741')
    """
    f = gu.makelist(f)
    if len(f) != 1:
        print("Error: correctauto uses only one fluorescence measurement.")
        return
    # correct for autofluorescence
    default_options = {
        "bd": None,
        "figs": True,
        "noboots": 10,
        "flcvfn": "matern",
        "nosamples": 1000,
        "maxdatapts": None,
        "fitderiv_figs": False,
    }
    if options is None:
        options = default_options
    else:
        options = default_options | options
    print(f"\nCorrecting autofluorescence using {refstrain} as the reference.")
    correctauto_bayesian(
        self,
        f,
        refstrain,
        noprocessors,
        experiments,
        experimentincludes,
        experimentexcludes,
        conditions,
        conditionincludes,
        conditionexcludes,
        strains,
        strainincludes,
        strainexcludes,
        options,
    )


@clogger.log
def correctauto_l(
    self,
    f=["GFP", "AutoFL"],
    refstrain="WT",
    method="default",
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
    Correct fluorescence for autofluorescence.

    The correction is made using the fluorescence of an untagged
    reference strain.

    The reference strain is used to estimate the autofluorescence via
    either the method of Lichten et al., 2014, where measurements of
    fluorescence at two wavelengths is required, or by using the
    fluorescence of the reference strain interpolated to the OD of the
    strain of interest (Berthoumieux et al., 2013).

    Using two measurements of fluorescence is thought to be more accurate,
    particularly for low fluorescence measurements (Mihalcescu et al.,
    2015).

    Arguments
    --
    f: string or list of strings
        The fluorescence measurements, typically either ['mCherry'] or
        ['GFP', 'AutoFL'].
    refstrain: string
        The reference strain used to estimate autofluorescence.
    method: string
        Either "default" or "bayesian".
    options: None or Dict
        If method = "default", the keys of options are:
            figs: boolean
                If True, display plots showing the fits to the reference
                strain's fluorescence.
            useGPs: boolean
                If True, use Gaussian processes to generate extra samples
                from the replicates. Recommended, particularly if there
                are only a few replicates, but slower.
            flcvfn: str, optional
                The covariance function to use for the Gaussian process
                applied to the logarithm of the fluorescence if useGPs=True.
            bd: dict, optional
                Specifies the bounds on the hyperparameters for the
                Gaussian process applied to the logarithm of the
                fluorescence,
                e.g. {2: (-2, 0)}.
            nosamples: int, optional
                The number of samples to take when using Gaussian processes.
            maxdatapts: int, optional
                The maximum number of data points to use for the Gaussian
                process. Too many data points, over 1500, can be slow.
        with two fluorescence measurements, you can also specify
            frac: float, optional
                The fraction of the data used for smoothing via statmodels'
                lowess.
        If method = "bayesian", the keys of options are:
            figs: boolean
                If True, display plots showing the smoothing of the inferred
                fluorescence.
            flcvfn: str, optional
                The covariance function to use for the Gaussian process
                that smooths the inferred fluorescence.
            bd: dict, optional
                Specifies the bounds on the hyperparameters for the
                Gaussian process applied to the logarithm of the inferred
                fluorescence.
                e.g. {2: (-2, 0)}.
            nosamples: int, optional
                The number of samples to take when using Gaussian processes.
            nosamples_for_bg: int, optional
                The number of samples of the background fluorescence.
            no_minimisation_attempts: int, optional
                The number of attempts to maximise the posterior.
            max_err_to_mean: float, optional
                The maximum value of the error-to-mean ratio used to define
                the low-error corrected fluorescence, prefixed
                with "s_".
    experiments: string or list of strings
        The experiments to include.
    conditions: string or list of strings
        The conditions to include.
    strains: string or list of strings
        The strains to include.
    experimentincludes: string, optional
        Selects only experiments that include the specified string in
        their name.
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
    To correct data with one type of fluorescence measurement, use:

    >>> p.correctauto('GFP', options = {"figs" : False})
    >>> p.correctauto('mCherry', refstrain= 'BY4741')

    To correct data with two types of fluorescence measurement, use:

    >>> p.correctauto(['GFP', 'AutoFL'], options= {"useGPs" : True})
    >>> p.correctauto(['GFP', 'AutoFL'], refstrain= 'WT')
    >>> p.correctauto(['GFP', 'AutoFL'], refstrain= 'WT', method = "bayesian")

    References
    ----------
    S Berthoumieux, H De Jong, G Baptist, C Pinel, C Ranquet, D Ropers,
    J Geiselmann (2013).
    Shared control of gene expression in bacteria by transcription factors
    and global physiology of the cell.
    Mol Syst Biol, 9, 634.

    CA Lichten, R White, IB Clark, PS Swain (2014).
    Unmixing of fluorescence spectra to resolve quantitative time-series
    measurements of gene expression in plate readers.
    BMC Biotech, 14, 1-11.

    I Mihalcescu, MVM Gateau, B Chelli, C Pinel, JL Ravanat (2015).
    Green autofluorescence, a double edged monitoring tool for bacterial
    growth and activity in micro-plates.
    Phys Biol, 12, 066016.
    """
    f = gu.makelist(f)
    exps, cons, strains = sunder.getall(
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
    # correct for autofluorescence
    if method == "default" and len(f) == 2:
        default_options = {
            "figs": True,
            "useGPs": True,
            "flcvfn": "matern",
            "bd": None,
            "nosamples": 1000,
            "maxdatapts": None,
            "frac": 0.33,
        }
    elif method == "default" and len(f) == 1:
        default_options = {
            "figs": True,
            "useGPs": True,
            "flcvfn": "matern",
            "bd": None,
            "nosamples": 1000,
            "maxdatapts": None,
        }
    if options is None:
        options = default_options
    else:
        options = default_options | options
    checking_error = correctauto_checks_l(
        self, f, method, options, exps, cons, strains
    )
    if checking_error:
        print("correctauto: failed checks.")
        return
    else:
        print(
            f"\nCorrecting autofluorescence using {refstrain} as the"
            " reference."
        )
    if len(f) == 2 and method == "default":
        correctauto2(
            self,
            f,
            refstrain,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
            **options,
        )
    elif len(f) == 1 and method == "default":
        correctauto1(
            self,
            f,
            refstrain,
            experiments,
            experimentincludes,
            experimentexcludes,
            conditions,
            conditionincludes,
            conditionexcludes,
            strains,
            strainincludes,
            strainexcludes,
            **options,
        )
    else:
        print(f"f = {f} must be a list of length 1 or 2.")


def correctauto_checks_l(self, f, method, options, exps, cons, strains):
    """Perform checks on arguents and data before running correctauto."""
    # check for negative fluorescence values and gr is available
    error = False
    for e in exps:
        for c in cons:
            if self.progress["negativevalues"][e]:
                for datatype in f:
                    if (
                        datatype in self.progress["negativevalues"][e]
                        and c in self.progress["negativevalues"][e]
                    ):
                        print(
                            f"{e}: The negative values for {datatype}"
                            f" in {c} will generate NaNs."
                        )
            if "useGPs" in options and options["useGPs"]:
                for s in strains:
                    if f"{s} in {c}" in self.allstrainsconditions[e]:
                        hypers, cvfn = gethypers(self, e, c, s, dtype="gr")
                        if hypers is None or cvfn is None:
                            print(
                                f"You first must run getstats for {s} in {c} "
                                f"for {e}."
                            )
                            error = True
    return error


def correctauto1(
    self,
    f,
    refstrain,
    experiments,
    experimentincludes,
    experimentexcludes,
    conditions,
    conditionincludes,
    conditionexcludes,
    strains,
    strainincludes,
    strainexcludes,
    **kwargs,
):
    """
    Correct autofluorescence for measurements with emissions at one wavelength.

    Corrects for autofluorescence for data with emissions measured at one
    wavelength using the fluorescence of the reference strain
    interpolated to the OD of the tagged strain.

    This method in principle corrects too for the fluorescence of the medium,
    although running correctmedia is still recommended.
    """
    print("Using one fluorescence wavelength.")
    print(f"Correcting autofluorescence using {f[0]}.")
    for e in sunder.getset(
        self,
        experiments,
        experimentincludes,
        experimentexcludes,
        "experiment",
        nonull=True,
    ):
        for c in sunder.getset(
            self,
            conditions,
            conditionincludes,
            conditionexcludes,
            "condition",
            nonull=True,
            nomedia=True,
        ):
            # process reference strain
            if c in self.allconditions[e]:
                refstrfn = processref1(
                    self, f, refstrain, kwargs["figs"], e, c
                )
            else:
                refstrfn = None
            if refstrfn is None:
                continue
            # correct strains
            for s in sunder.getset(
                self,
                strains,
                strainincludes,
                strainexcludes,
                "strain",
                nonull=True,
            ):
                if f"{s} in {c}" in self.allstrainsconditions[e]:
                    t, (od, rawfl) = sunder.extractwells(
                        self.r, self.s, e, c, s, ["OD", f[0]]
                    )
                    # no data
                    if od.size == 0 or rawfl.size == 0:
                        print(f"\n-> No data found for {e}: {s} in {c}.\n")
                        continue
                    # correct autofluorescence for each replicate
                    fl = np.transpose(
                        [
                            rawfl[:, i] - refstrfn(od[:, i])
                            for i in range(od.shape[1])
                        ]
                    )
                    fl[fl < 0] = np.nan
                    if kwargs["useGPs"]:
                        flperod = sample_flperod_with_GPs(
                            self,
                            f[0],
                            t,
                            fl,
                            od,
                            kwargs["flcvfn"],
                            kwargs["bd"],
                            kwargs["nosamples"],
                            e,
                            c,
                            s,
                            kwargs["maxdatapts"],
                            kwargs["figs"],
                        )
                    else:
                        # use only the replicates
                        flperod = np.transpose(
                            [fl[:, i] / od[:, i] for i in range(od.shape[1])]
                        )
                        flperod[flperod < 0] = np.nan
                    # check number of NaN
                    nonans = np.count_nonzero(np.isnan(fl))
                    if np.any(nonans):
                        if nonans == fl.size:
                            print(
                                "\n-> Corrected fluorescence is all NaN "
                                f"for {e}: {s} in {c}.\n"
                            )
                        else:
                            print(
                                f"Warning - {e}: {s} in {c}\n"
                                f"{nonans} corrected data points are"
                                " NaN: the corrected fluorescence"
                                " was negative.",
                            )
                        print("---")
                    # store results
                    autofdict = {
                        "experiment": e,
                        "condition": c,
                        "strain": s,
                        "time": t,
                        f"c{f[0]}": np.nanmean(fl, 1),
                        f"c{f[0]}_err": nanstdzeros2nan(fl, 1),
                        f"c{f[0]}perOD": np.nanmean(flperod, 1),
                        f"c{f[0]}perOD_err": nanstdzeros2nan(flperod, 1),
                    }
                    addtodataframes(self, autofdict)


def processref1(self, f, refstrain, figs, experiment, condition):
    """
    Process reference strain for data with one fluorescence measurement.

    Use lowess to smooth the fluorescence of the reference
    strain as a function of OD.

    Parameters
    ----------
    f: string
        The fluorescence to be corrected. For example, ['mCherry'].
    refstrain: string
        The reference strain. For example, 'WT'.
    figs: boolean
        If True, display fits of the reference strain's fluorescence.
    experiment: string
        The experiment to be corrected.
    condition: string
        The condition to be corrected.

    Returns
    -------
    refstrfn: function
        The reference strain's fluorescence as a function of OD.
    """
    e, c = experiment, condition
    print(f"{e}: Processing reference strain {refstrain} for {f[0]} in {c}.")
    _, (od, fl) = sunder.extractwells(
        self.r, self.s, e, c, refstrain, ["OD", f[0]]
    )
    if od.size == 0 or fl.size == 0:
        raise errors.CorrectAuto(f"{e}: {refstrain} not found in {c}.")
    else:
        odf = od.flatten("F")
        flf = fl.flatten("F")
        if ~np.any(flf[~np.isnan(flf)]):
            return None
        # smooth fluorescence as a function of OD using lowess to minimize
        # refstrain's autofluorescence

        def choosefrac(frac):
            res = lowess(flf, odf, frac=frac)
            refstrfn = interp1d(
                res[:, 0],
                res[:, 1],
                fill_value=(res[0, 1], res[-1, 1]),
                bounds_error=False,
            )
            # max gives smoother fits than mean
            return np.max(np.abs(flf - refstrfn(odf)))

        res = minimize_scalar(choosefrac, bounds=(0.1, 0.99), method="bounded")
        # choose the optimum frac
        frac = res.x if res.success else 0.33
        res = lowess(flf, odf, frac=frac)
        refstrfn = interp1d(
            res[:, 0],
            res[:, 1],
            fill_value=(res[0, 1], res[-1, 1]),
            bounds_error=False,
        )
        if figs:
            # plot fit
            plt.figure()
            plt.plot(odf, flf, ".", alpha=0.5)
            plt.plot(res[:, 0], res[:, 1])
            plt.xlabel("OD")
            plt.ylabel(f[0])
            plt.title(e + ": " + refstrain + " for " + c)
            plt.show(block=False)
        return refstrfn


def correctauto2(
    self,
    f,
    refstrain,
    experiments,
    experimentincludes,
    experimentexcludes,
    conditions,
    conditionincludes,
    conditionexcludes,
    strains,
    strainincludes,
    strainexcludes,
    **kwargs,
):
    """
    Correct autofluorescence for measurements with two emission wavelengths.

    Corrects for autofluorescence using spectral unmixing for data with
    measured emissions at two wavelengths.

    References
    ----------
    CA Lichten, R White, IB Clark, PS Swain (2014). Unmixing of fluorescence
    spectra to resolve quantitative time-series measurements of gene
    expression in plate readers.
    BMC Biotech, 14, 1-11.
    """
    # correct for autofluorescence
    print("Using two fluorescence wavelengths.")
    print(f"Correcting autofluorescence using {f[0]} and {f[1]}.")
    for e in sunder.getset(
        self,
        experiments,
        experimentincludes,
        experimentexcludes,
        "experiment",
        nonull=True,
    ):
        for c in sunder.getset(
            self,
            conditions,
            conditionincludes,
            conditionexcludes,
            labeltype="condition",
            nonull=True,
            nomedia=True,
        ):
            # local r data frame for media corrections
            lrdf = self.r[
                (self.r.experiment == e) & (self.r.condition == c)
            ].copy()
            # correct for background fluorescence using Null strain
            print("Correcting for background fluorescence of media.")
            for fl in f:
                negvalues = find_Null_and_correct(
                    self, lrdf, fl, e, c, kwargs["figs"], kwargs["frac"]
                )
                if negvalues:
                    print("Warning: negative values for\n", negvalues)
            # process reference strain
            refqrfn = processref2(
                self, lrdf, f, refstrain, kwargs["figs"], e, c
            )
            if refqrfn is None:
                # too many NaNs in reference strain
                continue
            # process other strains
            for s in sunder.getset(
                self,
                strains,
                strainincludes,
                strainexcludes,
                labeltype="strain",
                nonull=True,
            ):
                if (
                    s != refstrain
                    and f"{s} in {c}" in self.allstrainsconditions[e]
                ):
                    t, (fl_0, fl_1, od) = sunder.extractwells(
                        lrdf, self.s, e, c, s, f.copy() + ["OD"]
                    )
                    if fl_0.size == 0 or fl_1.size == 0:
                        print(f"Warning: No data found for {e}: {s} in {c}.")
                        continue
                    # set negative values to NaNs
                    fl_0[fl_0 < 0] = np.nan
                    fl_1[fl_1 < 0] = np.nan
                    # use mean OD for predicting ra from refstrain
                    odmean = np.nanmean(od, axis=1)
                    # correct autofluorescence
                    ra = refqrfn(odmean)
                    fl = applyautoflcorrection(self, ra, fl_0, fl_1)
                    fl[fl < 0] = np.nan
                    if kwargs["useGPs"]:
                        # sample to estimate errors
                        flperod = sample_flperod_with_GPs(
                            self,
                            f[0],
                            t,
                            fl,
                            od,
                            kwargs["flcvfn"],
                            kwargs["bd"],
                            kwargs["nosamples"],
                            e,
                            c,
                            s,
                            kwargs["maxdatapts"],
                            kwargs["figs"],
                        )
                    else:
                        # use the replicates
                        flperod = fl / od
                        flperod[flperod < 0] = np.nan
                    # store results
                    autofdict = {
                        "experiment": e,
                        "condition": c,
                        "strain": s,
                        "time": t,
                        f"c{f[0]}": np.nanmean(fl, 1),
                        f"c{f[0]}_err": naniqrzeros2nan(fl, 1),
                        f"c{f[0]}perOD_err": naniqrzeros2nan(flperod, 1),
                        f"c{f[0]}perOD": np.nanmean(flperod, 1),
                    }
                    # add to data frames
                    addtodataframes(self, autofdict)
                    print("---")


def processref2(self, lrdf, f, refstrain, figs, experiment, condition):
    """
    Process reference strain for spectral unmixing.

    Requires data with two fluorescence measurements.

    Use lowess to smooth the ratio of emitted fluorescence measurements
    so that the reference strain's data is corrected to zero as best
    as possible.

    Parameters
    ----------
    lrdf: pd.DataFrame
        A copy of the r data frame with fluorescence corrected for media.
    f: list of strings
        The fluorescence measurements. For example, ['GFP', 'AutoFL'].
    refstrain: string
        The reference strain. For example, 'WT'.
    figs: boolean
        If True, display fits of the fluorescence ratios.
    experiment: string
        The experiment to be corrected.
    condition: string
        The condition to be corrected.

    Returns
    -------
    qrfn: function
        The ratio of the two fluorescence values for the reference strain
        as a function of OD.
    """
    e, c = experiment, condition
    print(f"{e}: Processing reference strain {refstrain} for {f[0]} in {c}.")
    # refstrain data
    t, (f0, f1, od) = sunder.extractwells(
        lrdf, self.s, e, c, refstrain, f.copy() + ["OD"]
    )
    if f0.size == 0 or f1.size == 0 or od.size == 0:
        raise errors.CorrectAuto(f"{e}: {refstrain} not found in {c}.")
    else:
        f0[f0 < 0] = np.nan
        f1[f1 < 0] = np.nan
        odf = od.flatten("F")
        odrefmean = np.mean(od, 1)
        qrf = (f1 / f0).flatten("F")
        if np.all(np.isnan(qrf)):
            print(f"{e}: {refstrain} in {c} has too many NaNs.")
            return
        # smooth to minimise autofluorescence in refstrain

        def choosefrac(frac):
            qrfn, _ = find_qrfn(qrf, odf, frac)
            flref = applyautoflcorrection(self, qrfn(odrefmean), f0, f1)
            return np.max(np.abs(flref))

        res = minimize_scalar(choosefrac, bounds=(0.1, 0.99), method="bounded")
        # calculate the relationship between qr and OD
        frac = res.x if res.success else 0.95
        # apply lowess and find qrfn
        qrfn, res = find_qrfn(qrf, odf, frac)
        if figs:
            plt.figure()
            plt.plot(odf, qrf, ".", alpha=0.5)
            plt.plot(res[:, 0], res[:, 1])
            plt.xlabel("OD")
            plt.ylabel(f[1] + "/" + f[0])
            plt.title(e + ": " + refstrain + " in " + c)
            plt.show(block=False)
        # check autofluorescence correction for reference strain
        flref = applyautoflcorrection(self, qrfn(odrefmean), f0, f1)
        flrefperod = flref / od
        # set negative values to NaNs
        flref[flref < 0] = np.nan
        flrefperod[flrefperod < 0] = np.nan
        # store results
        autofdict = {
            "experiment": e,
            "condition": c,
            "strain": refstrain,
            "time": t,
            f"c{f[0]}": np.nanmean(flref, 1),
            f"c{f[0]}perOD": np.nanmean(flrefperod, 1),
            f"c{f[0]}_err": nanstdzeros2nan(flref, 1),
            f"c{f[0]}perOD_err": nanstdzeros2nan(flrefperod, 1),
        }
        addtodataframes(self, autofdict)
        return qrfn


def find_qrfn(qrf, odf, frac):
    """Use lowess and then interpolation to find qrfn."""
    res = lowess(qrf, odf, frac)
    qrfn = interp1d(
        res[:, 0],
        res[:, 1],
        fill_value=(res[0, 1], res[-1, 1]),
        bounds_error=False,
    )
    return qrfn, res


def applyautoflcorrection(self, ra, f0data, f1data):
    """Correct for autofluorescence returning an array of replicates."""
    nr = f0data.shape[1]
    raa = np.reshape(np.tile(ra, nr), (np.size(ra), nr), order="F")
    return (raa * f0data - f1data) / (
        raa - self._gamma * np.ones(np.shape(raa))
    )


def addtodataframes(self, datadict):
    """Added dict of data to s data frame."""
    newdf = pd.DataFrame(datadict)
    key_cols = ["experiment", "condition", "strain", "time"]
    self.s = gu.merge_df_into(self.s, newdf, key_cols)


def nanstdzeros2nan(a, axis=None):
    """Like nanstd but setting zeros to nan."""
    err = np.nanstd(a, axis)
    err[err == 0] = np.nan
    return err


def naniqrzeros2nan(a, axis=None):
    """Interquartile range but setting zeros to nan."""
    iqr = np.nanquantile(a, 0.75, axis) - np.nanquantile(a, 0.25, axis)
    iqr[iqr == 0] = np.nan
    return iqr


def gethypers(self, exp, con, s, dtype="gr"):
    """Find parameters for GP from sc data frame."""
    sdf = self.sc[
        (self.sc.experiment == exp)
        & (self.sc.condition == con)
        & (self.sc.strain == s)
    ]
    if sdf.empty:
        return None, None
    else:
        try:
            cvfn = sdf[f"gp_for_{dtype}"].values[0]
            hypers = [
                sdf[col].values[0]
                for col in sorted(sdf.columns)
                if ("hyper" in col and dtype in col)
            ]
            if np.any(np.isnan(hypers)):
                return None, None
            else:
                return hypers, cvfn
        except KeyError:
            return None, None


def instantiateGP(hypers, cvfn, x, y, maxdatapts):
    """Instantiate a Gaussian process."""
    xa, ya, _, _ = preprocess_data(x, y, merrors=[], maxdatapts=maxdatapts)
    # bounds are irrelevant because parameters are optimal
    go = getattr(gp, cvfn + "GP")(
        {0: (-5, 5), 1: (-4, 4), 2: (-5, 2)}, xa, ya, warnings=False
    )
    go.lth_opt = hypers
    go.success = True
    # make predictions so that samples can be generated
    go.predict(x, derivs=2)
    return go


def sample_ODs_with_GP(
    self, experiment, condition, strain, t, od, nosamples, maxdatapts
):
    """Instantiate Gaussian process for log OD and sample."""
    hypers, cvfn = gethypers(self, experiment, condition, strain, dtype="gr")
    if hypers is None or cvfn is None:
        raise SystemExit(
            f"You first must run getstats for {strain} in {condition} "
            f"for {experiment} unless useGPs=False."
        )
    od[od < 0] = np.nan
    # initialise GP for log ODs
    go = instantiateGP(hypers, cvfn, t, np.log(od), maxdatapts)
    # sample
    lod_samples = go.sample(nosamples)
    return lod_samples


def sample_flperod_with_GPs(
    self,
    flname,
    t,
    fl,
    od,
    flcvfn,
    bd,
    nosamples,
    e,
    c,
    s,
    maxdatapts=None,
    figs=True,
    logs=True,
    negs2nan=True,
):
    """
    Generate samples of fluorescence per OD.

    Smooth and sample fluorescence using a Gaussian process.
    Sample ODs using the Gaussian process generated by getstats.
    """
    if np.any(fl[~np.isnan(fl)]):
        # run GP for fluorescence or log fluorescence
        # omfitderiv deals with NaNs
        if logs:
            fitvar = f"log_{flname}"
        else:
            fitvar = flname
        f_fitderiv = runfitderiv(
            t,
            fl,
            fitvar,
            f"d/dt_{fitvar}",
            experiment=e,
            condition=c,
            strain=s,
            bd=bd,
            cvfn=flcvfn,
            logs=logs,
            negs2nan=negs2nan,
            maxdatapts=maxdatapts,
            plotlocalmax=False,
        )
        if not f_fitderiv.success:
            print(f"-> Fitting fluorescence failed for {e}: {s} in {c}.")
            return np.nan * np.ones((t.size, nosamples))
        # samples
        lod_samples = sample_ODs_with_GP(
            self, e, c, s, t, od, nosamples, maxdatapts
        )
        f_samples = f_fitderiv.fitderivsample(nosamples)[0]
        if logs:
            flperod_samples = np.exp(f_samples - lod_samples)
        else:
            flperod_samples = f_samples * np.exp(-lod_samples)
    else:
        print("No positive data.")
        # all NaN
        flperod_samples = np.nan * np.ones((t.size, nosamples))
    return flperod_samples
