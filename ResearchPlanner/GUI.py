#!/usr/bin/env python
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QDialogButtonBox, QVBoxLayout, QFormLayout, QCheckBox, QSpinBox, QDoubleSpinBox, QFileDialog, QLabel, QAction, qApp, QWidget, QMenu
import sys

import Plan as ResearchPlan


class GUI():
    def __init__(self):
        self.app = QApplication([])
        self.app.setApplicationName("Research Planner")
        self.app.setOrganizationName("Aarhus University")
        self.app.setOrganizationDomain("agro.au.dk")

    class ImportFileDialog(QFileDialog):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.setFileMode(QFileDialog.ExistingFile)

        def get_file(self, folder=None, caption='Select file', filter='All files (*.*)'):
            file_tuple = self.getOpenFileName(caption=caption, filter=filter)
            if not file_tuple[0]:
                output=None
                raise UserWarning('"' + caption + '" cancelled by user.')
            else:
                output = file_tuple[0]
            
            return output

    class ExportFileDialog(QFileDialog):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.setFileMode(QFileDialog.AnyFile)
        
        def get_file(self, folder=None, caption='Save file', filter='JSON (*.json);;All files (*.*)'):
            file_tuple = self.getSaveFileName(caption=caption, filter=filter)
            if not file_tuple[0]:
                output=None
                raise UserWarning('"' + caption + '" cancelled by user.')
            else:
                output = file_tuple[0]
            
            return output


    class PlotSettingsDialog(QDialog):

        def __init__(self, ID=None, ignore=False, force_direction=False, work=True, working_speed=1.0, hitch_height=0.6, pto_rpm=0.0, working_speed_min=1.0, working_speed_max=6.0, hitch_height_min=0.16, hitch_height_max=0.6, pto_rpm_min=0, pto_rpm_max=4000, *args, **kwargs):
            # super(PlotSettingsDialog, self).__init__(*args,**kwargs)
            super().__init__(*args,**kwargs)

            self.setWindowTitle('Plot settings')

            # Setup buttons
            self.buttonBox = QDialogButtonBox()
            self.buttonBox.addButton("Ok", QDialogButtonBox.AcceptRole)
            self.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole)
            self.buttonBox.accepted.connect(self.accept)
            self.buttonBox.rejected.connect(self.reject)

            self.ID_widget = QLabel()
            self.ID_widget.setText(str(ID))

            self.ignore_widget = QCheckBox()
            if (ignore):
                self.ignore_widget.setCheckState(Qt.Checked)
            else:
                self.ignore_widget.setCheckState(Qt.Unchecked)
            ignore_label = QLabel()
            ignore_label.setText('Ignore:')
            ignore_label.setWhatsThis('Ignored plots will never be entered during route planning.')

            self.force_direction_widget = QCheckBox()
            if (force_direction):
                self.force_direction_widget.setCheckState(Qt.Checked)
            else:
                self.force_direction_widget.setCheckState(Qt.Unchecked)
            self.force_direction_widget.setEnabled(False) #NOTE: Disable since the feature in the Robotti planner is currently disabled/not implemented
            force_direction_label = QLabel()
            force_direction_label.setText('Force A->B:')
            force_direction_label.setWhatsThis('Force the route planner to always drive in the A->B direction through plots. NOTE: This is currently disabled in the route planner.')

            self.work_widget = QCheckBox()
            if (work):
                self.work_widget.setCheckState(Qt.Checked)
            else:
                self.work_widget.setCheckState(Qt.Unchecked)
            work_label = QLabel()
            work_label.setText('Work:')
            work_label.setWhatsThis('Non-work plots may be used for traversing by the route planner. To completely avoid entering a plot use the Ignore field.')

            self.working_speed_widget = QDoubleSpinBox()
            self.working_speed_widget.setMinimum(working_speed_min)
            self.working_speed_widget.setMaximum(working_speed_max)
            self.working_speed_widget.setValue(working_speed)
            self.working_speed_widget.setSingleStep(0.5)
            self.working_speed_widget.setSuffix(' km/h')
            self.working_speed_widget.setAlignment(Qt.AlignRight)

            self.hitch_height_widget = QDoubleSpinBox()
            self.hitch_height_widget.setMinimum(hitch_height_min)
            self.hitch_height_widget.setMaximum(hitch_height_max)
            self.hitch_height_widget.setValue(hitch_height)
            self.hitch_height_widget.setSingleStep(0.05)
            self.hitch_height_widget.setSuffix(' m')
            self.hitch_height_widget.setAlignment(Qt.AlignRight)

            self.pto_rpm_widget = QSpinBox()
            self.pto_rpm_widget.setMinimum(pto_rpm_min)
            self.pto_rpm_widget.setMaximum(pto_rpm_max)
            self.pto_rpm_widget.setValue(pto_rpm)
            self.pto_rpm_widget.setSingleStep(100)
            self.pto_rpm_widget.setSuffix(' rpm')
            self.pto_rpm_widget.setAlignment(Qt.AlignRight)
            
            layout = QFormLayout()
            layout.addRow('Plot ID:', self.ID_widget)
            layout.addRow(ignore_label, self.ignore_widget)
            layout.addRow(force_direction_label, self.force_direction_widget)
            layout.addRow(work_label, self.work_widget)
            layout.addRow('Working speed:', self.working_speed_widget)
            layout.addRow('Hitch height:', self.hitch_height_widget)
            layout.addRow('PTO:', self.pto_rpm_widget)

            # Add buttons
            layout.addWidget(self.buttonBox)

            self.setLayout(layout)
            
        def get_settings(self):
            settings_dict = {'ID': self.ID_widget.text(),
                            'ignore': bool(self.ignore_widget.checkState()),
                            'force_direction': bool(self.force_direction_widget.checkState()),
                            'work': bool(self.work_widget.checkState()),
                            'working_speed': self.working_speed_widget.value(),
                            'hitch_height': self.hitch_height_widget.value(),
                            'pto_rpm': self.pto_rpm_widget.value()}
            return settings_dict

