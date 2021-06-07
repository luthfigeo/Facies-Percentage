
import os
import pandas as pd
import csv
import matplotlib
import sys
import lasio
import numpy as np
from os.path import dirname, realpath, join
from PyQt5 import QtCore,QtWidgets,QtGui
from PyQt5.QtWidgets import QApplication,QVBoxLayout,QMainWindow,QAction,QPushButton,QTableWidget,QTextEdit,QTableWidgetItem,QFileDialog,QLabel,QMessageBox,QDialog,QWidget
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from mpl_toolkits.mplot3d import axis3d ,axes3d
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.uic import loadUiType
from PyQt5.QtCore import Qt,QDir
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolBar
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
from sys import argv


#QtDesigner File
scriptDir = dirname(realpath(__file__))
FROM_MAIN, _ = loadUiType(join(dirname(__file__), "faciespercentage.ui"))

#Build UI
class Main(QMainWindow, FROM_MAIN):
    def __init__(self, parent = FROM_MAIN):
        super(Main, self).__init__()

        QMainWindow.__init__(self)
        self.setupUi(self)
        self.ToolBar()
        self.canvas = Canvas()
        self.button = QPushButton("% Facies Per Interval")
        self.button.setIcon(QIcon('icons/plotbar.png'))
        self.button.clicked.connect(self.PlotBar)
        self.textedit = QTextEdit()
        self.toolbar = NavigationToolBar(self.canvas, self)
        self.fr = QVBoxLayout(self.frame)
        self.fr.addWidget(self.button)
        self.fr.addWidget(self.canvas)
        self.fr.addWidget(self.toolbar)




    def ToolBar(self):
        menubar = self.menuBar()

        # Menubar horizontal
        fileMenu = menubar.addMenu('File')
        editMenu = menubar.addMenu('Edit')
        plotMenu = menubar.addMenu('Plot')
        helpMenu = menubar.addMenu('Help')
        fileToolBar = self.addToolBar('File')
        editToolBar = self.addToolBar('Edit')
        plotToolBar = self.addToolBar('Plot')
        self.addToolBar(Qt.LeftToolBarArea, plotToolBar)
        dataToolBar = self.addToolBar ('Show Data')
        self.addToolBar(Qt.LeftToolBarArea, dataToolBar)

        # File Menu
        self.textAction = QAction("&Text File", self)
        self.textAction.setIcon(QIcon('icons/open.svg'))
        self.lasAction = QAction("LAS", self)
        self.lasAction.setIcon(QIcon('icons/las.png'))
        self.topsAction = QAction("WELL TOP", self)
        self.topsAction.setIcon(QIcon('icons/top.png'))
        self.editAction = QAction("&Edit", self)
        self.editAction.setIcon(QIcon('icons/edit.svg'))
        self.saveAction = QAction("&Save", self)
        self.saveAction.setIcon(QIcon('icons/save.svg'))
        self.saveasAction = QAction("&Save As", self)
        self.saveasAction.setIcon(QIcon('icons/saveas.png'))

        openMenu = fileMenu.addMenu("Open Data")
        openMenu.addAction(self.textAction)
        openMenu.addAction(self.lasAction)
        openMenu.addAction(self.topsAction)
        fileMenu.addAction(self.editAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveasAction)
        fileToolBar.addAction(self.textAction)
        fileToolBar.addAction(self.lasAction)
        fileToolBar.addAction(self.topsAction)
        fileToolBar.addAction(self.editAction)
        fileToolBar.addAction(self.saveAction)
        fileToolBar.addAction(self.saveasAction)
        self.textAction.triggered.connect(self.opentextfile)
        self.lasAction.triggered.connect(self.openlasfile)
        self.topsAction.triggered.connect(self.opentopsfile)
        self.saveasAction.triggered.connect(self.outfile)

        # Edit Menu
        self.copyAction = QAction("&Copy", self)
        self.copyAction.setIcon(QIcon('icons/copy.svg'))
        self.pasteAction = QAction("&Paste", self)
        self.pasteAction.setIcon(QIcon('icons/paste.svg'))
        self.cutAction = QAction("&Cut", self)
        self.cutAction.setIcon(QIcon('icons/cut.svg'))
        self.dataAction = QAction("Show Data", self)
        self.dataAction.setIcon(QIcon('icons/push.png'))
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.cutAction)
        editToolBar.addAction(self.copyAction)
        editToolBar.addAction(self.pasteAction)
        editToolBar.addAction(self.cutAction)
        dataToolBar.addAction(self.dataAction)

        # Find and Replace submenu in the Edit menu
        findMenu = editMenu.addMenu("Find and Replace")
        self.findAction = QAction ("Find", self)
        self.replaceAction = QAction ("Replace", self)
        findMenu.addAction(self.findAction)
        findMenu.addAction(self.replaceAction)

        # Plot Menu
        self.tabledataAction = QAction("&Table Data", self)
        self.tabledataAction.setIcon(QIcon('icons/table.png'))
        self.plot2Action = QAction("&2D Plot", self)
        self.plot2Action.setIcon(QIcon('icons/plot2d.png'))
        self.plot3Action = QAction("&3D Plot", self)
        self.plot3Action.setIcon(QIcon('icons/plot3d.png'))
        self.plotbarAction = QAction("&Bar Chart", self)
        self.plotbarAction.setIcon(QIcon('icons/plotbar.png'))
        self.zoominAction = QAction("Zoom In Plot", self)
        self.zoominAction.setIcon(QIcon('icons/zoomin.svg'))
        self.zoomoutAction = QAction("Zoom Out Plot", self)
        self.zoomoutAction.setIcon(QIcon('icons/zoomout.svg'))
        plotMenu.addAction(self.tabledataAction)
        plotMenu.addAction(self.plot2Action)
        plotMenu.addAction(self.plot3Action)
        plotMenu.addAction(self.plotbarAction)
        plotToolBar.addAction(self.tabledataAction)
        plotToolBar.addAction(self.plot2Action)
        plotToolBar.addAction(self.plot3Action)
        plotToolBar.addAction(self.plotbarAction)
        plotToolBar.addAction(self.zoominAction)
        plotToolBar.addAction(self.zoomoutAction)
        self.tabledataAction.triggered.connect(self.table)
        self.plot2Action.triggered.connect(self.Plot2D)
        self.plot3Action.triggered.connect(self.Plot3D)
        self.plotbarAction.triggered.connect(self.PlotBar)
        self.zoominAction.triggered.connect(self.zoom)
        self.zoomoutAction.triggered.connect(self.zoom)

        # Help Menu
        self.workflowAction = QAction("&Workflow", self)
        self.workflowAction.triggered.connect(self.workflow)
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)
        helpMenu.addAction(self.workflowAction)
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)
        self.helpContentAction.triggered.connect(self.help)

    def textedit(self):
        self.textedit = QTextEdit(self)
        self.canvas.textedit()

    def workflow(self):
        self.canvas.workflow()

    def opentextfile(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', 'data/', "Text files (*.txt);; All files (*)")
        if filename[0]!='':
            self.path=filename[0]
            print(self.path)

    def zoom(self):
        self.toolbar.zoom(self)

    def savefile(self):
        self.toolbar.save_figure(self)

    def help(self):
        QMessageBox.critical(self, 'Help', "Facies Interval")

    def Plot2D(self):
        inputdata=self.path

        x = []
        y = []

        with open(inputdata, 'r') as f:
            plots = csv.reader(f, delimiter='\t')
            for row in plots:
                x.append(float(row[0]))
                y.append(float(row[1]))

        self.canvas.plot2(x, y)

    def Plot3D(self):
        inputdata=self.path

        x = []
        y = []
        z = []

        with open(inputdata, 'r') as f:
            plots = csv.reader(f, delimiter='\t')
            for row in plots:
                x.append(float(row[0]))
                y.append(float(row[1]))
                z.append(float(row[2]))

        self.canvas.plot3(x, y, z)

    def openlasfile(self):
        lasfile = QFileDialog.getOpenFileName(self, 'Open LAS', 'data/', "LAS files (*.las)")[0]
        print(lasfile)
        return lasfile

    def opentopsfile(self):
        topsfile = QFileDialog.getOpenFileName(self, 'Open Tops', 'data/', "Tops files (*.txt)")[0]
        print(topsfile)
        return topsfile

    def table(self):
        self.canvas.tableview()

    # Function to add your lasfile and embed the tops of intervals
    # source_dir = directory of your data
    # lasfile = LAS file name
    # topsfile = Tops data file name
    def InputWell(self, gr, rhob):
        lasfile = QFileDialog.getOpenFileName(self, 'Open LAS', 'data/', "LAS files (*.las)")[0]
        topsfile = QFileDialog.getOpenFileName(self, 'Open Tops', 'data/', "Tops files (*.txt)")[0]

        # Import your LAS file and convert it to a dataframe
        l = lasio.read(lasfile)
        data = l.df()
        data = data.replace('-999.00000', np.nan)
        data.index.names = ['DEPT']
        well = l.well.WELL.value  # This contain your well name
        data['WELL'] = well  # This contain your log data

        # Import your tops of interval
        tops = pd.read_csv(topsfile, sep='\t')
        tops_unit = tops['ROCK UNIT'].unique()  # This contain list of interval, adjust the column name to suit yours

        # Assign interval name to each point in your log data
        data_well = pd.DataFrame()
        for i in range(len(tops_unit)):
            top = tops.iloc[i]['DEPTH']
            if i < len(tops_unit) - 1:
                bottom = tops.iloc[i + 1]['DEPTH']
            else:
                bottom = int(round(data.tail(1).index.item()))
            data_interval = data.iloc[top:bottom, :]
            data_interval['INTERVAL'] = tops.iloc[i]['ROCK UNIT']
            data_well = data_well.append(data_interval)
        data = data_well


    # Function to determine lithology based on several conditions
    # data = your log data
    # gr = column number of GR log in your data
    # rhob = column number of RHOB log in your data

        GR = data.iloc[:, gr]
        RHOB = data.iloc[:, rhob]

        # each condition refer to its lithology in following order, adjust to your specifications
        conditions = [
            (GR <= 55) & (RHOB >= 2.71),
            (GR <= 55) & (RHOB >= 2.65),
            (GR <= 55) & (RHOB > 1.8),
            (GR <= 55) & (RHOB < 1.8),
            (GR <= 80),
            (GR >= 80)]
        lithology = ['Dolomite', 'Limestone', 'Sandstone', 'Coal', 'Siltstone', 'Shale']
        data['LITHOLOGY'] = np.select(conditions, lithology, default='Undefined', )
        return well, data


    # Function to calculate facies percentage for multiwell
    # data = your log data which already contain well name, interval name, and lithology each as a column

    def CalculatePercentage(self):
        well, data = Main.InputWell(self, 1, 7)

        data_well = pd.DataFrame()
        data_interval = pd.DataFrame()
        F_well = pd.DataFrame()
        Facies = pd.DataFrame()

        for i in range(len(Main.well)):
            data_well = data.where(data['WELL'] == well[i]).dropna()
            interval = data_well['INTERVAL'].unique()
            for j in range(len(interval)):
                data_interval = data_well.where(data_well['INTERVAL'] == interval[j]).dropna()
                F_percent = data_interval['LITHOLOGY'].value_counts(normalize=True) * 100
                F_percent = F_percent.sort_index()
                F_percent['INTERVAL'] = interval[j]
                F_percent = pd.DataFrame(F_percent).transpose()
                F_well = F_well.append(F_percent)
            F_well['WELL'] = Main.well[i]
            F_well = F_well.set_index('WELL')
            Facies = Facies.append(F_well)
            F_well = pd.DataFrame()

        Facies = Facies.reset_index()
        Facies = Facies.fillna(0)
        return Facies

    # Function to calculate facies percentage for single well
    # well = your well name
    # data = your log data which already contain well name, interval name, and lithology each as a column

    def CalculatePercentageSingleWell(self):
        well, data = Main.InputWell(self, 1, 7)

        data_well = pd.DataFrame()
        data_interval = pd.DataFrame()
        F_well = pd.DataFrame()
        Facies = pd.DataFrame()
        tops_unit = data['INTERVAL'].unique()

        for i in range(len(tops_unit)):
            data_interval = data.where(data['INTERVAL'] == tops_unit[i]).dropna()
            F_percent = data_interval['LITHOLOGY'].value_counts(normalize=True) * 100
            F_percent = F_percent.sort_index()
            F_percent['INTERVAL'] = tops_unit[i]
            F_percent = pd.DataFrame(F_percent).transpose()
            F_well = F_well.append(F_percent)
        F_well['WELL'] = well
        Facies = Facies.append(F_well)
        F_well = pd.DataFrame()

        Facies = Facies.reset_index()
        Facies = Facies.fillna(0)

        return Facies

    def outfile(self):
        Facies = Main.CalculatePercentageSingleWell(self)
        outfile = 'output/Facies Percentage.csv'
        Facies.to_csv(outfile)

    def PlotBar(self):
        self.canvas.PlotBarChart()


class Canvas(FigureCanvas):
    def __init__(self, parent=None, dpi=120):
        self.fig = plt.Figure(dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

    def textedit(self):
        self.textedit = QTextEdit(self)
        self.textedit.setText(l)
        self.textedit.show()


    def workflow(self):
        self.label = QLabel(self)
        self.pixmap = QPixmap('workflow.png')
        self.label.setPixmap(self.pixmap)
        self.label.move(300, 100)
        self.label.resize(self.pixmap.width(), self.pixmap.height())
        self.label.show()

    def plot2(self,x,y):
        self.ax = self.fig.add_subplot(111)
        self.ax.scatter(x, y, color='red')
        self.ax.set(xlabel='X', ylabel='Y', title='2D')
        self.ax.grid()
        self.draw()

    def plot3(self,x,y,z):
        self.ax1 = self.fig.add_subplot(111, projection='3d')
        self.ax1.scatter(x,y,z, color='black')
        self.ax1.plot_trisurf(x,y,z, color='black', alpha = 0.2, edgecolor = 'red', linewidth = 0.1,
                             antialiased = True, shade = 1 )
        self.ax1.set(xlabel='X', ylabel='Y', zlabel='Z', title='3D')
        self.draw()

    # Function to display a horizontal barchart of your calculated facies percentage
    def PlotBarChart(self):
        facies_well = Main.CalculatePercentageSingleWell(self)  # .where(Facies['WELL']==well)
        interval = facies_well['INTERVAL'].unique()

        self.axes = self.fig.add_subplot(111)
        self.axes.set_ylabel(ylabel="Formation")
        self.axes.set_xlabel(xlabel="Facies %")
        self.axes.set_title("Walakpa-1")
        facies_well.plot.barh(x='INTERVAL', stacked=True, ax=self.axes, color = ['#FFFF00', '#27AE60', '#ABEBC6', '#000000', '#40E0D0', '#6495ED'])
        self.axes.set_yticks(range(len('INTERVAL')), 'INTERVAL')
        self.axes.set_yticklabels(interval)
        self.axes.invert_yaxis()
        self.axes.legend(bbox_to_anchor=(1.01, 1))
        self.draw()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
