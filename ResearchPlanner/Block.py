import copy
import numpy as np

from Plot import Plot

class Block(object):
    def __init__(self, ID=None, plots=None):
        self.ID = ID
        self.plots = copy.deepcopy(plots)

        self._sort_plots()

    def _sort_plots(self):
        # TODO: Sort plots by distance from center. Choose plot furthest from center as starting point
        pass

    def draw(self, ax=None, show_ID=True, show_plot=True, show_AB_line=True, show_AB=True, show_end_points=True, hide_idle_plots=True):
        color_names = ['red', 'blue', 'green', 'purple', 'orange', 'darkred','lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
        bounds = [(np.Inf, np.Inf),(-np.Inf, -np.Inf)]  # [southwest, northeast] bounding box of block
        if (self.plots is not None):

            for idx, plot in enumerate(self.plots):

                if (hide_idle_plots and (not plot.work or plot.ignored)):
                    idle_alpha = 0.3
                else:
                    idle_alpha = 1.0

                # _bounds = plot.draw(ax=ax, show_ID=show_ID, show_plot=show_plot, show_AB_line=show_AB_line, show_AB=show_AB, show_end_points=show_end_points, idle_alpha=idle_alpha, color=color_names[int(self.ID)])
                _bounds = plot.draw(ax=ax, show_ID=show_ID, show_plot=show_plot, show_AB_line=show_AB_line, show_AB=show_AB, show_end_points=show_end_points, idle_alpha=idle_alpha, color=color_names[idx % len(color_names)])
                bounds[0] = tuple(np.minimum(_bounds[0], bounds[0]))
                bounds[1] = tuple(np.maximum(_bounds[1], bounds[1]))

        return bounds