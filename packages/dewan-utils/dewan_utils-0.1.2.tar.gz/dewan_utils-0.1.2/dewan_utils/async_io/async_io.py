from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Union

from dewan_utils.async_io import save_df, save_fig

import os
import logging
import pandas as pd

from matplotlib.figure import Figure
PICKLE_EXTENSIONS = [".pickle", ".pkl", ".pk"]


class AsyncIO(ThreadPoolExecutor):
    """
    AsyncIO class instantiates a ThreadPoolExecuter to allow for asyncronous saving of different files while
    the main thread continues execution. AsyncIO inherits from ThreadPoolExecuter.
    """

    def __init__(
        self,
        logger: logging.Logger = None,
        logfile: os.PathLike = None,
    ) -> None:
        """
        Constructs an AsyncIO object

        Parameters
        ----------
        logger (logging.Logger):
            An instance of logging.Logger can be supplied to write log messages from threads. If none is supplied,
             a new logging.Logger instance is created (default is None)

        logfile (os.PathLike):
            Path to a logfile (with extension) can be provided to save log output to disk (default is None)

        *args
            Additional arguments should be passed as keyword arguments
        **kwargs
            Extra arguments to `__init__`: refer to documentation for a
            list of all possible arguments.
        """
        super().__init__()

        self.logger: logging.Logger = Union[None, logging.Logger]
        self.setup_logger(logger, logfile)

    def setup_logger(self, logger: logging.Logger, logfile: os.PathLike):
        """
        Function checks if the user supplied a Logger or logfile path. If no Logger is supplied, a new one is instantiated.
        If a logfile path is provided, its added as a handler to the logger. Once finished, the class's logger field is
        set to the final Logger
        Parameters
        ----------
        logger (logging.Logger):
            An instance of logging.Logger can be supplied to write log messages from threads. If none is supplied,
             a new logging.Logger instance is created (default is None)

        logfile (os.PathLike):
            Path to a logfile (with extension) can be provided to save log output to disk (default is None)

        Returns
        -------
        None
        """

        if logger is None:
            logger = logging.getLogger(__name__)
        if logfile:
            logger.addHandler(logging.FileHandler(logfile))

        logging.basicConfig(level=logging.NOTSET)
        self.logger = logger

    def queue_save_df(
        self, df_to_save: pd.DataFrame, file_path: os.PathLike, *args, **kwargs
    ) -> None:
        """
        Public function to queue a Pandas Dataframe to be saved to disk
        Parameters
        ----------
        df_to_save (Pandas.DataFrame):
            Pandas dataframe the user wishes to save to disk
        file_path (os.PathLike):
            File path with extension pointing to the save directory

        Returns
        -------
            None
        """

        _path = Path(file_path)
        _extension = _path.suffix

        if not _path.parent.exists():
            self.logger.error(
                "Supplied file path directory [%s], does not exist! Unable to save!",
                _path.parent,
            )
            return

        if _extension == ".xlsx":
            _handle = save_df.save_df_as_excel
        elif _extension == ".csv":
            _handle = save_df.save_df_as_csv
        elif _extension in PICKLE_EXTENSIONS:
            _handle = save_df.save_df_as_pickle
        else:
            _pkl_ext_formatted = "".join([f"'{ext}', " for ext in PICKLE_EXTENSIONS])
            self.logger.error(
                "%s is not a known file extension. Known extensions are ['.xlsx', '.csv', %s]",
                _extension,
                _pkl_ext_formatted,
            )
            return

        self.submit(_handle, self.logger, df_to_save, file_path, *args, **kwargs)


    def queue_save_plot(self, figure_to_save: Figure, file_path: os.PathLike, *args, **kwargs) -> None:
        _path = Path(file_path)
        _extension = _path.suffix

        if not _path.parent.exists():
            self.logger.error(
                "Supplied file path directory [%s], does not exist! Unable to save!",
                _path.parent,
            )
            return

        self.submit(save_fig.save_figure, figure_to_save, file_path, self.logger, *args, **kwargs)