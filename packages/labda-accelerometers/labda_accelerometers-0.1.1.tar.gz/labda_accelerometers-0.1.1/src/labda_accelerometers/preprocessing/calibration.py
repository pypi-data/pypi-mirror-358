import logging
import warnings
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from skdh.preprocessing import CalibrateAccelerometer

from ..utils import get_sampling_frequency

logger = logging.getLogger(__name__)


@dataclass
class AutoCalibrate:
    min_hours: int = 72
    sampling_frequency: float | None = None

    def calibrate(
        self,
        df: pd.DataFrame,
        **kwargs: Any,
    ) -> pd.DataFrame:
        required_cols = ['acc_x', 'acc_y', 'acc_z']

        # Check if there are extra columns and warn user
        extra_cols = set(df.columns) - set(required_cols)
        if extra_cols:
            logger.warning(
                f'Extra columns {list(extra_cols)} found in the DataFrame. These will be ignored during calibration and not included in the output.'
            )

        # Get sampling frequency
        sampling_frequency = self.sampling_frequency or get_sampling_frequency(df)

        # Prepare data for calibration
        time = df.index
        accel = df[required_cols]
        del df

        # Initialize calibrator
        calibrator = CalibrateAccelerometer(min_hours=self.min_hours, **kwargs)

        # Perform calibration
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            accel = calibrator.predict(
                time=(time.astype(np.int64) // 10**9).values,
                accel=accel.values,
                fs=sampling_frequency,
            ).get('accel')

        if accel is None:
            logger.error('Calibration did not produce valid results. Returning original accelerometer data.')

        # Create result DataFrame with calibrated accelerometer data
        return pd.DataFrame(accel, columns=required_cols, index=time, dtype=np.float32)
