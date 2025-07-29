"""Find and analyse mid-log growth."""

import matplotlib.pylab as plt
import numpy as np
from nunchaku import Nunchaku

import omniplate.admin as admin
import omniplate.clogger as clogger
import omniplate.omgenutils as gu
import omniplate.sunder as sunder


@clogger.log
def getmidlog(
    self,
    stats=["mean", "median", "min", "max"],
    min_duration=1,
    max_num=4,
    prior=[-5, 5],
    use_smoothed=False,
    figs=True,
    experiments="all",
    experimentincludes=False,
    experimentexcludes=False,
    conditions="all",
    conditionincludes=False,
    conditionexcludes=False,
    strains="all",
    strainincludes=False,
    strainexcludes=False,
    **kwargs,
):
    """
    Calculate mid-log statistics.

    Find the region of mid-log growth using nunchaku and calculate a
    statistic for each variable in the s dataframe in this region only.

    The results are added to the sc dataframe.

    Parameters
    ----------
    stats: str, optional
        A list of statistics to be calculated (using pandas).
    min_duration: float, optional
        The expected minimal duration of the midlog phase in units of time.
    max_num: int, optional
        The maximum number of segments of a growth curve.
    prior: list of two floats, optional
        Prior for nunchaku giving the lower and upper bounds on the gradients of the line segments.
    use_smoothed: boolean, optional
        If True, use the smoothed OD found by getstats and its estimated
        errors.
        If False, use the OD of the replicates in different wells.
    figs: boolean, optional
        If True, show nunchaku's results with the mid-log region marked by
        black squares.
    experiments: string or list of strings, optional
        The experiments to include.
    conditions: string or list of strings, optional
        The conditions to include.
    strains: string or list of strings, optional
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
    kwargs: passed to Nunchaku
    """
    admin.check_kwargs(kwargs)
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
        nomedia=True,
    )
    # run Nunchaku to find midlog and take the mean of summary stats
    find_midlog_stats(
        self,
        stats,
        min_duration,
        max_num,
        prior,
        use_smoothed,
        figs,
        exps,
        cons,
        strs,
        **kwargs,
    )


def find_midlog_stats(
    self,
    stats,
    min_duration,
    max_num,
    prior,
    use_smoothed,
    figs,
    exps,
    cons,
    strs,
    **kwargs,
):
    """Find the stat of all variables in the s dataframe for mid-log growth."""
    stats = gu.makelist(stats)
    for e in exps:
        for c in cons:
            for s in strs:
                select = (
                    (self.s.experiment == e)
                    & (self.s.condition == c)
                    & (self.s.strain == s)
                )
                # get OD data
                if use_smoothed:
                    try:
                        Y = self.s[select]["smoothed_log_OD"].values
                        t = self.s[select]["time"].values
                        sd = self.s[select]["smoothed_log_OD_err"].values
                    except KeyError:
                        print(
                            f"Warning: smoothed ODs do not exist for {e}:{s}"
                            " in {c}"
                        )
                        continue
                else:
                    t, od = sunder.extractwells(self.r, self.s, e, c, s, "OD")
                    if np.any(t):
                        od[od < 0] = np.finfo(float).eps
                        Y = np.log(od.T)
                    else:
                        Y = []
                if len(Y):
                    print(f"\nFinding mid-log growth for {e} : {s} in {c}")
                    # run nunchaku on log(OD)
                    if use_smoothed:
                        # use standard deviation from GP
                        err = sd
                    else:
                        # estimate standard deviation from replicates
                        err = None
                    # find time points with no NaN
                    common_i = np.all(~np.isnan(Y), axis=0)
                    try:
                        # run nunchaku
                        nc = Nunchaku(
                            t[common_i],
                            Y[:, common_i],
                            err=err,
                            prior=prior,
                            **kwargs,
                        )
                        num_segs, evidence = nc.get_number(num_range=max_num)
                        bds, bds_std = nc.get_iboundaries(num_segs)
                        res_df = nc.get_info(bds)
                    except OverflowError:
                        print(
                            f"\nError finding midlog data for {e}: {s} in {c}."
                        )
                        continue
                    # pick midlog segment
                    t_st, t_en = pick_midlog(res_df, min_duration)
                    if np.isnan(t_st) or np.isnan(t_en):
                        print(
                            f"\nError finding midlog data for {e}: {s} in {c}."
                        )
                        continue
                    # plot nunchaku's results
                    if figs:
                        nc.plot(res_df, hlmax=None)
                        for tv in [t_st, t_en]:
                            iv = np.argmin((t - tv) ** 2)
                            if use_smoothed:
                                y_med = Y
                            else:
                                y_med = np.median(Y, axis=0)
                            plt.plot(
                                tv,
                                y_med[iv],
                                "ks",
                                markersize=10,
                            )
                        plt.xlabel("time")
                        plt.ylabel("log(OD)")
                        plt.title(f"mid-log growth for {e} : {s} in {c}")
                        plt.show(block=False)
                    # find statistics over mid-log growth
                    add_midlog_stats_to_sc(
                        self, select, e, c, s, t_st, t_en, stats
                    )


def add_midlog_stats_to_sc(self, select, e, c, s, t_st, t_en, stats):
    """Find and store stats from midlog growth."""
    sdf = self.s[select]
    midlog_sdf = sdf[(sdf.time >= t_st) & (sdf.time <= t_en)]
    for stat in stats:
        # store results in dict
        res_dict = {col: np.nan for col in self.s.columns}
        res_dict["experiment"] = e
        res_dict["condition"] = c
        res_dict["strain"] = s
        stat_res = getattr(midlog_sdf, stat)(numeric_only=True)
        for key, value in zip(stat_res.index, stat_res.values):
            res_dict[key] = value
        # add "midlog" to data names
        res_dict = {
            (
                f"{stat}_midlog_{k}"
                if k
                not in [
                    "experiment",
                    "condition",
                    "strain",
                ]
                else k
            ): v
            for k, v in res_dict.items()
        }
        # add to sc dataframe
        admin.add_dict_to_sc(self, res_dict)


def pick_midlog(res_df, min_duration):
    """Find midlog from nunchaku's results dataframe."""
    # midlog had a minimal duration and positive growth rate
    sdf = res_df[(res_df["delta x"] > min_duration) & (res_df.gradient > 0)]
    if sdf.empty:
        return np.nan, np.nan
    else:
        # find mid-log growth - maximal specific growth rate
        ibest = sdf.index[sdf.gradient.argmax()]
        t_st, t_en = sdf["x range"][ibest]
        return t_st, t_en
