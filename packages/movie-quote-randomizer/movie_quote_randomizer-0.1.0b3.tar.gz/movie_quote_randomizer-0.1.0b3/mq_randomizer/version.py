from . import __summary__, __title__, __version__


class MQRAbout:
    """
    Metadata container for the movie quote randomizer.

    Attributes
    ----------
    version : str
        The version number of the package.
    title : str
        The title of the package.
    summary : str
        A brief description of the package.
    """

    def __init__(self):
        self.version = __version__
        self.title = __title__
        self.summary = __summary__

    def __str__(self):
        """
        Generate a string representation of the package metadata.

        Returns
        -------
        str
            A formatted string containing the package title, summary, and version.
        """
        return f"{__title__} {__summary__} version {__version__}"
