import logging
import os

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

def save_figure(figure: Figure, file_path: os.PathLike, logger: logging.Logger, debug: bool = False, *args, **kwargs):
    """
    Private function that saves a figure. This function is submitted to the ThreadPoolExecuter as a job
    Parameters
    ----------
    figure (matplotlib.figure.Figure):
        Figure to save to disk
    file_path (os.PathLike):
        File path with extension pointing to the save directory
    logger (logging.Logger):
        Logger to pass messages back through

    Returns
    -------
        None
    """

    try:
        figure.savefig(file_path, **kwargs)
        plt.close(figure)
    except Exception as e:
        logger.error("Unable to save %s \n %s", file_path, e)
    if debug:
        logger.debug("Saved %s", file_path)