class ResearchPlannerGUI(QMainWindow):

    plan = None

    def __init__(self, app=None, plan=None, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self.plan = ResearchPlan.Plan()

        self._init_gui()

    def _init_gui(self):
        self.statusBar().showMessage('Loading GUI')
          
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Research Planner')

        ### Setup menus
        menubar = self.menuBar()
        ## "File" menu
        file_menu = menubar.addMenu('&File')

        exit_action = QAction('&Quit', self)        
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Quit Research Planner')
        exit_action.triggered.connect(qApp.quit)

        import_plots_action = QAction('Import &Plots', self)
        import_plots_action.setShortcut('Ctrl+P')
        import_plots_action.setStatusTip('Import plots')
        import_plots_action.triggered.connect(self.import_plots)

        import_field_action = QAction('Import Field', self)
        import_field_action.setShortcut('Ctrl+F')
        import_field_action.setStatusTip('Import field')
        import_field_action.triggered.connect(self.import_field)

        export_plots_action = QAction('Export Plots', self)
        export_plots_action.setStatusTip('Export plots to FieldSurveyor compatible json-format')
        export_plots_action.triggered.connect(self.export_plots)

        export_field_action = QAction('Export Field', self)
        export_field_action.setStatusTip('Export field to Robotti compatible json-format')
        export_field_action.triggered.connect(self.export_field)

        
        file_menu.addAction(import_plots_action)
        file_menu.addAction(import_field_action)
        file_menu.addSeparator()
        file_menu.addAction(export_plots_action)
        file_menu.addAction(export_field_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        ## "Edit" menu
        edit_menu = menubar.addMenu('&Edit')
        settings_all_plots_action = QAction('All Plots', self)
        settings_all_plots_action.setStatusTip('Edit the settings of all plots at once')
        settings_all_plots_action.triggered.connect(self.settings_all_plots)

        edit_menu.addAction(settings_all_plots_action)

        ## "View" menu
        view_menu = menubar.addMenu('&View')

        view_plot_action = QAction('Show plots', self, checkable=True)
        view_plot_action.setStatusTip('Toggle displaying plot outlines')
        view_plot_action.setChecked(True)
        view_plot_action.triggered.connect(self.toggle_view_plot)

        view_ab_line_action = QAction('Show AB-lines', self, checkable=True)
        view_ab_line_action.setStatusTip('Toggle displaying the AB-lines of plots')
        view_ab_line_action.setChecked(False)
        view_ab_line_action.triggered.connect(self.toggle_view_ab_line)

        view_end_points_action = QAction('Show end points', self, checkable=True)
        view_end_points_action.setStatusTip('Toggle displaying the end points of plots on the AB-line')
        view_end_points_action.setChecked(True)
        view_end_points_action.triggered.connect(self.toggle_view_end_points)

        view_field_action = QAction('Show field', self, checkable=True)
        view_field_action.setStatusTip('Toggle displaying field outlines')
        view_field_action.setChecked(True)
        view_field_action.triggered.connect(self.toggle_view_field)

        view_menu.addAction(view_plot_action)
        view_menu.addAction(view_ab_line_action)
        view_menu.addAction(view_end_points_action)
        view_menu.addSeparator()
        view_menu.addAction(view_field_action)

        self._reset_view()

        ### Setup main area
        window_widget = QWidget()
        ## Setup  figure canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.canvas.mpl_connect('pick_event', self.on_pick_event)
        ## Setup layout of window widget
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        window_widget.setLayout(layout)

        # Set window widget as central widget of main window
        self.setCentralWidget(window_widget)

        self.statusBar().showMessage('Ready')
        self.show()

    def on_pick_event(self, event):
        # print(event.artist)
        plot_id = event.artist.get_text()

        plot = None
        for idx, _plot in enumerate(self.plan.plots):
            if _plot.ID == plot_id:
                plot = _plot
                plot_idx = idx
                break

        if plot is not None:
            plotDlg = GUI.PlotSettingsDialog(ID=plot_id, ignore=plot.ignored, force_direction=plot.force_direction, work=plot.work, working_speed=plot.working_speed, hitch_height=plot.hitch_height, pto_rpm=plot.pto_rpm)
            if (plotDlg.exec_()):
                settings = plotDlg.get_settings()

                print(settings)

                plot.ignored = settings['ignore']
                plot.force_direction = settings['force_direction']
                plot.work = settings['work']
                plot.working_speed = settings['working_speed']
                plot.hitch_height = settings['hitch_height']
                plot.pto_rpm = settings['pto_rpm']

                self._update_canvas()


    def _reset_view(self):
        self._show_plots = True
        self._show_ab_lines = False
        self._show_end_points = True
        self._show_field = True

    def import_plots(self):
        self.statusBar().showMessage('Importing plots...')
        try:
            import_dlg = GUI.ImportFileDialog()
            filename_plots = import_dlg.get_file(caption='Import plots', filter='CSV (*.csv);;All files (*.*)')
            self.plan.read_plot_csv(filename_plots, is_utm=True)
                    
            self._update_canvas()

            self.statusBar().showMessage('Plots imported: ' + filename_plots)
        except UserWarning as e:
            self.statusBar().showMessage(str(e))


    def import_field(self):
        self.statusBar().showMessage('Importing field...')
        try:
            import_dlg = GUI.ImportFileDialog()
            filename_field = import_dlg.get_file(caption='Import field', filter='CSV (*.csv);;All files (*.*)')
            self.plan.read_field_csv(filename_field, is_utm=True)
            
            self._update_canvas()

            self.statusBar().showMessage('Field imported: ' + filename_field)
        except UserWarning as e:
            self.statusBar().showMessage(str(e))

    def export_plots(self):
        self.statusBar().showMessage('Exporting plots...')
        
        try:
            export_dlg = GUI.ExportFileDialog()
            filename_out_plots = export_dlg.get_file(caption='Export plots')
            self.plan.export_plots_to_field_surveyor(filename_out_plots)
            self.statusBar().showMessage('Plots exported: ' + filename_out_plots)
        except UserWarning as e:
            self.statusBar().showMessage(str(e))

    def export_field(self):
        self.statusBar().showMessage('Exporting field...')
        
        try:
            export_dlg = GUI.ExportFileDialog()
            filename_out_field = export_dlg.get_file(caption='Export field')
            self.plan.export_field(filename_out_field)
            self.statusBar().showMessage('Field exported: ' + filename_out_field)
        except UserWarning as e:
            self.statusBar().showMessage(str(e))

    def settings_all_plots(self):
        if (self.plan.plots is not None):
            plot = self.plan.plots[0]

            plotDlg = GUI.PlotSettingsDialog(ignore=plot.ignored, force_direction=plot.force_direction, work=plot.work, working_speed=plot.working_speed, hitch_height=plot.hitch_height, pto_rpm=plot.pto_rpm)
            if (plotDlg.exec_()):
                settings = plotDlg.get_settings()

                print('Settings:')
                print(settings)

                # Update all plots with settings
                for plot in self.plan.plots:
                    plot.ignored = settings['ignore']
                    plot.force_direction = settings['force_direction']
                    plot.work = settings['work']
                    plot.working_speed = settings['working_speed']
                    plot.hitch_height = settings['hitch_height']
                    plot.pto_rpm = settings['pto_rpm']

                self._update_canvas()

    def toggle_view_plot(self, state):
        if state:
            self._show_plots = True
        else:
            self._show_plots = False
        self._update_canvas()

    def toggle_view_field(self, state):
        if state:
            self._show_field = True
        else:
            self._show_field = False
        self._update_canvas()

    def toggle_view_ab_line(self, state):
        if state:
            self._show_ab_lines = True
        else:
            self._show_ab_lines = False
        self._update_canvas()

    def toggle_view_end_points(self, state):
        if state:
            self._show_end_points = True
        else:
            self._show_end_points = False
        self._update_canvas()

    def _update_canvas(self):

        self.statusBar().showMessage('Updating canvas...')
        self.ax.clear()

        self.plan.draw(ax=self.ax, show_field=self._show_field, show_plot=self._show_plots, show_AB_line=self._show_ab_lines, show_AB=self._show_ab_lines, show_end_points=self._show_end_points)

        ResearchPlan.plt.show()

        self.canvas.draw()
        self.statusBar().showMessage('Canvas updated')

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = ResearchPlannerGUI()
    main.show()

    sys.exit(app.exec_())