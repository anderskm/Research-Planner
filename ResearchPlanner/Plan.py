import copy
import csv
import json
import folium
import numpy as np
from scipy.spatial import distance
from sklearn.cluster import *

from Point import Point
from Plot import Plot
from Block import Block
from Field import Field
#from openpyxl import load_workbook # For readin xls(x)-files

class Plan(object):

    plots = None
    field = None

    def __init__(self):
        pass

    def read_plot_json(self, filename):
        # # Loads, sets and returns a research plan from a json-file.
        # fob = open(filename,'r')
        # plan = json.load(fob)
        # self.plan = plan
        # return self.plan
        pass

    def read_plot_csv(self, filename, is_utm=False, is_latlon=False, utm_zone=None, work=True, hitch_height=0.6, working_speed=1.0, pto_rpm=0):
        # Assumes, that csv-file has no header and 4 columns: latitude, longitude, altitude, and id.
        # If is_utm or is_latlon is set to True, it will try to reinforce that interpretation. Otherwise, it will try to guess it based on the size of the numbers.

        plot_id = []

        P = []
        with open(filename, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in csvreader:
                if (is_utm):
                    P.append(Point(north=float(row[0]), east=float(row[1]), altitude=float(row[2])))
                elif (is_latlon):
                    P.append(Point(latitude=float(row[0]), longitude=float(row[1]), altitude=float(row[2])))
                else:
                    P.append(Point(x=float(row[0]), y=float(row[1]), altitude=float(row[2])))
                plot_id.append(str(row[3]))

        plot_ids_unique = list(set(plot_id))

        # Sort plots by numeric ID
        try:
            plot_ids_unique.sort(key=lambda x: int(x))
        except ex:
            print('Could not sort plots automatically by number.')
            pass

        plots = []
        for this_id in plot_ids_unique:
            corner_points = [p for p, i in zip(P,plot_id) if (i == this_id)]
            assert(len(corner_points) == 4)
            
            plot = Plot(corners=corner_points, ID=this_id, work=work, hitch_height=hitch_height, working_speed=working_speed, pto_rpm=pto_rpm)
            plots.append(plot)

        # self.plots = plots

        self.blocks = copy.deepcopy(self._cluster_plots_into_blocks(plots))

    # def from_plot_xls(self, filename, sheetname=None, sheetIdx=0):
    #     wb = load_workbook(filename) # https://openpyxl.readthedocs.io/en/stable/usage.html#read-an-existing-workbook
    #     if (sheetname is None):
    #         sheetnames = wb.sheetnames
    #         sheetname = sheetnames[sheetIdx]
    #     print(sheetname)
    #     sheet = wb[sheetname]

    #     # Read header
    #     sheet.row

    #     # Read body
        
    #     for row in sheet.rows:
    #         print(row[0].value)
    #     pass

    def read_field_csv(self, filename, is_utm=False, is_latlon=False):

        P = []
        with open(filename, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                if (is_utm):
                    P.append(Point(north=float(row[0]), east=float(row[1]), altitude=float(row[2])))
                elif (is_latlon):
                    P.append(Point(latitude=float(row[0]), longitude=float(row[1]), altitude=float(row[2])))
                else:
                    P.append(Point(x=float(row[0]), y=float(row[1]), altitude=float(row[2])))

        self.field = Field(points=P)

    def export_plots_to_robotti(self, filename):

        rows = []

        for plot in self.plots:
            A = {'latitude': float(plot.ab_line[0].latitude), 'longitude': float(plot.ab_line[0].longitude)}
            B = {'latitude': float(plot.ab_line[1].latitude), 'longitude': float(plot.ab_line[1].longitude)}
            ab_line = {'A': A, 'B': B}

            point_1 = {'latitude': float(plot.end_points[0].latitude), 'longitude': float(plot.end_points[0].longitude)}
            point_2 = {'latitude': float(plot.end_points[1].latitude), 'longitude': float(plot.end_points[1].longitude)}

            plot_dict = {'id': plot.ID,
                         'point_1': point_1,
                         'point_2': point_2,
                         'work': 0 if plot.work is False else 1,
                         'hitch_height': plot.hitch_height,
                         'working_speed': plot.working_speed,
                         'pto_rpm': plot.pto_rpm}
            row = {'ab_line': ab_line,
                    'plots': [plot_dict],
                    'ignored': 0 if plot.ignored is False else 1,
                    'force_direction': 0 if plot.force_direction is False else 1}
            rows.append(row)
        robotti_plan = {'rows': rows}

        fob = open(filename, 'w')
        json.dump(robotti_plan, fob, indent=3)

    def export_plots_to_field_surveyor(self, filename, useUTM=True):
        coordinates = []
        for plot in self.plots:
            if (useUTM):
                A = [float(plot.ab_line[0].east), float(plot.ab_line[0].north)]
                B = [float(plot.ab_line[1].east), float(plot.ab_line[1].north)]
            else:
                A = [float(plot.ab_line[0].longitude), float(plot.ab_line[0].latitude)]
                B = [float(plot.ab_line[1].longitude), float(plot.ab_line[1].latitude)]
            coordinates.append([A, B])
        field_surveyor_plan = {"type": "MultiLineString",
                               "coordinates": coordinates}
        
        fob = open(filename, 'w')
        json.dump(field_surveyor_plan, fob, indent=3)

    def export_field(self, filename):

        field_dict = [{'latitude': float(point.latitude), 'longitude': float(point.longitude)} for point in self.field.points]

        robotti_field = {'field': field_dict}

        fob = open(filename, 'w')
        json.dump(robotti_field, fob, indent=3)

    def to_json(self, filename):
        # fob = open(filename, 'w')
        # json.dump(self.plan, fob, indent=3)
        pass

    def _cluster_plots_into_blocks(self, plots):
        plot_centers = []
        for plot in plots:
            plot_centers.append([plot.center.east, plot.center.north])
        cm_distances = distance.squareform(distance.pdist(plot_centers))
        distance_thresh = np.median([plot.width for plot in plots])*1.5
        connectivity = np.logical_and(cm_distances < distance_thresh, cm_distances > 0).astype(int)
        connectivity_arrays = np.nonzero(connectivity)
        connectivity_list = [[] for i in range(len(plot_centers))]
        for ca_r, ca_c in zip(connectivity_arrays[0], connectivity_arrays[1]):
            connectivity_list[ca_r].append(ca_c)


        def assign_cluster_recursive(p, new_cluster_id):
            for p2 in p:
                if cluster_ids[p2]:
                    continue
                cluster_ids[p2] = new_cluster_id
                assign_cluster_recursive(connectivity_list[p2], new_cluster_id)

        cluster_ids = np.zeros((len(connectivity_list),1))
        for p, c in zip(connectivity_list, cluster_ids):
            if c:
                continue

            new_cluster_id = cluster_ids.max()+1
            c = new_cluster_id

            assign_cluster_recursive(p, new_cluster_id)
            pass

        blocks = []
        for cluster in np.unique(cluster_ids):
            block_plots = [plot for plot, cluster_id in zip(plots, cluster_ids) if cluster_id == cluster]
            blocks.append(Block(cluster, block_plots))

        return blocks

        # for cluster, plot in zip(cluster_id, self.plots):
            # plot.block = int(cluster)

    def _smooth_route(self, start_ID=None):

        # Select starting plot
        if start_ID is None:
            end_points = []
            for plot in self.plots:
                for end_point in plot.end_points:
                    end_points.append([end_point.east, end_point.north])
            center_point = np.mean(end_points, axis=0)
            end_point_distances = np.sqrt(np.sum(np.power(end_points - center_point, 2), axis=1))
            max_distance_idx = np.argmax(end_point_distances)
            plot_idx = int(max_distance_idx/2)
            self.plots = self.plots[plot_idx:] + self.plots[:plot_idx]
            if (max_distance_idx % 2):
                self.plots[0]._swap_ends()

        # TODO: For each plot, swap ends so the first end points is closest to the last end point of the previous plot
        for prev_plot, next_plot in zip(self.plots[0:-1], self.plots[1:]):
            if prev_plot.end_points[-1].distance(next_plot.end_points[0]) > prev_plot.end_points[-1].distance(next_plot.end_points[-1]):
                next_plot._swap_ends()
                # print(prev_plot.ID, next_plot.ID, 'Swapped')

    def _draw_route(self, ax):
        waypoints = []
        segment_id = []
        self._smooth_route()
        for idx, plot in enumerate(self.plots):
            for point in plot.ab_line:
                waypoints.append((point.latitude, point.longitude))
            segment_id.append(idx)
            segment_id.append(-1)
        # folium.PolyLine(waypoints, color='blue', weight=1, opacity=1).add_to(ax)
        folium.ColorLine(waypoints, colors=segment_id[:-1], colormap=("blue", "red")).add_to(ax)
        folium.Marker(location=waypoints[0], color='blue', popup='Start').add_to(ax)
        folium.Marker(location=waypoints[-1], color='red', popup='Stop').add_to(ax)

    def draw(self, ax=None, show_ID=True, show_plot=True, show_AB_line=True, show_AB=True, show_end_points=True, hide_idle_plots=True, show_field=True):
        bounds = [(np.Inf, np.Inf),(-np.Inf, -np.Inf)]  # [southwest, northeast] bounding box of plots and field

        #TODO: draw field

        if (self.blocks is not None):
            for block in self.blocks:
                _bounds = block.draw(ax=ax, show_ID=show_ID, show_plot=show_plot, show_AB_line=show_AB_line, show_AB=show_AB, show_end_points=show_end_points)
                bounds[0] = tuple(np.minimum(_bounds[0], bounds[0]))
                bounds[1] = tuple(np.maximum(_bounds[1], bounds[1]))

        return bounds
