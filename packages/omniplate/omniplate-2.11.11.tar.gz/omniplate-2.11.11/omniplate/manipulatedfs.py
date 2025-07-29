import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import omniplate.admin as admin
import omniplate.clogger as clogger
import omniplate.omerrors as errors
import omniplate.sunder as sunder


@clogger.log
def rename_combined(self, newname):
    """Rename a combined experiment."""
    if self.allexperiments == [self.combined]:
        for df in [self.r, self.s, self.sc]:
            df["experiment"] = df.experiment.replace({self.combined: newname})
        self.allexperiments = [newname]
        self.combined = newname


def search(self, listofstrings):
    """
    Search self.allstrainsconditions.

    Example
    -------
    >>> p.search(["HXT6", "Glu"])
    """
    if isinstance(listofstrings, str):
        listofstrings = [listofstrings]
    for e in self.allstrainsconditions:
        for sc in self.allstrainsconditions[e]:
            hits = [q for q in listofstrings if q in sc]
            if len(hits) == len(listofstrings):
                print(f"{e}: {sc}")


@clogger.log
def rename(self, translatedict, regex=True, **kwargs):
    """
    Rename strains or conditions.

    Uses a dictionary to replace all occurrences of a strain or a condition
    with an alternative.

    Note that instances of self.progress will not be updated.

    Parameters
    ----------
    translatedict: dictionary
        A dictionary of old name - new name pairs
    regex: boolean (optional)
        Value of regex to pass to panda's replace.
    kwargs: keyword arguments
        Passed to panda's replace.

    Example
    -------
    >>> p.rename({'77.WT' : 'WT', '409.Hxt4' : 'Hxt4'})
    """
    # check for duplicates
    if (
        len(translatedict.values())
        != np.unique(list(translatedict.values())).size
    ):
        print("Warning: new names are not unique.")
        # replace in dataframes
        for df in [self.r, self.sc]:
            exps = df.experiment.copy()
            df.replace(translatedict, inplace=True, regex=regex, **kwargs)
            # do not change names of experiments
            df["experiment"] = exps
        # remake s so that strains with the same name are combined
        self.s = admin.make_s(self)
        # remake sc
        self.sc = self.sc.drop_duplicates().reset_index(drop=True)
    else:
        # replace in dataframes
        for df in [self.r, self.s, self.sc]:
            exps = df.experiment.copy()
            df.replace(translatedict, inplace=True, regex=regex, **kwargs)
            df["experiment"] = exps
    self.wellsdf = admin.makewellsdf(self.r)
    # replace in attributes - allstrains and allconditions
    for e in self.allexperiments:
        for listattr in [self.allconditions[e], self.allstrains[e]]:
            for i, listitem in enumerate(listattr):
                for key in translatedict:
                    if key in listitem:
                        listattr[i] = listitem.replace(key, translatedict[key])
        # unique values in case two strains have been renamed to one
        self.allconditions[e] = sorted(list(np.unique(self.allconditions[e])))
        self.allstrains[e] = sorted(list(np.unique(self.allstrains[e])))
        self.allstrainsconditions[e] = list(
            (self.r.strain + " in " + self.r.condition).dropna().unique()
        )


@clogger.log
def addcolumn(self, newcolumnname, oldcolumn, newcolumnvalues):
    """
    Add a new column to all dataframes by parsing an existing column.

    All possible entries for the new column are specified as strings and
    the entry in the new column will be whichever of these strings is
    present in the entry of the existing column.

    Parameters
    ----------
    newcolumnname: string
        The name of the new column.
    oldcolumn: string
        The name of the column to be parsed to create the new column.
    newcolumnvalues: list of strings
        All of the possible values for the entries in the new column.

    Example
    -------
    >>> p.addcolumn('medium', 'condition', ['Raffinose',
    ...                                     'Geneticin'])

    will parse each entry in 'condition' to create a new column called
    'medium' that has either a value 'Raffinose' if 'Raffinose' is in the
    entry from 'condition' or a value 'Geneticin' if 'Geneticin' is in the
    entry from 'condition'.
    """
    for dftype in ["r", "s", "sc"]:
        df = getattr(self, dftype)
        oldcol = df[oldcolumn].to_numpy()
        newcol = np.array(("none",) * oldcol.size, dtype="object")
        for i, oldcolvalue in enumerate(oldcol):
            for newcolvalue in newcolumnvalues:
                if newcolvalue in oldcolvalue:
                    newcol[i] = newcolvalue
        newcolseries = pd.Series(newcol, index=df.index, name=newcolumnname)
        setattr(self, dftype, pd.concat([df, newcolseries], axis=1))


