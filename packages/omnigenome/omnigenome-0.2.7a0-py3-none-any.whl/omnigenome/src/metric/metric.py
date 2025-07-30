# -*- coding: utf-8 -*-
# file: regression_metric.py
# time: 12:57 09/04/2024
# author: YANG, HENG <hy345@exeter.ac.uk> (杨恒)
# github: https://github.com/yangheng95
# huggingface: https://huggingface.co/yangheng
# google scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2019-2024. All Rights Reserved.


import types
import warnings

import numpy as np
import sklearn.metrics as metrics

from ..abc.abstract_metric import OmniGenomeMetric


def mcrmse(y_true, y_pred):
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape")
    mask = y_true != -100
    filtered_y_pred = y_pred[mask]
    filtered_y_true = y_true[mask]
    rmse_per_target = np.sqrt(np.mean((filtered_y_true - filtered_y_pred) ** 2, axis=0))
    mcrmse_value = np.mean(rmse_per_target)
    return mcrmse_value


setattr(metrics, "mcrmse", mcrmse)


class Metric(OmniGenomeMetric):
    """
    Classification metric class
    """

    def __init__(self, metric_func=None, ignore_y=-100, *args, **kwargs):
        super().__init__(metric_func, ignore_y, *args, **kwargs)
        self.kwargs = kwargs
        self.metrics = {"mcrmse": mcrmse}
        for key, value in metrics.__dict__.items():
            setattr(self, key, value)

    def __getattribute__(self, name):
        # Get the metric function
        metric_func = getattr(metrics, name, None)

        if metric_func and isinstance(metric_func, types.FunctionType):
            setattr(self, "compute", metric_func)
            # If the metric function exists, return a wrapper function

            def wrapper(y_true=None, y_score=None, *args, **kwargs):
                """
                Compute the metric, based on the true and predicted values.
                :param y_true: the true values
                :param y_score: the predicted values
                :param ignore_y: the value to ignore in the predictions and true values in corresponding positions
                """
                # This is an ugly method to handle the case when the predictions are in the form of a tuple
                # for huggingface trainers
                if y_true is not None and y_score is None:
                    if hasattr(y_true, "predictions"):
                        y_score = y_true.predictions
                    if hasattr(y_true, "label_ids"):
                        y_true = y_true.label_ids
                    if hasattr(y_true, "labels"):
                        y_true = y_true.labels
                    if len(y_score[0][1]) == np.max(y_true) + 1:
                        y_score = y_score[0]
                    else:
                        y_score = y_score[1]
                    y_score = np.argmax(y_score, axis=1)
                elif y_true is not None and y_score is not None:
                    pass  # y_true and y_score are provided
                else:
                    raise ValueError(
                        "Please provide the true and predicted values or a dictionary with 'y_true' and 'y_score'."
                    )

                y_true, y_score = Metric.flatten(y_true, y_score)
                y_true_mask_idx = np.where(y_true != self.ignore_y)
                if self.ignore_y is not None:
                    y_true = y_true[y_true_mask_idx]
                    try:
                        y_score = y_score[y_true_mask_idx]
                    except Exception as e:
                        warnings.warn(str(e))
                kwargs.update(self.kwargs)

                return {name: self.compute(y_true, y_score, *args, **kwargs)}

            return wrapper
        else:
            return super().__getattribute__(name)

    def compute(self, y_true, y_score, *args, **kwargs):
        """
        Compute the metric, based on the true and predicted values.
        :param y_true: the true values
        :param y_score: the predicted values
        """
        if self.metric_func is not None:
            kwargs.update(self.kwargs)
            return self.metric_func(y_true, y_score, *args, **kwargs)

        else:
            raise NotImplementedError(
                "Method compute() is not implemented in the child class."
            )
