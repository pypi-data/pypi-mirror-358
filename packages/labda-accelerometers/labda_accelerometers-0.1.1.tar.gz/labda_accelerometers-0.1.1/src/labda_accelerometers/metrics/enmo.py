from typing import Literal

import numpy as np
import pandas as pd


def get_enmo(
    df: pd.DataFrame,
    epoch: int = 5,
    absolute: bool = False,
    trim: bool = True,
) -> pd.Series:
    name: Literal['enmo', 'enmoa'] = 'enmo'

    # Calculate vector magnitude and subtract 1g (gravity)
    time = df.index
    vm = np.linalg.norm(df[['acc_x', 'acc_y', 'acc_z']].values, axis=1) - 1.0
    del df

    # Apply absolute if requested
    if absolute:
        vm = np.abs(vm)
        name = 'enmoa'

    # Apply trimming if requested
    vm = np.maximum(vm, 0.0) if trim else vm

    # Create series with proper index
    vm_series = pd.Series(vm, index=time, name=name, dtype=np.float32)

    # Resample to epoch
    epoch_td = pd.Timedelta(seconds=epoch)
    return vm_series.resample(epoch_td).mean()
