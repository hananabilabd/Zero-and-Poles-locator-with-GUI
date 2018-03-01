import numpy as np
from scipy.signal import zpk2ss, ss2zpk, tf2zpk, zpk2tf
from numpy import linspace, logspace
from numpy import asarray, tan, array, pi, arange, cos, log10, unwrap, angle
from matplotlib.pyplot import axvline, axhline
from scipy.signal import freqz
import matplotlib.pyplot as plt
from PyQt4.uic import loadUiType

import matplotlib.backends.backend_qt4agg
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from PyQt4.QtGui import *
import cPickle
import pickle
import copy ,copyreg
Ui_MainWindow, QMainWindow = loadUiType('zero_poles.ui')


class Main(QMainWindow, Ui_MainWindow):

    """
    Demonstrates a basic example of the "scaffolding" you need to efficiently
    blit drawable/draggable/deleteable artists on top of a background.
    """

    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)

        pixmap = QPixmap('x.jpg')
        self.label.setPixmap(pixmap)

        #self.fig, self.ax = plt.subplots()
        self.fig = plt.figure()
        plt.axis('scaled')
        plt.axis([-1, 1, -1, 1])
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.circle = plt.Circle((0, 0), 1, fill=False)
        self.ax.add_patch(self.circle)
        axvline(0, color='0.3')
        axhline(0, color='0.3')
        self.ax.plot()

        self.canvas = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg(self.fig)
        self.verticalLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.ax.set_title('Left click to add/drag a point\nRight-click to delete')
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.addToolBar(self.toolbar)

        self.figure2 = Figure()
        self.drawing2 = self.figure2.add_subplot(111)
        self.figure2.suptitle('Frequency Response')
        self.drawing2.plot()
        self.drawing2.set_xlabel('Normalized frequency',fontsize = 9)
        self.drawing2.set_ylabel('Amplitude[dB]', fontsize=9)
        self.canvas2 = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg(self.figure2)
        self.verticalLayout_2.addWidget(self.canvas2)
        self.canvas2.draw()
        self.toolbar = NavigationToolbar(self.canvas2, self, coordinates=True)
        self.addToolBar(self.toolbar)

        # self.fig, self.ax = self.setup_axes()
        self.xy = [] #for the circle
        self.xy2 = []
        self.zero = [] #for trans func
        self.poles = []
        self.tolerance = 10
        #self._num_clicks = 0
        self.points = self.ax.scatter([], [], s=30, color='blue',
                                      picker=self.tolerance, animated=True) #for zeros
        self.points2 = self.ax.scatter([], [], s=30, color='red',
                                      picker=self.tolerance, animated=True) #for poles


        connect = self.fig.canvas.mpl_connect
        connect('button_press_event', self.on_click)
        self.draw_cid = connect('draw_event', self.grab_background)

        self.pushButton.clicked.connect(self.browse)
        self.pushButton_2.clicked.connect(self.file_save)
        self.pushButton_3.clicked.connect(self.reset)

        #self.radioButton.toggled.connect(self.setup)







    def reset(self):
        if self.radioButton.isChecked() == True:
            index = len(self.xy) -2
            while 0 <= index :

                self.delete_point(index)
                index -= 2
        if self.radioButton_2.isChecked() == True:
            index = len(self.xy2) - 2
            while 0 <= index:
                self.delete_point(index)
                index -= 2




    def on_click(self, event):
        """Decide whether to add, delete, or drag a point."""
        # If we're using a tool on the toolbar, don't add/draw a point...
        # if self.fig.canvas.toolbar._active is not None:
        # return
        if self.radioButton.isChecked() == True:

            contains, info = self.points.contains(event)

            if contains:
                i = info['ind'][0]
                if event.button == 1:
                    self.start_drag(i)
                elif event.button == 3:

                    self.delete_point(i)
            else:

                self.x=event.xdata
                self.y=event.ydata
                self.add_point()

        if self.radioButton_2.isChecked() == True:
            contains2, info2 = self.points2.contains(event)

            if contains2:
                i = info2['ind'][0]
                if event.button == 1:
                    self.start_drag(i)
                elif event.button == 3:
                    self.delete_point(i)
            else:
                self.x2 = event.xdata
                self.y2 = event.ydata
                self.add_point()


    def update(self):
        """Update the artist for any changes to self.xy."""
        if self.radioButton.isChecked() == True:

            self.points.set_offsets(self.xy)
            self.blit()
        if self.radioButton.isChecked() == False:
            self.points2.set_offsets(self.xy2)
            self.blit()

    def add_point(self):
        if self.radioButton.isChecked() == True:
            #limitation of circle
            if ((self.x) ** 2 + (self.y) ** 2) ** 0.5 < 1 and self.y > 0:
                z = self.x + self.y * 1j

                self.xy.append([self.x, self.y])
                self.xy.append([self.x, -self.y])


                self.zero.append(z)
                print (self.zero)
                #print (self.xy)
                self.update()
                self.drawOn2()
        if self.radioButton_2.isChecked() == True:
            if ((self.x2) ** 2 + (self.y2) ** 2) ** 0.5 < 1 and self.y2 > 0:
                z = self.x2 + self.y2 * 1j

                self.xy2.append([self.x2, self.y2])
                self.xy2.append([self.x2, -self.y2])
                self.poles.append(z)
                print (self.poles)
                self.update()
                self.drawOn2()



    def delete_point(self, i):
        if self.radioButton.isChecked() == True:
            self.xy.pop(i)
            self.xy.pop()
            self.zero.pop()
            print (self.zero)

            self.update()
            self.drawOn2()
        if self.radioButton.isChecked() == False:
            self.xy2.pop(i)
            self.xy2.pop()
            self.poles.pop()
            print (self.poles)
            self.update()
            self.drawOn2()

    def start_drag(self, i):
        """Bind mouse motion to updating a particular point."""
        if self.radioButton.isChecked() == True:

            self.drag_i = i
            connect = self.fig.canvas.mpl_connect
            cid1 = connect('motion_notify_event', self.drag_update)
            cid2 = connect('button_release_event', self.end_drag)

            self.drag_cids = [cid1, cid2 ]

        if self.radioButton.isChecked() == False:
            self.drag_i2 = i
            connect = self.fig.canvas.mpl_connect
            cid1 = connect('motion_notify_event', self.drag_update)
            cid2 = connect('button_release_event', self.end_drag)

            self.drag_cids2 = [cid1, cid2]


    def drag_update(self, event):
        """Update a point that's being moved interactively."""
        if self.radioButton.isChecked() == True:
            if ((event.xdata) ** 2 + (event.ydata) ** 2) ** 0.5 < 1 and event.ydata > 0:

                self.xy[self.drag_i] = [event.xdata, event.ydata]
                self.xy[self.drag_i+1] = [event.xdata, -event.ydata]
                z = event.xdata + event.ydata * 1j
                self.zero[self.drag_i /2] = z

                self.update()
                self.drawOn2()
        if self.radioButton.isChecked() == False:
            if ((event.xdata) ** 2 + (event.ydata) ** 2) ** 0.5 < 1 and event.ydata > 0:

                self.xy2[self.drag_i2] = [event.xdata, event.ydata]
                self.xy2[self.drag_i2 + 1] = [event.xdata, -event.ydata]

                z = event.xdata + event.ydata * 1j
                self.poles[self.drag_i2/2] = z

                self.update()
                self.drawOn2()



    def end_drag(self, event):
        """End the binding of mouse motion to a particular point."""
        if self.radioButton.isChecked() == True:

            for cid in self.drag_cids:
                self.fig.canvas.mpl_disconnect(cid)
        if self.radioButton.isChecked() == False:
            for cid in self.drag_cids2:
                self.fig.canvas.mpl_disconnect(cid)


    def safe_draw(self):
        if self.radioButton.isChecked() == True:

            #"""Temporarily disconnect the draw_event callback to avoid recursion"""
            canvas = self.fig.canvas
            #canvas.mpl_disconnect(self.draw_cid)
            #canvas.draw()
            self.draw_cid = canvas.mpl_connect('draw_event', self.grab_background)
        if self.radioButton.isChecked() == False:
            #canvas = self.fig.canvas
            #canvas.mpl_disconnect(self.draw_cid)
            #canvas.draw()
            self.draw_cid = canvas.mpl_connect('draw_event', self.grab_background)


    def grab_background(self, event=None):
        """
        When the figure is resized, hide the points, draw everything,
        and update the background.
        """
        if self.radioButton.isChecked() == True:

            self.points.set_visible(False)
            self.safe_draw()

            # With most backends (e.g. TkAgg), we could grab (and refresh, in
            # self.blit) self.ax.bbox instead of self.fig.bbox, but Qt4Agg, and
            # some others, requires us to update the _full_ canvas, instead.
            self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)


            self.points.set_visible(True)
            self.blit()
        if self.radioButton_2.isChecked() == True    :
            self.points2.set_visible(False)
            self.safe_draw()

            self.background2 = self.fig.canvas.copy_from_bbox(self.fig.bbox)

            self.points2.set_visible(True)
            self.blit()


    def blit(self):
        """
        Efficiently update the figure, without needing to redraw the
        "background" artists.
        """


        self.fig.canvas.restore_region(self.background)
        self.ax.draw_artist(self.points)
        self.ax.draw_artist(self.points2)
        self.fig.canvas.blit(self.fig.bbox)



    def drawOn2(self):
        #self.drawing2.hold(False)
        self.drawing2.clear()

        num, den = zpk2tf(self.zero, self.poles, 1)




        w, h = freqz(num, den,worN=10000)


        #print (h.size)

        # put the values to draw
        self.drawing2.plot(w, 10 * log10(abs(h)))

        #self.drawing2.plot(w / pi, 20 * log10(abs(h)))
        #self.drawing2.set_xscale('log')
        # self.drawing2.set_xlim([0, 10000])
        # self.drawing2.set_ylim([0, 100000])
        self.drawing2.set_xlabel('Normalized frequency', fontsize=9)
        self.drawing2.set_ylabel('Amplitude[dB]', fontsize=9)
        self.canvas2.draw()



    def browse(self):

        filepath = QtGui.QFileDialog.getOpenFileName(self, 'Single File', "C:\Users\Hanna Nabil\Desktop",'*.txt')



        with open(filepath, "r") as f:
            content = f.readlines()
        content = [x.strip() for x in content]

        if self.radioButton.isChecked() == True:
            index = 0
            while index < len(content):
                self.x = float(content[index])
                self.y = float(content[index + 1])
                self.add_point()
                index += 2
        if self.radioButton_2.isChecked() == True:
            index = 0
            while index < len(content):
                self.x2 = float(content[index])
                self.y2 = float(content[index + 1])
                self.add_point()
                index += 2






    def file_save(self):


        name = QtGui.QFileDialog.getSaveFileName(self, 'Save Point', "C:\Users\Hanna Nabil\Desktop", '*.txt')



        file = open(name, "w")
        index = 0
        p = []

        while index < len(self.zero):
            y = self.zero[index]
            r = y.real
            i = y.imag


            file.write(str(r) + "\n")

            file.write(str(i) + "\n")
            index += 1
        file.close()



if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui
    import numpy as np

    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
