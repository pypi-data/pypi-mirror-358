import numpy as np
import pandas as pd
from SurvivalEVAL import SurvivalEvaluator

# generate 290816 samples with event time and event indicator
n_samples = 290816
event_times = np.random.weibull(a=1, size=n_samples).round(1)
censoring_times = np.random.lognormal(mean=1, sigma=1, size=n_samples).round(1)
event_indicators = event_times < censoring_times
observed_times = np.minimum(event_times, censoring_times)

# generate survival curves with 4794 time points
n_time_points = 4794
time_bins = np.linspace(0.1, 5, n_time_points)
# generate random survival curves
predictions = np.random.rand(n_samples, n_time_points)
# normalize the predictions to sum to 1, meaning the probability mass function
pmf = predictions / predictions.sum(axis=1)[:, None]
survival_curves = 1 - np.cumsum(pmf, axis=1)
# make a dataframe with survival curves, each row is a time point and each column is a sample
# survival_curves_df = pd.DataFrame(survival_curves, columns=[i for i in range(n_samples)])

