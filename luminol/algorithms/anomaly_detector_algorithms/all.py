from luminol.algorithms.anomaly_detector_algorithms import (bitmap_detector,
    default_detector, derivative_detector, exp_avg_detector, absolute_threshold,
    diff_percent_threshold, sign_test)

anomaly_detector_algorithms = {
        'bitmap_detector': bitmap_detector.BitmapDetector,
        'default_detector': default_detector.DefaultDetector,
        'derivative_detector': derivative_detector.DerivativeDetector,
        'exp_avg_detector': exp_avg_detector.ExpAvgDetector,
        'absolute_threshold': absolute_threshold.AbsoluteThreshold,
        'diff_percent_threshold': diff_percent_threshold.DiffPercentThreshold,
        'sign_test': sign_test.SignTest
}
