#!/usr/bin/env python

# Nordic ARC Utilities
# Copyright (C) 2019  Nordic ARC Node
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from __future__ import print_function
from casacore.tables import table, taql
import numpy as np
from argparse import ArgumentParser
import warnings

try:
    import matplotlib.pyplot as plt
    CAN_PLOT = True
except ImportError:
    warnings.warn("Could not import matplotlib. Plotting disabled.")
    CAN_PLOT = False


class MSInfo(object):
    def __init__(self, msname):
        self.msname = msname
        self._validate()
    
    def contains_table(self, subtable_name):
        try:
            table("{ms}::{subtable}".format(ms=self.msname, subtable=subtable_name), ack=False)
        except:
            return False
        else:
            return True

    def table(self, table_name="MAIN"):
        if table_name.upper() == "MAIN":
            return table(self.msname, ack=False)
        elif self.contains_table(table_name):
            return table("{ms}::{subtable}".format(ms=self.msname, subtable=table_name), ack=False)
        else:
            raise KeyError("Could not open {} table".format(table_name))

    def _validate(self):
        assert self.contains_table("SPECTRAL_WINDOW")
        assert self.contains_table("DATA_DESCRIPTION")
        assert self.contains_table("FIELD")
        assert self.contains_table("STATE")

    def spw_ids_used(self, intent_pattern="*", field_name_pattern="*", exact_match=False):
        if not exact_match:
            intent_pattern = "*" + intent_pattern + "*"
            field_name_pattern = "*" + field_name_pattern + "*"
        vtab = taql("""select SPECTRAL_WINDOW_ID as SPW from {ms}::DATA_DESCRIPTION where
                        rowid() in [select unique DATA_DESC_ID from {ms} where
                            (STATE_ID in [select rowid() from ::STATE where OBS_MODE = pattern('{intent}')]
                                and
                             FIELD_ID in [select rowid() from ::FIELD where NAME = pattern('{field}')])];
                    """.format(ms=self.msname, intent=intent_pattern, field=field_name_pattern))
        return vtab.getcol("SPW")

    def spw_coverage(self, spw_ids=None):
        if spw_ids is None:
            qtab = taql("select REF_FREQUENCY, TOTAL_BANDWIDTH from {ms}::SPECTRAL_WINDOW".format(ms=self.msname))
        else:
            qtab = taql("""select REF_FREQUENCY, TOTAL_BANDWIDTH from {ms}::SPECTRAL_WINDOW 
                            where rowid() in {spw_ids}""".format(ms=self.msname, spw_ids=list(spw_ids)))
        ref_freq = qtab.getcol("REF_FREQUENCY")
        bandwidth = qtab.getcol("TOTAL_BANDWIDTH")
        return np.vstack((ref_freq - bandwidth/2, ref_freq + bandwidth/2)).T


class MSFrequencyPlotter(object):
    def __init__(self, *ms_list):
        assert CAN_PLOT
        self.ms_list = ms_list

    @staticmethod
    def unit_to_divisor(unit):
        divisors = {"HZ": 1e0, "KHZ": 1e3, "MHZ": 1e6, "GHZ": 1e9, "THZ": 1e12}
        return divisors[unit.upper()]

    def plot(self, intent="OBSERVE_TARGET", quick=False, unit="Hz", yaxis_labels=False):
        fig = plt.figure(1)
        axes = fig.add_subplot(1, 1, 1)
        y_ticks = []
        y_labels = []
        lines = []
        colours = ['b', 'g', 'r', 'c', 'm', 'y']
        for i, msname in enumerate(self.ms_list):
            ms_info = MSInfo(msname)
            y_ticks.append(i+1)
            y_labels.append(msname)
            colour = colours[i % len(colours)]
            if quick:
                freqs = ms_info.spw_coverage()
            else:
                freqs = ms_info.spw_coverage(ms_info.spw_ids_used(intent))
            for j, f in enumerate(freqs):
                freq_plot = f / self.unit_to_divisor(unit)
                tmp = axes.plot(freq_plot, np.full_like(freq_plot, i+1), colour) 
                if j == 0:
                    # Store the first line for each ms so we can legend it
                    lines.append(tmp[0])

        legend_labels = ["{}: {}".format(i+1, name) for i, name in enumerate(self.ms_list)]
        axes.legend(lines, legend_labels)
        axes.set_ylim(0, len(self.ms_list) + 1)
        axes.set_xlabel("Frequency ({unit})".format(unit=unit))
        axes.set_title("Frequency Coverage")
        fig.canvas.set_window_title("Frequency Coverage")
        if yaxis_labels:
            plt.yticks(y_ticks, y_labels)
        else:
            plt.yticks(y_ticks)
        plt.show()


def command_line_frequency_plotter():
    parser = ArgumentParser("Plot the frequency coverage of one or more Measurement Sets")
    parser.add_argument("-q", "--quick", action="store_true", default=False, help="Plot all Spectral Windows in MS. Default is to scan for SPWs used with INTENT=OBSERVE_TARGET")
    parser.add_argument("-u", "--unit", type=str, default="GHz", help="Frequency unit to plot. Default is 'GHz'")
    parser.add_argument("-y", "--ylabels", action="store_true", default=False, help="Put labels on y-axis. Default is to plot legend only.")
    parser.add_argument("ms", type=str, nargs="+", help="Measurement Set(s) to plot")
    args = parser.parse_args()
    MSFrequencyPlotter(*args.ms).plot(quick=args.quick, unit=args.unit, yaxis_labels=args.ylabels)

