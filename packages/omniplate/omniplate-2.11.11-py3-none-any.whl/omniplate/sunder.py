"""Functions for extracting subsets of the data."""

import numpy as np

import omniplate.omerrors as errors
import omniplate.omgenutils as gu


def getall_labels(self, labeltype, nonull, nomedia):
    """List all the labels available for a given label type."""
    if labeltype == "experiment":
        all_labels = self.allexperiments
    elif labeltype == "condition":
        all_labels = list(
            set(
                [
                    con
                    for e in self.allconditions
                    for con in self.allconditions[e]
                ]
            )
        )
        if nomedia and "media" in all_labels:
            all_labels.pop(all_labels.index("media"))
    elif labeltype == "strain":
        all_labels = list(
            set(
                [
                    strain
                    for e in self.allstrains
                    for strain in self.allstrains[e]
                ]
            )
        )
        if nonull and "Null" in all_labels:
            all_labels.pop(all_labels.index("Null"))
    else:
        raise errors.getsubset("Nothing found.")
    return all_labels


def getset(
    self,
    label,
    labelincludes,
    labelexcludes,
    labeltype,
    nonull,
    nomedia=True,
):
    """Find user-specified list of experiments, conditions, or strains."""
    all_labels = getall_labels(self, labeltype, nonull, nomedia)
    if label != "all":
        # prioritise explicitly specified labels
        labels = gu.makelist(label)
        # check user's choice exists
        bad_labels = [label for label in labels if label not in all_labels]
        # keep only good labels
        labels = [label for label in labels if label not in bad_labels]
    else:
        labels = all_labels
        if labelincludes:
            # find those items containing keywords given in 'includes'
            includes = gu.makelist(labelincludes)
            newset = []
            for s in all_labels:
                gotone = 0
                for item in includes:
                    if item in s:
                        gotone += 1
                if gotone == len(includes):
                    newset.append(s)
            labels = newset
        if labelexcludes:
            # remove any items containing keywords given in 'excludes'
            excludes = gu.makelist(labelexcludes)
            exs = []
            for s in all_labels:
                for item in excludes:
                    if item in s:
                        exs.append(s)
                        break
            for ex in exs:
                if ex in labels:
                    labels.pop(labels.index(ex))
    if labels:
        # sort by numeric values in list entries
        return sorted(labels, key=gu.natural_keys)
    else:
        raise errors.getsubset("No data found.")


def getall(
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
    nomedia=True,
):
    """Return experiments, conditions, and strains."""
    exps = getset(
        self,
        experiments,
        experimentincludes,
        experimentexcludes,
        "experiment",
        nonull,
        nomedia,
    )
    cons = getset(
        self,
        conditions,
        conditionincludes,
        conditionexcludes,
        "condition",
        nonull,
        nomedia,
    )
    strs = getset(
        self,
        strains,
        strainincludes,
        strainexcludes,
        "strain",
        nonull,
        nomedia,
    )
    return exps, cons, strs


def extractwells(r_df, s_df, experiment, condition, strain, datatypes):
    """
    Extract a list of data matrices from the r dataframe.

    Each column in each matrix contains the data
    from one well.

    Data is returned for each dtype in datatypes, which may include "time", for
    the given experiment, condition, and strain.
    """
    datatypes = gu.makelist(datatypes)
    # restrict time if necessary
    lrdf = r_df[
        (r_df.time >= s_df.time.min()) & (r_df.time <= s_df.time.max())
    ]
    df = lrdf.query(
        "experiment == @experiment and condition == @condition "
        "and strain == @strain"
    )
    if df.empty:
        return None, None
    else:
        # extract time
        dfw_time = (
            df[["time", "well"]]
            .groupby("well", group_keys=True)["time"]
            .apply(list)
        )
        well_times = [dfw_time[well] for well in dfw_time.index]
        # data may have different durations
        longest_i = np.argmax([len(dfw_time[well]) for well in dfw_time.index])
        t = np.array(well_times[longest_i])
        # extract data
        matrices = []
        for dtype in datatypes:
            dfw_dtype = (
                df[[dtype, "well"]]
                .groupby("well", group_keys=True)[dtype]
                .apply(list)
            )
            data = np.nan * np.ones((len(t), dfw_dtype.shape[0]))
            for i, well in enumerate(dfw_dtype.index):
                data[: len(dfw_dtype[well]), i] = np.array(dfw_dtype[well])
            matrices.append(data)
        if len(datatypes) == 1:
            # return array
            return t, matrices[0]
        else:
            # return list of arrays
            return t, matrices
