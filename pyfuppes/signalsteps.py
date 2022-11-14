# -*- coding: utf-8 -*-
"""
Detect steps in a signal with a threshold.

Details:
    data is analysed step-wise, comparing the average of n values before each
    value v_i with the average of m values after v_i.

Input arguments:
    v: data, array.
    thresh: threshold to detect a step.
    look_around[n,m]: values to average for comparison.
"""
import numpy as np
from matplotlib import pyplot as plt


###############################################################################


class SteppedData:
    """Class to hold the "stepped" data and its properties."""

    def __init__(self, values):
        self.values = values
        self.n_steps = 0
        self.n_plats = 0
        self.len_steps = []
        self.len_plats = []
        self.log = []
        self.ix_plat = []
        self.ix_stepup = []
        self.ix_stepdown = []
        self.values_plat = []
        self.plat_nv = []
        self.plat_mean = []
        self.plat_median = []
        self.plat_stddev = []
        self.plat_rsd = []
        self.plat_eom = []

    def detect_steps(
        self,
        look_around,
        thresh=20,  # look_around = [2, 2]
        extend_edges=True,
        plot=True,
    ):
        """You guessed it: a function to detect steps in the signal."""
        if extend_edges:
            self.values = np.insert(
                self.values, 0, np.repeat(self.values[0], look_around[0])
            )
            self.values = np.append(
                self.values, np.repeat(self.values[-1], look_around[1])
            )
        self.log = np.zeros(len(self.values))
        clrs = ["k"] * len(self.values)
        for i in range(look_around[0], len(self.values) - look_around[1]):
            before = np.average(self.values[i - look_around[0] : i])
            after = np.average(self.values[i + 1 : i + look_around[1] + 1])
            if before - after < thresh * -1:  # step up
                self.log[i], clrs[i] = 1, "r"
            if before - after > thresh:  # step down
                self.log[i], clrs[i] = -1, "b"
            if self.log[i - 1] == 0 and self.log[i] != 0:
                self.n_steps += 1
            if self.log[i - 1] != 0 and self.log[i] == 0:
                self.n_plats += 1
            if i == look_around[0] and self.log[i] == 0:
                self.n_plats += 1

        if extend_edges:
            self.values = self.values[look_around[0] : -look_around[1]]
            self.log = self.log[look_around[0] : -look_around[1]]
            clrs = clrs[look_around[0] : -look_around[1]]

        self.ix_plat = np.where(self.log == 0)
        self.values_plat = self.values[self.ix_plat]
        self.ix_stepup = np.where(self.log == 1)
        self.ix_stepdown = np.where(self.log == -1)

        for i in range(len(self.log)):
            if self.log[i] == 0:
                if not self.len_plats:
                    self.len_plats.append(0)
                self.len_plats[-1] += 1
            if self.log[i] != 0:
                if not self.len_steps:
                    self.len_steps.append(0)
                self.len_steps[-1] += 1
            if i < len(self.log) - 1:
                if self.log[i] == 0 and self.log[i + 1] != 0:
                    self.len_steps.append(0)
                if self.log[i] != 0 and self.log[i + 1] == 0:
                    self.len_plats.append(0)

        if plot:
            x_all = np.array(list(range(len(self.values))))
            x_plat = x_all[self.ix_plat]
            fig, ax = plt.subplots()
            ax.scatter(x_all, self.values, c=clrs)
            ax.plot(x_plat, self.values_plat, color="g")

        return self

    def plat_stat(self, plats_cut, use_last_n=5):  # plats_cut=[1, 1]
        """Calculate statistical parameters for each of the steps (plateaus) found in the input vector."""
        if self.n_plats == 0:
            raise ValueError("No plateaus found!")
        for i in range(self.n_plats):
            ix0 = sum(self.len_plats[0:i]) + plats_cut[0]
            ix1 = ix0 + self.len_plats[i] - sum(plats_cut)
            if (ix1 - ix0) >= use_last_n > 0:
                ix0 = ix1 - use_last_n
            ix0, ix1 = int(ix0), int(ix1)
            if ix1 - ix0 >= 1:
                self.plat_nv.append(len(self.values_plat[ix0:ix1]))
                self.plat_mean.append(np.mean(self.values_plat[ix0:ix1]))
                self.plat_median.append(np.median(self.values_plat[ix0:ix1]))
                if ix1 - ix0 > 1:
                    self.plat_stddev.append(np.std(self.values_plat[ix0:ix1]))
                    self.plat_eom.append(
                        self.plat_stddev[-1] / np.sqrt(self.plat_nv[-1])
                    )
                    self.plat_rsd.append(self.plat_stddev[-1] / self.plat_mean[-1])
                else:
                    self.plat_stddev.append(np.nan)
                    self.plat_eom.append(np.nan)
            else:
                self.plat_nv.append(0)
                self.plat_mean.append(np.nan)
                self.plat_median.append(np.nan)
                self.plat_stddev.append(np.nan)
                self.plat_eom.append(np.nan)

        return self
