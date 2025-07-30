from pathlib import Path

from dewan_utils.async_io import AsyncIO
import pandas as pd
import numpy as np

def test():
    writer = AsyncIO()
    rng = np.random.default_rng()
    df_to_save = pd.DataFrame(rng.integers(0, 100, size=(100,4)), columns=['A','B', 'C', 'D'])
    test_save_dir = Path('./test_output_dir/')
    test_save_dir.mkdir(exist_ok=True, parents=True)
    bad_test_save_dir = Path('./does_not_exist/folder/')

    test_extensions = ['.xlsx', '.csv', '.pickle', '.pkl', '.pk', '.txt', '.fake']

    good_save_dir_paths = [test_save_dir.joinpath('test_file').with_suffix(ext) for ext in test_extensions]
    bad_save_dir_paths = [bad_test_save_dir.joinpath('test_file').with_suffix(ext) for ext in test_extensions]

    for good_path in good_save_dir_paths:
        writer.queue_save_df(df_to_save, good_path)

    for bad_path in bad_save_dir_paths:
        writer.queue_save_df(df_to_save, bad_path)

    writer.shutdown(wait=True)
if __name__ == "__main__":
    test()