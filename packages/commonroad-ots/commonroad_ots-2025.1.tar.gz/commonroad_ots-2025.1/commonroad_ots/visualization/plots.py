import numpy as np
from matplotlib import pyplot as plt, patches
import matplot2tikz
from pathlib import Path

# this is a fix for an issue with matplotlib >3.6.2 and dashed lines
from matplotlib.lines import Line2D
from matplotlib.legend import Legend

Line2D._us_dashSeq = property(lambda self: self._dash_pattern[1])
Line2D._us_dashOffset = property(lambda self: self._dash_pattern[0])
Legend._ncol = property(lambda self: self._ncols)

export_plots = True


def draw_multi_plot(data, warmup, legend, title, caption, xlabel, ylabel, max_y, min_y=0, mean=0, std=0):
    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(10)
    for i in range(len(data)):
        d = data[i]
        linestyle = "solid"
        if i == 0 and mean > 0:
            linestyle = "dashed"
        ax.plot(d[0], d[1], linewidth=2.0, linestyle=linestyle)
    ax.legend(legend)
    if not export_plots:
        plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.figtext(0.5, 0.01, caption, horizontalalignment="center")
    plt.ylim(min_y, max_y)
    if mean > 0:
        rect = patches.Rectangle(
            (warmup, mean - std),
            max(data[0][0]) - warmup,
            2 * std,
            linewidth=1,
            edgecolor="lightblue",
            facecolor="lightblue",
            label="_nolegend_",
        )
        ax.add_patch(rect)
    if warmup > 0:
        plt.axvline(x=warmup, color="r", label="warmup")
    if export_plots:
        dir = Path(__file__).parents[2].joinpath("figures")
        dir.mkdir(parents=True, exist_ok=True)
        matplot2tikz.save(f"{dir}/{title.replace(' ', '_')}.tikz")
    plt.show()


def draw_bar_plot(delays, labels, median, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(15)
    x_data = np.linspace(0, len(delays) - 1, len(delays))
    ax.bar(x_data, delays, width=0.8, align="center")
    ax.hlines(y=median, xmin=0, xmax=len(delays) - 1, linewidth=2.0, color="orange")
    plt.xticks(x_data, labels, horizontalalignment="center", rotation=70)
    if not export_plots:
        plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if export_plots:
        dir = Path(__file__).parents[2].joinpath("figures")
        dir.mkdir(parents=True, exist_ok=True)
        matplot2tikz.save(f"{dir}/{title.replace(' ', '_')}.tikz")
    plt.show()
