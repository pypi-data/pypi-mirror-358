import os
import pandas as pd
import logging


def save_df_as_excel(
    logger: logging.Logger,
    df_to_save: pd.DataFrame,
    file_path: os.PathLike,
    debug: bool = False,
    *args,
    **kwargs,
) -> None:
    """
    Private function that saves a Dataframe. This function is submitted to the ThreadPoolExecuter as a job
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
    try:
        df_to_save.to_excel(file_path, *args, **kwargs)
    except Exception:
        logger.error("Unable to save %s", file_path)

    if debug:
        logger.debug("Saved %s", file_path)


def save_df_as_csv(
    logger: logging.Logger,
    df_to_save: pd.DataFrame,
    file_path: os.PathLike,
    debug: bool = False,
    *args,
    **kwargs,
) -> None:
    """
    Private function that saves a Dataframe. This function is submitted to the ThreadPoolExecuter as a job
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
    try:
        df_to_save.to_csv(file_path, *args, **kwargs)
    except Exception:
        logger.error("Unable to save %s", file_path)

    if debug:
        logger.debug("Saved %s", file_path)


def save_df_as_pickle(
    logger: logging.Logger,
    df_to_save: pd.DataFrame,
    file_path: os.PathLike,
    debug: bool = False,
    *args,
    **kwargs,
) -> None:
    """
    Private function that saves a Dataframe. This function is submitted to the ThreadPoolExecuter as a job
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
    try:
        df_to_save.to_pickle(file_path, *args, **kwargs)
    except Exception:
        logger.error("Unable to save %s", file_path)

    if debug:
        logger.debug("Saved %s", file_path)
