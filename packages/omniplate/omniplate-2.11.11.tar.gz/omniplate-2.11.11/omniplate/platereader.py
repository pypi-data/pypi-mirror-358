"""Define the platereader class."""

import warnings
from pathlib import Path

import omniplate
import omniplate.clogger as clogger


class platereader:
    """
    To analyse plate-reader data.

    Data are corrected for autofluorescence and growth rates found using
    a Gaussian process.

    All data is stored used Panda's dataframes and plotted using Seaborn.

    Three dataframes are created. If p is an instance of the platereader class,
    then p.r contains the raw data for each well in the plate; p.s contains the
    processed time-series using the data from all relevant wells; and p.sc
    contains any summary statistics, such as 'max gr'.

    For time series sampled from a Gaussian process, the mean is used as the
    statistics and errors are estimated by the standard deviation.
    For statistics calculated from time series, the median is used and errors
    are estimated by half the interquartile range, with the distribution of
    the statistic calculated by sampling time series.

    Examples
    -------
    A typical work flow is:

    >>> import omniplate as om

    then either

    >>> p= om.platereader('GALdata.xlsx', 'GALcontents.xlsx',
    ...                    wdir= 'data/')

    or

    >>> p= om.platereader()
    >>> p.load('GALdata.xls', 'GALcontents.xlsx')

    and to analyse OD data

    >>> p.plot('OD', plate= True)
    >>> p.correctOD()
    >>> p.correctmedia()
    >>> p.plot(y= 'OD')
    >>> p.plot(y= 'OD', hue= 'strain',
    ...        conditionincludes= ['Gal', 'Glu'],
    ...        strainexcludes= 'HXT7')
    >>> p.getstats('OD')

    and for fluorescence data

    >>> p.correctauto(['GFP', 'AutoFL'])
    >>> p.plot(y= 'cGFPperOD', hue= 'condition')

    and to save the results

    >>> p.savefigs()
    >>> p.exportdf()

    General properties of the data and of previous processing are shown with:

    >>> p.info
    >>> p.attributes()
    >>> p.corrections()
    >>> p.log

    See also
        http://swainlab.bio.ed.ac.uk/software/omniplate/index.html
    for a tutorial, which can be opened directly using

    >>> p.webhelp()
    """

    # ratio of fluorescence emission at 585nm to emiisions at 525nm for eGFP
    _gamma = 0.114  # TODO delete

    def __init__(
        self,
        dnames=None,
        anames=None,
        experimenttype=None,
        wdir=".",
        datadir=".",
        platereadertype="Tecan",
        dsheets=False,
        asheets=False,
        ODfname=None,
        info=True,
        ls=True,
    ):
        """
        Initiate and potentially immediately load data for processing.

        Parameters
        ----------
        dnames: string or list of strings, optional
            The name of the file containing the data from the plate reader or
            a list of file names.
        anames: string or list of strings, optional
            The name of file containing the corresponding annotation or a list
            of file names.
        experimenttype: string or list of strings, optional
            If specified, creates a new experiment_type column in each
            dataframe.
        wdir: string, optional
            The working directory where new files should be saved.
        datadir: string, optional
             The directory containing the data files.
        platereadertype: string
            The type of plate reader, currently either "Tecan" or "tidy" for
            data parsed into a tsv file of columns, with headings "time",
            "well", "OD", "GFP", and any other measurements taken.
        dsheets: list of integers or strings, optional
            The relevant sheets of the Excel files storing the data.
        asheets: list of integers or strings, optional
            The relevant sheets of the corresponding Excel files for the
            annotation.
        info: boolean
            If True (default), display summary information on the data once
            loaded.
        ls: boolean
            If True (default), display contents of working directory.
        """
        # absolute path
        self.wdirpath = Path(wdir)
        self.datadirpath = Path(datadir)
        # enable logging
        self.logger, self.logstream = clogger.initlog(omniplate.__version__)
        if True:
            # warning generated occasionally when sampling from the Gaussian
            # process likely because of numerical errors
            warnings.simplefilter("ignore", RuntimeWarning)
        # dictionary recording extent of analysis
        self.progress = {
            "ignoredwells": {},
            "negativevalues": {},
        }
        self.allexperiments = []
        self.allconditions = {}
        self.allstrains = {}
        self.datatypes = {}
        self.allstrainsconditions = {}
        self.find_available_data
        if dnames is None:
            # list all files in current directory
            if ls:
                self.ls
        else:
            # immediately load data
            self.load(
                dnames=dnames,
                anames=anames,
                experimenttype=experimenttype,
                platereadertype=platereadertype,
                dsheets=dsheets,
                asheets=asheets,
                info=info,
            )
        self.combined = "__combined__"

    ###
    # import methods
    ###
    from .admin import cols_to_underscore, drop
    from .corrections import (
        correctauto,
        correctauto_l,
        correctODformedia,
        correctOD,
    )
    from .getstats import getstats
    from .loaddata import load
    from .manipulatedfs import (
        add_to_sc,
        addcolumn,
        addcommonvar,
        addnumericcolumn,
        getdataframe,
        rename,
        rename_combined,
        restricttime,
        search,
    )
    from .midlog import getmidlog
    from .misc import averageoverexpts, getfitnesspenalty
    from .ominfo import (
        changewdir,
        changedatadir,
        find_available_data,
        info,
        log,
        ls,
        webhelp,
        experiment_map,
    )
    from .omio import exportdf, importdf, savelog, save
    from .omplot import close, plot, savefigs, inspect
    from .omwells import contentsofwells, ignorewells, showwells
    from .promoteractivity import getpromoteractivity

    def __repr__(self):
        """Give standard representation."""
        repstr = f"omniplate.{self.__class__.__name__}: "
        if self.allexperiments:
            for e in self.allexperiments:
                repstr += e + " ; "
            if repstr[-2:] == "; ":
                repstr = repstr[:-3]
        else:
            repstr += "no experiments"
        return repstr


if __name__ == "__main__":
    print(platereader.__doc__)