@clogger.log
def addnumericcolumn(
    self,
    newcolumnname,
    oldcolumn,
    picknumber=0,
    leftsplitstr=None,
    rightsplitstr=None,
    asstr=False,
):
    """
    Add a new numeric column.

    Parse the numbers from the entries of an existing column.

    Run only after the basic analyses - ignorewells, correctOD, and
    correctmedia - have been performed because addnumericolumn changes
    the structure of the dataframes.

    Parameters
    ----------
    newcolumnname: string
        The name of the new column.
    oldcolumn: string
        The name of column to be parsed.
    picknumber: integer
        The number to pick from the list of numbers extracted from the
        existing column's entry.
    leftsplitstr: string, optional
        Split the entry of the column using whitespace and parse numbers
        from the substring to the immediate left of leftsplitstr rather
        than the whole entry.
    rightsplitstr: string, optional
        Split the entry of the column using whitespace and parse numbers
        from the substring to the immediate right of rightsplitstr rather
        than the whole entry.
    asstr: boolean
        If True, convert the numeric value to a string to improve plots
        with seaborn.

    Examples
    --------
    To extract concentrations from conditions use

    >>> p.addnumericcolumn('concentration', 'condition')

    For a condition like '0.5% Raf 0.05ug/mL Cycloheximide', use

    >>> p.addnumericcolumn('raffinose', 'condition',
    ...                     picknumber= 0)
    >>> p.addnumericcolumn('cycloheximide', 'condition',
    ...                     picknumber= 1)
    """
    # process splitstrs
    if leftsplitstr or rightsplitstr:
        splitstr = leftsplitstr if leftsplitstr else rightsplitstr
        locno = -1 if leftsplitstr else 1
    else:
        splitstr = False
    # change each dataframe
    for dftype in ["r", "s", "sc"]:
        df = getattr(self, dftype)
        if asstr:
            # new column of strings
            newcol = np.full_like(df[oldcolumn].to_numpy(), "", dtype="object")
        else:
            # new column of floats
            newcol = np.full_like(
                df[oldcolumn].to_numpy(), np.nan, dtype="float"
            )
        # parse old column
        for i, oldcolvalue in enumerate(df[oldcolumn].to_numpy()):
            if oldcolvalue:
                # split string first on spaces and then find substring
                # adjacent to specified splitstring
                if splitstr:
                    if splitstr in oldcolvalue:
                        # oldcolvalue contains leftsplitstring or
                        # rightsplitstring
                        bits = oldcolvalue.split()
                        for k, bit in enumerate(bits):
                            if splitstr in bit:
                                loc = k + locno
                                break
                        # adjacent string
                        oldcolvalue = bits[loc]
                    else:
                        # oldcolvalue does not contain leftsplitstring
                        # or rightsplitstring
                        oldcolvalue = ""
                # loop through all floats in oldcolvalue
                nocount = 0
                for ci in re.split(
                    r"[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)", oldcolvalue
                ):
                    try:
                        no = float(ci)
                        if nocount == picknumber:
                            newcol[i] = ci if asstr else no
                            break
                        nocount += 1
                    except ValueError:
                        pass
        newcolseries = pd.Series(newcol, index=df.index, name=newcolumnname)
        setattr(self, dftype, pd.concat([df, newcolseries], axis=1))


