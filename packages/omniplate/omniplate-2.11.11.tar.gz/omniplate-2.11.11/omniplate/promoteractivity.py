import numpy as np

import omniplate.corrections as omcorr
import omniplate.sunder as sunder
from omniplate.omfitderiv import runfitderiv


def getpromoteractivity(
    self,
    f="GFP",
    figs=True,
    flcvfn="matern",
    bd=None,
    nosamples=1000,
    maxdatapts=None,
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
    Estimate the promoter activity from the corrected fluorescence.

    A Gaussian process is run on the corrected fluorescence, and
    the results from getstats are used.

    Arguments
    --
    f: string
        The fluorescence measurement, typically either 'GFP or 'mCherry'.
    figs: boolean
        If True, display plots showing the fits to the corrected fluorescence.
    flcvfn: str, optional
        The covariance function to use for the Gaussian process applied
        to the logarithm of the corrected fluorescence.
    bd: dict, optional
        Specifies the bounds on the hyperparameters for the Gaussian
        process applied to the logarithm of the corrected fluorescence,
        e.g. {2: (-2, 0)}.
    nosamples: int, optional
        The number of samples to take when using Gaussian processes.
    maxdatapts: int, optional
        The maximum number of data points to use for the Gaussian process.
        Too many data points, over 1500, can be slow.
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
    """
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
            for s in sunder.getset(
                self,
                strains,
                strainincludes,
                strainexcludes,
                labeltype="strain",
                nonull=True,
            ):
                if f"{s} in {c}" in self.allstrainsconditions[e]:
                    choose = (
                        (self.s.experiment == e)
                        & (self.s.condition == c)
                        & (self.s.strain == s)
                    )
                    if f"c{f}" in self.s.columns:
                        cfl = self.s[choose][f"c{f}"].values
                        cfls = np.array(
                            [
                                cfl,
                                cfl + self.s[choose][f"c{f}_err"].values,
                                cfl - self.s[choose][f"c{f}_err"].values,
                            ]
                        ).T
                        t = self.s[choose].time.values
                        if cfl.size == 0:
                            print(
                                f"Warning: No corrected {f} found for"
                                f" {e}: {s} in {c}."
                            )
                            continue
                        fitvar = f"log_c{f}"
                        derivname = f"d/dt_{fitvar}"
                        f_fitderiv = runfitderiv(
                            t=t,
                            d=cfls,
                            fitvar=fitvar,
                            derivname=derivname,
                            experiment=e,
                            condition=c,
                            strain=s,
                            bd=bd,
                            cvfn=flcvfn,
                            logs=True,
                            maxdatapts=maxdatapts,
                        )
                        if not f_fitderiv.success:
                            print(
                                "\n-> Fitting corrected fluorescence failed"
                                f" for {e}: {s} in {c}.\n"
                            )
                            continue
                        if figs:
                            f_fitderiv.plotfit(
                                e, c, s, fitvar, derivname, logs=True
                            )
                        # samples
                        t_od, od = sunder.extractwells(
                            self.r, self.s, e, c, s, ["OD"]
                        )
                        lod_samples = omcorr.sample_ODs_with_GP(
                            self, e, c, s, t_od, od, nosamples
                        )
                        lfl_samples, lfl_deriv_samples = (
                            f_fitderiv.fitderivsample(nosamples)[:2]
                        )
                        # promoter activity samples
                        pa_samples = lfl_deriv_samples * np.exp(
                            lfl_samples - lod_samples
                        )
                        # store results
                        resdict = {
                            "experiment": e,
                            "condition": c,
                            "strain": s,
                            "time": t,
                            f"promoter_activity_{f}_err": omcorr.naniqrzeros2nan(
                                pa_samples, 1
                            ),
                            f"promoter_activity_{f}": np.nanmean(
                                pa_samples, 1
                            ),
                        }
                        # add to data frames
                        omcorr.addtodataframes(
                            self, resdict, "promoter_activity_{f}"
                        )
                else:
                    print(
                        "No corrected fluorescence found for "
                        f"{e}: {s} in {c}."
                    )
