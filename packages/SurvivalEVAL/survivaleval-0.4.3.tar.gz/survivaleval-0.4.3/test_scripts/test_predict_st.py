import time
import numpy as np
import pandas as pd
import os

from SurvivalEVAL.Evaluations.util import predict_rmst, predict_mean_st, predict_median_st, predict_median_st, predict_mean_st_old

def f(x):
    return x*x

if __name__ == '__main__':
    # generate some random points
    logits = np.random.weibull(a=1, size=2000).reshape(100, 20)
    # geenrate pdf using softmax
    pdf = np.exp(logits) / np.exp(logits).sum(axis=1)[:, None]
    surv = 1 - np.cumsum(pdf, axis=1)
    surv = surv[:, :10]

    # generate some random time points
    time_points = np.random.uniform(0, 6, size=1000).reshape(100, 10)
    time_points = np.cumsum(time_points, axis=1)

    # add 1 at the start of the surv and add 0 at the start of time_points
    surv = np.concatenate([np.ones((100, 1)), surv], axis=1)
    time_points = np.concatenate([np.zeros((100, 1)), time_points], axis=1)

    # add a all 1s surv at the end
    surv = np.concatenate([surv, np.ones((1, 11))], axis=0)
    time_points = np.concatenate([time_points, time_points[-1, :].reshape(1, -1)], axis=0)

    start = time.time()
    rmst = predict_rmst(surv, time_points)
    end = time.time()
    print(f"Time taken for RMST: {end - start}")
    rmst_ = np.empty_like(rmst)
    for i in range(surv.shape[0]):
        rmst_[i] = predict_rmst(surv[i], time_points[i])
    assert np.all(rmst == rmst_), "RMST is not correct."

    start = time.time()
    mean_st = predict_mean_st(surv, time_points)
    end = time.time()
    print(f"Time taken for mean survival time: {end - start}")
    strat = time.time()
    mean_st_ = np.empty_like(mean_st)
    for i in range(surv.shape[0]):
        mean_st_[i] = predict_mean_st_old(surv[i], time_points[i])
    end = time.time()
    print(f"Time taken for mean survival time: {end - start}")

    # assert np.all(mean_st == mean_st_), "Mean survival time is not correct."

    start = time.time()
    median_st = predict_median_st(surv, time_points)
    end = time.time()
    median_st_ = np.empty_like(mean_st_)
    for i in range(surv.shape[0]):
        median_st_[i] = predict_median_st(surv[i], time_points[i])
    print(f"Time taken for median survival time: {end - start}")