@clogger.log
def add_to_sc(
    self,
    newcolumn=None,
    s_column=None,
    func=None,
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
    Apply func to a column in the s dataframe.

    The results are stored in the sc dataframe.

    Parameters
    ----------
    newcolumn:  string
        The name of the new column in the sc dataframe
    s_column:   string
        The name of the column in s dataframe from which the
        data is to be processed
    func:   function
        The function to be applied to the data in the s dataframe.

    Examples
    --------
    >>> p.add_to_sc(newcolumn= "max_GFP", s_column= "mean_GFP",
    ...             func= np.nanmax)
    >>> p.add_to_sc(newcolumn= "lower_quartile_GFP", s_column= "mean_GFP",
    ...             func= lambda x: np.nanquantile(x, 0.25))
    """
    # extract data
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
    self.sc[newcolumn] = np.nan
    for e in exps:
        for c in cons:
            for s in strs:
                d = self.s.query(
                    "experiment == @e and condition == @c and strain == @s"
                )[s_column].values
                res = np.asarray(func(d))
                if res.size == 1:
                    self.sc.loc[
                        (self.sc.experiment == e)
                        & (self.sc.condition == c)
                        & (self.sc.strain == s),
                        newcolumn,
                    ] = func(d)
                else:
                    print("func must return a single value.")
                    return False


@clogger.log
def addcommonvar(
    self,
    var="time",
    dvar=None,
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
):
    """
    Add a common variable to all time-dependent dataframes.

    The common variable allows averaging across experiments
    and typically is time.

    A common variable is added to time-dependent dataframes. This
    variable's values only come from a fixed array so that they are
    from the same array for all experiments.

    For example, the plate reader often does not perfectly increment time
    between measurements and different experiments can have slightly
    different time points despite the plate reader having the same
    settings. These unique times prevent seaborn from taking averages.

    If experiments have measurements that start at the same time point and
    have the same interval between measurements, then setting a commontime
    for all experiments will allow seaborn to perform averaging.

    The array of the common variable has an interval dvar, which is
    automatically calculated, but may be specified.

    Each instance of var is assigned a common value - the closest instance
    of the common variable to the instance of var. Measurements are assumed
    to the same for the true instance of var and for the assigned common
    value, which may generate errors if these two are sufficiently
    distinct.

    An alternative method is averageoverexpts.

    Parameters
    ----------
    var: string
        The variable from which the common variable is generated,
        typically 'time'.
    dvar: float, optional
        The interval between the values comprising the common array.
    figs: boolean
        If True, generate plot to check if the variable and the common
        variable generated from it are sufficiently close in value.
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

    Example
    -------
    To plot averages of time-dependent variables over experiments, use for
    example

    >>> p.addcommonvar('time')
    >>> p.plot(x= 'commontime', y= 'cGFPperOD', hue= 'condition')
    """
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
        nonull=False,
    )
    for i, df in enumerate([self.r, self.s]):
        if var in df:
            loc = (
                df.experiment.isin(exps)
                & df.condition.isin(cons)
                & df.strain.isin(strs)
            )
            if dvar is None and df.equals(self.r):
                # group data by experiment generating average time
                mdf = (
                    df[loc]
                    .sort_values(by=["experiment", "well", var])[
                        ["experiment", "well", var, "OD"]
                    ]
                    .groupby(["experiment", var])
                    .mean(numeric_only=True)
                ).reset_index()[["experiment", var]]
                # find experiment with longest duration
                longest_i = np.argmax(
                    [mdf[mdf.experiment == e][var].size for e in exps]
                )
                # chose the var for this longest experiment
                cvar = mdf[mdf.experiment == exps[longest_i]][var].values
            elif dvar is not None:
                cvar = np.arange(df[loc][var].min(), df[loc][var].max(), dvar)
            # define common var
            df.loc[loc, f"common{var}"] = df[loc][var].apply(
                lambda x: cvar[np.argmin((x - cvar) ** 2)]
            )
            if figs and i == 0:
                plt.figure()
                sl = np.linspace(
                    df[loc][var].min(), 1.05 * df[loc][var].max(), 100
                )
                plt.plot(sl, sl, alpha=0.4)
                plt.plot(
                    df[loc][var].to_numpy(),
                    df[loc]["common" + var].to_numpy(),
                    ".",
                )
                plt.xlabel(var)
                plt.ylabel("common" + var)
                title = "r dataframe" if df.equals(self.r) else "s dataframe"
                plt.title(title)
                plt.suptitle(
                    f"comparing {var} with common{var} – "
                    "the line y= x is expected."
                )
                plt.tight_layout()
                plt.show(block=False)


@clogger.log
def restricttime(self, tmin=None, tmax=None):
    """
    Restrict the processed data to a range of time.

    Points outside this time range are ignored.

    Note that data in the dataframes outside the time range is lost.
    Exporting the dataframes before running restricttime is recommended.

    Parameters
    ----------
    tmin: float
        The minimum value of time, with data kept only for t >= tmin.
    tmax: float
        The maximum value of time, with data kept only for t <= tmax.

    Example
    -------
    >>> p.restricttime(tmin= 5)
    """
    if tmin is None:
        tmin = self.r.time.min()
    if tmax is None:
        tmax = self.r.time.max()
    if tmax > tmin:
        self.r = self.r[(self.r.time >= tmin) & (self.r.time <= tmax)]
        self.s = self.s[(self.s.time >= tmin) & (self.s.time <= tmax)]
    else:
        print("tmax or tmin is not properly defined.")


@clogger.log
def getdataframe(
    self,
    dfname="s",
    experiments="all",
    conditions="all",
    strains="all",
    experimentincludes=False,
    experimentexcludes=False,
    conditionincludes=False,
    conditionexcludes=False,
    strainincludes=False,
    strainexcludes=False,
    nonull=True,
):
    """
    Obtain a subset of the data in a dataframe.

    This data can be used plotted directly.

    Parameters
    ---------
    dfname: string
        The dataframe of interest either 'r' (raw data),
        's' (default; processed data),
        or 'sc' (summary statistics).
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
    nonull: boolean, optional
        If True, ignore 'Null' strains

    Returns
    -------
    ndf: dataframe

    Example
    -------
    >>> ndf= p.getdataframe('s', conditions= ['2% Glu'],
    ...                     nonull= True)
    """
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
        nonull,
    )
    if hasattr(self, dfname):
        df = getattr(self, dfname)
        ndf = df.query(
            "experiment == @exps and condition == @cons " "and strain == @strs"
        )
        if ndf.empty:
            print("No data found.")
        else:
            return ndf.copy()
    else:
        raise errors.UnknownDataFrame(
            "Dataframe " + dfname + " is not recognised."
        )
