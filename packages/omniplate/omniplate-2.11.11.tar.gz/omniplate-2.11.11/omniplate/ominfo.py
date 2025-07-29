"""Display information on the data sets and on omniplate."""

import pprint
from pathlib import Path

import omniplate.omgenutils as gu


@property
def info(self):
    """
    Display conditions, strains, and data types.

    Example
    -------
    >>> p.info
    """
    if self.allexperiments:
        for exp in self.allexperiments:
            print("\nExperiment:", exp, "\n---")
            print("Conditions:")
            for c in sorted(self.allconditions[exp], key=gu.natural_keys):
                print("\t", c)
            print("Strains:")
            for s in sorted(self.allstrains[exp], key=gu.natural_keys):
                print("\t", s)
            print("Data types:")
            for d in self.datatypes[exp]:
                print("\t", d)
            if self.progress["ignoredwells"]:
                print("Ignored wells:")
                if self.progress["ignoredwells"][exp]:
                    for d in self.progress["ignoredwells"][exp]:
                        print("\t", d)
                else:
                    print("\t", "None")
        print()
    else:
        print("No experiments loaded.")


@property
def find_available_data(self):
    """Create files and data sets as attributes."""
    files = []
    datasets = []
    for f in self.datadirpath.glob("*.*"):
        if f.is_file() and (
            f.suffix == ".xlsx"
            or f.suffix == ".json"
            or f.suffix == ".tsv"
            or f.suffix == ".csv"
            or f.suffix == ".xls"
        ):
            files.append(f.stem + f.suffix)
            if f.suffix == ".tsv" or f.suffix == ".json" or f.suffix == ".csv":
                froot = "_".join(f.stem.split("_")[:-1])
                if froot not in datasets:
                    datasets.append(froot)
    self.files = {i: f for i, f in enumerate(sorted(files))}
    self.datasets = {i: f for i, f in enumerate(sorted(datasets))}


@property
def ls(self):
    """
    List all files in the data directory.

    A dictionary of available files to load and a list of available
    data sets to import are created as a shortcuts.

    Parameter
    --------
    output: boolean
        If True, list available files.

    Examples
    --------
    >>> p.ls
    >>> p.files
    >>> p.load(p.files[0], p.files[1])
    >>> p.importdf(p.datasets)
    """
    print(f"Data directory is {str(self.datadirpath.resolve())}.")
    print(f"Working directory is {str(self.wdirpath.resolve())}.")
    print("Files available - see .files - are:", "\n---")
    pprint.pprint(self.files)
    print()


def changewdir(self, wdir, ls=True):
    """
    Change working directory.

    Parameters
    ----------
    wdir: string
        The new working directory specified from the current directory.
    ls: boolean
        If True (default), display contents of the working directory.

    Example
    -------
    >>> p.changewdir('newdata/')
    """
    self.wdirpath = Path(wdir)
    self.find_available_data
    if ls:
        self.ls


def changedatadir(self, datadir, ls=True):
    """
    Change data directory.

    Parameters
    ----------
    datadir: string
        The new working directory specified from the current directory.
    ls: boolean
        If True (default), display contents of the working directory.

    Example
    -------
    >>> p.changewdir('newdata/')
    """
    self.datadirpath = Path(datadir)
    self.find_available_data
    if ls:
        self.ls


@property
def webhelp(self):
    """
    Open detailed examples of how to use in omniplate in a web browser.

    Example
    -------
    >>> p.webhelp
    """
    import webbrowser

    url = "https://swainlab.bio.ed.ac.uk/software/omniplate/index.html"
    webbrowser.get(None).open_new(url)


@property
def log(self):
    """
    Print a log of all methods called and their arguments.

    Example
    -------
    >>> p.log
    """
    print(self.logstream.getvalue())


@property
def experiment_map(self):
    """For a combined experiment, show the original experiments and IDs."""
    if hasattr(self, "_exp_map"):
        return self._exp_map
    else:
        if "experiment_id" and "original_experiment" in self.r.columns:
            self._exp_map = {
                name: int(id)
                for id, name in zip(
                    self.r.experiment_id.unique(),
                    self.r.original_experiment.unique(),
                )
            }
            return self._exp_map
        else:
            print("There is only one experiment.")
