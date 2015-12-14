# coding=utf-8
"""
© 2015 LinkedIn Corp. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""
"""
Constants to use for luminol
"""

"""
Detector Constants
"""
# Indicate which algorithm to use to calculate anomaly scores.
ANOMALY_DETECTOR_ALGORITHM = 'bitmap_detector'

# Indicate which algorithm to use to get refined maximal score within each anomaly.
ANOMALY_DETECTOR_REFINE_ALGORITHM = 'exp_avg_detector'

# Default percent threshold value on anomaly score above which is considered an anomaly.
DEFAULT_SCORE_PERCENT_THRESHOLD = 0.2

# Constants for BitmapDetector.
# Window sizes as percentiles of the whole data length.
DEFAULT_BITMAP_LEADING_WINDOW_SIZE_PCT = 0.2 / 16

DEFAULT_BITMAP_LAGGING_WINDOW_SIZE_PCT = 0.2 / 16

DEFAULT_BITMAP_MINIMAL_POINTS_IN_WINDOWS = 50

DEFAULT_BITMAP_MAXIMAL_POINTS_IN_WINDOWS = 200

# Chunk size.
# Data points form chunks and frequencies of similar chunks are used to determine anomaly scores.
DEFAULT_BITMAP_CHUNK_SIZE = 2

DEFAULT_BITMAP_PRECISION = 4

# Constants for ExpAvgDetector.
DEFAULT_EMA_SMOOTHING_FACTOR = 0.2

DEFAULT_EMA_WINDOW_SIZE_PCT = 0.2

# Constants for DerivativeDetector.
DEFAULT_DERI_SMOOTHING_FACTOR = 0.2

ANOMALY_THRESHOLD = {
    'exp_avg_detector': 3,
    'default_detector': 3
}

# Percentage threshold on anomaly score below which is considered noises.
DEFAULT_NOISE_PCT_THRESHOLD = 0.001

# The score weight default detector uses.
DEFAULT_DETECTOR_EMA_WEIGHT = 0.65

# The default minimal ema score for the deault detector to use weighted score.
DEFAULT_DETECTOR_EMA_SIGNIFICANT = 0.94

"""
Correlator Constants
"""
CORRELATOR_ALGORITHM = 'cross_correlator'

# Since anomalies take time to propagate between two different timeseries,
# similar irregularities may happen close in time but not exactly at the same point in time.
# To take this into account, when correlates, we allow a "shift room".
DEFAULT_ALLOWED_SHIFT_SECONDS = 60

# The threshold above which is considered "correlated".
DEFAULT_CORRELATE_THRESHOLD = 0.7

# The impact of shift on shifted correlation coefficient.
DEFAULT_SHIFT_IMPACT = 0.05

TIMESTAMP_STR_FORMATS = [
    '%Y%m%d_%H:%M:%S',
    '%Y-%m-%d %H:%M:%S.%f',
    '%Y%m%d %H:%M:%S',
    '%Y-%m-%d_%H:%M:%S',
    '%Y-%m-%dT%H:%M:%S.%f',
    '%H:%M:%S.%f',
    '%Y-%m-%dT%H:%M:%S.%f%z',
    '%Y%m%dT%H:%M:%S',
    '%Y-%m-%d_%H:%M:%S.%f',
    '%Y%m%d_%H:%M:%S.%f',
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%d %H:%M:%S',
    '%Y%m%dT%H:%M:%S.%f',
    '%H:%M:%S',
    '%Y%m%d %H:%M:%S.%f']
