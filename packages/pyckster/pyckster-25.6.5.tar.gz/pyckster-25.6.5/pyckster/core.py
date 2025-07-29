#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script is a PyQt5 GUI for picking seismic traveltimes.
Copyright (C) 2024, 2025 Sylvain Pasquet
Email: sylvain.pasquet@sorbonne-universite.fr

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# Import libraries
import sys, os, re, ast
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QSizePolicy,
    QFileDialog, QAction, QActionGroup, QLabel, QListWidget, QComboBox, QStatusBar, QScrollArea,QProgressDialog,
    QPushButton, QDialog, QHBoxLayout, QVBoxLayout, QLineEdit, QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox,
)
from PyQt5.QtCore import QLocale, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
import pyqtgraph as pqg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

from .obspy_utils import (
    read_seismic_file,
    check_format,
    swap_traces,
    remove_trace,
    move_trace,
    mute_trace,
    swap_header_format,
    merge_streams,
    get_max_decimals,
)

from .pyqtgraph_utils import *

# Set the locale globally to English (United States) to use '.' as the decimal separator
QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

#######################################
# Custom classes for QT GUI
#######################################

# Custom ViewBox class
class CustomViewBox(pqg.ViewBox):
    # Define custom mode for Ctrl+Right rectangle zoom
    # CtrlRightRectMode = 10
    
    rectSelectionFinished = pyqtSignal(object)      # For rectangle selection (middle drag)
    freehandPickFinished = pyqtSignal(list)         # For freehand pick (left drag)
    singlePickRequested = pyqtSignal(object)        # For left click
    removePickRequested = pyqtSignal(object)        # For middle click

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._drag_path = []
        self._ctrl_right_dragging = False  # Add this line

    def mouseClickEvent(self, ev):
        if ev.button() == pqg.QtCore.Qt.LeftButton:
            self.singlePickRequested.emit(ev)
        elif ev.button() == pqg.QtCore.Qt.MiddleButton:
            self.removePickRequested.emit(ev)
        # Do NOT handle right-click here; let the base class show the default menu
        super().mouseClickEvent(ev)

    def mouseDragEvent(self, ev, axis=None):
        # Check if we're in the middle of a Ctrl+Right drag operation
        if hasattr(self, '_ctrl_right_dragging') and self._ctrl_right_dragging and ev.button() == pqg.QtCore.Qt.RightButton:
            # Continue handling as Ctrl+Right drag even if Ctrl is released
            self.handleCtrlRightRectZoom(ev)
            return
        
        # Ctrl+Left drag => pan
        if ev.button() == pqg.QtCore.Qt.LeftButton and ev.modifiers() == pqg.QtCore.Qt.ControlModifier:
            self.setMouseMode(self.PanMode)
            super().mouseDragEvent(ev, axis)
        # Ctrl+Right drag => rectangle zoom (custom implementation)
        elif ev.button() == pqg.QtCore.Qt.RightButton and ev.modifiers() == pqg.QtCore.Qt.ControlModifier:
            self.handleCtrlRightRectZoom(ev)
        # Right drag => axis zoom (default)
        elif ev.button() == pqg.QtCore.Qt.RightButton:
            self.setMouseMode(self.RectMode)
            super().mouseDragEvent(ev, axis)
        # Middle drag (with or without Ctrl) => rectangle selection for removal (custom)
        elif ev.button() == pqg.QtCore.Qt.MiddleButton:
            self.setMouseMode(self.RectMode)
            if ev.isFinish():
                self.rectSelectionFinished.emit(ev)
                ev.accept()  # Prevent default zoom
                return       # Stop further processing
            super().mouseDragEvent(ev, axis)
        # Left drag => freehand pick (custom)
        elif ev.button() == pqg.QtCore.Qt.LeftButton:
            if ev.isStart():
                self._drag_path = []
            self._drag_path.append(ev.scenePos())
            if ev.isFinish():
                self.freehandPickFinished.emit(self._drag_path)
            ev.accept()  # Prevent ViewBox from panning
            return
        else:
            self.setMouseMode(self.PanMode)
            super().mouseDragEvent(ev, axis)

    def handleCtrlRightRectZoom(self, ev):
        """Handle Ctrl+Right drag for rectangle zoom"""
        ev.accept()
        
        if ev.isStart():
            # Mark that we're in a Ctrl+Right drag operation
            self._ctrl_right_dragging = True
            
            # Don't set custom mouse mode - use RectMode instead
            self.setMouseMode(self.RectMode)
            
            # Create or show the scale box for visual feedback
            if not hasattr(self, 'rbScaleBox') or self.rbScaleBox is None:
                self.rbScaleBox = pqg.QtGui.QGraphicsRectItem()
                self.rbScaleBox.setPen(pqg.QtGui.QPen(pqg.QtGui.QColor(255, 255, 100)))
                self.rbScaleBox.setBrush(pqg.QtGui.QBrush(pqg.QtGui.QColor(255, 255, 0, 100)))
                self.addItem(self.rbScaleBox, ignoreBounds=True)
            
            self.rbScaleBox.show()
            self.updateScaleBox(ev.buttonDownPos(ev.button()), ev.pos())
            
        elif ev.isFinish():
            # Finish rectangle zoom - apply the zoom
            self._ctrl_right_dragging = False
            
            if hasattr(self, 'rbScaleBox') and self.rbScaleBox is not None:
                self.rbScaleBox.hide()
                
                # Get the rectangle coordinates
                start_pos = ev.buttonDownPos(ev.button())
                end_pos = ev.pos()
                
                # Create rectangle and map to view coordinates
                rect = pqg.QtCore.QRectF(start_pos, end_pos).normalized()
                rect = self.childGroup.mapRectFromParent(rect)
                
                # Apply the zoom to this rectangle
                self.setRange(rect, padding=0)
        else:
            # Update rectangle during drag
            if hasattr(self, 'rbScaleBox') and self.rbScaleBox is not None:
                self.updateScaleBox(ev.buttonDownPos(ev.button()), ev.pos())

    def updateScaleBox(self, p1, p2):
        """Update the scale box rectangle during drag"""
        if hasattr(self, 'rbScaleBox') and self.rbScaleBox is not None:
            # Create rectangle in scene coordinates
            rect = pqg.QtCore.QRectF(p1, p2).normalized()
            # Map to child coordinates for proper display
            rect = self.childGroup.mapRectFromParent(rect)
            self.rbScaleBox.setRect(rect)

# Generic Parameter Dialog
class GenericParameterDialog(QDialog):
    def __init__(self, title, parameters, add_checkbox=False, checkbox_text = '', parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        self.layout = QVBoxLayout(self)

        self.lineEdits = {}
        self.checkBoxes = {}

        for param in parameters:
            label_text = param['label']
            initial_value = param['initial_value']
            param_type = param['type']

            if param_type == 'bool':
                # Create checkbox for boolean parameters
                checkbox = QCheckBox()
                checkbox.setChecked(bool(initial_value))
                self.checkBoxes[label_text] = checkbox
                self.layout.addLayout(self.createFormItem(label_text, checkbox))
            elif param_type == 'combo':
                # Create a dropdown (QComboBox) for list parameters
                combo = QComboBox(self)
                # Fill the combo box with the provided choices (expect the parameter to include a key 'values')
                for choice in param.get('values', []):
                    combo.addItem(f"'{choice}'")
                # Set current value if provided
                combo.setCurrentText(f"'{initial_value}'")
                self.lineEdits[label_text] = (combo, param_type)
                self.layout.addLayout(self.createFormItem(label_text, combo))
            else:    
                if param_type == 'str':
                    if initial_value == '\t':
                        initial_value = "'\\t'"
                    else:
                        initial_value = f"'{initial_value}'"

                lineEdit = self.createLineEdit(initial_value)
                self.lineEdits[label_text] = (lineEdit, param_type)
                self.layout.addLayout(self.createFormItem(label_text, lineEdit))

        # Add a checkbox
        if add_checkbox:
            self.applyToAllCheckBox = QCheckBox(checkbox_text, self)
            self.layout.addWidget(self.applyToAllCheckBox)

        # Add OK and Cancel buttons
        self.buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK", self)
        self.cancelButton = QPushButton("Cancel", self)
        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.layout.addLayout(self.buttonLayout)

        # Connect buttons
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def createLineEdit(self, value):
        lineEdit = QLineEdit()
        if value is not None:
            lineEdit.setText(str(value))
        return lineEdit

    def createFormItem(self, label, widget):
        layout = QHBoxLayout()
        label_widget = QLabel(label)
        label_widget.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(label_widget, alignment=QtCore.Qt.AlignLeft)
        widget.setMinimumWidth(150)  # Set a uniform minimum width for all answer boxes
        layout.addWidget(widget, alignment=QtCore.Qt.AlignLeft)
        return layout

    def getValues(self):
        values = {}
        for label, (lineEdit, param_type) in self.lineEdits.items():
            if param_type == 'int':
                text = lineEdit.text()
                values[label] = int(text) if text else None
            elif param_type == 'float':
                text = lineEdit.text()
                values[label] = float(text) if text else None
            elif param_type == 'str':
                text = lineEdit.text()
                if text == "'\\t'":
                    values[label] = '\t'
                else:
                    values[label] = text.strip("'")
            elif param_type == 'combo':
                # For dropdown lists, get the current text
                value = lineEdit.currentText()
                # Optionally remove surrounding quotes if present
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                values[label] = value
            elif param_type == 'list':
                text = lineEdit.text()
                try:
                    parsed = ast.literal_eval(text)
                    if not isinstance(parsed, list):
                        parsed = [parsed]
                    values[label] = parsed
                except Exception:
                    values[label] = []  # or raise an error

        # Get values from checkboxes
        for label, checkbox in self.checkBoxes.items():
            values[label] = checkbox.isChecked()
                
        return values

    def isChecked(self):
        return self.applyToAllCheckBox.isChecked()

class TraceSelector(QDialog):
    def __init__(self, trace_numbers, trace_positions=None, parent=None, title="Select Trace", show_position=True):
        super().__init__(parent)
        self.setWindowTitle(title)

        self.layout = QVBoxLayout(self)

        self.trace_numbers = trace_numbers
        self.show_position = show_position

        # Create a dropdown list for trace numbers
        self.traceNumberComboBox = QComboBox(self)
        self.traceNumberComboBox.addItems([str(num) for num in trace_numbers])
        self.layout.addWidget(self.createFormItem("Select Trace Number:", self.traceNumberComboBox))

        # Create a field to modify the corresponding trace position if enabled
        if self.show_position:
            self.tracePositionLineEdit = QLineEdit(self)
            self.layout.addWidget(self.createFormItem("Trace Position (m):", self.tracePositionLineEdit))
            
            # If trace_positions provided, initialize with the first trace position
            if trace_positions and len(trace_positions) > 0:
                self.tracePositionLineEdit.setText(str(trace_positions[0]))

        # Add a checkbox to apply the changes to all shots
        self.applyToAllCheckBox = QCheckBox("Apply to all shots", self)
        self.layout.addWidget(self.applyToAllCheckBox)

        # Add OK and Cancel buttons
        self.buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK", self)
        self.cancelButton = QPushButton("Cancel", self)
        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.layout.addLayout(self.buttonLayout)

        # Connect buttons
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def createFormItem(self, label, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addWidget(widget)
        container = QWidget()
        container.setLayout(layout)
        return container

    def getValues(self):
        selected_index = self.traceNumberComboBox.currentIndex()
        apply_to_all = self.applyToAllCheckBox.isChecked()
        
        if self.show_position:
            try:
                new_position = float(self.tracePositionLineEdit.text())
            except ValueError:
                new_position = 0.0  # Default value if input isn't a valid number
            return selected_index, new_position, apply_to_all
        else:
            return selected_index, apply_to_all

class HeaderDialog(QDialog):
    def __init__(self, files, headers, header_values, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Header Fields")
        self.setGeometry(100, 100, 1000, 600)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Select a file:")
        layout.addWidget(self.label)
        
        self.comboBox = QComboBox()
        self.comboBox.addItems(files)
        self.comboBox.currentIndexChanged.connect(self.updateTable)
        layout.addWidget(self.comboBox)
        
        # Create a QTableWidget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(headers))  # Set column count to the number of headers
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # Make the table scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table_widget)
        
        layout.addWidget(scroll_area)
        
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        layout.addWidget(self.okButton)
        
        self.header_values = header_values
        self.updateTable()

    def updateTable(self):
        # Clear existing items
        self.table_widget.clearContents()

        file_name = self.comboBox.itemText(self.comboBox.currentIndex())
        values = self.header_values.get(file_name, {})

        # Calculate the maximum number of rows needed
        # Use direct list access since showHeaders builds lists directly, not dicts with 'values' key
        max_rows = max((len(values.get(self.table_widget.horizontalHeaderItem(col).text(), [])) 
                    for col in range(self.table_widget.columnCount())), default=0)
        self.table_widget.setRowCount(max_rows)
        
        for col in range(self.table_widget.columnCount()):
            header = self.table_widget.horizontalHeaderItem(col).text()
            # Access list values directly without assuming a nested 'values' key
            header_values = values.get(header, [])
            
            if len(header_values) == 1:
                # Populate all rows with the single value
                for row in range(max_rows):
                    self.table_widget.setItem(row, col, QTableWidgetItem(str(header_values[0])))
            else:
                for row, value in enumerate(header_values):
                    self.table_widget.setItem(row, col, QTableWidgetItem(str(value)))

        # Resize the columns to fit the contents
        self.table_widget.resizeColumnsToContents()

#######################################
# Main window class
#######################################

class MainWindow(QMainWindow):

    #######################################
    # GUI Initialization
    #######################################

    def __init__(self):
        # Initialize the main window

        super().__init__()

        from pyckster import __version__ as version

        if version:
            self.setWindowTitle(f"PyCKSTER {version}")
        else:
            # Fallback title if no version could be determined.
            self.setWindowTitle("PyCKSTER")

        centralWidget = QWidget()
        mainLayout = QHBoxLayout(centralWidget)  # Main horizontal layout
        self.setCentralWidget(centralWidget)

        # Create a horizontal QSplitter
        horSplitter = QSplitter(QtCore.Qt.Horizontal)

        # Create a vertical layout for the left side
        leftLayout = QVBoxLayout()

        # Create a QComboBox to select the display option
        self.displayOptionComboBox = QComboBox()
        self.displayOptionComboBox.addItems(["Filename", "Source Position", "FFID"])
        self.displayOptionComboBox.currentIndexChanged.connect(self.updateFileListDisplay)
        self.displayOptionComboBox.setMinimumSize(50, 30)  # Set minimum size for the QComboBox
        leftLayout.addWidget(self.displayOptionComboBox)

        # Create a QListWidget for file names and add it to the left
        self.fileListWidget = QListWidget()
        self.fileListWidget.itemSelectionChanged.connect(self.onFileSelectionChanged)
        self.fileListWidget.setMinimumSize(50, 200)  # Set minimum size for the QListWidget
        self.fileListWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Ensure it expands to fill space
        leftLayout.addWidget(self.fileListWidget)

        # Create a QWidget to hold the left layout and add it to the horizontal splitter
        leftWidget = QWidget()
        leftWidget.setLayout(leftLayout)
        horSplitter.addWidget(leftWidget)

        # Create a vertical QSplitter
        vertSplitter = QSplitter(QtCore.Qt.Vertical)

        # Create a top ViewBox for seismograms
        self.viewBox = CustomViewBox()
        self.viewBox.setBackgroundColor('w')
        self.viewBox.invertY(True)  # Invert the y-axis

        # Create a plot widget with the top ViewBox
        self.plotWidget = pqg.PlotWidget(viewBox=self.viewBox)
        self.plotWidget.setBackground('w')  # Set background color to white
        vertSplitter.addWidget(self.plotWidget)

        # Create the bottom ViewBox for the acquisition setup / traveltimes view
        self.bottomViewBox = CustomViewBox()
        self.bottomViewBox.setBackgroundColor('w')

        # Create a plot widget with the bottom ViewBox
        self.bottomPlotWidget = pqg.PlotWidget(viewBox=self.bottomViewBox)
        self.bottomPlotWidget.setBackground('w')  # Set background color to white
        vertSplitter.addWidget(self.bottomPlotWidget)

        # Set initial sizes for the splitters
        horSplitter.setSizes([25, 100])
        vertSplitter.setSizes([300, 300])

        # Add the vertical splitter to the horizontal splitter
        horSplitter.addWidget(vertSplitter)

        # Add the horizontal splitter to the main layout
        mainLayout.addWidget(horSplitter)

        # Resize the window to almost full screen
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        self.resize(int(screen_size.width() * 0.9), int(screen_size.height() * 0.9))  # Resize to 90% of the screen size

        # Alternatively, you can use the following line to maximize the window
        # self.showMaximized()

        # Set the title of the window
        self.statusBar = QStatusBar(self)
        permanentMessage = QLabel(self.statusBar)
        try:
            from pyckster import __version__
            permanentMessage.setText(f'S. Pasquet - 2025 (v{__version__})')
        except ImportError:
            # Fallback when running as a script or during development
            permanentMessage.setText('S. Pasquet - 2025')
        self.statusBar.addPermanentWidget(permanentMessage)
        self.setStatusBar(self.statusBar)
        self.statusBar.addPermanentWidget(permanentMessage)
        self.setStatusBar(self.statusBar)      

        # Connect the mouseClickEvent signal to the handleAddPick slot
        self.plotWidget.scene().sigMouseClicked.connect(self.handleAddPick)

        # Connect custom signals to handlers
        self.viewBox.rectSelectionFinished.connect(self.handleRectRemove)
        self.viewBox.freehandPickFinished.connect(self.handleFreehandPick)
        self.viewBox.singlePickRequested.connect(self.handleAddPick)
        self.viewBox.removePickRequested.connect(self.handleRemovePick)

        # Connect the mouseClickEvent signal to the bottom plot
        self.bottomPlotWidget.scene().sigMouseClicked.connect(self.bottomPlotClick)

        # Add a QLabel to the MainWindow
        self.label = QLabel(self)

        #######################################
        # Create a menu bar and add a File menu
        #######################################
        self.fileMenu = self.menuBar().addMenu('File')

        # Create QAction for opening a file
        self.openFileAction = QAction('Open file(s)', self)
        self.fileMenu.addAction(self.openFileAction)
        self.openFileAction.triggered.connect(self.openFile)

        # Create a submenu for saving single files
        self.saveSingleFileSubMenu = self.fileMenu.addMenu('Save current shot')

        # Create QAction for saving current file in SEGY
        self.saveSingleFileSegyAction = QAction('in a SEGY file', self)
        self.saveSingleFileSubMenu.addAction(self.saveSingleFileSegyAction)
        self.saveSingleFileSegyAction.triggered.connect(self.saveSingleFileSEGY)

        # Create QAction for saving current file in SU
        self.saveSingleFileSuAction = QAction('in a Seismic Unix file', self)
        self.saveSingleFileSubMenu.addAction(self.saveSingleFileSuAction)
        self.saveSingleFileSuAction.triggered.connect(self.saveSingleFileSU)

        # Create a submenu for saving all files
        self.saveFileSubMenu = self.fileMenu.addMenu('Save all shots')

        # Create QAction for saving all files in SEGY
        self.saveAllFilesSegyAction = QAction('in separate SEGY files', self)
        self.saveFileSubMenu.addAction(self.saveAllFilesSegyAction)
        self.saveAllFilesSegyAction.triggered.connect(self.saveAllFilesSEGY)

        # Create QAction for saving all files in SU
        self.saveAllFilesSuAction = QAction('in separate Seismic Unix files', self)
        self.saveFileSubMenu.addAction(self.saveAllFilesSuAction)
        self.saveAllFilesSuAction.triggered.connect(self.saveAllFilesSU)

        # Create QAction for saving all files in a single SEGY file
        self.saveAllFilesSingleSegyAction = QAction('in a single SEGY file', self)
        self.saveFileSubMenu.addAction(self.saveAllFilesSingleSegyAction)
        self.saveAllFilesSingleSegyAction.triggered.connect(self.saveAllFilesSingleSEGY)

        # Create QAction for saving all files in a single SU file
        self.saveAllFilesSingleSuAction = QAction('in a single Seismic Unix file', self)
        self.saveFileSubMenu.addAction(self.saveAllFilesSingleSuAction)
        self.saveAllFilesSingleSuAction.triggered.connect(self.saveAllFilesSingleSU)

        # Create QAction for removing current file
        self.removeShotAction = QAction('Remove current shot', self)
        self.fileMenu.addAction(self.removeShotAction)
        self.removeShotAction.triggered.connect(self.removeShot)

        # Create QAction for clearing the memory
        self.clearMemoryAction = QAction('Clear Memory', self)
        self.fileMenu.addAction(self.clearMemoryAction)
        self.clearMemoryAction.triggered.connect(self.clearMemory)

        #######################################
        # Create a menu bar and add Header menu
        #######################################
        self.headerMenu = self.menuBar().addMenu('Edit')

        # Create a submenu for showing the headers
        self.showHeadersSubMenu = self.headerMenu.addMenu('Show Headers')

        # Create QAction for showing all headers
        self.showRawHeadersAction = QAction('Show All Headers', self)
        self.showHeadersSubMenu.addAction(self.showRawHeadersAction)
        self.showRawHeadersAction.triggered.connect(self.showRawHeaders)

        # Create QAction for showing clean headers
        self.showSelectedHeadersAction = QAction('Show Clean Headers', self)
        self.showHeadersSubMenu.addAction(self.showSelectedHeadersAction)
        self.showSelectedHeadersAction.triggered.connect(self.showHeaders)

        # Create a submenu for editing traces
        self.editTraceSubMenu = self.headerMenu.addMenu('Edit Traces')

        # Create QAction for swapping traces
        self.swapTracesAction = QAction('Swap Traces', self)
        self.editTraceSubMenu.addAction(self.swapTracesAction)
        self.swapTracesAction.triggered.connect(self.swapTraces)

        # Create QAction for removing trace
        self.removeTraceAction = QAction('Remove Trace', self)
        self.editTraceSubMenu.addAction(self.removeTraceAction)
        self.removeTraceAction.triggered.connect(self.removeTrace)

        # Create a QAction for moving trace
        self.moveTraceAction = QAction('Move Trace', self)
        self.editTraceSubMenu.addAction(self.moveTraceAction)
        self.moveTraceAction.triggered.connect(self.moveTrace)

        # Create a QAction for muting trace
        self.muteTraceAction = QAction('Mute Trace', self)
        self.editTraceSubMenu.addAction(self.muteTraceAction)
        self.muteTraceAction.triggered.connect(self.muteTrace)

        # Create a submenu for batch editing traces
        self.batchEditTraceSubMenu = self.headerMenu.addMenu('Batch Edit Traces')

        # Create a QAction for batch swapping traces
        self.batchSwapTracesAction = QAction('Batch Swap Traces', self)
        self.batchEditTraceSubMenu.addAction(self.batchSwapTracesAction)
        self.batchSwapTracesAction.triggered.connect(self.batchSwapTraces)

        # Create a QAction for batch removing traces
        self.batchRemoveTracesAction = QAction('Batch Remove Traces', self)
        self.batchEditTraceSubMenu.addAction(self.batchRemoveTracesAction)
        self.batchRemoveTracesAction.triggered.connect(self.batchRemoveTraces)

        # Create a QAction for batch moving traces
        self.batchMoveTracesAction = QAction('Batch Move Traces', self)
        self.batchEditTraceSubMenu.addAction(self.batchMoveTracesAction)
        self.batchMoveTracesAction.triggered.connect(self.batchMoveTraces)

        # Create a QAction for batch muting traces
        self.batchMuteTracesAction = QAction('Batch Mute Traces', self)
        self.batchEditTraceSubMenu.addAction(self.batchMuteTracesAction)
        self.batchMuteTracesAction.triggered.connect(self.batchMuteTraces)

        # Create a submenu for editing the headers
        self.editHeadersSubMenu = self.headerMenu.addMenu('Edit Headers')

        # Create QAction for editing FFID
        self.editFFIDAction = QAction('Edit FFID', self)
        self.editHeadersSubMenu.addAction(self.editFFIDAction)
        self.editFFIDAction.triggered.connect(self.editFFID)

        # Create QAction for editing the delay
        self.editDelayAction = QAction('Edit Delay', self)
        self.editHeadersSubMenu.addAction(self.editDelayAction)
        self.editDelayAction.triggered.connect(self.editDelay)

        # # Create QAction for editing the sample interval
        # self.editSampleIntervalAction = QAction('Edit Sample Interval', self)
        # self.editHeadersSubMenu.addAction(self.editSampleIntervalAction)
        # self.editSampleIntervalAction.triggered.connect(self.editSampleInterval)

        # Create QAction for editing the source position
        self.editSourcePositionAction = QAction('Edit Source Position', self)
        self.editHeadersSubMenu.addAction(self.editSourcePositionAction)
        self.editSourcePositionAction.triggered.connect(self.editSourcePosition)

        # Create QAction for editing the trace position
        self.editTracePositionAction = QAction('Edit Trace Position', self)
        self.editHeadersSubMenu.addAction(self.editTracePositionAction)
        self.editTracePositionAction.triggered.connect(self.editTracePosition)

        # Create a submenu for batch editing headers
        self.batchEditHeadersSubMenu = self.headerMenu.addMenu('Batch Edit Headers')

        # Create QAction for batch editing FFID
        self.batchEditFFIDAction = QAction('Batch Edit FFID', self)
        self.batchEditHeadersSubMenu.addAction(self.batchEditFFIDAction)
        self.batchEditFFIDAction.triggered.connect(self.batchEditFFID)

        # Create QAction for batch editing delay
        self.batchEditDelayAction = QAction('Batch Edit Delay', self)
        self.batchEditHeadersSubMenu.addAction(self.batchEditDelayAction)
        self.batchEditDelayAction.triggered.connect(self.batchEditDelay)

        # # Create QAction for batch editing sample interval
        # self.batchEditSampleIntervalAction = QAction('Batch Edit Sample Interval', self)
        # self.batchEditHeadersSubMenu.addAction(self.batchEditSampleIntervalAction)
        # self.batchEditSampleIntervalAction.triggered.connect(self.batchEditSampleInterval)

        # Create QAction for batch editing source positions
        self.batchEditSourcePositionAction = QAction('Batch Edit Source Position', self)
        self.batchEditHeadersSubMenu.addAction(self.batchEditSourcePositionAction)
        self.batchEditSourcePositionAction.triggered.connect(self.batchEditSourcePosition)

        # Create a QAction for batch editing trace positions
        self.batchEditTracePositionAction = QAction('Batch Edit Trace Position', self)
        self.batchEditHeadersSubMenu.addAction(self.batchEditTracePositionAction)
        self.batchEditTracePositionAction.triggered.connect(self.batchEditTracePosition)

        # Create a submenu for importing topography
        self.topographySubMenu = self.headerMenu.addMenu('Topography')

        # Create QAction for importing topography
        self.importTopoAction = QAction('Import Topography', self)
        self.topographySubMenu.addAction(self.importTopoAction)
        self.importTopoAction.triggered.connect(self.importTopo)

        # Create a QAction for resetting the topography to 0
        self.resetTopoAction = QAction('Reset Topography', self)
        self.topographySubMenu.addAction(self.resetTopoAction)
        self.resetTopoAction.triggered.connect(self.resetTopo)

        # Create a QAction for showing the topography
        self.showTopoTableAction = QAction('Show Topography', self)
        self.topographySubMenu.addAction(self.showTopoTableAction)
        self.showTopoTableAction.triggered.connect(self.setPlotTopo)

        #######################################
        # Create a menu bar and add a View menu
        #######################################
        self.viewMenu = self.menuBar().addMenu('View')

        # Create a submenu for x-axis plot types
        self.plotTypeSubMenu = self.viewMenu.addMenu('Plot traces by')

        # Create QAction to plot traces by shot trace number
        self.shotTraceNumberAction = QAction("Number", self)
        self.shotTraceNumberAction.setCheckable(True)
        self.plotTypeSubMenu.addAction(self.shotTraceNumberAction)
        self.shotTraceNumberAction.triggered.connect(self.setShotTraceNumberPlot)

        # Create QAction to plot traces by trace position
        self.tracePositionAction = QAction("Position", self)
        self.tracePositionAction.setCheckable(True)
        self.plotTypeSubMenu.addAction(self.tracePositionAction)
        self.tracePositionAction.triggered.connect(self.setTracePositionPlot)

        # Ensure only one option is checked at a time
        self.plotTypeGroup = QActionGroup(self)
        self.plotTypeGroup.addAction(self.shotTraceNumberAction)
        self.plotTypeGroup.addAction(self.tracePositionAction)

        # Redundant with trace position now that files with multiple streams are separated
        # self.fileTraceNumberAction = QAction("File Trace Number", self)
        # self.plotTypeSubMenu.addAction(self.fileTraceNumberAction)
        # self.fileTraceNumberAction.triggered.connect(self.setFileTraceNumber)

        # Create a submenu for y-axis plot types
        self.plotTypeSubMenu = self.viewMenu.addMenu('Plot sources by')

        # Create QAction to plot sources by FFID
        self.ffidAction = QAction("FFID", self)
        self.ffidAction.setCheckable(True)
        self.plotTypeSubMenu.addAction(self.ffidAction)
        self.ffidAction.triggered.connect(self.setFFIDPlot)

        # Create QAction to plot sources by source position
        self.sourcePositionAction = QAction("Position", self)
        self.sourcePositionAction.setCheckable(True)
        self.plotTypeSubMenu.addAction(self.sourcePositionAction)
        self.sourcePositionAction.triggered.connect(self.setSourcePositionPlot)

        # Create QAction to plot sources by offset
        self.offsetAction = QAction("Offset", self)
        self.offsetAction.setCheckable(True)
        self.plotTypeSubMenu.addAction(self.offsetAction)
        self.offsetAction.triggered.connect(self.setOffsetPlot)

        # Ensure only one option is checked at a time
        self.plotSourceGroup = QActionGroup(self)
        self.plotSourceGroup.addAction(self.ffidAction)
        self.plotSourceGroup.addAction(self.sourcePositionAction)
        self.plotSourceGroup.addAction(self.offsetAction)

        # Create Menu for choosing bottom plot type
        self.bottomPlotSubMenu = self.viewMenu.addMenu('Bottom Plot Type')

        # Create QAction for setting the bottom plot type to source / trace
        self.bottomPlotSetupAction = QAction('Source / Trace', self)
        self.bottomPlotSetupAction.setCheckable(True)
        self.bottomPlotSubMenu.addAction(self.bottomPlotSetupAction)
        self.bottomPlotSetupAction.triggered.connect(self.setPlotSetup)

        # Create QAction for setting the bottom plot type to travel times
        self.bottomPlotTravelTimeAction = QAction('Traveltimes', self)
        self.bottomPlotTravelTimeAction.setCheckable(True)
        self.bottomPlotSubMenu.addAction(self.bottomPlotTravelTimeAction)
        self.bottomPlotTravelTimeAction.triggered.connect(self.setPlotTravelTime)

        # Create QAction for setting the bottom plot type to topography
        self.bottomPlotTopographyAction = QAction('Topography', self)
        self.bottomPlotTopographyAction.setCheckable(True)
        self.bottomPlotSubMenu.addAction(self.bottomPlotTopographyAction)
        self.bottomPlotTopographyAction.triggered.connect(self.setPlotTopo)

        # Ensure only one option is checked at a time
        self.bottomPlotGroup = QActionGroup(self)
        self.bottomPlotGroup.addAction(self.bottomPlotSetupAction)
        self.bottomPlotGroup.addAction(self.bottomPlotTravelTimeAction)
        self.bottomPlotGroup.addAction(self.bottomPlotTopographyAction)

        # Create QAction for resetting the view
        self.resetViewAction = QAction("Reset View", self)
        self.viewMenu.addAction(self.resetViewAction)
        self.resetViewAction.triggered.connect(self.resetSeismoView)
        self.resetViewAction.triggered.connect(self.resetBottomView)

        # Create QAction for toggling dark mode
        self.darkModeAction = QAction("Dark Mode", self)
        self.darkModeAction.setCheckable(True)
        self.viewMenu.addAction(self.darkModeAction)
        self.darkModeAction.triggered.connect(self.toggleDarkMode)

        #######################################
        # Create a menu bar and add a Seismogram menu
        #######################################
        self.seismoMenu = self.menuBar().addMenu('Seismogram')

        # Create a submenu for displyaing seismograms either as wiggle or image
        self.seismoTypeSubMenu = self.seismoMenu.addMenu('Plot Type')

        # Create QAction for displaying seismograms as wiggle
        self.wiggleAction = QAction("Wiggle", self)
        self.wiggleAction.setCheckable(True)
        self.seismoTypeSubMenu.addAction(self.wiggleAction)
        self.wiggleAction.triggered.connect(self.setWigglePlot)

        # Create QAction for displaying seismograms as image
        self.imageAction = QAction("Image", self)
        self.imageAction.setCheckable(True)
        self.seismoTypeSubMenu.addAction(self.imageAction)
        self.imageAction.triggered.connect(self.setImagePlot)

        # Ensure only one option is checked at a time
        self.seismoTypeGroup = QActionGroup(self)
        self.seismoTypeGroup.addAction(self.wiggleAction)
        self.seismoTypeGroup.addAction(self.imageAction)

        # Create a submenu for wiggle plot options
        self.plotWiggleSubMenu = self.seismoMenu.addMenu('Amplitude Fill')

        # Create QAction for filling positive amplitudes
        self.fillPositiveAction = QAction("Fill positive amplitudes", self)
        self.fillPositiveAction.setCheckable(True)
        self.plotWiggleSubMenu.addAction(self.fillPositiveAction)
        self.fillPositiveAction.triggered.connect(self.fillPositive)

        # Create QAction for filling negative amplitudes
        self.fillNegativeAction = QAction("Fill negative amplitudes", self)
        self.fillNegativeAction.setCheckable(True)
        self.plotWiggleSubMenu.addAction(self.fillNegativeAction)
        self.fillNegativeAction.triggered.connect(self.fillNegative)

        # Create QAction for filling neither positive nor negative amplitudes
        self.noFillAction = QAction("No fill", self)
        self.noFillAction.setCheckable(True)
        self.plotWiggleSubMenu.addAction(self.noFillAction)
        self.noFillAction.triggered.connect(self.noFill)

        # Ensure only one option is checked at a time
        self.fillGroup = QActionGroup(self)
        self.fillGroup.addAction(self.fillPositiveAction)
        self.fillGroup.addAction(self.fillNegativeAction)
        self.fillGroup.addAction(self.noFillAction)

        # Create a QAction for normalizing the traces
        self.normalizeAction = QAction("Normalize traces", self)
        self.seismoMenu.addAction(self.normalizeAction)
        self.normalizeAction.setCheckable(True)
        self.normalizeAction.triggered.connect((self.toggleNormalize))

        # Create a QAction for clipping the traces
        self.clipAction = QAction("Clip traces", self)
        self.seismoMenu.addAction(self.clipAction)
        self.clipAction.setCheckable(True)
        self.clipAction.triggered.connect((self.toggleClip))

        # Create a QAction for showing time samples
        self.showTimeSamplesAction = QAction("Show time samples", self)
        self.seismoMenu.addAction(self.showTimeSamplesAction)
        self.showTimeSamplesAction.setCheckable(True)
        self.showTimeSamplesAction.triggered.connect(self.toggleShowTimeSamples)

        # Create a QAction for showing the air wave
        self.showAirWaveAction = QAction("Show air wave", self)
        self.seismoMenu.addAction(self.showAirWaveAction)
        self.showAirWaveAction.setCheckable(True)
        self.showAirWaveAction.triggered.connect(self.toggleShowAirWave)

        # Create a QAction for showing t0
        self.showT0Action = QAction("Show t0", self)
        self.seismoMenu.addAction(self.showT0Action)
        self.showT0Action.setCheckable(True)
        self.showT0Action.triggered.connect(self.toggleShowT0)

        # Create a QAction for setting the gain
        self.setGainAction = QAction("Set Gain", self)
        self.seismoMenu.addAction(self.setGainAction)
        self.setGainAction.triggered.connect(self.setGain)

        # Create a QAction for setting the maximum time 
        self.setMaxTimeAction = QAction("Set Maximum Time", self)
        self.seismoMenu.addAction(self.setMaxTimeAction)
        self.setMaxTimeAction.triggered.connect(self.setMaxTime)

        #######################################
        # Create a menu bar and add a Picks menu
        #######################################
        self.picksMenu = self.menuBar().addMenu('Picks')

        # Create QAction for saving picks as a new file
        self.savePicksAsAction = QAction('Save Picks As...', self)
        self.picksMenu.addAction(self.savePicksAsAction)
        self.savePicksAsAction.triggered.connect(self.savePicksAsNewFile)

        # Create QAction for saving picks to the current file
        self.savePicksAction = QAction('Save Picks', self)
        self.picksMenu.addAction(self.savePicksAction)
        self.savePicksAction.triggered.connect(self.savePicksInPreviousFile)

        # Create QAction for loading picks
        self.loadPicksAction = QAction('Load Picks', self)
        self.picksMenu.addAction(self.loadPicksAction)
        self.loadPicksAction.triggered.connect(self.loadPicks)

        # Create a submenu for selecting picks colormap
        self.picksColormapMenu = self.picksMenu.addMenu('Picks Colormap')
        self.populatePicksColormapMenu()

        # Create a submenu for picking options
        self.clearPicksMenu = self.picksMenu.addMenu('Clear Picks')

        # Create QAction for clearing all picks
        self.clearAllPicksAction = QAction('Clear All Picks', self)
        self.clearPicksMenu.addAction(self.clearAllPicksAction)
        self.clearAllPicksAction.triggered.connect(self.clearAllPicks)

        # Create QAction for clearing current picks
        self.clearCurrentPicksAction = QAction('Clear Current Picks', self)
        self.clearPicksMenu.addAction(self.clearCurrentPicksAction)
        self.clearCurrentPicksAction.triggered.connect(self.clearCurrentPicks)

        # Create a submenu for error parameters
        self.errorPicksMenu = self.picksMenu.addMenu('Error Parameters')

        # Create QAction for setting error parameters
        self.setErrorParametersAction = QAction('Set Error Parameters', self)
        self.errorPicksMenu.addAction(self.setErrorParametersAction)
        self.setErrorParametersAction.triggered.connect(self.setErrorParameters)

        # Create QAction for setting error parameters
        self.setAllPickErrorAction = QAction('Set Errors For All Picks', self)
        self.errorPicksMenu.addAction(self.setAllPickErrorAction)
        self.setAllPickErrorAction.triggered.connect(self.setAllPickError)

        # Create a submenu for assisted picking
        self.assistedPickingMenu = self.picksMenu.addMenu('Assisted Picking (experimental)')

        # Create a QAction for showing time samples
        self.assistedPickingAction = QAction("Assisted Picking", self)
        self.assistedPickingMenu.addAction(self.assistedPickingAction)
        self.assistedPickingAction.setCheckable(True)
        self.assistedPickingAction.triggered.connect(self.toggleAssistedPicking)

        # Create a QAction for setting assisted picking parameters
        self.setAssistedPickingParametersAction = QAction("Assisted Picking Parameters", self)
        self.assistedPickingMenu.addAction(self.setAssistedPickingParametersAction)
        self.setAssistedPickingParametersAction.triggered.connect(self.setAssistedPickingParameters)

        ######################################
        # Create a menu bar for inverting data
        ######################################
        self.inversionMenu = self.menuBar().addMenu('Inversion')

        # Create QAction for running inversion
        self.runInversionAction = QAction('Run Inversion Module', self)
        self.inversionMenu.addAction(self.runInversionAction)
        self.runInversionAction.triggered.connect(self.runInversionModule)

        #######################################
        # Create a Menu bar for exporting figures
        #######################################
        self.exportMenu = self.menuBar().addMenu('Export')

        # Create QAction for exporting the seismogram
        self.exportSeismoAction = QAction('Export Seismogram', self)
        self.exportMenu.addAction(self.exportSeismoAction)
        self.exportSeismoAction.triggered.connect(self.exportSeismoPlot)

        # Create QAction for exporting the acquisition setup
        self.exportSetupAction = QAction('Export Source / Trace Diagram', self)
        self.exportMenu.addAction(self.exportSetupAction)
        self.exportSetupAction.triggered.connect(self.exportSetupPlot)

        # Create QAction for exporting traveltime plot
        self.exportTravelTimeAction = QAction('Export Traveltime Plot', self)
        self.exportMenu.addAction(self.exportTravelTimeAction)
        self.exportTravelTimeAction.triggered.connect(self.exportTravelTimePlot)

        # Initialize the variables
        self.initMemory()

        # Update the file list display initially
        self.updateFileListDisplay() 

    def closeEvent(self, event):
        """
        Show a confirmation dialog when the user tries to close the window.
        """
        reply = QMessageBox.question(
            self, 
            'Confirm Exit', 
            'Make sure all changes are saved before exiting PyCKSTER.\nDo you want to exit?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()  # Proceed with closing the window
        else:
            event.ignore()  # Cancel the close event 
    
    #######################################
    # Initialization, update and reset functions
    #######################################

    def initializeAttributes(self):
        # Initialize the attributes 

        self.currentFileName = None
        self.currentIndex = None
        self.streamIndex = None
        self.stream = None
        self.toggleDarkMode = False
        self.seismoType = 'wiggle'
        self.normalize = True
        self.fill = 'negative'
        self.clip = True
        self.show_time_samples = False
        self.show_air_wave = False
        self.show_t0 = False
        self.assisted_picking = False
        self.smoothing_window_size = 5  
        self.deviation_threshold = 15  
        self.picking_window_size = 20 
        self.column_x = 0
        self.column_z = 1
        self.delimiter = '\t'
        self.skiprows = 0
        self.usecols = None
        self.gain = 1
        self.mean_dg = 1
        self.mean_ds = 1
        self.rounding = 4 # Risk of error if > 4 when saving in SU file with topography
        self.display_option = "Filename"
        self.bottomPlotType = 'setup'
        self.max_time = None
        self.col = 'k'
        self.fill_brush = (0, 0, 0, 150)
        self.plotTypeX = 'trace_position'
        self.plotTypeY = 'source_position'
        self.x_label = 'Trace Position (m)'
        self.y_label = 'Source Position (m)'
        self.t_label = 'Time (s)'
        self.relativeError = 0.05
        self.absoluteError = 0
        self.maxRelativeError = None
        self.minAbsoluteError = None
        self.maxAbsoluteError = None
        self.legend = None
        self.colormap_str = 'plasma'
        self.colormap = pqg.colormap.get(self.colormap_str, source='matplotlib')
        self.colorbar = None
        self.update_pick_flag = False
        self.update_file_flag = False
        self.pick_file = ""
        self.refrac_manager = None
        self.output_format = 'SEGY'

        # pygimli default parameters
        # self.pg_vTop = 300
        # self.pg_vBottom = 3000
        # self.pg_secNodes = 2
        # self.pg_paraDX = 0.33
        # self.pg_paraDepth = None
        # self.pg_balanceDepth = False
        # self.pg_paraMaxCellSize = None
        # self.pg_zWeight = 0.5
        # self.pg_lam = 30
        # self.pg_maxIter = 6
        # self.pg_verbose = True

        # matplotlib export defaults
        self.cancelDialog = False
        self.mpl_dpi = 300
        self.mpl_aspect_ratio = (10,5)
        self.mpl_line_color = 'k'
        self.mpl_line_width = 0.5
        self.mpl_fill_color = 'k'
        self.mpl_fill_alpha = 0.75    
        self.mpl_show_source = True
        self.mpl_source_color = 'r'
        self.mpl_source_marker = '*'
        self.mpl_source_marker_size = 20
        self.mpl_font_size = 12
        self.mpl_xaxis_position = 'top'
        self.mpl_yaxis_position = 'left'
        self.mpl_invert_yaxis = True
        self.mpl_show_grid = True
        self.mpl_show_title = True
        self.mpl_grid_color = 'k'
        self.mpl_line_colorstyle = 'qualitative colormap'
        self.mpl_qualitative_cm = 'tab10'
        self.mpl_sequential_cm = 'plasma'
        self.mpl_xmin = None
        self.mpl_xmax = None
        self.mpl_ymin = None
        self.mpl_ymax = None
        self.mpl_trace_marker = '.'
        self.mpl_trace_marker_size = 6
        self.mpl_trace_marker_color = 'k'
        self.mpl_trace_marker_alpha = 0.5
        self.mpl_show_picks = False
        self.mpl_pick_color = 'r'    
        self.mpl_pick_marker = 's'
        self.mpl_pick_marker_alt = '+'
        self.mpl_pick_marker_size = 8
        self.mpl_pick_marker_size_alt = 4
        self.mpl_pick_colormap = 'plasma'
        self.mpl_reverse_colormap = False
        self.mpl_colorbar_position = 'right'
        self.mpl_tmin = None
        self.mpl_tmax = None
        self.mpl_equal_aspect = True
        self.mpl_time_in_ms = False

    def setCheckboxes(self):
        # Set checkboxes based on the current values

        self.normalizeAction.setChecked(self.normalize)
        self.clipAction.setChecked(self.clip)
        self.showTimeSamplesAction.setChecked(self.show_time_samples)
        self.showAirWaveAction.setChecked(self.show_air_wave)
        self.assistedPickingAction.setChecked(self.assisted_picking)
        self.showT0Action.setChecked(self.show_t0)
        self.darkModeAction.setChecked(self.toggleDarkMode)
        self.wiggleAction.setChecked(self.seismoType == 'wiggle')
        self.imageAction.setChecked(self.seismoType == 'image')
        self.fillPositiveAction.setChecked(self.fill == 'positive')
        self.fillNegativeAction.setChecked(self.fill == 'negative')
        self.noFillAction.setChecked(self.fill == 'none')
        self.shotTraceNumberAction.setChecked(self.plotTypeX == 'shot_trace_number')
        self.tracePositionAction.setChecked(self.plotTypeX == 'trace_position')
        self.ffidAction.setChecked(self.plotTypeY == 'ffid')
        self.sourcePositionAction.setChecked(self.plotTypeY == 'source_position')
        self.offsetAction.setChecked(self.plotTypeY == 'offset')
        self.bottomPlotSetupAction.setChecked(self.bottomPlotType == 'setup')
        self.bottomPlotTravelTimeAction.setChecked(self.bottomPlotType == 'traveltime')
        self.bottomPlotTopographyAction.setChecked(self.bottomPlotType == 'topography')

    def initMemory(self):
        # Initialize the memory
        #         
        # Clear the legend if it exists
        self.removeLegend()

        # Clear the colorbar if it exists
        self.removeColorBar()

        # Clear the title
        self.removeTitle()
        # self.label.clear()
        # self.label.setText('')
        
        self.initializeAttributes()
        self.setCheckboxes()

        # Clear the plot widgets
        self.plotWidget.clear()
        self.plotWidget.autoRange()
        self.viewBox.setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        self.bottomPlotWidget.clear()
        self.bottomPlotWidget.autoRange()
        self.bottomViewBox.setLimits(xMin=None, xMax=None, yMin=None, yMax=None)
        self.fileListWidget.clear()

        # Initialize the lists for each stream
        self.attributes_to_initialize = [
            'fileNames', 'streams', 'input_format', 'n_sample', 
            'sample_interval', 'delay', 'time', 'record_length','ffid',  
            'source_position', 'shot_trace_number', 'trace_position', 
            'file_trace_number', 'trace_elevation', 'source_elevation',
            'offset', 'picks', 'error', 'pickSeismoItems', 'pickSetupItems', 'airWaveItems'
        ]

        # Initialize the lists for each stream
        for attr in self.attributes_to_initialize:
            setattr(self, attr, [])

        self.updatePlotTypeDict()

    def clearMemory(self):
        # Clear memory (reset the application)

        # Warning
        reply = QMessageBox.question(self, 'Warning', 'Are you sure you want to clear the memory?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        self.initMemory()

    def updatePlotTypeDict(self):
        # Update the dictionary mapping plot types to attributes

        self.plotTypeDict = {
            'shot_trace_number': self.shot_trace_number,
            'file_trace_number': self.file_trace_number,
            'trace_position': self.trace_position,
            'source_position': self.source_position,
            'ffid': self.ffid,
            'offset': self.offset
        }

    def resetSeismoView(self):
        # Reset the seismogram view

        self.plotWidget.autoRange()
        self.plotWidget.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)

        if self.streams:
            # Ensure the dictionary is updated
            self.updatePlotTypeDict()

            # Access the appropriate attribute based on self.plotTypeX
            plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

            # Flatten the list of lists into a single list
            flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]

            # Set x and y limits
            self.plotWidget.getViewBox().setXRange(min(flat_plot_data_x) - self.mean_dg, 
                                                max(flat_plot_data_x) + self.mean_dg)
            self.plotWidget.getViewBox().setYRange(min(self.time[self.currentIndex]), 
                                                self.max_time)
            # Set zoom limits
            self.plotWidget.getViewBox().setLimits(xMin=min(flat_plot_data_x) - self.mean_dg, 
                                                xMax=max(flat_plot_data_x) + self.mean_dg, 
                                                yMin=min(self.time[self.currentIndex]), 
                                                yMax=self.max_time)
    
    def resetBottomView(self):
        # Reset the bottom plot view

        if self.bottomPlotType == 'setup':
            self.resetSetupView()
        elif self.bottomPlotType == 'traveltime':
            self.resetTravelTimeView()
        elif self.bottomPlotType == 'topo':
            self.resetTopoView()

    def resetSetupView(self):
        # Reset the setup view

        self.bottomPlotWidget.autoRange()
        self.bottomPlotWidget.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)

        self.updatePlotTypeDict()
        
        if self.source_position:
            # Access the appropriate attribute based on self.plotTypeX (shot_trace_number, file_trace_number, trace_position)
            plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])
            # Flatten the list of lists into a single list
            flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]

            # Access the appropriate attribute based on self.plotTypeY (source_position, ffid, offset)
            plot_data_y = self.plotTypeDict.get(self.plotTypeY, [])
            if self.plotTypeY == 'offset':
                flat_plot_data_y = [item for sublist in plot_data_y for item in sublist] # Flatten the list of lists into a single list
            else:
                flat_plot_data_y = plot_data_y
            
            # Get unique traces and sources from list of list of traces array that are not None
            traces = [trace for trace in flat_plot_data_x if trace is not None]
            sources = [source for source in flat_plot_data_y if source is not None]

            # Set x and y limits
            self.bottomPlotWidget.getViewBox().setXRange(min(traces) - self.mean_dg, 
                                                         max(traces) + self.mean_dg)
            self.bottomPlotWidget.getViewBox().setYRange(min(sources) - 1,
                                                         max(sources) + 1)
            self.bottomPlotWidget.getViewBox().setLimits(xMin=min(traces) - self.mean_dg,
                                                         xMax=max(traces) + self.mean_dg,
                                                         yMin=min(sources) - 1,
                                                         yMax=max(sources) + 1)
    
    def resetTravelTimeView(self):
        # Reset the travel time view

        self.bottomPlotWidget.autoRange()
        self.bottomPlotWidget.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)

        self.updatePlotTypeDict()
        
        if self.source_position:
            # Access the appropriate attribute based on self.plotTypeX (shot_trace_number, file_trace_number, trace_position)
            plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])
            # Flatten the list of lists into a single list
            flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]

            # Access the appropriate attribute based on self.plotTypeY (source_position, ffid, offset)
            plot_data_y = self.picks
            # Flatten the list of lists into a single list
            flat_plot_data_y = [item for sublist in plot_data_y for item in sublist]

            # Get unique traces and times from list of list of traces array that are not None
            traces = [trace for trace in flat_plot_data_x if trace is not None]
            times = [time for time in flat_plot_data_y if time is not None]

            # Keep only the times where times is not Nan
            times = [time for time in times if not np.isnan(time)]

            # If there are no times, set the min time to 0 and max time to 1
            if not times:
                times = [np.min(self.time[self.currentIndex]), np.max(self.time[self.currentIndex])]
            
            # Set x and y limits
            self.bottomPlotWidget.getViewBox().setXRange(min(traces) - self.mean_dg, 
                                                         max(traces) + self.mean_dg)
            self.bottomPlotWidget.getViewBox().setYRange(min(times) - min(times)*0.1,
                                                         max(times) + max(times)*0.1)
            self.bottomPlotWidget.getViewBox().setLimits(xMin=min(traces) - self.mean_dg,
                                                            xMax=max(traces) + self.mean_dg,
                                                            yMin=min(times) - min(times)*0.1,
                                                            yMax=max(times) + max(times)*0.1)

    def resetTopoView(self):
        # Reset the topography view

        self.bottomPlotWidget.autoRange()
        self.bottomPlotWidget.getViewBox().setLimits(xMin=None, xMax=None, yMin=None, yMax=None)

        self.updatePlotTypeDict()
        
        if self.trace_elevation:

            # Get all trace positions
            all_positions,_,_,_ = self.getUniquePositions()

            # Get the mean dx
            x_positions = np.unique([x for x, _ in all_positions])

            if len(x_positions) > 1:
                mean_dx = np.mean(np.diff(x_positions))
            else:
                mean_dx = 0

            # Get the minimum and maximum x values from source and trace positions
            min_x = min([x for x, _ in all_positions])
            max_x = max([x for x, _ in all_positions])

            # Get the minimum and maximum z values from source and trace positions
            min_z = min([z for _, z in all_positions])
            max_z = max([z for _, z in all_positions])

            range_z = max_z - min_z

            # Set x and y limits
            self.bottomPlotWidget.getViewBox().setXRange(min_x - mean_dx*2, 
                                                         max_x + mean_dx*2)
            self.bottomPlotWidget.getViewBox().setYRange(min_z - range_z*0.2 - 1, 
                                                         max_z + range_z*0.2 + 1)
            self.bottomPlotWidget.getViewBox().setLimits(xMin=min_x -  mean_dx*2, xMax=max_x + mean_dx*2,
                                                        yMin=min_z - range_z*0.2 - 1, yMax=max_z + range_z*0.2 + 1)

    def populatePicksColormapMenu(self):
        # Define grouped colormaps
        colormaps = {
            "Perceptually Uniform Sequential": ['viridis', 'plasma', 'inferno', 'magma', 'cividis'],
            "Sequential": ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                        'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                        'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'],
            "Miscellaneous": ['flag', 'prism', 'ocean', 'gist_earth', 'terrain',
                            'gist_stern', 'binary', 'gist_gray', 'bone', 'rainbow',
                            'jet', 'nipy_spectral', 'gist_heat']
        }
        
        # Clear the existing menu items
        self.picksColormapMenu.clear()
        
        # Loop over each group and add the header (disabled) then each colormap action
        for group, cmap_list in colormaps.items():
            header_action = QAction(group, self)
            header_action.setEnabled(False)
            self.picksColormapMenu.addAction(header_action)
            
            for cmap in cmap_list:
                action = QAction("   " + cmap, self)
                # Use a lambda with a default argument to capture the current cmap name
                action.triggered.connect(lambda checked, cmap_name=cmap: self.setPicksColormapFromAction(cmap_name))
                self.picksColormapMenu.addAction(action)

    def toggleDarkMode(self):
        self.dark_mode_enabled = not getattr(self, 'dark_mode_enabled', False)
        self.update_pick_flag = True
        
        if self.dark_mode_enabled:
            # Set dark palette
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, QColor(200, 200, 200))
            dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
            dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
            dark_palette.setColor(QPalette.ToolTipBase, QColor(200, 200, 200))
            dark_palette.setColor(QPalette.ToolTipText, QColor(200, 200, 200))
            dark_palette.setColor(QPalette.Text, QColor(200, 200, 200))
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, QColor(200, 200, 200))
            dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
            QApplication.instance().setPalette(dark_palette)

            self.plotWidget.setBackground(QColor(53, 53, 53).name())
            self.plotWidget.getViewBox().setBackgroundColor(QColor(42, 42, 42).name())
            self.bottomPlotWidget.setBackground(QColor(53, 53, 53).name())
            self.bottomPlotWidget.getViewBox().setBackgroundColor(QColor(42, 42, 42).name())
            self.col = QColor(200, 200, 200).name()
            self.fill_brush = (255, 255, 255, 150)

        else:
            # Reset to system (light) palette
            QApplication.instance().setPalette(QApplication.instance().style().standardPalette())
            self.plotWidget.setBackground('w')
            self.plotWidget.getViewBox().setBackgroundColor('w')
            self.bottomPlotWidget.setBackground('w')
            self.bottomPlotWidget.getViewBox().setBackgroundColor('w')
            self.col = 'k'
            self.fill_brush = (0, 0, 0, 150)
        
        self.plotSeismo()
        self.plotBottom()

    #######################################
    # File listing and sorting functions
    #######################################

    def sortFiles(self):
        # Sort files based on the file names

        # Original file paths
        fileNames = self.fileNames
        
        # Get sorted indices based on the file names
        sorted_indices = sorted(range(len(fileNames)), key=lambda i: self.naturalSortKey(os.path.basename(fileNames[i])))

        # Sort each attribute using the sorted indices
        for attr in self.attributes_to_initialize:
            setattr(self, attr, [getattr(self, attr)[i] for i in sorted_indices])

    def extractFileNumber(self, filename):
        # Extract the numeric part from the filename

        match = re.search(r'\d+', filename)
        return int(match.group()) if match else float('inf')
    
    def naturalSortKey(self, filename):
        # Split the string into a list of substrings and integers

        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', filename)]

    def sortFileList(self):
        # Sort the file list widget based on the file names

        self.fileListWidget.clear()  # Clear the list widget
        for fileName in self.fileNames: #: Add the file names to the list widget
            baseName = os.path.basename(fileName)
            self.fileListWidget.addItem(baseName)
        
        self.fileListWidget.setCurrentRow(self.currentIndex) # Set the current row to the current index

    def updateFileListDisplay(self):
        # Update the file list display based on the selected display option

        # Clear the current items in the QListWidget
        self.fileListWidget.clear()

        # Get the selected display option
        self.display_option = self.displayOptionComboBox.currentText()

        # Update the QListWidget based on the selected display option
        if self.display_option == "Filename":
            for file_path in self.fileNames:
                self.fileListWidget.addItem(os.path.basename(file_path))
        elif self.display_option == "Source Position":
            for source_position in self.source_position:
                self.fileListWidget.addItem(str(source_position))
        elif self.display_option == "FFID":
            for ffid in self.ffid:
                self.fileListWidget.addItem(str(ffid))

        if self.currentIndex is not None:
            self.fileListWidget.setCurrentRow(self.currentIndex)

    def onFileSelectionChanged(self):
        # When the file selection is changed

        # Set the file update flag to True
        self.update_file_flag = True

        # Get the selected item
        selectedItems = self.fileListWidget.selectedItems()

        # If an item is selected
        if selectedItems:
            selectedBaseName = selectedItems[0].text() # Get the text of the selected item
            
            # Find the index of the selected file path
            for index in range(self.fileListWidget.count()):
                # If the text of the item at the index is the same as the selected base name
                if self.fileListWidget.item(index).text() == selectedBaseName:
                    self.currentFileName = self.fileNames[index] # Set the current file name
                    self.currentIndex = index # Set the current index
                    break

            # Plot the selected file
            self.plotSeismo()
            self.plotBottom()

    #######################################
    # File loading and processing functions
    ########################################    
    
    def openFile(self, fileNames_new=None):       
        # Open a file dialog to select the seismic file(s) to load

        if fileNames_new is None or not fileNames_new:
            fileNames_new, _ = QFileDialog.getOpenFileNames(self, "Open seismic file(s)", "", 
                                                        "Seismic files (*.seg2 *.dat *.segy *.sgy *.sg2 *.su)")
            
        firstNewFile = None
        counter_files = 0
        counter_stream = 0
        if fileNames_new:
            progress = None
            if len(fileNames_new) > 1:
                # Create and configure the progress dialog
                progress = QProgressDialog("Loading files...", "Cancel", 0, len(fileNames_new), self)
                progress.setWindowTitle(f"Loading Files") # Explicitly set the window title
                progress.setMinimumDuration(0)  # Show immediately
                progress.setWindowModality(QtCore.Qt.WindowModal)
                progress.setValue(0)
                progress.show()
                QApplication.processEvents()  # Ensure the dialog is displayed

            # fileNames_new.sort(key=lambda x: self.extractFileNumber(os.path.basename(x)))  # Sort the new file paths by filename
            fileNames_new.sort(key=lambda x: self.naturalSortKey(os.path.basename(x)))  # Sort the new file paths by filename

            # Check if files are already in the list
            for i, fileName in enumerate(fileNames_new):
                if progress:
                    progress.setValue(i)
                    if progress.wasCanceled():
                        break
                    QApplication.processEvents()

                if not fileName in self.fileNames:
                    counter_files += 1
                    
                    self.currentFileName = fileName
                    self.loadFile() # Load the file
                    
                    
                    for j in range(len(self.stream)):
                        fileName_to_check = fileName
                        if len(self.stream) > 1:
                            fileName_to_check = fileName + f'_{j+1}'

                        ffid = self.stream[j][0].stats[check_format(self.stream[0])].trace_header.original_field_record_number

                        if not fileName_to_check in self.fileNames:
                            if ffid in self.ffid:
                                # Prompt user to choose to load the file with incrementing FFID
                                msg = QMessageBox()
                                msg.setIcon(QMessageBox.Warning)
                                msg.setText(f'FFID {ffid} already loaded. Do you want to load the file with incrementing FFID?')
                                msg.setWindowTitle("FFID already loaded")
                                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                msg.setDefaultButton(QMessageBox.Yes)
                                response = msg.exec_()
                                if response == QMessageBox.Yes:
                                    flag = True
                                    while flag:
                                        ffid += 1
                                        if not ffid in self.ffid:
                                            self.stream[j][0].stats[check_format(self.stream[0])].trace_header.original_field_record_number = int(ffid)
                                            msg.setText(f'FFID set to {ffid}')
                                            flag = False
                                else:
                                    continue
                            counter_stream += 1
                            if firstNewFile is None: # Get the first new file
                                firstNewFile = fileName_to_check

                            self.currentIndex = len(self.fileNames) # Set the current index to the length of the file names list
                            self.currentFileName = fileName_to_check 
                            self.streamIndex = j

                            # Create attributes_to_append_none by excluding 'fileNames' and 'airWaveItems'
                            attributes_to_append_none = [attr for attr in self.attributes_to_initialize if attr not in ['fileNames', 'airWaveItems']]

                            for attr in attributes_to_append_none:
                                getattr(self, attr).append(None)

                            self.fileNames.append(fileName_to_check)  # Append the file name to the list
                            self.airWaveItems.append([None,None,None])  # Append the air wave items to the list

                            self.loadStream() # Load the file

                        else:
                            QMessageBox.information(self, "File Already Loaded", f"{os.path.basename(fileName)} is already loaded.")

                    if i == 0:
                        if self.max_time is None:
                            self.max_time = max(self.time[0])

                    if counter_stream > 0:           
                        self.currentFileName = firstNewFile
                        self.currentIndex = self.fileNames.index(firstNewFile)
                
                else:
                    QMessageBox.information(self, "File Already Loaded", f"{os.path.basename(fileName)} is already loaded.")
            
            if progress:
                progress.setValue(len(fileNames_new))  # Ensure the dialog closes

            if counter_stream > 0:
                if len(fileNames_new) > 1:
                    if counter_stream > 1:
                        QMessageBox.information(self, "Files Loaded", f"{counter_files} file(s) successfully loaded\n{counter_stream} streams successfully loaded")
                    else:
                        QMessageBox.information(self, "Files Loaded", f"{counter_files} file(s) successfully loaded")
                else:
                    QMessageBox.information(self, "File Loaded", f"File '{os.path.basename(fileNames_new[0])}' loaded successfully.")
            elif counter_files > 0:
                QMessageBox.information(self, "Files Loaded", f"{counter_files} file(s) successfully loaded")
            else:
                QMessageBox.information(self, "No New Files", "No new files were loaded.")

            self.sortFiles()  # Sort the files based on the file names
            self.updateFileListDisplay() # Update the file list display
            self.sortFileList() # Sort the file list widget
            self.updatePlotTypeDict() # Update the plot type dictionary

    def loadFile(self):
        # Show loading message in the status bar
        print(f"Loading file: {self.currentFileName}")
        # Load the seismic file
        self.stream = read_seismic_file(self.currentFileName, separate_sources=True)

    def loadStream(self):
        self.streams[self.currentIndex] = self.stream[self.streamIndex]
        self.input_format[self.currentIndex] = check_format(self.streams[self.currentIndex])
        self.getPlotParameters()

        # If it is the first time the file is loaded, update the sources and traces lists
        if self.picks[self.currentIndex] is None:
            # Initialize picks for the current file with a list of nans of the same length as the traces
            self.picks[self.currentIndex] = [np.nan] * len(self.trace_position[self.currentIndex])
            # Intialize errors for the current file with a list of nans of the same length as the traces
            self.error[self.currentIndex] = [np.nan] * len(self.trace_position[self.currentIndex])
            # Initialize the scatter items for the current file with list of empty lists of the same length as the traces
            self.pickSeismoItems[self.currentIndex] = [None] * len(self.trace_position[self.currentIndex])
            # Initialize the scatter items for the current file with list of empty lists of the same length as the traces
            self.pickSetupItems[self.currentIndex] = [None] * len(self.trace_position[self.currentIndex])

    def removeShot(self):
        if self.currentIndex is not None:
            # Remove the current file from the lists
            for attr in self.attributes_to_initialize:
                getattr(self, attr).pop(self.currentIndex)

            # Reset index
            self.currentIndex = 0

            # Update the plot type dictionary
            self.updatePlotTypeDict()

            # Update the file list display
            self.updateFileListDisplay()

            # Update selected file in the list display
            self.fileListWidget.setCurrentRow(self.currentIndex)

            if self.streams:
                # Update the plot
                self.plotSeismo()
                self.plotBottom()
            else:
                QMessageBox.information(self, "No Shots Remaining", "No shots remaining. Memory will be cleared.")
                self.initMemory()

    #######################################
    # Saving shot functions
    #######################################

    def saveSingleFile(self, format='SEGY'):
        # Save the current shot as a SEGY/SU file

        if self.streams:

            # Set the headers
            self.setHeaders()

            # Get the file path to save the SEGY/SU file
            # Default name is the current file name with the extension changed to .segy or .su
            # defaultSavePath = os.path.splitext(self.currentFileName)[0] + '.' + format.lower()
            if str(self.ffid[self.currentIndex]) in os.path.basename(self.currentFileName):
                defaultSavePath = os.path.splitext(self.currentFileName)[0] + '.' + format.lower()
            else:
                defaultSavePath = os.path.splitext(self.currentFileName)[0] + '_' + str(self.ffid[self.currentIndex]) + '.' + format.lower()

            savePath, _ = QFileDialog.getSaveFileName(self, "Save as " + format.upper() + " file", defaultSavePath, 
                format.upper() + " files (*." + format.lower() + ")")

            if savePath:
                stream = self.streams[self.currentIndex]

                stream = swap_header_format(stream, format)
                
                # Save the stream as a SEGY or SU file
                stream.write(savePath, format=format, 
                    data_encoding=5, byteorder='>')
                QMessageBox.information(self, "File Saved", f"File saved as: {savePath}")
                
    def saveAllFiles(self, single=False):
        # Save all shots as SEGY or SU files

        if self.streams:

            # Set the headers
            self.setHeaders()

            if single is False:
                # Get the directory to save the SEGY or SU files
                saveDir = QFileDialog.getExistingDirectory(self, "Save as " + self.output_format.upper() + " files")

                if saveDir:

                    # Start progress dialog if there are multiple files
                    if len(self.streams) > 1:
                        progress = QProgressDialog("Saving files...", "Cancel", 0, len(self.streams), self)
                        progress.setWindowTitle(f"Saving Files") # Explicitly set the window title
                        progress.setMinimumDuration(0)  # Show immediately
                        progress.setWindowModality(QtCore.Qt.WindowModal)
                        progress.setValue(0)
                        progress.show()
                        QApplication.processEvents()

                    for i, stream in enumerate(self.streams):
                        if len(self.streams) > 1:
                            # Update the progress dialog
                            progress.setValue(i)
                            QApplication.processEvents()

                        stream = swap_header_format(stream, self.output_format)
                        self.input_format[i] = check_format(stream)

                        # Default file name is fileNames[i] without extension _ffid.format
                        # check if ffid is in the original file name
                        if str(self.ffid[i]) in os.path.basename(self.fileNames[i]):
                            defaultSavePath = os.path.splitext(self.fileNames[i])[0] + '.' + self.output_format.lower()
                        else:
                            defaultSavePath = os.path.splitext(self.fileNames[i])[0] + '_' + str(self.ffid[i]) + '.' + self.output_format.lower()

                        savePath = os.path.join(saveDir, os.path.basename(defaultSavePath))
                        # Make sure we're not overwriting an existing file
                        # if os.path.exists(savePath):
                        savePath = savePath.replace('.' + self.output_format.lower(), '_updated.' + self.output_format.lower())
                        stream.write(savePath, format=self.output_format, 
                            data_encoding=5, byteorder='>')
                        print(f"File saved as: {savePath}")

                    if len(self.streams) > 1:
                        # Ensure the progress dialog closes
                        progress.setValue(len(self.streams))
                        QMessageBox.information(self, "Files Saved", f"{len(self.streams)} files saved successfully in: {saveDir}")
            else:
                # Ask for single filename
                savePath, _ = QFileDialog.getSaveFileName(self, "Save as " + self.output_format.upper() + " file", 
                    'merged_shots.' + self.output_format.lower(), 
                    self.output_format.upper() + " files (*." + self.output_format.lower() + ")")
                
                if savePath:
                    # Merge all streams into a single stream
                    merged_stream = merge_streams(self.streams)

                    merged_stream = swap_header_format(merged_stream, self.output_format)
                    for i, stream in enumerate(self.streams):
                        self.input_format[i] = check_format(stream)

                    # Save the merged stream as a SEGY or SU file
                    merged_stream.write(savePath, format=self.output_format, 
                        data_encoding=5, byteorder='>')
                    QMessageBox.information(self, "File Saved", f"File saved as: {savePath}")
                
                    
    def saveSingleFileSEGY(self):
        # Save the current shot as a SEGY file
        self.output_format = 'SEGY'
        self.saveSingleFile()
    
    def saveAllFilesSEGY(self):
        # Save all shots as SEGY files
        self.output_format = 'SEGY'
        self.saveAllFiles()

    def saveSingleFileSU(self):
        # Save the current shot as a SU file
        self.output_format = 'SU'
        self.saveSingleFile()

    def saveAllFilesSU(self):
        # Save all shots as SU files
        self.output_format = 'SU'
        self.saveAllFiles()

    def saveAllFilesSingleSEGY(self):
        # Save all shots in a single SEGY file
        self.output_format = 'SEGY'
        self.saveAllFiles(single=True)

    def saveAllFilesSingleSU(self):
        # Save all shots in a single SU file
        self.output_format = 'SU'
        self.saveAllFiles(single=True)
                
    def setHeaders(self):
        # Set stream headers based on self attributes
        coordinate_scalar = self.calculateCoordinateScalar()
        
        for i, st in enumerate(self.streams):
            input_format = check_format(st)
            for trace_index, trace in enumerate(st):
                trace.stats[input_format].trace_header.scalar_to_be_applied_to_all_coordinates = int(-coordinate_scalar)
                trace.stats[input_format].trace_header.original_field_record_number = int(self.ffid[i])
                trace.stats[input_format].trace_header.delay_recording_time = int(self.delay[i]*1000)
                trace.stats[input_format].trace_header.datum_elevation_at_receiver_group = int(np.round(np.mean(np.diff(self.trace_position[self.currentIndex])),self.rounding)*coordinate_scalar)
                
                trace.stats[input_format].trace_header.distance_from_center_of_the_source_point_to_the_center_of_the_receiver_group = int(self.source_position[i]*coordinate_scalar) - int(self.trace_position[self.currentIndex][trace_index]*coordinate_scalar)
                trace.stats[input_format].trace_header.group_coordinate_x = int(self.trace_position[self.currentIndex][trace_index]*coordinate_scalar)
                trace.stats[input_format].trace_header.group_coordinate_y = int(0)
                trace.stats[input_format].trace_header.receiver_group_elevation = int(self.trace_elevation[self.currentIndex][trace_index]*coordinate_scalar)
                
                trace.stats[input_format].trace_header.source_coordinate_x = int(self.source_position[i]*coordinate_scalar)
                trace.stats[input_format].trace_header.source_coordinate_y = int(0)
                trace.stats[input_format].trace_header.surface_elevation_at_source = int(self.source_elevation[i]*coordinate_scalar)
        
    #######################################
    # Main file header functions
    #######################################

    def getPlotParameters(self):
        # Get the trace numbers from the Stream
        shot_trace_number = [trace.stats[self.input_format[self.currentIndex]].trace_header.trace_number_within_the_original_field_record 
                             for trace in self.streams[self.currentIndex]]
        # Get the file trace numbers from the Stream
        file_trace_number = np.arange(1, len(self.streams[self.currentIndex])+1)

        # Get the data and group coordinates from the Stream
        group_coordinates_x = [trace.stats[self.input_format[self.currentIndex]].trace_header.group_coordinate_x / abs(trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates) 
                               if trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates < 0 
                               else trace.stats[self.input_format[self.currentIndex]].trace_header.group_coordinate_x * trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates 
                               for trace in self.streams[self.currentIndex]]
        
        receiver_group_elevation = [trace.stats[self.input_format[self.currentIndex]].trace_header.receiver_group_elevation / abs(trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates) 
                                    if trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates < 0 
                                    else trace.stats[self.input_format[self.currentIndex]].trace_header.receiver_group_elevation * trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates
                                    for trace in self.streams[self.currentIndex]]
        
        # Check if group_coordinates_x has only zeros
        if np.all(np.array(group_coordinates_x) == 0):
            group_coordinates_x = file_trace_number

        # Get the source coordinate from the first trace
        source_coordinates_x = [trace.stats[self.input_format[self.currentIndex]].trace_header.source_coordinate_x / abs(trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates) 
                                if trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates < 0 
                                else trace.stats[self.input_format[self.currentIndex]].trace_header.source_coordinate_x * trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates 
                                for trace in self.streams[self.currentIndex]]
        source_coordinate_x = np.unique(source_coordinates_x)[0]

        surface_elevation_at_source = [trace.stats[self.input_format[self.currentIndex]].trace_header.surface_elevation_at_source / abs(trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates)
                            if trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates < 0
                            else trace.stats[self.input_format[self.currentIndex]].trace_header.surface_elevation_at_source * trace.stats[self.input_format[self.currentIndex]].trace_header.scalar_to_be_applied_to_all_coordinates
                            for trace in self.streams[self.currentIndex]]
        surface_elevation_at_source = np.unique(surface_elevation_at_source)[0]

        # Get the sample interval and delay from the first trace
        self.sample_interval[self.currentIndex] = self.streams[self.currentIndex][0].stats[self.input_format[self.currentIndex]].trace_header.sample_interval_in_ms_for_this_trace / 1_000_000 
        self.delay[self.currentIndex] = self.streams[self.currentIndex][0].stats[self.input_format[self.currentIndex]].trace_header.delay_recording_time/1000

        self.n_sample[self.currentIndex] = len(self.streams[self.currentIndex][0].data)

        self.time[self.currentIndex] = np.arange(self.n_sample[self.currentIndex]) * self.sample_interval[self.currentIndex] + self.delay[self.currentIndex]
        self.ffid[self.currentIndex] = self.streams[self.currentIndex][0].stats[self.input_format[self.currentIndex]].trace_header.original_field_record_number
        self.offset[self.currentIndex] = np.round([group_coordinates_x[i] - source_coordinate_x for i in range(len(group_coordinates_x))],self.rounding)
        self.source_position[self.currentIndex] = source_coordinate_x
        self.trace_position[self.currentIndex] = group_coordinates_x
        self.source_elevation[self.currentIndex] = surface_elevation_at_source
        self.trace_elevation[self.currentIndex] = receiver_group_elevation
        self.shot_trace_number[self.currentIndex] = shot_trace_number
        self.file_trace_number[self.currentIndex] = file_trace_number
        self.record_length[self.currentIndex] = (self.n_sample[self.currentIndex]-1) * self.sample_interval[self.currentIndex]

        self.updateMeanSpacing()

    def updateMeanSpacing(self):
        # Update the mean_dg and mean_ds
        if self.plotTypeX == 'trace_position':
            if len(self.streams[self.currentIndex]) == 1:
                self.mean_dg = 1
            else:
                self.mean_dg = np.round(np.mean(np.diff(self.trace_position[self.currentIndex])),self.rounding)
        else:
            self.mean_dg = 1
        
        if self.plotTypeY == 'ffid':
            self.mean_ds = 1
        else:
            if len(self.streams) == 1:
                self.mean_ds = 1
            else:
                self.mean_ds = np.round(np.mean(np.diff(self.source_position)),self.rounding)

    # Compute the coordinate scalar
    def calculateCoordinateScalar(self):

        # Get the trace and source positions
        _, unique_positions, _, _ = self.getUniquePositions()
        
        # Get the maximum number of decimals from unique x,z positions in a np.array
        max_decimals = get_max_decimals(np.array(unique_positions).flatten())

        # Define the coordinate scalar
        coordinate_scalar = 10 ** max_decimals

        return coordinate_scalar

    def getUniquePositions(self):
        # Get unique traces position/elevation from list of list of traces array that are not None
        traces = [(trace, elevation) for sublist_position, sublist_elevation in zip(self.trace_position, self.trace_elevation) if sublist_position is not None for trace, elevation in zip(sublist_position, sublist_elevation)]

        # Get unique sources position/elevation from list of sources array that are not None
        sources = [(source, elevation) for source, elevation in zip(self.source_position, self.source_elevation) if source is not None]

        # Concatenate traces and sources (x,z) positions
        all_positions = np.concatenate((traces, sources))

        # Get unique (x,z) positions from concatenated array of (x,z) positions
        unique_positions = np.unique(all_positions, axis=0)
        unique_traces = np.unique(traces, axis=0)
        unique_sources = np.unique(sources, axis=0)

        return all_positions, unique_positions, unique_traces, unique_sources

    #######################################
    # Show and edit headers functions
    #######################################

    def showRawHeaders(self):
        if self.streams:
            files = [os.path.basename(file) for file in self.fileNames]
            file_header_values = {}
            
            # Collect headers for all files, not just the current one
            for file_idx, file_name in enumerate(self.fileNames):
                raw_header_values = {}
                file_basename = os.path.basename(file_name)
                
                # Collect unique headers and their values across all traces
                for trace in self.streams[file_idx]:
                    for header, value in trace.stats[self.input_format[file_idx]].trace_header.items():
                        if header not in raw_header_values:
                            raw_header_values[header] = []
                        raw_header_values[header].append(value)
                        
                file_header_values[file_basename] = raw_header_values
            
            # Pass all files to HeaderDialog, not just the current one
            dialog = HeaderDialog(files, list(set().union(*[set(values.keys()) for values in file_header_values.values()])), file_header_values, self)
            dialog.exec_()

    def showHeaders(self):
        if self.streams:
            files = [os.path.basename(file) for file in self.fileNames]
            attributes_to_collect = {
                "ffid": "FFID",
                "shot_trace_number": "Trace No",
                "delay": "Delay (s)",
                "sample_interval": "Sample Interval (s)",
                "n_sample": "Number of Samples",
                "record_length": "Record Length (s)",
                "source_position": "Source Position (m)",
                "source_elevation": "Source Elevation (m)",
                "trace_position": "Trace Position (m)",
                "trace_elevation": "Trace Elevation (m)",
                "offset": "Offset (m)",
            }

            # Collect unique headers and their values across all traces
            header_values = {}

            for i, file in enumerate(files):
                header_values[file] = {}
                for header, display_name in attributes_to_collect.items():
                    header_values[file][display_name] = []
                    attribute_values = getattr(self, header, [])[i]
                    trace_numbers = getattr(self, "shot_trace_number", [])[i]
                    if not isinstance(attribute_values, list):
                        attribute_values = [attribute_values]

                    for trace_number, value in zip(trace_numbers, attribute_values):
                        if isinstance(value, (list, tuple, np.ndarray)):
                            # Flatten the list if it contains lists
                            for item in value:
                                if isinstance(item, (list, tuple, np.ndarray)):
                                    header_values[file][display_name].extend((trace_number, v) for v in item)
                                else:
                                    header_values[file][display_name].append((trace_number, item))
                        else:
                            header_values[file][display_name].append((trace_number, value))

            # Sort the values by trace number
            for file in header_values:
                for key in header_values[file]:
                    header_values[file][key] = [v for _, v in sorted(header_values[file][key], key=lambda x: x[0])]

            dialog = HeaderDialog(files, list(attributes_to_collect.values()), header_values, self)
            dialog.exec_()

    def editFFID(self):
        if self.streams:
            parameters = [
            {'label': 'FFID', 'initial_value': self.ffid[self.currentIndex], 'type': 'int'},
            ]

            dialog = GenericParameterDialog(
                title="Edit FFID",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()

                ffid = values['FFID']
                self.ffid[self.currentIndex] = int(ffid)
                QMessageBox.information(self, "FFID Updated", f"FFID set to {ffid} for file {os.path.basename(self.currentFileName)}")

                self.updateTitle()
                self.updateFileListDisplay()
                self.plotBottom()


    def editDelay(self):
        if self.streams:
            parameters = [
            {'label': 'Delay (in s)', 'initial_value': self.delay[self.currentIndex], 'type': 'float'},
            ]

            dialog = GenericParameterDialog(
                title="Edit Delay",
                parameters=parameters,
                add_checkbox=True,
                checkbox_text="Apply to all shots",
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                apply_to_all = dialog.isChecked()
                delay = values['Delay (in s)']
                diff_delay = delay - self.delay[self.currentIndex]

                if apply_to_all: 
                    self.delay = [delay] * len(self.delay)  # Apply the delay to all files
                    self.time = [np.arange(n_sample) * sample_interval + delay for n_sample, sample_interval in zip(self.n_sample, self.sample_interval)]
                    # Update the picks with the new delay for files containing picks
                    for i, picks in enumerate(self.picks):
                        if picks is not None:
                            self.picks[i] = [pick + diff_delay for pick in picks]
                    QMessageBox.information(self, "Delay Updated", f"Delay set to {delay} s for all files")

                else:
                    self.delay[self.currentIndex] = delay
                    self.time[self.currentIndex] = np.arange(self.n_sample[self.currentIndex]) * self.sample_interval[self.currentIndex] + self.delay[self.currentIndex]
                    if self.picks is not None:
                        self.picks[self.currentIndex] = [pick + diff_delay for pick in self.picks[self.currentIndex]]
                    QMessageBox.information(self, "Delay Updated", f"Delay set to {delay} s for file {os.path.basename(self.currentFileName)}")
                
                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def editSampleInterval(self):
        if self.streams:
            parameters = [
            {'label': 'Sample Interval (in s)', 'initial_value': self.sample_interval[self.currentIndex], 'type': 'float'},
            ]

            dialog = GenericParameterDialog(
                title="Edit Sample Interval",
                parameters=parameters,
                add_checkbox=True,
                checkbox_text="Apply to all shots",
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                apply_to_all = dialog.isChecked()

                sample_interval = values['Sample Interval (in s)']
                self.sample_interval[self.currentIndex] = sample_interval
                self.time[self.currentIndex] = np.arange(self.n_sample[self.currentIndex]) * self.sample_interval[self.currentIndex] + self.delay[self.currentIndex]
                if apply_to_all:
                    self.sample_interval = [sample_interval] * len(self.sample_interval)
                    self.time = [np.arange(n_sample) * sample_interval + delay for n_sample, delay in zip(self.n_sample, self.delay)]
                    QMessageBox.information(self, "Sample Interval Updated", f"Sample interval set to {sample_interval} s for all files")
                else:
                    QMessageBox.information(self, "Sample Interval Updated", f"Sample interval set to {sample_interval} s for file {os.path.basename(self.currentFileName)}")

                self.plotSeismo()

    def editSourcePosition(self):
        if self.streams:
            parameters = [
            {'label': 'Source Position (in m)', 'initial_value': self.source_position[self.currentIndex], 'type': 'float'},
            ]

            dialog = GenericParameterDialog(
                title="Edit Source Position",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                source_position = values['Source Position (in m)']
                self.source_position[self.currentIndex] = source_position
                self.offset[self.currentIndex] = self.trace_position[self.currentIndex] - source_position
                QMessageBox.information(self, "Source Position Updated", f"Source position set to {source_position} m for file {os.path.basename(self.currentFileName)}")

                self.updateMeanSpacing()
                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def editTracePosition(self):
        if self.streams:
            trace_numbers = self.shot_trace_number[self.currentIndex]
            trace_positions = self.trace_position[self.currentIndex]

            dialog = TraceSelector(trace_numbers, trace_positions, parent=self,title="Edit Trace Position",show_position=True)
            if dialog.exec_():
                selected_index, new_position, apply_to_all = dialog.getValues()
                if apply_to_all:
                    # Set trace position for all files
                    for i in range(len(self.streams)):
                        self.trace_position[i][selected_index] = new_position
                        self.offset[i][selected_index] = new_position - self.source_position[i]
                    QMessageBox.information(self, "Trace Position Updated", f"Trace position for trace #{trace_numbers[selected_index]} set to {new_position} m for all files")
                else:
                    self.trace_position[self.currentIndex][selected_index] = new_position
                    self.offset[self.currentIndex][selected_index] = new_position - self.source_position[self.currentIndex]
                    QMessageBox.information(self, "Trace Position Updated", f"Trace position for trace #{trace_numbers[selected_index]} set to {new_position} m for file {os.path.basename(self.currentFileName)}")

                self.updateMeanSpacing()
                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def swapTraces(self):
        if self.streams:
            parameters = [
            {'label': 'First Trace #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Second Trace #', 'initial_value': 2, 'type': 'int'}
            ]

            dialog = GenericParameterDialog(
                title="Swap Traces",
                parameters=parameters,
                add_checkbox=True,
                checkbox_text="Apply to all shots",
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                first_trace = values['First Trace #']
                second_trace = values['Second Trace #']

                # Swap the traces
                if dialog.isChecked():
                    for i in range(len(self.streams)):
                        self.streams[i] = swap_traces(self.streams[i], first_trace, second_trace)
                    QMessageBox.information(self, "Traces Swapped", f"Traces {first_trace} and {second_trace} swapped for all files")
                else:
                    self.streams[self.currentIndex] = swap_traces(self.streams[self.currentIndex], first_trace, second_trace)
                    QMessageBox.information(self, "Traces Swapped", f"Traces {first_trace} and {second_trace} swapped for file {os.path.basename(self.currentFileName)}")

                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def removeTrace(self):
        if self.streams:
            trace_numbers = self.shot_trace_number[self.currentIndex]
            dialog = TraceSelector(trace_numbers, trace_positions=None, parent=self,title="Remove Trace",show_position=False)
            if dialog.exec_():
                selected_index, apply_to_all = dialog.getValues()
                selected_trace = trace_numbers[selected_index]

                if apply_to_all:
                    # Remove the trace for all files
                    for i in range(len(self.streams)):
                        trace_numbers = self.shot_trace_number[i]
                        selected_indices = np.where(np.array(trace_numbers) == selected_trace)[0]

                        if selected_indices.size == 0:
                            QMessageBox.information(self, "Trace Not Found", f"Trace #{selected_trace} not found in file {os.path.basename(self.fileNames[i])}")
                            continue  # Skip to the next file if the trace is not found
                        
                        selected_index = selected_indices[0]
                        
                        self.streams[i] = remove_trace(self.streams[i], selected_trace)
                        self.offset[i] = np.delete(self.offset[i], selected_index)
                        self.trace_position[i] = np.delete(self.trace_position[i], selected_index)
                        self.trace_elevation[i] = np.delete(self.trace_elevation[i], selected_index)
                        self.shot_trace_number[i] = np.delete(self.shot_trace_number[i], selected_index)
                        self.file_trace_number[i] = np.delete(self.file_trace_number[i], selected_index)
                        self.picks[i] = np.delete(self.picks[i], selected_index)
                        self.error[i] = np.delete(self.error[i], selected_index)
                        self.pickSeismoItems[i] = np.delete(self.pickSeismoItems[i], selected_index)
                        self.pickSetupItems[i] = np.delete(self.pickSetupItems[i], selected_index)
                    QMessageBox.information(self, "Trace Removed", f"Trace #{trace_numbers[selected_index]} removed for all files")
                else:
                    selected_indices = np.where(np.array(trace_numbers) == selected_trace)[0]
                    if selected_indices.size == 0:
                        QMessageBox.information(self, "Trace Not Found", f"Trace #{selected_trace} not found in file {os.path.basename(self.currentFileName)}")
                        return  # Exit the function if the trace is not found
                    
                    selected_index = selected_indices[0]
    
                    # Remove the trace for the current file
                    self.streams[self.currentIndex] = remove_trace(self.streams[self.currentIndex], selected_trace)
                    self.offset[self.currentIndex] = np.delete(self.offset[self.currentIndex], selected_index)
                    self.trace_position[self.currentIndex] = np.delete(self.trace_position[self.currentIndex], selected_index)
                    self.trace_elevation[self.currentIndex] = np.delete(self.trace_elevation[self.currentIndex], selected_index)
                    self.shot_trace_number[self.currentIndex] = np.delete(self.shot_trace_number[self.currentIndex], selected_index)
                    self.file_trace_number[self.currentIndex] = np.delete(self.file_trace_number[self.currentIndex], selected_index)
                    self.picks[self.currentIndex] = np.delete(self.picks[self.currentIndex], selected_index)
                    self.error[self.currentIndex] = np.delete(self.error[self.currentIndex], selected_index)
                    self.pickSeismoItems[self.currentIndex] = np.delete(self.pickSeismoItems[self.currentIndex], selected_index)
                    self.pickSetupItems[self.currentIndex] = np.delete(self.pickSetupItems[self.currentIndex], selected_index)
                    QMessageBox.information(self, "Trace Removed", f"Trace #{trace_numbers[selected_index]} removed for file {os.path.basename(self.currentFileName)}")

                self.updateMeanSpacing()
                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def moveTrace(self):
        if self.streams:
            parameters = [
            {'label': 'Trace #', 'initial_value': 1, 'type': 'int'},
            {'label': 'New Position', 'initial_value': 1, 'type': 'int'}
            ]

            dialog = GenericParameterDialog(
                title="Move Trace",
                parameters=parameters,
                add_checkbox=True,
                checkbox_text="Apply to all shots",
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                # trace_number in seismic file header trace_number_within_the_original_field_record
                trace_number = values['Trace #']
                # new_position in 0-based python indexing => potential conflict if trace in seismic file don't start at 1
                new_position = values['New Position'] - 1

                if dialog.isChecked():
                    for i in range(len(self.streams)):
                        self.streams[i] = move_trace(self.streams[i], trace_number, new_position)
                    QMessageBox.information(self, "Trace Moved", f"Trace #{trace_number} moved to position {new_position + 1} for all files")
                else:
                    self.streams[self.currentIndex] = move_trace(self.streams[self.currentIndex], trace_number, new_position)
                    QMessageBox.information(self, "Trace Moved", f"Trace #{trace_number} moved to position {new_position + 1} for file {os.path.basename(self.currentFileName)}")

                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def muteTrace(self):
        if self.streams:
            trace_numbers = self.shot_trace_number[self.currentIndex]
            dialog = TraceSelector(trace_numbers, trace_positions=None, parent=self,title="Mute Trace",show_position=False)
            if dialog.exec_():
                selected_index, apply_to_all = dialog.getValues()
                selected_trace = trace_numbers[selected_index]

                if apply_to_all:
                    # Mute the trace for all files
                    for i in range(len(self.streams)):
                        trace_numbers = self.shot_trace_number[i]
                        selected_indices = np.where(np.array(trace_numbers) == selected_trace)[0]

                        if selected_indices.size == 0:
                            QMessageBox.information(self, "Trace Not Found", f"Trace #{selected_trace} not found in file {os.path.basename(self.fileNames[i])}")
                            continue  # Skip to the next file if the trace is not found
                        selected_index = selected_indices[0]
                        self.streams[i] = mute_trace(self.streams[i], selected_trace)
                    QMessageBox.information(self, "Trace Muted", f"Trace #{trace_numbers[selected_index]} muted for all files")
                else:
                    selected_indices = np.where(np.array(trace_numbers) == selected_trace)[0]
                    if selected_indices.size == 0:
                        QMessageBox.information(self, "Trace Not Found", f"Trace #{selected_trace} not found in file {os.path.basename(self.currentFileName)}")
                        return  # Exit the function if the trace is not found
                    selected_index = selected_indices[0]
                    # Mute the trace for the current file
                    self.streams[self.currentIndex] = mute_trace(self.streams[self.currentIndex], selected_trace)
                    QMessageBox.information(self, "Trace Muted", f"Trace #{trace_numbers[selected_index]} muted for file {os.path.basename(self.currentFileName)}")
                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def batchEditFFID(self):
        if self.streams:
            parameters = [
            {'label': 'First Source #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Source #', 'initial_value': len(self.source_position), 'type': 'int'},
            {'label': 'First FFID', 'initial_value': self.ffid[0], 'type': 'int'},
            {'label': 'Increment', 'initial_value': 1, 'type': 'int'}
            ]

            dialog = GenericParameterDialog(
                title="Batch Edit FFID",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                first_shot = values['First Source #'] - 1
                last_shot = values['Last Source #']
                first_ffid = values['First FFID']
                increment = values['Increment']

                for i in range(first_shot, last_shot):
                    self.ffid[i] = first_ffid + i * increment
                QMessageBox.information(self, "FFIDs Updated", f"FFIDs set from {first_ffid} to {self.ffid[last_shot-1]} with increment {increment} for shots {first_shot+1} to {last_shot}")

                self.updateTitle()
                self.updateFileListDisplay()
                self.plotBottom()
    
    def batchEditDelay(self):
        if self.streams:
            parameters = [
            {'label': 'First Source #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Source #', 'initial_value': len(self.source_position), 'type': 'int'},
            {'label': 'Delay (in s)', 'initial_value': self.delay[self.currentIndex], 'type': 'float'},
            ]

            dialog = GenericParameterDialog(
                title="Batch Edit Delay",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                first_shot = values['First Source #'] - 1
                last_shot = values['Last Source #']
                delay = values['Delay (in s)']
                diff_delay = delay - self.delay[self.currentIndex]

                for i in range(first_shot, last_shot):
                    self.delay[i] = delay
                    self.time[i] = np.arange(self.n_sample[i]) * self.sample_interval[i] + self.delay[i]
                    if self.picks[i] is not None:
                        self.picks[i] = [pick + diff_delay for pick in self.picks[i]]

                QMessageBox.information(self, "Delays Updated", f"Delays set to {delay} s for shots {first_shot+1} to {last_shot}")

                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def batchEditSampleInterval(self):
        if self.streams:
            parameters = [
            {'label': 'First Source #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Source #', 'initial_value': len(self.source_position), 'type': 'int'},
            {'label': 'Sample Interval (in s)', 'initial_value': self.sample_interval[self.currentIndex], 'type': 'float'},
            ]

            dialog = GenericParameterDialog(
                title="Batch Edit Sample Interval",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                first_shot = values['First Source #'] - 1
                last_shot = values['Last Source #']
                sample_interval = values['Sample Interval (in s)']

                for i in range(first_shot, last_shot):
                    self.sample_interval[i] = sample_interval
                    self.time[i] = np.arange(self.n_sample[i]) * self.sample_interval[i] + self.delay[i]
                QMessageBox.information(self, "Sample Interval Updated", f"Sample intervals set to {sample_interval} s for shots {first_shot+1} to {last_shot}")

                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def batchEditSourcePosition(self):
        if self.streams:
            parameters = [
            {'label': 'First Source #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Source #', 'initial_value': len(self.source_position), 'type': 'int'},
            {'label': 'First Source Position (in m)', 'initial_value': self.source_position[0], 'type': 'float'},
            {'label': 'Spacing (in m)', 'initial_value': np.mean(np.diff(self.source_position)), 'type': 'float'}
            ]

            dialog = GenericParameterDialog(
                title="Batch Edit Source Position",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                first_shot = values['First Source #'] - 1
                last_shot = values['Last Source #']
                first_source_position = values['First Source Position (in m)']
                spacing = values['Spacing (in m)']
                source_pos = np.round(np.arange(first_shot,last_shot,1) * spacing + first_source_position, self.rounding)

                for i in range(first_shot, last_shot):
                    self.source_position[i] = source_pos[i]
                    for j in range(len(self.trace_position[i])):    
                        self.offset[i][j] = np.round(self.trace_position[i][j] - self.source_position[i], self.rounding)
                QMessageBox.information(self, "Source Positions Updated", f"Source positions set from {first_source_position} m with spacing {spacing} m for shots {first_shot+1} to {last_shot}")

                self.updateMeanSpacing()
                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def batchEditTracePosition(self):
        if self.streams:
            parameters = [
            {'label': 'First Source #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Source #', 'initial_value': len(self.source_position), 'type': 'int'},
            {'label': 'First Trace #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Trace #', 'initial_value': len(self.trace_position[self.currentIndex]), 'type': 'int'},
            {'label': 'First Trace Position (in m)', 'initial_value': self.trace_position[self.currentIndex][0], 'type': 'float'},
            {'label': 'Spacing (in m)', 'initial_value': np.mean(np.diff(self.trace_position[self.currentIndex])), 'type': 'float'}
            ]

            dialog = GenericParameterDialog(
                title="Batch Edit Trace Position",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                first_shot = values['First Source #'] - 1
                last_shot = values['Last Source #']
                first_trace = values['First Trace #'] - 1
                last_trace = values['Last Trace #']
                first_trace_position = values['First Trace Position (in m)']
                spacing = values['Spacing (in m)']
                trace_pos = np.round(np.arange(first_trace,last_trace,1) * spacing + first_trace_position, self.rounding)

                for i in range(first_shot, last_shot):
                    for j in range(first_trace, last_trace):
                        self.trace_position[i][j] = trace_pos[j]
                        self.offset[i][j] = np.round(self.trace_position[i][j] - self.source_position[i], self.rounding)
                QMessageBox.information(
                    self,
                    "Trace Positions Updated",
                    f"Trace positions set from {first_trace_position} m with spacing {spacing} m for traces {first_trace+1} to {last_trace} for shots {first_shot+1} to {last_shot}"
                )

                self.updateMeanSpacing()
                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def batchSwapTraces(self):
        if self.streams:
            parameters = [
            {'label': 'First Source #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Source #', 'initial_value': len(self.source_position), 'type': 'int'},
            {'label': 'First Trace # to swap', 'initial_value': 1, 'type': 'int'},
            {'label': 'Second Trace # to swap', 'initial_value': 2, 'type': 'int'}
            ]

            dialog = GenericParameterDialog(
                title="Batch Swap Traces",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                first_shot = values['First Source #'] - 1
                last_shot = values['Last Source #']
                first_trace = values['First Trace # to swap']
                second_trace = values['Second Trace # to swap']

                for i in range(first_shot, last_shot):
                    self.streams[i] = swap_traces(self.streams[i], first_trace, second_trace)
                QMessageBox.information(self, "Traces Swapped", f"Traces {first_trace} and {second_trace} swapped for all files")

                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def batchRemoveTraces(self):
        if self.streams:
            parameters = [
            {'label': 'First Source #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Source #', 'initial_value': len(self.source_position), 'type': 'int'},
            {'label': 'First Trace # to remove', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Trace # to remove', 'initial_value': len(self.trace_position[self.currentIndex]), 'type': 'int'}
            ]

            dialog = GenericParameterDialog(
                title="Batch Remove Traces",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                first_shot = values['First Source #'] - 1
                last_shot = values['Last Source #']
                first_trace = values['First Trace # to remove']
                last_trace = values['Last Trace # to remove'] + 1

                for i in range(first_shot, last_shot):
                    for j in range(first_trace, last_trace):
                        trace_numbers = self.shot_trace_number[i]
                        selected_indices = np.where(np.array(trace_numbers) == j)[0]
                        if selected_indices.size == 0:
                            QMessageBox.information(self, "Trace Not Found", f"Trace #{j} not found in file {os.path.basename(self.fileNames[i])}")
                            continue
                        selected_index = selected_indices[0]
                        # Remove the trace for the current file
                        self.streams[i] = remove_trace(self.streams[i], j)
                        self.offset[i] = np.delete(self.offset[i], selected_index)
                        self.trace_position[i] = np.delete(self.trace_position[i], selected_index)
                        self.trace_elevation[i] = np.delete(self.trace_elevation[i], selected_index)
                        self.shot_trace_number[i] = np.delete(self.shot_trace_number[i], selected_index)
                        self.file_trace_number[i] = np.delete(self.file_trace_number[i], selected_index)
                        self.picks[i] = np.delete(self.picks[i], selected_index)
                        self.error[i] = np.delete(self.error[i], selected_index)
                        self.pickSeismoItems[i] = np.delete(self.pickSeismoItems[i], selected_index)
                        self.pickSetupItems[i] = np.delete(self.pickSetupItems[i], selected_index)
                        
                QMessageBox.information(self, "Traces Removed", f"Traces {first_trace} to {last_trace-1} removed for all files")

                self.updateMeanSpacing()
                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def batchMoveTraces(self):
        if self.streams:
            parameters = [
            {'label': 'First Source #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Source #', 'initial_value': len(self.source_position), 'type': 'int'},
            {'label': 'First Trace # to move', 'initial_value': 1, 'type': 'int'},
            {'label': 'New Position', 'initial_value': 1, 'type': 'int'}
            ]

            dialog = GenericParameterDialog(
                title="Batch Move Traces",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                first_shot = values['First Source #'] - 1
                last_shot = values['Last Source #']
                first_trace = values['First Trace # to move']
                new_position = values['New Position'] - 1

                for i in range(first_shot, last_shot):
                    self.streams[i] = move_trace(self.streams[i], first_trace, new_position)
                    
                QMessageBox.information(self, "Trace Moved", f"Trace #{first_trace} moved to position {new_position + 1} for all files")

                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    def batchMuteTraces(self):
        if self.streams:
            parameters = [
            {'label': 'First Source #', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Source #', 'initial_value': len(self.source_position), 'type': 'int'},
            {'label': 'First Trace # to mute', 'initial_value': 1, 'type': 'int'},
            {'label': 'Last Trace # to mute', 'initial_value': len(self.trace_position[self.currentIndex]), 'type': 'int'}
            ]

            dialog = GenericParameterDialog(
                title="Batch Mute Traces",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

            if dialog.exec_():
                values = dialog.getValues()
                first_shot = values['First Source #'] - 1
                last_shot = values['Last Source #']
                first_trace = values['First Trace # to mute']
                last_trace = values['Last Trace # to mute'] + 1

                for i in range(first_shot, last_shot):
                    for j in range(first_trace, last_trace):
                        trace_numbers = self.shot_trace_number[i]
                        selected_indices = np.where(np.array(trace_numbers) == j)[0]
                        if selected_indices.size == 0:
                            QMessageBox.information(self, "Trace Not Found", f"Trace #{j} not found in file {os.path.basename(self.fileNames[i])}")
                            continue

                        # Mute the trace for the current file
                        self.streams[i] = mute_trace(self.streams[i], j)
                        
                QMessageBox.information(self, "Traces Muted", f"Traces {first_trace+1} to {last_trace} muted for all files")

                self.plotSeismo()
                self.updateFileListDisplay()
                self.plotBottom()

    #######################################
    # Set parameters functions
    #######################################

    def setPicksColormapFromAction(self, cmap_name):
        # Remove any extra space if needed
        selected_cmap = cmap_name.strip()
        self.colormap_str = selected_cmap
        self.mpl_pick_colormap = selected_cmap

        # Optionally, print or log the new colormap
        self.statusBar.showMessage(f"Selected colormap: {selected_cmap}", 2000)
        self.update_pick_flag = True
        self.plotBottom()  # Refresh the plot with the new colormap

    def setMaxTime(self):
        if self.max_time is None:
            self.max_time = 0.05

        parameters = [
            {'label': 'Maximum Time (in s)', 'initial_value': self.max_time, 'type': 'float'}
        ]

        dialog = GenericParameterDialog(
                title="Set Maximum Time",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

        if dialog.exec_():
            self.cancelDialog = False
            values = dialog.getValues()
            if values['Maximum Time (in s)'] is not None:
                self.max_time = values['Maximum Time (in s)']
                self.mpl_tmax = self.max_time
                self.statusBar.showMessage(f"Maximum time set to {self.max_time} s", 2000)
                self.resetSeismoView()
            
        else:
            self.cancelDialog = True

    def setGain(self):
        if self.gain is None:
            self.gain = 1

        parameters = [
            {'label': 'Gain', 'initial_value': self.gain, 'type': 'float'}
        ]

        dialog = GenericParameterDialog(
                title="Set Gain",
                parameters=parameters,
                add_checkbox=False,
                parent=self
            )

        if dialog.exec_():
            self.cancelDialog = False
            values = dialog.getValues()
            if values['Gain'] is not None:
                self.gain = values['Gain']
                self.statusBar.showMessage(f"Gain set to {self.gain}", 2000)
                self.plotSeismo()
            
        else:
            self.cancelDialog = True

    def setErrorParameters(self):
        parameters = [
        {'label': 'Relative Error', 'initial_value': self.relativeError, 'type': 'float'},
        {'label': 'Absolute Error', 'initial_value': self.absoluteError, 'type': 'float'},
        {'label': 'Max Relative Error', 'initial_value': self.maxRelativeError, 'type': 'float'},
        {'label': 'Min Absolute Error', 'initial_value': self.minAbsoluteError, 'type': 'float'},
        {'label': 'Max Absolute Error', 'initial_value': self.maxAbsoluteError, 'type': 'float'}
        ]

        dialog = GenericParameterDialog(
            title="Set Error Parameters",
            parameters=parameters,
            parent=self
        )
        if dialog.exec_():
            self.cancelDialog = False
            values = dialog.getValues()
            self.relativeError = values['Relative Error']
            self.absoluteError = values['Absolute Error']
            self.maxRelativeError = values['Max Relative Error']
            self.minAbsoluteError = values['Min Absolute Error']
            self.maxAbsoluteError = values['Max Absolute Error']
            
        else:
            self.cancelDialog = True

    def setAssistedPickingParameters(self):
        parameters = [
        {'label': 'Smoothing Window Size', 'initial_value': self.smoothing_window_size, 'type': 'int'},
        {'label': 'Deviation Threshold', 'initial_value': self.deviation_threshold, 'type': 'float'},
        {'label': 'Picking Window Size', 'initial_value': self.picking_window_size, 'type': 'int'}
        ]

        dialog = GenericParameterDialog(
            title="Set Assisted Picking Parameters",
            parameters=parameters,
            parent=self
        )
        if dialog.exec_():
            self.cancelDialog = False
            values = dialog.getValues()
            self.smoothing_window_size = values['Smoothing Window Size']
            self.deviation_threshold = values['Deviation Threshold']
            self.picking_window_size = values['Picking Window Size']
            
        else:
            self.cancelDialog = True

    def setTopoParameters(self):
        parameters = [
        {'label': 'X Column #', 'initial_value': self.column_x + 1, 'type': 'int'},
        {'label': 'Z Column #', 'initial_value': self.column_z + 1, 'type': 'int'},
        {'label': 'Delimiter', 'initial_value': self.delimiter, 'type': 'str'},
        {'label': 'Number of rows to skip (0 to read all lines)', 'initial_value': self.skiprows, 'type': 'int'},
        {'label': 'List of columns to import (within brackets)', 'initial_value': self.usecols, 'type': 'list'}
        ]

        dialog = GenericParameterDialog(
            title="Set Topography Parameters",
            parameters=parameters,
            parent=self
        )

        if dialog.exec_():
            self.cancelDialog = False
            values = dialog.getValues()
            self.column_x = values['X Column #'] - 1
            self.column_z = values['Z Column #'] - 1
            self.delimiter = values['Delimiter']
            self.skiprows = values['Number of rows to skip (0 to read all lines)']
            self.usecols = values['List of columns to import (within brackets)']
            if self.usecols == []:
                self.usecols = None
            else:
                # check if 0 is in the list
                if 0 not in self.usecols:
                    # remove 1 from each column number
                    self.usecols = [col - 1 for col in self.usecols]
                else:
                    QMessageBox.information(self, "Column Indexing", "Column numbers start at 0, assuming Python indexing.")

        else:
            self.cancelDialog = True

    def setMplExportSeismoParameters(self):
        parameters = [
            {'label': 'Figure DPI', 'initial_value': self.mpl_dpi, 'type': 'int'},
            {'label': 'Figure Width (in inches)', 'initial_value': self.mpl_aspect_ratio[0], 'type': 'float'},
            {'label': 'Figure Height (in inches)', 'initial_value': self.mpl_aspect_ratio[1], 'type': 'float'},
            {'label': 'Font Size', 'initial_value': self.mpl_font_size, 'type': 'int'},
            {'label': 'X-Axis Position', 'initial_value': self.mpl_xaxis_position, 'type': 'combo', 'values': ['top', 'bottom']},
            {'label': 'Y-Axis Position', 'initial_value': self.mpl_yaxis_position, 'type': 'combo', 'values': ['left', 'right']},
            {'label': 'Invert Y-Axis', 'initial_value': self.mpl_invert_yaxis, 'type': 'bool'},
            {'label': 'Show Title', 'initial_value': self.mpl_show_title, 'type': 'bool'},
            {'label': 'Line Color', 'initial_value': 'self.mpl_line_color', 'type': 'combo', 'values': ['k', 'r', 'g', 'b', 'c', 'm', 'y']},
            {'label': 'Line Width', 'initial_value': self.mpl_line_width, 'type': 'float'},
            {'label': 'Fill Color', 'initial_value': self.mpl_fill_color, 'type': 'combo', 'values': ['k', 'r', 'g', 'b', 'c', 'm', 'y']},
            {'label': 'Fill Alpha', 'initial_value': self.mpl_fill_alpha, 'type': 'float'},
            {'label': 'Show Picks', 'initial_value': self.mpl_show_picks, 'type': 'bool'},
            {'label': 'Pick Color', 'initial_value': self.mpl_pick_color, 'type': 'combo', 'values': ['k', 'r', 'g', 'b', 'c', 'm', 'y']},
            {'label': 'Pick Marker', 'initial_value': self.mpl_pick_marker_alt, 'type': 'combo', 'values': ['o', 's', 'p', 'P', '*', '+', 'x']},
            {'label': 'Pick Marker Size', 'initial_value': self.mpl_pick_marker_size_alt, 'type': 'int'},
            {'label': 'Show Source', 'initial_value': self.mpl_show_source, 'type': 'bool'},
            {'label': 'Source Color', 'initial_value': self.mpl_source_color, 'type': 'combo', 'values': ['k', 'r', 'g', 'b', 'c', 'm', 'y']},
            {'label': 'Source Marker', 'initial_value': self.mpl_source_marker, 'type': 'combo', 'values': ['o', 's', 'p', 'P', '*', '+', 'x']},
            {'label': 'Source Size', 'initial_value': self.mpl_source_marker_size, 'type': 'int'},
            {'label': 'Time in Milliseconds', 'initial_value': self.mpl_time_in_ms, 'type': 'bool'},
            {'label': 'X Min (in m)', 'initial_value': self.mpl_xmin, 'type': 'float'},
            {'label': 'X Max (in m)', 'initial_value': self.mpl_xmax, 'type': 'float'},
            {'label': 'T Min (in s)', 'initial_value': self.mpl_tmin, 'type': 'float'},
            {'label': 'T Max (in s)', 'initial_value': self.mpl_tmax, 'type': 'float'}
        ]

        # Create parameter mapping
        param_map = {param['label']: param['initial_value'] for param in parameters}

        dialog = GenericParameterDialog(
            title="Set Matplotlib Export Parameters",
            parameters=parameters,
            parent=self
        )

        if dialog.exec_():
            self.cancelDialog = False
            values = dialog.getValues()
            # Get values with defaults
            self.mpl_dpi = values.get('Figure DPI', param_map['Figure DPI'])
            self.mpl_aspect_ratio = (
                values.get('Figure Width (in inches)', param_map['Figure Width (in inches)']),
                values.get('Figure Height (in inches)', param_map['Figure Height (in inches)'])
            )
            self.mpl_font_size = values.get('Font Size', param_map['Font Size'])
            self.mpl_xaxis_position = values.get('X-Axis Position', param_map['X-Axis Position'])
            self.mpl_yaxis_position = values.get('Y-Axis Position', param_map['Y-Axis Position'])
            self.mpl_invert_yaxis = values.get('Invert Y-Axis', param_map['Invert Y-Axis'])
            self.mpl_show_title = values.get('Show Title', param_map['Show Title'])
            self.mpl_line_color = values.get('Line Color', param_map['Line Color'])
            self.mpl_line_width = values.get('Line Width', param_map['Line Width'])
            self.mpl_fill_color = values.get('Fill Color', param_map['Fill Color'])
            self.mpl_fill_alpha = values.get('Fill Alpha', param_map['Fill Alpha'])
            self.mpl_show_picks = values.get('Show Picks', param_map['Show Picks'])
            self.mpl_pick_color = values.get('Pick Color', param_map['Pick Color'])
            self.mpl_pick_marker_alt = values.get('Pick Marker', param_map['Pick Marker'])
            self.mpl_pick_marker_size_alt = values.get('Pick Marker Size', param_map['Pick Marker Size'])
            self.mpl_show_source = values.get('Show Source', param_map['Show Source'])
            self.mpl_source_color = values.get('Source Color', param_map['Source Color'])
            self.mpl_source_marker = values.get('Source Marker', param_map['Source Marker'])
            self.mpl_source_marker_size = values.get('Source Size', param_map['Source Size'])
            self.mpl_time_in_ms = values.get('Time in Milliseconds', param_map['Time in Milliseconds'])
            self.mpl_xmin = values.get('X Min (in m)', param_map['X Min (in m)'])
            self.mpl_xmax = values.get('X Max (in m)', param_map['X Max (in m)'])
            self.mpl_tmin = values.get('T Min (in s)', param_map['T Min (in s)'])
            self.mpl_tmax = values.get('T Max (in s)', param_map['T Max (in s)'])
        else:
            self.cancelDialog = True

    def setMplExportSetupParameters(self):
        pick_min, pick_max = self.getMinMaxPicks()
        parameters = [
                {'label': 'Figure DPI', 'initial_value': self.mpl_dpi, 'type': 'int'},
                {'label': 'Figure Width (in inches)', 'initial_value': self.mpl_aspect_ratio[0], 'type': 'float'},
                {'label': 'Figure Height (in inches)', 'initial_value': self.mpl_aspect_ratio[1], 'type': 'float'},
                {'label': 'Equal Aspect Ratio', 'initial_value': self.mpl_equal_aspect, 'type': 'bool'},
                {'label': 'Font Size', 'initial_value': self.mpl_font_size, 'type': 'int'},
                {'label': 'X-Axis Position', 'initial_value': self.mpl_xaxis_position, 'type': 'combo', 'values': ['top', 'bottom']},
                {'label': 'Y-Axis Position', 'initial_value': self.mpl_yaxis_position, 'type': 'combo', 'values': ['left', 'right']},
                {'label': 'Invert Y-Axis', 'initial_value': self.mpl_invert_yaxis, 'type': 'bool'},
                {'label': 'Trace Marker', 'initial_value': self.mpl_trace_marker, 'type': 'combo', 'values': ['o', 's', 'p', 'P', '*', '+', 'x']},
                {'label': 'Trace Marker Size', 'initial_value': self.mpl_trace_marker_size, 'type': 'int'},
                {'label': 'Trace Marker Color', 'initial_value': self.mpl_trace_marker_color, 'type': 'combo', 'values': ['k', 'r', 'g', 'b', 'c', 'm', 'y']},
                {'label': 'Trace Marker Alpha', 'initial_value': self.mpl_trace_marker_alpha, 'type': 'float'},
                {'label': 'Pick Marker', 'initial_value': self.mpl_pick_marker, 'type': 'combo', 'values': ['o', 's', 'p', 'P', '*', '+', 'x']},
                {'label': 'Pick Marker Size', 'initial_value': self.mpl_pick_marker_size, 'type': 'int'},
                {'label': 'Pick Colormap', 'initial_value': self.mpl_pick_colormap, 'type': 'combo', 'values': ['viridis', 'plasma', 'inferno', 'magma', 'cividis'
                                                                                                                'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 
                                                                                                                'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 
                                                                                                                'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
                                                                                                                'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone',
                                                                                                                'pink', 'spring', 'summer', 'autumn', 'winter', 'cool',
                                                                                                                'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper'
                                                                                                                'ocean', 'gist_earth', 'terrain',
                                                                                                                'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap',
                                                                                                                'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet',
                                                                                                                'turbo', 'nipy_spectral', 'gist_ncar']},
                {'label': 'Reverse Colormap', 'initial_value': self.mpl_reverse_colormap, 'type': 'bool'},
                {'label': 'Colorbar Position', 'initial_value': self.mpl_colorbar_position, 'type': 'combo', 'values': ['right', 'left', 'top', 'bottom', 'None']},
                {'label': 'Time in Milliseconds', 'initial_value': self.mpl_time_in_ms, 'type': 'bool'},
                {'label': 'Min Time (in s)', 'initial_value': pick_min, 'type': 'float'},
                {'label': 'Max Time (in s)', 'initial_value': pick_max, 'type': 'float'},
                {'label': 'X Min (in m)', 'initial_value': self.mpl_xmin, 'type': 'float'},
                {'label': 'X Max (in m)', 'initial_value': self.mpl_xmax, 'type': 'float'},
                {'label': 'Y Min (in m)', 'initial_value': self.mpl_ymin, 'type': 'float'},
                {'label': 'Y Max (in m)', 'initial_value': self.mpl_ymax, 'type': 'float'}
            ]
        
        # Create parameter mapping
        param_map = {param['label']: param['initial_value'] for param in parameters}

        dialog = GenericParameterDialog(
            title="Set Matplotlib Export Parameters",
            parameters=parameters,
            parent=self
        )

        if dialog.exec_():
            self.cancelDialog = False
            values = dialog.getValues()
            # Get values with defaults
            self.mpl_dpi = values.get('Figure DPI', param_map['Figure DPI'])
            self.mpl_aspect_ratio = (
                values.get('Figure Width (in inches)', param_map['Figure Width (in inches)']),
                values.get('Figure Height (in inches)', param_map['Figure Height (in inches)'])
            )
            self.mpl_equal_aspect = values.get('Equal Aspect Ratio', param_map['Equal Aspect Ratio'])
            self.mpl_font_size = values.get('Font Size', param_map['Font Size'])
            self.mpl_xaxis_position = values.get('X-Axis Position', param_map['X-Axis Position'])
            self.mpl_yaxis_position = values.get('Y-Axis Position', param_map['Y-Axis Position'])
            self.mpl_invert_yaxis = values.get('Invert Y-Axis', param_map['Invert Y-Axis'])
            self.mpl_trace_marker = values.get('Trace Marker', param_map['Trace Marker'])
            self.mpl_trace_marker_size = values.get('Trace Marker Size', param_map['Trace Marker Size'])
            self.mpl_trace_marker_color = values.get('Trace Marker Color', param_map['Trace Marker Color'])
            self.mpl_trace_marker_alpha = values.get('Trace Marker Alpha', param_map['Trace Marker Alpha'])
            self.mpl_pick_marker = values.get('Pick Marker', param_map['Pick Marker'])
            self.mpl_pick_marker_size = values.get('Pick Marker Size', param_map['Pick Marker Size'])
            self.mpl_pick_colormap = values.get('Pick Colormap', param_map['Pick Colormap'])
            self.mpl_reverse_colormap = values.get('Reverse Colormap', param_map['Reverse Colormap'])
            self.mpl_colorbar_position = values.get('Colorbar Position', param_map['Colorbar Position'])
            self.mpl_time_in_ms = values.get('Time in Milliseconds', param_map['Time in Milliseconds'])
            self.mpl_tmin = values.get('Min Time (in s)', param_map['Min Time (in s)'])
            self.mpl_tmax = values.get('Max Time (in s)', param_map['Max Time (in s)'])
            self.mpl_xmin = values.get('X Min (in m)', param_map['X Min (in m)'])
            self.mpl_xmax = values.get('X Max (in m)', param_map['X Max (in m)'])
            self.mpl_ymin = values.get('Y Min (in m)', param_map['Y Min (in m)'])
            self.mpl_ymax = values.get('Y Max (in m)', param_map['Y Max (in m)'])
        else:
            self.cancelDialog = True

    def setMplExportTravelTimeParameters(self):
        pick_min, pick_max = self.getMinMaxPicks()
        parameters = [
            {'label': 'Figure DPI', 'initial_value': self.mpl_dpi, 'type': 'int'},
            {'label': 'Figure Width (in inches)', 'initial_value': self.mpl_aspect_ratio[0], 'type': 'float'},
            {'label': 'Figure Height (in inches)', 'initial_value': self.mpl_aspect_ratio[1], 'type': 'float'},
            {'label': 'Font Size', 'initial_value': self.mpl_font_size, 'type': 'int'},
            {'label': 'X-Axis Position', 'initial_value': self.mpl_xaxis_position, 'type': 'combo', 'values': ['top', 'bottom']},
            {'label': 'Y-Axis Position', 'initial_value': self.mpl_yaxis_position, 'type': 'combo', 'values': ['left', 'right']},
            {'label': 'Invert Y-Axis', 'initial_value': self.mpl_invert_yaxis, 'type': 'bool'},
            {'label': 'Show Grid', 'initial_value': self.mpl_show_grid, 'type': 'bool'},
            {'label': 'Line Color Style','initial_value': self.mpl_line_colorstyle, 'type': 'combo', 'values': ['single color', 'qualitative colormap', 'sequential colormap']},
            {'label': 'Qualitative Colormap', 'initial_value': self.mpl_qualitative_cm, 'type': 'combo', 'values': ['tab10', 'tab20', 'tab20b', 'tab20c',
                                                                                                                    'Pastel1', 'Pastel2', 'Paired', 'Accent',
                                                                                                                    'Dark2', 'Set1', 'Set2', 'Set3']},
            {'label': 'Sequential Colormap', 'initial_value': self.mpl_sequential_cm, 'type': 'combo', 'values': ['viridis', 'plasma', 'inferno', 'magma', 'cividis',
                                                                                                                'Greys', 'Purples', 'Blues', 'Greens', 'Oranges',
                                                                                                                'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu',
                                                                                                                'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
                                                                                                                'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone',
                                                                                                                'pink', 'spring', 'summer', 'autumn', 'winter', 'cool',
                                                                                                                'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper'
                                                                                                                'ocean', 'gist_earth', 'terrain',
                                                                                                                'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap',
                                                                                                                'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet',
                                                                                                                'turbo', 'nipy_spectral', 'gist_ncar']},
            {'label': 'Line Color', 'initial_value': self.mpl_line_color, 'type': 'combo', 'values': ['k', 'r', 'g', 'b', 'c', 'm', 'y']},
            {'label': 'Line Width', 'initial_value': self.mpl_line_width, 'type': 'float'},
            {'label': 'Pick Color', 'initial_value': self.mpl_pick_color, 'type': 'combo', 'values': ['k', 'r', 'g', 'b', 'c', 'm', 'y']},
            {'label': 'Pick Marker', 'initial_value': self.mpl_pick_marker_alt, 'type': 'combo', 'values': ['o', 's', 'p', 'P', '*', '+', 'x']},
            {'label': 'Pick Marker Size', 'initial_value': self.mpl_pick_marker_size_alt, 'type': 'int'},
            {'label': 'Show Source', 'initial_value': self.mpl_show_source, 'type': 'bool'},
            {'label': 'Source Color', 'initial_value': self.mpl_source_color, 'type': 'combo', 'values': ['k', 'r', 'g', 'b', 'c', 'm', 'y']},
            {'label': 'Source Marker', 'initial_value': self.mpl_source_marker, 'type': 'combo', 'values': ['o', 's', 'p', 'P', '*', '+', 'x']},
            {'label': 'Source Size', 'initial_value': self.mpl_source_marker_size, 'type': 'int'},
            {'label': 'Time in Milliseconds', 'initial_value': self.mpl_time_in_ms, 'type': 'bool'},
            {'label': 'Min Time (in s)', 'initial_value': pick_min, 'type': 'float'},
            {'label': 'Max Time (in s)', 'initial_value': pick_max, 'type': 'float'},
            {'label': 'X Min (in m)', 'initial_value': self.mpl_xmin, 'type': 'float'},
            {'label': 'X Max (in m)', 'initial_value': self.mpl_xmax, 'type': 'float'},
        ]

        # Create parameter mapping
        param_map = {param['label']: param['initial_value'] for param in parameters}

        dialog = GenericParameterDialog(
            title="Set Matplotlib Export Parameters",
            parameters=parameters,
            parent=self
        )

        if dialog.exec_():
            self.cancelDialog = False
            values = dialog.getValues()
            # Get values with defaults
            self.mpl_dpi = values.get('Figure DPI', param_map['Figure DPI'])
            self.mpl_aspect_ratio = (
                values.get('Figure Width (in inches)', param_map['Figure Width (in inches)']),
                values.get('Figure Height (in inches)', param_map['Figure Height (in inches)'])
            )
            self.mpl_font_size = values.get('Font Size', param_map['Font Size'])
            self.mpl_xaxis_position = values.get('X-Axis Position', param_map['X-Axis Position'])
            self.mpl_yaxis_position = values.get('Y-Axis Position', param_map['Y-Axis Position'])
            self.mpl_invert_yaxis = values.get('Invert Y-Axis', param_map['Invert Y-Axis'])
            self.mpl_show_grid = values.get('Show Grid', param_map['Show Grid'])
            self.mpl_line_colorstyle = values.get('Line Color Style', param_map['Line Color Style'])
            self.mpl_qualitative_cm = values.get('Qualitative Colormap', param_map['Qualitative Colormap'])
            self.mpl_sequential_cm = values.get('Sequential Colormap', param_map['Sequential Colormap'])
            self.mpl_line_color = values.get('Line Color', param_map['Line Color'])
            self.mpl_line_width = values.get('Line Width', param_map['Line Width'])
            self.mpl_pick_color = values.get('Pick Color', param_map['Pick Color'])
            self.mpl_pick_marker_alt = values.get('Pick Marker', param_map['Pick Marker'])
            self.mpl_pick_marker_size_alt = values.get('Pick Marker Size', param_map['Pick Marker Size'])
            self.mpl_show_source = values.get('Show Source', param_map['Show Source'])
            self.mpl_source_color = values.get('Source Color', param_map['Source Color'])
            self.mpl_source_marker = values.get('Source Marker', param_map['Source Marker'])
            self.mpl_source_marker_size = values.get('Source Size', param_map['Source Size'])
            self.mpl_time_in_ms = values.get('Time in Milliseconds', param_map['Time in Milliseconds'])
            self.mpl_tmin = values.get('Min Time (in s)', param_map['Min Time (in s)'])
            self.mpl_tmax = values.get('Max Time (in s)', param_map['Max Time (in s)'])
            self.mpl_xmin = values.get('X Min (in m)', param_map['X Min (in m)'])
            self.mpl_xmax = values.get('X Max (in m)', param_map['X Max (in m)'])
        else:
            self.cancelDialog = True

    #######################################
    # Toggle functions
    #######################################

    def fillPositive(self):
        self.fill = 'positive'
        self.fillPositiveAction.setChecked(True)
        self.fillNegativeAction.setChecked(False)
        self.noFillAction.setChecked(False)
        self.statusBar.showMessage('Filling positive amplitudes',1000)
        if self.streams:
            self.plotSeismo()

    def fillNegative(self):
        self.fill = 'negative'
        self.fillPositiveAction.setChecked(False)
        self.fillNegativeAction.setChecked(True)
        self.noFillAction.setChecked(False)
        self.statusBar.showMessage('Filling negative amplitudes',1000)
        if self.streams:
            self.plotSeismo()

    def noFill(self):
        self.fill = 'none'
        self.fillPositiveAction.setChecked(False)
        self.fillNegativeAction.setChecked(False)
        self.noFillAction.setChecked(True)
        self.statusBar.showMessage('No fill',1000)
        if self.streams:
            self.plotSeismo()

    def toggleClip(self):
        self.clip = self.clipAction.isChecked()
        if self.streams:
            self.plotSeismo()

    def toggleNormalize(self):
        self.normalize = self.normalizeAction.isChecked()
        if self.streams:
            self.plotSeismo()

    def toggleShowTimeSamples(self):
        self.show_time_samples = self.showTimeSamplesAction.isChecked()
        if self.streams:
            self.plotSeismo()

    def toggleShowAirWave(self):
        self.show_air_wave = self.showAirWaveAction.isChecked()
        if self.streams:
            if self.show_air_wave:
                if self.plotTypeX == 'trace_position':
                    self.plotAirWave()
                else:   
                    QMessageBox.information(self, "Air Wave Not Plotted", "Air wave is not plotted when using trace number as X axis.")
            else:     
                self.hideAirWave()

    def toggleShowT0(self):
        self.show_t0 = self.showT0Action.isChecked()
        if self.streams:
            if self.show_t0:
                self.showT0()
            else:
                self.hideT0()

    def toggleAssistedPicking(self):
        self.assisted_picking = self.assistedPickingAction.isChecked()

    #######################################
    # Plot type functions
    #######################################

    def setWigglePlot(self):
        self.seismoType = 'wiggle'
        self.wiggleAction.setChecked(True)
        self.imageAction.setChecked(False)
        self.statusBar.showMessage('Switching to wiggle plot',1000)
        if self.streams:
            self.update_file_flag = True
            self.plotSeismo()

    def setImagePlot(self):
        self.seismoType = 'image'
        self.wiggleAction.setChecked(False)
        self.imageAction.setChecked(True)
        self.statusBar.showMessage('Switching to image plot',1000)
        if self.streams:
            self.update_file_flag = True
            self.plotSeismo()
        
    def setPlotTravelTime(self):
        self.bottomPlotType = 'traveltime'
        self.bottomPlotSetupAction.setChecked(False)
        self.bottomPlotTopographyAction.setChecked(False)
        self.bottomPlotTravelTimeAction.setChecked(True)
        self.statusBar.showMessage('Switching to traveltime plot',1000)
        if self.streams:
            self.update_file_flag = True
            self.plotBottom()

    def setPlotSetup(self):
        self.bottomPlotType = 'setup'
        self.bottomPlotTravelTimeAction.setChecked(False)
        self.bottomPlotTopographyAction.setChecked(False)
        self.bottomPlotSetupAction.setChecked(True)
        self.statusBar.showMessage('Switching to source/trace diagram',1000)
        if self.streams:
            self.update_file_flag = True
            self.plotBottom()

    def setPlotTopo(self):
        self.bottomPlotType = 'topo'
        self.bottomPlotTravelTimeAction.setChecked(False)
        self.bottomPlotSetupAction.setChecked(False)
        self.bottomPlotTopographyAction.setChecked(True)
        self.statusBar.showMessage('Switching to topography plot',1000)
        if self.streams:
            self.update_file_flag = True
            self.plotBottom()

    def setTracePositionPlot(self):
        self.plotTypeX = 'trace_position'
        self.tracePositionAction.setChecked(True)
        self.shotTraceNumberAction.setChecked(False)
        self.statusBar.showMessage('Switching to trace position',1000)
        if len(self.streams[self.currentIndex]) == 1:
            self.mean_dg = 1
        else:
            self.mean_dg = np.mean(np.diff(self.trace_position[self.currentIndex]))
        self.x_label = 'Trace Position (m)'
        if self.streams:
            self.update_file_flag = True
            self.plotSeismo()
            self.plotBottom()

    # def setFileTraceNumber(self):
    #     self.plotTypeX = 'file_trace_number'
    #     self.statusBar.showMessage('Switching to file trace number',1000)
    #     self.mean_dg = 1
    #     self.x_label = 'Trace number in file'
    #     if self.streams:
    #         self.plotSeismo()
    #         self.plotBottom()

    def setShotTraceNumberPlot(self):
        self.plotTypeX = 'shot_trace_number'
        self.shotTraceNumberAction.setChecked(True)
        self.tracePositionAction.setChecked(False)
        self.statusBar.showMessage('Switching to trace number',1000)
        self.mean_dg = 1
        self.x_label = 'Trace Number'
        if self.streams:
            self.update_file_flag = True
            self.plotSeismo()
            self.plotBottom()
                
    def setSourcePositionPlot(self):
        self.plotTypeY = 'source_position'
        self.sourcePositionAction.setChecked(True)
        self.ffidAction.setChecked(False)
        self.offsetAction.setChecked(False)
        self.statusBar.showMessage('Switching to source position',1000)
        if len(self.streams) == 1:
            self.mean_ds = 1
        else:
            self.mean_ds = np.mean(np.diff(self.source_position))
        self.y_label = 'Source Position (m)'
        if self.streams:
            self.update_file_flag = True
            self.plotBottom()

    def setFFIDPlot(self):
        self.plotTypeY = 'ffid'
        self.ffidAction.setChecked(True)
        self.sourcePositionAction.setChecked(False)
        self.offsetAction.setChecked(False)
        self.statusBar.showMessage('Switching to FFID',1000)
        self.mean_ds = 1
        self.y_label = 'FFID'
        if self.streams:
            self.update_file_flag = True
            self.plotBottom()

    def setOffsetPlot(self):
        self.plotTypeY = 'offset'
        self.offsetAction.setChecked(True)
        self.ffidAction.setChecked(False)
        self.sourcePositionAction.setChecked(False)
        self.statusBar.showMessage('Switching to offset',1000)
        if len(self.streams) == 1:
            self.mean_ds = 1
        else:
            self.mean_ds = np.mean(np.diff(self.source_position))
        self.y_label = 'Offset (m)'
        if self.streams:
            self.update_file_flag = True
            self.plotBottom()

    #######################################
    # Seismo plot functions
    #######################################

    def plotAirWave(self):
        # Velocity of the air wave in m/s
        air_wave_velocity = 340.0

        # Get the source position and offsets for the current index
        source_position = self.source_position[self.currentIndex]
        offsets = self.offset[self.currentIndex]

        # Separate positive and negative offsets
        positive_offsets = offsets[offsets > 0]
        negative_offsets = offsets[offsets < 0]

        # Calculate the corresponding times
        positive_times = positive_offsets / air_wave_velocity
        negative_times = -negative_offsets / air_wave_velocity

        # Concatenate positive and negative times and add 0 at source position
        positive_times = np.concatenate((np.array([0]), positive_times))
        negative_times = np.concatenate((np.array([0]), negative_times))

        # Concatenate positive and negative offsets and add 0 at the beginning
        positive_offsets = np.concatenate((np.array([0]), positive_offsets))
        negative_offsets = np.concatenate((np.array([0]), negative_offsets))

        # Plot the positive offsets
        self.airWaveItems[self.currentIndex][0] = pqg.PlotDataItem(positive_offsets + source_position, positive_times, pen='b')
        self.plotWidget.addItem(self.airWaveItems[self.currentIndex][0])

        # Plot the negative offsets
        self.airWaveItems[self.currentIndex][1] = pqg.PlotDataItem(negative_offsets + source_position, negative_times, pen='b')
        self.plotWidget.addItem(self.airWaveItems[self.currentIndex][1])

        # Add point scatter at the source position
        self.airWaveItems[self.currentIndex][2] = pqg.PlotDataItem(x=[source_position], y=[0], pen='b', symbol='o', 
                                                                        symbolBrush='b', symbolPen='b', symbolSize=5)
        self.plotWidget.addItem(self.airWaveItems[self.currentIndex][2])

    def hideAirWave(self):
        for item in self.airWaveItems[self.currentIndex]:
            if item is not None:
                self.plotWidget.removeItem(item)
                item = None

    def showT0(self):
        # Show an horizontal line at t=0
        self.t0Item = pqg.InfiniteLine(pos=0, angle=0, pen=self.col)
        self.plotWidget.addItem(self.t0Item)

    def hideT0(self):
        if self.t0Item is not None:
            self.plotWidget.removeItem(self.t0Item)
            self.t0Item = None

    def removeLegend(self):
        if hasattr(self, 'legend') and self.legend is not None:
            self.legend.scene().removeItem(self.legend)
            self.legend = None
        
    def removeColorBar(self):
        if hasattr(self, 'colorbar') and self.colorbar is not None:
            self.colorbar.scene().removeItem(self.colorbar)
            self.colorbar = None

    def removeTitle(self):
        self.plotWidget.getPlotItem().setTitle("")

    def updatePickPosition(self, i):
        # Ensure the dictionary is updated
        self.updatePlotTypeDict()

        # Access the appropriate attribute based on self.plotTypeX
        plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

        # Flatten the list of lists into a single list
        flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]

        # Get the x position based on the plot type
        x_ok = flat_plot_data_x[i] if i < len(flat_plot_data_x) else None

        # Get the y position (assuming y_ok is already defined)
        y_ok = self.picks[self.currentIndex][i] if i < len(self.picks[self.currentIndex]) else None

        # Update the pick position if x_ok and y_ok are valid
        if x_ok is not None and y_ok is not None:
            self.pickSeismoItems[self.currentIndex][i].setData(x=[x_ok], y=[y_ok])

    def updateTitle(self):
        if self.streams:
            title = f"FFID: {self.ffid[self.currentIndex]}  |  Source at {self.source_position[self.currentIndex]} m"
            self.plotWidget.getPlotItem().setTitle(title, size='12pt', color=self.col)

    def getWiggleInfo(self, i, trace):

        # Ensure trace.data is a NumPy array of floats
        trace_data = np.array(trace.data, dtype=float)

        if self.normalize:
            if np.all(trace_data == 0):
                normalized_trace_data = trace_data
            else:
                # Normalize to max value of 1 and scale by mean_dg/2
                normalized_trace_data = (trace_data / np.max(np.abs(trace_data))) * (self.mean_dg/2) * self.gain
        else: 
            normalized_trace_data = trace_data * self.gain

        # Clip the trace data
        if self.clip:
            normalized_trace_data = np.clip(normalized_trace_data, -(self.mean_dg/2), (self.mean_dg/2))

        # Access the appropriate attribute based on self.plotTypeX (shot_trace_number, file_trace_number, trace_position)
        plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

        # Ensure offset is a float
        offset = float(plot_data_x[self.currentIndex][i])

        # Add the offset to the normalized trace data
        x = normalized_trace_data + offset

        # Get the fill level and put in a NumPy array of floats (in order to make the curve filling work)
        fillLevel = np.array(offset)

        # Create a mask for positive or negative amplitudes
        if self.fill == 'positive':
            mask = x >= fillLevel
        elif self.fill == 'negative':
            mask = x <= fillLevel
        else:
            mask = None

        # Interpolate points to ensure smooth transition
        x_interpolated = []
        t_interpolated = []
        for j in range(len(x) - 1):
            x_interpolated.append(x[j])
            t_interpolated.append(self.time[self.currentIndex][j])
            if mask is not None and mask[j] != mask[j + 1]:
                # Linear interpolation
                t_interp = self.time[self.currentIndex][j] + (self.time[self.currentIndex][j + 1] - self.time[self.currentIndex][j]) * (fillLevel - x[j]) / (x[j + 1] - x[j])
                x_interpolated.append(fillLevel)
                t_interpolated.append(t_interp)

        x_interpolated.append(x[-1])
        t_interpolated.append(self.time[self.currentIndex][-1])

        x_interpolated = np.array(x_interpolated)
        t_interpolated = np.array(t_interpolated)

        # Create arrays for the positive parts
        if self.fill == 'positive':
            x_filled = np.where(x_interpolated >= fillLevel, x_interpolated, fillLevel)
        elif self.fill == 'negative':
            x_filled = np.where(x_interpolated <= fillLevel, x_interpolated, fillLevel)
        else:
            x_filled = x_interpolated

        return x, x_filled, t_interpolated, fillLevel, mask

    #######################################
    # Main plotting functions
    #######################################

    def plotSeismoWiggle(self):
        # Clear previous plots
        self.plotWidget.clear()

        # Update the title
        self.updateTitle()

        # Set axis labels
        self.plotWidget.setLabel('left', self.t_label)
        self.plotWidget.setLabel('top', self.x_label)

        # Move x-axis to the top
        self.plotWidget.getAxis('bottom').setLabel('')
        self.plotWidget.getAxis('top').setLabel(self.x_label)
        self.plotWidget.showAxis('top')
        self.plotWidget.showAxis('bottom')
        self.plotWidget.showAxis('left')
        self.plotWidget.showAxis('right')

        # Display shot position and ffid in the title
        self.statusBar.showMessage(f'FFID: {self.ffid[self.currentIndex]} | Source at {self.source_position[self.currentIndex]} m')

        #####
        # Plotting could be optimized to only plot time samples, 
        # or positive negative parts instead of replotting the whole thing (as it is done for airwave)
        #####
        
        for i, trace in enumerate(self.streams[self.currentIndex]):
            
            # Get the wiggle info
            x, x_filled, t_interpolated, fillLevel, mask = self.getWiggleInfo(i, trace)

            # Plot the original curve
            if self.show_time_samples:
                self.plotWidget.plot(x, self.time[self.currentIndex], pen=self.col,
                                                 symbol='o', symbolBrush=self.col, symbolPen=self.col, symbolSize=2)
            else:
                self.plotWidget.plot(x, self.time[self.currentIndex], pen=self.col)

            # Plot the positive/negative part of the curve with fill
            if mask is not None:
                self.plotWidget.plot(x_filled, t_interpolated, pen=None, 
                                    fillLevel=fillLevel, fillBrush=self.fill_brush)

            # Plot the picks
            if not np.isnan(self.picks[self.currentIndex][i]):
                self.updatePickPosition(i)
                scatter = self.pickSeismoItems[self.currentIndex][i]
                self.plotWidget.addItem(scatter)

        if self.show_air_wave:
            self.plotAirWave()

        if self.show_t0:
            self.showT0()
        
        self.resetSeismoView()  # Reset the plot

    def plotSeismoImage(self):

        # Clear previous plots
        self.plotWidget.clear()

        # Update the title
        self.updateTitle()

        # Set axis labels
        self.plotWidget.setLabel('left', self.t_label)
        self.plotWidget.setLabel('top', self.x_label)

        # Show axes
        self.plotWidget.showAxis('top')
        self.plotWidget.showAxis('bottom')
        self.plotWidget.showAxis('left')
        self.plotWidget.showAxis('right')

        # Display shot position and ffid in the title
        self.statusBar.showMessage(f'FFID: {self.ffid[self.currentIndex]} | Source at {self.source_position[self.currentIndex]} m')

        # Get data: shape (n_traces, n_samples)
        data = np.array([np.array(trace.data, dtype=float) for trace in self.streams[self.currentIndex]])

        # Normalize data
        if self.normalize:
            data = data / np.max(np.abs(data), axis=1, keepdims=True)

        # Apply gain
        data *= self.gain

        # Get x (trace positions) and y (time)
        x = np.array(self.plotTypeDict[self.plotTypeX][self.currentIndex])
        t = np.array(self.time[self.currentIndex])

        left = x[0] - self.mean_dg/2
        top = t[0] - self.sample_interval[self.currentIndex]/2
        width = x[-1] - x[0] + self.mean_dg
        height = t[-1] - t[0] + self.sample_interval[self.currentIndex]

        # Create the image item
        image_item = pqg.ImageItem()

        # PyQtGraph expects image shape (columns, rows)
        image_item.setImage(data)
        image_item.setRect(QtCore.QRectF(left, top, width, height))

        # Add image to plot
        self.plotWidget.addItem(image_item)

        # Plot the picks
        for i in range(len(self.streams[self.currentIndex])):
            if not np.isnan(self.picks[self.currentIndex][i]):
                self.updatePickPosition(i)
                scatter = self.pickSeismoItems[self.currentIndex][i]
                self.plotWidget.addItem(scatter)

        if self.show_air_wave:
            self.plotAirWave()
        if self.show_t0:
            self.showT0()

        self.resetSeismoView()

    def plotSeismo(self):
        if self.seismoType == 'wiggle':
            self.plotSeismoWiggle()
        elif self.seismoType == 'image':
            self.plotSeismoImage()

    def plotBottom(self):
        # Plot the bottom plot based on the current bottom plot type

        if self.bottomPlotType == 'traveltime':
            self.plotTravelTime()
        elif self.bottomPlotType == 'setup':
            self.plotSetup()
        elif self.bottomPlotType == 'topo':
            self.plotTopo()

        # Reset the update_pick_flag flag
        self.update_pick_flag = False
        # Reset the update_file_flag flag
        self.update_file_flag = False

    def getAllPositions(self):
        # Get all positions

        # Flatten the traces and repeat sources
        x_all = []
        y_all = []
        pick_all = []
        
        for i, _ in enumerate(self.source_position):
            traces = self.plotTypeDict[self.plotTypeX][i]  # List of traces for the current source
            m = len(traces)  # Number of traces for the current source
            x_all.extend(traces)  # Add traces to x_values
            plot_y = self.plotTypeDict[self.plotTypeY] # List of sources for the current trace

            if self.plotTypeY == 'offset':
                y_all.extend(plot_y[i])
            else:
                y_all.extend([plot_y[i]] * m)
            pick_all.extend(self.picks[i])  # Add picks to pick_all

        return x_all, y_all, pick_all

    def getAllPicks(self, x_all, y_all, pick_all):
        # Get all picks

        # If there are picks that are not nan, plot them with colors      
        x_pick = [x_all[i] for i in range(len(x_all)) if not np.isnan(pick_all[i])]
        y_pick = [y_all[i] for i in range(len(y_all)) if not np.isnan(pick_all[i])]
        pick_all = [pick_all[i] for i in range(len(pick_all)) if not np.isnan(pick_all[i])]

        return x_pick, y_pick, pick_all
    
    def getMinMaxPicks(self):
        # Get the min and max picks
        pick_all = []
        for i, _ in enumerate(self.source_position):
            pick_all.extend(self.picks[i])
        if np.isnan(pick_all).all():
            return 0, 0
        return min(pick_all), max(pick_all)

    def plotSetup(self):

        # Remove legend if it exists
        self.removeLegend()

        if self.update_file_flag or self.update_pick_flag:
            # Clear previous plots
            self.bottomPlotWidget.clear()

            x_all, y_all, pick_all = self.getAllPositions()

            scatter = pqg.ScatterPlotItem(x=x_all, y=y_all, symbol='o',
                                        brush=self.fill_brush, size=5) 
            self.bottomPlotWidget.addItem(scatter)

            x_pick, y_pick, pick_all = self.getAllPicks(x_all, y_all, pick_all)

            # If there are more than one pick, plot them with colors
            if len(x_pick) > 1:

                # Remove colorbar if it exists
                if self.update_pick_flag:
                    self.removeColorBar()

                # Create a colormap
                self.createPicksColorMap()

                # Create ScatterPlotItem with colors
                scatter = pqg.ScatterPlotItem(x=x_pick, y=y_pick, symbol='s', 
                                            brush=self.colors, pen=self.colors, size=8)
                self.bottomPlotWidget.addItem(scatter)

                # Add colorbar
                if self.update_pick_flag:
                    self.colorbar = pqg.ColorBarItem(colorMap=self.colormap, values=(min(pick_all), max(pick_all)),
                                                label='Picked Time (s)',interactive=False)
                    self.bottomPlotWidget.plotItem.layout.setColumnFixedWidth(4, 5) # enforce some space to axis on the left
                    self.bottomPlotWidget.plotItem.layout.addItem(self.colorbar,2,5)

            # Add horizontal lines around the current source position
            if self.source_position:
                current_source = self.plotTypeDict[self.plotTypeY][self.currentIndex]
                first_trace = self.plotTypeDict[self.plotTypeX][self.currentIndex][0]
                last_trace = self.plotTypeDict[self.plotTypeX][self.currentIndex][-1]

                if len(self.source_position) > 1:
                    if self.plotTypeY == 'offset':
                        first_y = current_source[0]
                        last_y = current_source[-1]
                        mean_dy = np.mean(np.abs(np.diff(self.plotTypeDict[self.plotTypeY][self.currentIndex])))
                        x_line = [first_trace, last_trace]
                    else:
                        first_y = current_source
                        last_y = current_source
                        mean_dy = self.mean_ds
                        x_line = [first_trace - self.mean_dg, last_trace + self.mean_dg]

                    y_line_1 = [first_y - mean_dy, last_y - mean_dy]
                    y_line_2 = [first_y + mean_dy, last_y + mean_dy]

                    line1 = pqg.PlotDataItem(x_line, y_line_1, pen=self.col)
                    line2 = pqg.PlotDataItem(x_line, y_line_2, pen=self.col)
                    self.bottomPlotWidget.addItem(line1)
                    self.bottomPlotWidget.addItem(line2)

            # Set axis labels
            self.bottomPlotWidget.setLabel('left', self.y_label)
            self.bottomPlotWidget.setLabel('top', self.x_label)
            self.bottomPlotWidget.showAxis('top')
            self.bottomPlotWidget.showAxis('bottom')
            self.bottomPlotWidget.showAxis('left')
            self.bottomPlotWidget.showAxis('right')

            # Reset the view
            self.resetSetupView()

    def plotTravelTime(self):

        # Clear previous plots
        self.bottomPlotWidget.clear()

        # Remove legend if it exists
        self.removeLegend()

        # Remove colorbar if it exists
        self.removeColorBar()

        # Loop over the sources
        for i, _ in enumerate(self.source_position):
            # Check if the list of picks is not None or full of nans
            if self.picks[i] is not None and not np.isnan(self.picks[i]).all():
                
                # Plot trace position vs travel time with points and lines
                if i == self.currentIndex:
                    pen = pqg.mkPen('b', width=2)
                    # Plot the trace position vs travel time with different color
                    plot_item = pqg.PlotDataItem(x=self.plotTypeDict[self.plotTypeX][i], y=self.picks[i], 
                                                 symbol='+', pen=pen, symbolBrush='r', symbolPen='r', symbolSize=8)
                else:
                    # Plot the trace position vs travel time with default color
                    plot_item = pqg.PlotDataItem(x=self.plotTypeDict[self.plotTypeX][i], y=self.picks[i], 
                                                 symbol='o', pen=self.col, symbolBrush=self.col, 
                                                 symbolPen=self.col, symbolSize=2)
                self.bottomPlotWidget.addItem(plot_item)

        # Set axis labels
        self.bottomPlotWidget.setLabel('left', self.t_label)
        self.bottomPlotWidget.setLabel('top', self.x_label)
        self.bottomPlotWidget.showAxis('top')
        self.bottomPlotWidget.showAxis('bottom')
        self.bottomPlotWidget.showAxis('left')
        self.bottomPlotWidget.showAxis('right')

        # Reset the view
        self.resetTravelTimeView()

    def plotTopo(self):

        # Remove colorbar if it exists
        self.removeColorBar()
        
        if self.update_file_flag:
            # Clear previous plots
            self.bottomPlotWidget.clear()

            # Get unique positions
            _,unique_positions,unique_traces,unique_sources = self.getUniquePositions()
            
            # Plot the topography
            self.bottomPlotWidget.plot(unique_positions[:,0], unique_positions[:,1], pen=self.col)

            # Plot the traces
            trace_plot = self.bottomPlotWidget.plot(unique_traces[:,0], unique_traces[:,1], pen=None, 
                                                    symbol='t', symbolBrush='w', symbolPen=self.col, symbolSize=5)

            # Plot the sources
            source_plot = self.bottomPlotWidget.plot(unique_sources[:,0], unique_sources[:,1], pen=None, 
                                                    symbol='star', symbolBrush='w', symbolPen=self.col, symbolSize=7)

            # Plot current traces position
            self.bottomPlotWidget.plot(self.trace_position[self.currentIndex], self.trace_elevation[self.currentIndex], pen=None, 
                                    symbol='t', symbolBrush='b', symbolPen='b', symbolSize=8)

            # Plot current source position       
            self.bottomPlotWidget.plot([self.source_position[self.currentIndex]], [self.source_elevation[self.currentIndex]], pen=None, 
                                    symbol='star', symbolBrush='r', symbolPen='r', symbolSize=16)

            # Set axis labels
            self.bottomPlotWidget.setLabel('left', 'Elevation (m)')
            self.bottomPlotWidget.setLabel('top', 'Position (m)')
            self.bottomPlotWidget.showAxis('top')
            self.bottomPlotWidget.showAxis('bottom')
            self.bottomPlotWidget.showAxis('left')
            self.bottomPlotWidget.showAxis('right')

            # Add legend
            if self.legend is None:
                self.legend = pqg.LegendItem((100,60), offset=(10,10))
                self.legend.setParentItem(self.bottomPlotWidget.getViewBox())
                self.legend.addItem(trace_plot, 'Traces')
                self.legend.addItem(source_plot, 'Sources')

            # Reset the view
            self.resetTopoView()

    #######################################
    # Topo functions
    #######################################

    def importTopo(self):
        # Import a topography file

        # The first argument returned is the filename and path
        fname, _ = QFileDialog.getOpenFileName(
            self, 'Open file', filter='Topography files (*.xyz *.csv *.txt)')

        if fname != "":
            # Set import parameters
            self.setTopoParameters()

            try:
                # Load the file
                data = np.loadtxt(fname, delimiter=self.delimiter, 
                                  skiprows=self.skiprows, usecols=self.usecols)
                self.input_position = data[:, self.column_x]
                self.input_elevation = np.round(data[:, self.column_z], self.rounding)
                self.updateTopography()
                QMessageBox.information(self, "Topography Loaded", f"Topography loaded from: {fname}")
                self.setPlotTopo()

            except Exception as e:
                QMessageBox.critical(self, "Topography Load Error", f"Error loading topography:\n{e}")

    def updateTopography(self):
        # Interpolate the topography at the station positions
        # Create an interpolation function
        f = interp1d(self.input_position,self.input_elevation, fill_value="extrapolate", kind='linear')

        # Update the trace and source
        for i, (trace, elevation) in enumerate(zip(self.trace_position, self.trace_elevation)):
            if trace is not None:
                for j, (x, y) in enumerate(zip(trace, elevation)): 
                    self.trace_position[i][j] = x
                    self.trace_elevation[i][j] = float(np.round(f(x),self.rounding))

        for i, (source, elevation) in enumerate(zip(self.source_position, self.source_elevation)):
            if source is not None:
                self.source_elevation[i] = float(np.round(f(source),self.rounding))

    def resetTopo(self):
        # Reset the topography to the 0
        self.input_position = np.array([0, 1])
        self.input_elevation = np.array([0, 0])
        self.updateTopography()
        self.setPlotTopo()

    #######################################
    # Pick functions
    #######################################

    def bottomPlotClick(self, event):
        # Exit early if no streams are loaded
        if not self.streams:
            return
        
        if self.bottomPlotType == 'traveltime':
            self.travelTimeClick(event)
        elif self.bottomPlotType == 'setup':
            self.setupClick(event)
        elif self.bottomPlotType == 'topo':
            self.topoClick(event)

        # Set flag to update file display
        self.update_file_flag = True

        # Batch the updates to improve performance
        self.plotSeismo()
        self.updateFileListDisplay()
        self.plotBottom()

    def setupClick(self, event):

        if event.button() == QtCore.Qt.LeftButton:
            # Convert the scene position to view coordinates
            mousePoint = self.bottomPlotWidget.plotItem.vb.mapSceneToView(event.scenePos())
            x = mousePoint.x()
            y = mousePoint.y()
            
            # Get the plot data based on current plot types
            plot_data_y = self.plotTypeDict.get(self.plotTypeY)
            
            # Special handling for offset plot type
            if self.plotTypeY == 'offset':
                # Use vectorized operations instead of creating intermediate arrays
                y_values = np.array(self.source_position)
                # Find the closest source position to the adjusted y-coordinate
                distances = np.abs(y_values - (x - y))
                self.currentIndex = np.argmin(distances)
            else:
                # For non-offset plot types, directly find the closest source
                y_values = np.array(plot_data_y)
                distances = np.abs(y_values - y)
                self.currentIndex = np.argmin(distances)

    def travelTimeClick(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Convert the scene position to view coordinates
            mousePoint = self.bottomPlotWidget.plotItem.vb.mapSceneToView(event.scenePos())
            x = mousePoint.x()
            y = mousePoint.y()
            
            # Get the plot data based on current plot types
            # Each is a list of lists
            plot_data_x = self.plotTypeDict[self.plotTypeX]
            plot_data_y = self.picks
            data_source = self.plotTypeDict[self.plotTypeY]

            # Repeat the source position for each trace
            source_position_repeat = [data_source[i] for i in range(len(data_source)) for _ in range(len(plot_data_x[i]))]

            # Flatten the list of lists into a single list
            flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]
            flat_plot_data_y = [item for sublist in plot_data_y for item in sublist]

            # Remove NaN values from the plot data
            flat_plot_data_x = np.array(flat_plot_data_x)[~np.isnan(flat_plot_data_y)]
            flat_data_source = np.array(source_position_repeat)[~np.isnan(flat_plot_data_y)]
            flat_plot_data_y = np.array(flat_plot_data_y)[~np.isnan(flat_plot_data_y)]

            # Find the closest point in the plot data
            distances = np.sqrt((flat_plot_data_x - x)**2 + (flat_plot_data_y - y)**2)
            index = np.argmin(distances)

            # Get the corresponding source position and update the current index
            source_position = flat_data_source[index]
            self.currentIndex = np.where(np.array(data_source) == source_position)[0][0]

    def topoClick(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Convert the scene position to view coordinates
            mousePoint = self.bottomPlotWidget.plotItem.vb.mapSceneToView(event.scenePos())
            x = mousePoint.x()
            y = mousePoint.y()

            # Find the closest source position
            distances = np.abs(np.array(self.source_position) - x)
            self.currentIndex = np.argmin(distances)

    def handleAddPick(self, event):
        """
        Called when a left mouse click occurs (add single pick).
        Adds a pick at the clicked position.
        """
        if not self.streams:
            return

        if event.button() == QtCore.Qt.LeftButton:
            mousePoint = self.plotWidget.plotItem.vb.mapSceneToView(event.scenePos())
            x = mousePoint.x()
            y = mousePoint.y()
            self._add_pick_at(x, y)
            self.update_pick_flag = True
            self.plotBottom()

    def handleFreehandPick(self, drag_path):
        """
        Called when a left mouse drag finishes (freehand pick).
        Adds picks along the drag path.
        """
        if not self.streams:
            return
        
        for pt in drag_path:
            mousePoint = self.plotWidget.plotItem.vb.mapSceneToView(pt)
            x = mousePoint.x()
            y = mousePoint.y()
            self._add_pick_at(x, y)
        self.update_pick_flag = True
        self.plotBottom()

    def handleRemovePick(self, event):
        """
        Called when a middle mouse click occurs (remove single pick).
        """
        if not self.streams:
            return

        if event.button() == QtCore.Qt.MiddleButton:
            mousePoint = self.plotWidget.plotItem.vb.mapSceneToView(event.scenePos())
            x = mousePoint.x()
            y = mousePoint.y()
            self._remove_pick_at(x, y)
            self.update_pick_flag = True
            self.plotBottom()

    def handleRectRemove(self, ev):
        """
        Called when a middle mouse drag finishes (rectangle selection).
        Removes all picks inside the rectangle.
        """
        if not self.streams:
            return
        
        vb = self.plotWidget.getViewBox()
        rb = getattr(vb, "rbScaleBox", None)
        if rb is None:
            return
        rect = rb.rect()
        if rect is None:
            return

        # Correct mapping from scene to view coordinates
        topLeft_scene = rb.mapToScene(rect.topLeft())
        bottomRight_scene = rb.mapToScene(rect.bottomRight())
        topLeft = vb.mapSceneToView(topLeft_scene)
        bottomRight = vb.mapSceneToView(bottomRight_scene)
        x_min, x_max = sorted([topLeft.x(), bottomRight.x()])
        y_min, y_max = sorted([topLeft.y(), bottomRight.y()])
        for i, (x, y) in enumerate(zip(self.plotTypeDict[self.plotTypeX][self.currentIndex], self.picks[self.currentIndex])):
            if not np.isnan(y) and x_min <= x <= x_max and y_min <= y <= y_max:
                if self.pickSeismoItems[self.currentIndex][i] is not None:
                    self.plotWidget.removeItem(self.pickSeismoItems[self.currentIndex][i])
                    self.pickSeismoItems[self.currentIndex][i] = None
                self.picks[self.currentIndex][i] = np.nan
                self.error[self.currentIndex][i] = np.nan
        self.update_pick_flag = True
        self.plotBottom()

        # Remove the selection rectangle
        if hasattr(vb, "rbScaleBox") and vb.rbScaleBox is not None:
            vb.rbScaleBox.hide()
            vb.rbScaleBox = None
            vb.update()

    def _add_pick_at(self, x, y):
        """
        Helper function to add a pick at (x, y).
        """
        plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])
        x_distance = np.array(plot_data_x[self.currentIndex]) - x
        y_distance = np.array(self.time[self.currentIndex]) - y
        index_x = np.argmin(np.abs(x_distance))
        index_y = np.argmin(np.abs(y_distance))
        x_ok = np.array(self.plotTypeDict[self.plotTypeX][self.currentIndex])[index_x]
        y_ok = np.array(self.time[self.currentIndex])[index_y]

        if self.assisted_picking:
            # Smooth the trace data
            trace_data = np.array(self.streams[self.currentIndex][index_x].data, dtype=float)
            trace_data = trace_data / np.max(np.abs(trace_data))
            smoothed_trace_data = np.convolve(trace_data, np.ones(self.smoothing_window_size)/self.smoothing_window_size, mode='same')

            # Calculate the mean and standard deviation of the data within the window around the pick
            pick_index = np.argmin(np.abs(self.time[self.currentIndex] - y))
            window_start = 0
            window_end = pick_index
            mean_window = np.mean(np.abs(smoothed_trace_data[window_start:window_end]))
            std_window = np.std(np.abs(smoothed_trace_data[window_start:window_end]))
            deviation_threshold = std_window * self.deviation_threshold

            # Look for significant deviation within the window
            for i in range(pick_index, min(pick_index + self.picking_window_size, len(smoothed_trace_data))):
                if np.abs(smoothed_trace_data[i] - mean_window) > deviation_threshold:
                    y_ok = self.time[self.currentIndex][i]
                    break

        if self.pickSeismoItems[self.currentIndex][index_x] is not None:
            self.pickSeismoItems[self.currentIndex][index_x].setData(x=[x_ok], y=[y_ok])
            self.picks[self.currentIndex][index_x] = y_ok
            self.error[self.currentIndex][index_x] = self.pickError(y_ok)
        else:
            scatter1 = pqg.ScatterPlotItem(x=[x_ok], y=[y_ok], pen='r', symbol='+')
            self.plotWidget.addItem(scatter1)
            self.pickSeismoItems[self.currentIndex][index_x] = scatter1
            self.picks[self.currentIndex][index_x] = y_ok
            self.error[self.currentIndex][index_x] = self.pickError(y_ok)

    def _remove_pick_at(self, x, y):
        """
        Helper function to remove a pick at (x, y).
        """
        plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])
        x_distance = np.array(plot_data_x[self.currentIndex]) - x
        y_distance = np.array(self.time[self.currentIndex]) - y
        index_x = np.argmin(np.abs(x_distance))
        index_y = np.argmin(np.abs(y_distance))
        if self.pickSeismoItems[self.currentIndex][index_x] is not None:
            self.plotWidget.removeItem(self.pickSeismoItems[self.currentIndex][index_x])
            self.pickSeismoItems[self.currentIndex][index_x] = None
            self.picks[self.currentIndex][index_x] = np.nan
            self.error[self.currentIndex][index_x] = np.nan

    # def handleAddPick(self, event):

    #     if not self.streams:
    #         return
        
    #     if event.button() == QtCore.Qt.LeftButton or event.button() == QtCore.Qt.MiddleButton:
    #         mousePoint = self.plotWidget.plotItem.vb.mapSceneToView(event.scenePos())
    #         x = mousePoint.x()
    #         y = mousePoint.y()
            
    #         # Get the current axis ranges
    #         x_range = self.plotWidget.plotItem.vb.viewRange()[0]
    #         y_range = self.plotWidget.plotItem.vb.viewRange()[1]

    #         # Access the appropriate attribute based on self.plotTypeX (shot_trace_number, file_trace_number, trace_position)
    #         plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

    #         # Check if the clicked position is within the axis bounds
    #         if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]:
    #             # Calculate the distance between the clicked point and the trace
    #             x_distance = np.array(plot_data_x[self.currentIndex]) - x
    #             y_distance = np.array(self.time[self.currentIndex]) - y

    #             # Get index of the closest trace
    #             index_x = np.argmin(np.abs(x_distance))
    #             index_y = np.argmin(np.abs(y_distance))

    #             # Get the x and y values of the closest trace
    #             x_ok = np.array(self.plotTypeDict[self.plotTypeX][self.currentIndex])[index_x]
    #             y_ok = np.array(self.time[self.currentIndex])[index_y]

    #             if self.assisted_picking:

    #                 # Smooth the trace data
    #                 trace_data = np.array(self.streams[self.currentIndex][index_x].data)
    #                 trace_data = trace_data / np.max(np.abs(trace_data))
    #                 smoothed_trace_data = np.convolve(trace_data, np.ones(self.smoothing_window_size)/self.smoothing_window_size, mode='same')

    #                 # Calculate the mean and standard deviation of the data within the window around the pick
    #                 pick_index = np.argmin(np.abs(self.time[self.currentIndex] - y))
    #                 window_start = 0
    #                 window_end = pick_index
    #                 mean_window = np.mean(np.abs(smoothed_trace_data[window_start:window_end]))
    #                 std_window = np.std(np.abs(smoothed_trace_data[window_start:window_end]))
    #                 deviation_threshold = std_window * self.deviation_threshold

    #                 # Look for significant deviation within the window
    #                 for i in range(pick_index, pick_index+self.picking_window_size):
    #                     if np.abs(smoothed_trace_data[i] - mean_window) > deviation_threshold:
    #                         # plt.close()  # Clear the current figure
    #                         # plt.plot(smoothed_trace_data[window_start:window_end+self.picking_window_size] - mean_window)
    #                         # plt.plot(i, np.abs(smoothed_trace_data[i]) - mean_window, 'ro')
    #                         # plt.plot([window_start, window_end+self.picking_window_size], [mean_window, mean_window], 'g')
    #                         # plt.plot([window_start, window_end+self.picking_window_size], [mean_window+deviation_threshold, mean_window+deviation_threshold], 'r')
    #                         # plt.plot([window_start, window_end+self.picking_window_size], [mean_window-deviation_threshold, mean_window-deviation_threshold], 'r')
    #                         # plt.show()
    #                         y_ok = self.time[self.currentIndex][i]
    #                         break

    #             # Set the text of the QLabel to the clicked position
    #             self.label.setText(f"Clicked position: x = {x_ok}, y = {y_ok}")

    #             # If there's already a scatter plot item for this trace, update its position
    #             if self.pickSeismoItems[self.currentIndex][index_x] is not None:
    #                 if event.button() == QtCore.Qt.LeftButton:
    #                     self.pickSeismoItems[self.currentIndex][index_x].setData(x=[x_ok], y=[y_ok])
                        
    #                     self.picks[self.currentIndex][index_x] = y_ok # Update the pick
    #                     self.error[self.currentIndex][index_x] = self.pickError(y_ok) # Update the error
                        
    #                 else:
    #                     self.plotWidget.removeItem(self.pickSeismoItems[self.currentIndex][index_x])
    #                     self.pickSeismoItems[self.currentIndex][index_x] = None

    #                     self.picks[self.currentIndex][index_x] = np.nan # Remove the pick
    #                     self.error[self.currentIndex][index_x] = np.nan # Remove the error
    #             else:
    #                 if event.button() == QtCore.Qt.LeftButton:
    #                     # Otherwise, create a new scatter plot item and add it to the plot widget and the dictionary
    #                     scatter1 = pqg.ScatterPlotItem(x=[x_ok], y=[y_ok], pen='r', symbol='+')
    #                     self.plotWidget.addItem(scatter1)
    #                     self.pickSeismoItems[self.currentIndex][index_x] = scatter1

    #                     self.picks[self.currentIndex][index_x] = y_ok # Add the pick
    #                     self.error[self.currentIndex][index_x] = self.pickError(y_ok) # Add the error

    #             x_all, y_all, pick_all = self.getAllPositions()
    #             x_pick, _, _ = self.getAllPicks(x_all, y_all, pick_all)

    #             # Update the color map if there are picks that are not nan in all files
    #             if len(x_pick) > 1:
    #                 self.createPicksColorMap()

    #             self.update_pick_flag = True

    #             self.plotBottom() # Update the setup plot
    
    def pickError(self, pick):
        
        error = pick * self.relativeError + self.absoluteError
        if self.maxAbsoluteError is not None:
            if error > self.maxAbsoluteError:
                error = self.maxAbsoluteError
        if self.minAbsoluteError is not None:
            if error < self.minAbsoluteError:
                error = self.minAbsoluteError
        if self.maxRelativeError is not None:
            if error > self.maxRelativeError * pick:
                error = self.maxRelativeError * pick

        return error
    
    def setAllPickError(self):
        # Set self.error to the error calculated from the picks
        for i, _ in enumerate(self.picks):
            for j, pick in enumerate(self.picks[i]):
                if not np.isnan(pick):
                    self.error[i][j] = self.pickError(pick)

    def createPicksColorMap(self):
        # Create a colormap
        self.colormap = pqg.colormap.get(self.colormap_str, source='matplotlib')

        # Get the values of the picks that are not nan in a list of list
        values = [value for sublist in self.picks for value in sublist if not np.isnan(value)]

        # Normalize the values to the range [0, 1]
        min_val = min(values)
        max_val = max(values)
        if min_val == max_val:
            min_val = min_val - 1
            max_val = max_val + 1
        normalized_values = [(val - min_val) / (max_val - min_val) for val in values]

        # Map values to colors
        self.colors = self.colormap.map(normalized_values, mode='qcolor')

    def savePicksAsNewFile(self):
        # Save the picks to a new file

        # The first argument returned is the filename and path
        fname, _ = QFileDialog.getSaveFileName(
            self, 'Save to file', filter='Source-Geophone-Time file (*.sgt)')
        
        if fname != "":
            # Check if fname has the right extension
            if not fname.endswith('.sgt'):
                fname += '.sgt'

            self.pick_file = fname
            self.savePicks()

    def savePicksInPreviousFile(self):
        # Save the picks in the previous file

        if self.pick_file != "":
            self.savePicks()
        else:
            self.savePicksAsNewFile()

    def savePicks(self, output_file=None):
        """
        Save the picks to a pygimli .sgt file
        
        Parameters:
        -----------
        output_file : str, optional
            File path to save picks to. If None, uses self.pick_file
        """
        # Use provided output_file or self.pick_file
        file_to_use = output_file if output_file is not None else self.pick_file
    
        if not file_to_use:
            QMessageBox.warning(self, "No Output File", "No output file specified for saving picks.")
            return

        # Get unique traces from list of list of traces array that are not None
        trace_pairs = []
        for sublist_position, sublist_elevation in zip(self.trace_position, self.trace_elevation):
            if sublist_position is not None:
                for trace, elevation in zip(sublist_position, sublist_elevation):
                    trace_pairs.append((trace, elevation))

        # Get unique sources from list of sources array
        source_pairs = [(source, elevation) for source, elevation in zip(self.source_position, self.source_elevation) if source is not None]

        # Convert trace_pairs and source_pairs to numpy structured arrays
        trace_pairs = np.array(trace_pairs, dtype=[('position', float), ('elevation', float)])
        source_pairs = np.array(source_pairs, dtype=[('position', float), ('elevation', float)])

        # Concatenate trace_pairs and source_pairs
        all_pairs = np.concatenate((trace_pairs, source_pairs))

        # Get unique stations from all_pairs
        stations = np.unique(all_pairs)

        # Get trace indices in station list
        trace_indices = [np.where((stations['position'] == trace_pair['position']) & (stations['elevation'] == trace_pair['elevation']))[0][0] for trace_pair in trace_pairs]

        # Get source indices in station list
        source_indices = [np.where((stations['position'] == source_pair['position']) & (stations['elevation'] == source_pair['elevation']))[0][0] for source_pair in source_pairs]

        # Number of non-NaN picks in the list of picks where list of picks is not None
        picks = [pick for sublist in self.picks if sublist is not None for pick in sublist]
        n_picks = np.sum(~np.isnan(picks))

        # Write file with the following format:
        # Number of stations
        # x, y, z coordinates of stations
        # Number of picks
        # Source index, trace index, pick time, pick error

        ### TODO
        # Remove unused stations (or not)

        if n_picks == 0:
            QMessageBox.information(self, "No Picks", "No picks to save!")
            return
        
        if file_to_use != "":
            with open(file_to_use, 'w') as f:
                # Write number of stations
                f.write(f"{len(stations)} # shot/geophone points\n")
                f.write("# x\ty\n")
                for station in stations:
                    x = station[0]
                    y = station[1]
                    f.write(f"{x}\t{y}\n")
                # Write number of picks
                f.write(f"{n_picks} # measurements\n")
                f.write("# s\tg\tt\terr\n")

                for i, pick_list in enumerate(self.picks):
                    if pick_list is not None:
                        for j, pick in enumerate(pick_list):
                            if not np.isnan(pick):
                                # Write source index, trace index, pick time, pick error
                                # format for time is in seconds with 5 decimal places
                                error = self.error[i][j]
                                f.write(f"{source_indices[i] + 1}\t{trace_indices[j] + 1}\t{pick:.5f}\t{error:.5f}\n")

            QMessageBox.information(self, "Picks Saved", f"Picking saved at: {file_to_use}.")
        else:
            QMessageBox.warning(self, "No File Saved", "No file was saved!")

    def loadPicks(self, fname=None, verbose=False):
        # Load picks from a pygimli .sgt file

        # The first argument returned is the filename and path
        if fname is None or not fname:
            fname, _ = QFileDialog.getOpenFileName(
                self, 'Open file', filter='Source-Geophone-Time file (*.sgt)')
        
        if fname != "":
            with open(fname, 'r') as f:
                # Read number of stations
                n_stations = int(f.readline().split('#')[0].strip())
                if verbose:
                    print(f"Number of stations: {n_stations}")

                # Read line and check if it is a comment
                flag_comment = True
                while flag_comment:
                    line = f.readline().strip()
                    
                    if '#' in line[0]:
                        if verbose:
                            print(f"Comment: {line}")
                        flag_comment = True
                    else:
                        flag_comment = False

                # Read x, y coordinates of stations
                uploaded_stations = []
                for i in range(n_stations):
                    if i>0:
                        line = f.readline().strip()

                    if verbose:
                        if i < 5 or i > n_stations - 5:
                            print(f"Reading station line: {line}")
                
                    if line:  # Check if the line is not empty
                        parts = line.split()
                        if len(parts) == 2:  # Ensure there are exactly two values
                            x, y = map(float, parts)
                            uploaded_stations.append((x, y))
                        elif len(parts) == 3:  # Ensure there are exactly three values
                            x, y, z = map(float, parts)
                            uploaded_stations.append((x, y, z))
                            
                # Read number of picks
                n_picks = int(f.readline().split('#')[0].strip())
                if verbose:
                    print(f"Number of picks: {n_picks}")

                # Read line and check if it is a comment
                flag_comment = True
                while flag_comment:
                    line = f.readline().strip()
                    
                    if '#' in line[0]:
                        if verbose:
                            print(f"Comment: {line}")
                        flag_comment = True
                        # Find order of s, g, t and err in comment line
                        if 's' in line:
                            s_ind = line.split().index('s') - 1
                        if 'g' in line:
                            g_ind = line.split().index('g') - 1
                        if 't' in line:
                            t_ind = line.split().index('t') - 1
                        if 'err' in line:
                            err_ind = line.split().index('err') - 1
                    else:
                        flag_comment = False

                # Read source index, trace index, pick time, pick error
                uploaded_picks = []
                for i in range(n_picks):
                    if i>0:
                        line = f.readline().strip()

                    if verbose:
                        if i < 5 or i > n_picks - 5:
                            print(f"Reading pick line: {line}")

                    if line:  # Check if the line is not empty
                        parts = line.split()
                        #### TODO 
                        # handle more or less values than 4
                        if len(parts) == 4:  # Ensure there are exactly four values (could be more or less)
                            # use the indices to get the values
                            source = int(parts[s_ind])
                            trace = int(parts[g_ind])
                            pick = float(parts[t_ind])
                            error = float(parts[err_ind])
                            uploaded_picks.append((source, trace, pick, error))

                self.statusBar.showMessage(f'Picking loaded from: {fname}.', 10000)    

            if self.currentFileName is not None:
                # Get current file index
                n_picks_total = 0
                n_sources_total = 0
                max_picked_time = 0

                # Create and configure the progress dialog
                progress = QProgressDialog("Loading picks...", "Cancel", 0, len(self.fileNames), self)
                progress.setWindowTitle("Loading Picks")
                progress.setMinimumDuration(0)  # Show immediately
                progress.setWindowModality(QtCore.Qt.WindowModal)
                progress.setValue(0)
                progress.show()
                QApplication.processEvents()  # Ensure the dialog is displayed

                # Loop over files in self.fileNames
                for i, _ in enumerate(self.fileNames):
                    # Update the progress dialog
                    progress.setValue(i)
                    QApplication.processEvents()  # Process events to keep the UI responsive

                    # Get the current source
                    source = self.source_position[i]

                    # Loop over uploaded picks
                    if source is not None:

                        # Find the source index in the uploaded stations
                        try:
                            source_index = np.where(np.array(uploaded_stations) == source)[0][0]
                        except IndexError:
                            QMessageBox.warning(self, "Source Not Found", f"Source {source} not found in uploaded stations.")
                            # Handle the case where the source is not found
                            source_index = None  # or any other appropriate action

                        # Find the corresponding picks for the current source
                        up_picks_tmp = [pick for pick in uploaded_picks if pick[0] == source_index + 1]
                
                        # Unpack the picks to get the trace indices, picks and errors
                        trace_indices = [int(pick[1]) - 1 for pick in up_picks_tmp]
                        picks = [pick[2] for pick in up_picks_tmp]
                        errors = [pick[3] for pick in up_picks_tmp]

                        if picks:
                            print(f"{len(picks)} picks loaded for source at {source} m")
                            n_picks_total += len(picks)
                            n_sources_total += 1

                        # Update the picks list
                        if self.picks[i] is None:
                            self.picks[i] = [np.nan] * len(self.trace_position[i])

                        # Access the appropriate attribute based on self.plotTypeX (shot_trace_number, file_trace_number, trace_position)
                        plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

                        for trace_index_all, pick, error in zip(trace_indices, picks, errors):
                            # Get trace position from uploaded_stations
                            trace = uploaded_stations[trace_index_all][0]

                            # Find the trace index in the current file
                            trace_indices_source = np.where(np.array(self.trace_position[i]) == trace)[0]
                            if trace_indices_source.size == 0:
                                QMessageBox.warning(self, "Trace Not Found", f"Trace {trace} not found in trace_position for source {i}")
                                continue    

                            trace_index_source = trace_indices_source[0]

                            scatter1 = pqg.ScatterPlotItem(x=[plot_data_x[i][trace_index_source]], 
                                                          y=[pick], pen='r', symbol='+')

                            if i == self.currentIndex:
                                if ~np.isnan(self.picks[i][trace_index_source]):
                                    self.plotWidget.removeItem(self.pickSeismoItems[i][trace_index_source])
                                
                                self.plotWidget.addItem(scatter1)

                            self.pickSeismoItems[i][trace_index_source] = scatter1
                            self.picks[i][trace_index_source] = pick
                            self.error[i][trace_index_source] = error

                            if pick > max_picked_time:
                                max_picked_time = pick

                progress.setValue(len(self.fileNames))  # Set progress to maximum   

                QMessageBox.information(self, "Picks Loaded", f"{n_picks_total} picks loaded for {n_sources_total} sources")
                self.update_pick_flag = True
                self.max_time = max_picked_time * 2
                if self.max_time > max(self.time[self.currentIndex]):
                    self.max_time = max(self.time[self.currentIndex])
                self.plotSeismo()
                self.plotBottom()

        else:
            QMessageBox.warning(self, "No File Loaded", "No file loaded!")

    def clearAllPicks(self):
        # Show warning message box
        reply = QMessageBox.question(self, 'Clear all picks', 'Are you sure you want to clear all picks?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Reset all picks to nan
            for i, _ in enumerate(self.picks):
                if self.picks[i] is not None:
                    for j, _ in enumerate(self.picks[i]):
                        self.picks[i][j] = np.nan
                        self.error[i][j] = np.nan
                        if self.pickSeismoItems[i][j] is not None:
                            self.plotWidget.removeItem(self.pickSeismoItems[i][j])
                            self.pickSeismoItems[i][j] = None
            self.update_pick_flag = True
            self.removeColorBar()
            self.plotBottom()
        else:
            self.statusBar.showMessage('Keeping picks safe', 2000)

    def clearCurrentPicks(self):
        # Show warning message box
        reply = QMessageBox.question(self, 'Clear current picks', 'Are you sure you want to clear the picks for the current shot?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Reset picks to nan for the current file
            if self.fileNames:
                if self.picks[self.currentIndex] is not None:
                    for i, _ in enumerate(self.picks[self.currentIndex]):
                        self.picks[self.currentIndex][i] = np.nan
                        self.error[self.currentIndex][i] = np.nan
                        if self.pickSeismoItems[self.currentIndex][i] is not None:
                            self.plotWidget.removeItem(self.pickSeismoItems[self.currentIndex][i])
                            self.pickSeismoItems[self.currentIndex][i] = None
                self.update_pick_flag = True
                self.plotBottom()
        else:
            self.statusBar.showMessage('Keeping picks safe', 2000)

    #####################################
    # Inversion functions
    #####################################

    def runInversionModule(self):
        """Run seismic traveltime inversion module with the current picks"""

        try:
            import pygimli
        except ImportError:
            QMessageBox.warning(self, "Warning", "pygimli is not installed. Please install it first to run the inversion module.")
            return
        
        # Check if the picks are not empty
        picks = [pick for sublist in self.picks if sublist is not None for pick in sublist]
        n_picks = np.sum(~np.isnan(picks))
        if n_picks == 0:
            QMessageBox.information(self, "No Picks", "No picks to run the inversion.")
            return

        inversion_data = {
            'picks': self.picks,
            'error': self.error,
            'source_position': self.source_position,
            'trace_position': self.trace_position,
            'trace_elevation': self.trace_elevation,
            'source_elevation': self.source_elevation
            # Add any other data the inversion app might need here
        }
        
        # Run the inversion module
        try:
            from . import inversion_app
        except ImportError:
            import inversion_app

        try:
            inversion_app.launch_inversion_app(inversion_data, parent_window=self)
        except Exception as e:
            QMessageBox.critical(self, "Error Launching Inversion", f"Could not start the inversion app:\n{e}")
        
    #######################################
    # Export figures functions
    #######################################

    def mplPlotSeismo(self):
        # Plot the seismogram using matplotlib

        if self.streams:
            # Create a figure and axis
            _, ax = plt.subplots(figsize=self.mpl_aspect_ratio)

            if self.mpl_show_source:
                if self.plotTypeX == 'trace_position':
                    # Display a red star at the source location on the bottom x-axis
                    ax.scatter(self.source_position[self.currentIndex], 1, 
                            color=self.mpl_source_color, marker=self.mpl_source_marker, s=self.mpl_source_marker_size, 
                            transform=ax.get_xaxis_transform(), clip_on=False, zorder=10)
                else:
                    QMessageBox.information(self, "Source Display", "Source position cannot be displayed for this plot type.")

                if self.mpl_show_title:
                    title = f"FFID: {self.ffid[self.currentIndex]}  |  Source at {self.source_position[self.currentIndex]} m"

                    # Set the title
                    plt.text(0.025, 0.05, title, fontsize=self.mpl_font_size, ha='left', va='bottom', fontstyle='italic',
                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'), transform=plt.gca().transAxes)

            if self.mpl_time_in_ms:
                t_label = 'Time (ms)'
                scale_factor = 1000
            else:
                t_label = 'Time (s)'
                scale_factor = 1
                
            for i, trace in enumerate(self.streams[self.currentIndex]):
                
                # Get the wiggle info
                x, _, _, _, mask = self.getWiggleInfo(i, trace)

                ax.plot(x, self.time[self.currentIndex]*scale_factor, color=self.mpl_line_color,linewidth=self.mpl_line_width)
                ax.fill_betweenx(self.time[self.currentIndex]*scale_factor, self.plotTypeDict[self.plotTypeX][self.currentIndex][i],
                                    x, where=mask, color=self.mpl_fill_color, alpha=self.mpl_fill_alpha, 
                                    interpolate=True, edgecolor=None)

                if self.mpl_show_picks:
                    pick = self.picks[self.currentIndex][i]
                    if not np.isnan(pick):
                        ax.plot(self.plotTypeDict[self.plotTypeX][self.currentIndex][i], pick*scale_factor, color=self.mpl_pick_color, 
                                marker=self.mpl_pick_marker_alt, markersize=self.mpl_pick_marker_size_alt)

            # Access the appropriate attribute based on self.plotTypeX
            plot_data_x = self.plotTypeDict.get(self.plotTypeX, [])

            # Flatten the list of lists into a single list
            flat_plot_data_x = [item for sublist in plot_data_x for item in sublist]

            if self.mpl_xmin is None:
                self.mpl_xmin = min(flat_plot_data_x) - self.mean_dg
            if self.mpl_xmax is None:
                self.mpl_xmax = max(flat_plot_data_x) + self.mean_dg
            if self.mpl_tmin is None:
                self.mpl_tmin = min(self.time[self.currentIndex])
            if self.mpl_tmax is None:
                self.mpl_tmax = max(self.time[self.currentIndex])
        
            # Set the limits of the x and y axes
            ax.set_xlim(self.mpl_xmin, self.mpl_xmax)
            ax.set_ylim(self.mpl_tmin*scale_factor, self.mpl_tmax*scale_factor)

            # Move the x-axis labels to the top
            if self.mpl_xaxis_position == 'top':
                ax.xaxis.tick_top()
            ax.xaxis.set_label_position(self.mpl_xaxis_position)

            # Move the y-axis labels to the right
            if self.mpl_yaxis_position == 'right':
                ax.yaxis.tick_right()
            ax.yaxis.set_label_position(self.mpl_yaxis_position)

            # Invert the y-axis
            if self.mpl_invert_yaxis:
                ax.invert_yaxis()  
        
            # Set the font size of the tick labels
            ax.tick_params(axis='both', labelsize=self.mpl_font_size)
            # Set the x-axis label and get its position
            ax.set_xlabel(self.x_label, fontsize=self.mpl_font_size)
            # Set the y-axis label and get its position
            ax.set_ylabel(t_label, fontsize=self.mpl_font_size)

    def mplPlotSetup(self):
        # Plot the setup using matplotlib

        if self.trace_position:
            # Create a figure and axis
            _, ax = plt.subplots(figsize=self.mpl_aspect_ratio)

            x_all, y_all, pick_all = self.getAllPositions()

            # Plot the traces positions
            ax.scatter(x_all, y_all, color=self.mpl_trace_marker_color, alpha=self.mpl_trace_marker_alpha,
                       s=self.mpl_trace_marker_size, marker=self.mpl_trace_marker)
            
            # Set aspect ratio to 1:1
            if self.mpl_equal_aspect:
                ax.set_aspect('equal')
            
            x_pick, y_pick, pick_all = self.getAllPicks(x_all, y_all, pick_all)
            
            # Plot the picks and add colorbar
            if not np.isnan(pick_all).all():
                if self.mpl_time_in_ms:
                    t_label = 'Picked Time (ms)'
                    scale_factor = 1000
                else:
                    t_label = 'Picked Time (s)'
                    scale_factor = 1

                if self.mpl_tmin is None:
                    mpl_tmin = np.nanmin(pick_all)
                else:
                    mpl_tmin = self.mpl_tmin
                if self.mpl_tmax is None:
                    mpl_tmax = np.nanmax(pick_all)
                else:
                    mpl_tmax = self.mpl_tmax
                
                # Get the colormap object based on the string stored in self.mpl_pick_colormap
                colormap = plt.get_cmap(self.mpl_pick_colormap)
                if self.mpl_reverse_colormap:
                    colormap = colormap.reversed()

                scatter = ax.scatter(x_pick, y_pick, c=np.array(pick_all)*scale_factor, cmap=colormap, 
                       s=self.mpl_pick_marker_size, marker=self.mpl_pick_marker,
                        vmin=mpl_tmin*scale_factor, vmax=mpl_tmax*scale_factor)

                if self.mpl_colorbar_position in ['right', 'left', 'top', 'bottom']:
                    # Set colorbar position and orientation
                    if self.mpl_colorbar_position in ['right', 'left']:
                        # Vertical orientation
                        cbar = plt.colorbar(scatter, orientation='vertical', 
                                        ax=ax, location=self.mpl_colorbar_position)
                        cbar.ax.yaxis.set_label_position(self.mpl_colorbar_position)
                        
                    elif self.mpl_colorbar_position in ['top', 'bottom']:
                        # Horizontal orientation  
                        cbar = plt.colorbar(scatter, orientation='horizontal',
                                        ax=ax, location=self.mpl_colorbar_position)
                        cbar.ax.xaxis.set_label_position(self.mpl_colorbar_position)

                    cbar.set_label(t_label, fontsize=self.mpl_font_size)
                    cbar.ax.tick_params(labelsize=self.mpl_font_size)

            # Set the limits of the x and y axes
            ax.set_xlim(self.mpl_xmin, self.mpl_xmax)
            ax.set_ylim(self.mpl_ymin, self.mpl_ymax)

            # Move the x-axis labels to the top
            if self.mpl_xaxis_position == 'top':
                ax.xaxis.tick_top()
            ax.xaxis.set_label_position(self.mpl_xaxis_position)

            # Move the y-axis labels to the right
            if self.mpl_yaxis_position == 'right':
                ax.yaxis.tick_right()
            ax.yaxis.set_label_position(self.mpl_yaxis_position)

            # Invert the y-axis
            if self.mpl_invert_yaxis:
                ax.invert_yaxis()

            # Set the font size of the tick labels
            ax.tick_params(axis='both', labelsize=self.mpl_font_size)
            # Set the x-axis label and get its position
            ax.set_xlabel(self.x_label, fontsize=self.mpl_font_size)
            # Set the y-axis label and get its position
            ax.set_ylabel(self.y_label, fontsize=self.mpl_font_size)

    def mplPlotTravelTime(self):
        # Plot the travel time using matplotlib

        if self.picks:

            # Get the picks
            x_all, y_all, pick_all = self.getAllPositions()
            x_pick, y_pick, pick_all = self.getAllPicks(x_all, y_all, pick_all)

            if self.mpl_time_in_ms:
                t_label = 'Picked Time (ms)'
                scale_factor = 1000
            else:
                t_label = 'Picked Time (s)'
                scale_factor = 1

            if self.mpl_tmin is None:
                mpl_tmin = np.nanmin(pick_all)
            else:
                mpl_tmin = self.mpl_tmin
            if self.mpl_tmax is None:
                mpl_tmax = np.nanmax(pick_all)
            else:
                mpl_tmax = self.mpl_tmax

            # Create a figure and axis
            _, ax = plt.subplots(figsize=self.mpl_aspect_ratio)

            cm_to_use = self.mpl_line_colorstyle
            if cm_to_use == 'qualitative colormap':
                cm = self.mpl_qualitative_cm
                cmap_obj = plt.get_cmap(cm)
                # Determine number of discrete colors from the ListedColormap
                if hasattr(cmap_obj, 'colors'):
                    n_disc = len(cmap_obj.colors)
                else:
                    n_disc = 256  # fallback for continuous maps
                discrete_colors = [cmap_obj(i) for i in np.linspace(0, 1, n_disc, endpoint=False)]
                colors = [discrete_colors[i % n_disc] for i in range(len(self.source_position))]

            elif cm_to_use == 'sequential colormap':
                cm = self.mpl_sequential_cm
                # Normalize source_position values between 0 and 1
                norm = plt.Normalize(vmin=min(self.source_position), vmax=max(self.source_position))
                # Get a colormap, e.g., 'plasma'
                cmap = plt.get_cmap(cm)
                # Map each source_position to an RGBA color
                colors = cmap(norm(self.source_position))

            # Plot traveltime curves for each source
            for i, _ in enumerate(self.source_position):
                if self.picks[i] is not None and not np.isnan(self.picks[i]).all():
                    
                    if cm_to_use == 'qualitative colormap' or cm_to_use == 'sequential colormap':
                        ax.plot(self.plotTypeDict[self.plotTypeX][i], np.array(self.picks[i])*scale_factor,
                                linestyle='-', linewidth=self.mpl_line_width, color=colors[i],
                                markerfacecolor=colors[i], markeredgecolor=colors[i],
                                marker=self.mpl_pick_marker_alt, markersize=self.mpl_pick_marker_size_alt)

                    else:
                        ax.plot(self.plotTypeDict[self.plotTypeX][i], np.array(self.picks[i])*scale_factor, 
                                linestyle='-', linewidth=self.mpl_line_width, color=self.mpl_line_color,
                                markerfacecolor=self.mpl_pick_color, markeredgecolor=self.mpl_pick_color,
                                marker=self.mpl_pick_marker_alt, markersize=self.mpl_pick_marker_size_alt)
            
                    if self.mpl_show_source:

                        if cm_to_use == 'qualitative colormap' or cm_to_use == 'sequential colormap':
                            # Display a red star at the source location on the bottom x-axis
                            ax.scatter(self.source_position[i], 1, 
                                    color=colors[i], marker=self.mpl_source_marker, s=self.mpl_source_marker_size, 
                                    transform=ax.get_xaxis_transform(), clip_on=False, zorder=10)
                        else:
                            # Display source location on the bottom x-axis
                            ax.scatter(self.source_position[i], 1, 
                                    color=self.mpl_source_color, marker=self.mpl_source_marker, s=self.mpl_source_marker_size, 
                                    transform=ax.get_xaxis_transform(), clip_on=False, zorder=10)

            if cm_to_use == 'qualitative colormap':               
                # Create a discrete colormap and norm that reflects the cycling
                boundaries = np.arange(0, n_disc + 1)  # boundaries for each discrete bin
                cmap_discrete = ListedColormap(discrete_colors)
                norm_discrete = BoundaryNorm(boundaries, cmap_discrete.N)

                # Create a ScalarMappable with the discrete colormap and norm
                sm = plt.cm.ScalarMappable(cmap=cmap_discrete, norm=norm_discrete)
                sm._A = []  # dummy array for ScalarMappable

                # Create colorbar with ticks centered in each bin
                tick_locs = np.arange(0.5, n_disc, 1)
                cbar = plt.colorbar(sm, ax=ax, ticks=tick_locs)
                cbar.set_ticklabels(np.arange(1, n_disc+1))
                cbar.set_label('Source Number (mod %d)' % n_disc, fontsize=self.mpl_font_size)
                cbar.ax.tick_params(labelsize=self.mpl_font_size)

            elif cm_to_use == 'sequential colormap':
                # Create a colorbar
                sm = plt.cm.ScalarMappable(cmap=cm, norm=plt.Normalize(vmin=min(self.source_position), vmax=max(self.source_position)))
                sm._A = []
                cbar = plt.colorbar(sm, ax=ax)
                cbar.set_label('Source Position (m)', fontsize=self.mpl_font_size)
                cbar.ax.tick_params(labelsize=self.mpl_font_size)

            # Show grid  
            if self.mpl_show_grid:
                ax.grid(True)

            # Set the limits of the x and y axes
            ax.set_xlim(self.mpl_xmin, self.mpl_xmax)
            ax.set_ylim(mpl_tmin*scale_factor, mpl_tmax*scale_factor)

            # Move the x-axis labels to the top
            if self.mpl_xaxis_position == 'top':
                ax.xaxis.tick_top()
            ax.xaxis.set_label_position(self.mpl_xaxis_position)

            # Move the y-axis labels to the right
            if self.mpl_yaxis_position == 'right':
                ax.yaxis.tick_right()
            ax.yaxis.set_label_position(self.mpl_yaxis_position)

            # Invert the y-axis
            if self.mpl_invert_yaxis:
                ax.invert_yaxis()
            
            # Set the font size of the tick labels
            ax.tick_params(axis='both', labelsize=self.mpl_font_size)
            # Set the x-axis label and get its position
            ax.set_xlabel(self.x_label, fontsize=self.mpl_font_size)
            # Set the y-axis label and get its position
            ax.set_ylabel(t_label, fontsize=self.mpl_font_size)

    def exportMplPlot(self, type):
        # Define supported formats
        file_filter = "PNG image (*.png);;PDF file (*.pdf);;JPEG image (*.jpg);;TIFF image (*.tiff)"
        
        # Get filename and selected format
        fname, selected_filter = QFileDialog.getSaveFileName(
            self, 'Save to file', filter=file_filter)
        
        if fname:

            if type == 'seismo':
                # Set export parameters
                self.setMplExportSeismoParameters()
                # Create figure and axis with matplotlib
                self.mplPlotSeismo()

            elif type == 'setup':
                # Set export parameters
                self.setMplExportSetupParameters()
                # Create figure and axis with matplotlib
                self.mplPlotSetup()

            elif type == 'traveltime':
                # Set export parameters
                self.setMplExportTravelTimeParameters()
                # Create figure and axis with matplotlib
                self.mplPlotTravelTime()
                

            if self.cancelDialog:
                return
            
            plt.show(block=False)

            # Extract format from filter string
            format_map = {
                "PNG image (*.png)": ("png", ".png"),
                "PDF file (*.pdf)": ("pdf", ".pdf"), 
                "JPEG image (*.jpg)": ("jpg", ".jpg"),
                "TIFF image (*.tiff)": ("tiff", ".tiff")
            }
            
            # Get format and extension from selected filter
            format_type, extension = format_map[selected_filter]
            
            # Strip any existing extension and add correct one
            base_fname = os.path.splitext(fname)[0]
            final_fname = base_fname + extension
            
            # Save the figure
            plt.savefig(final_fname, format=format_type, dpi=self.mpl_dpi, bbox_inches='tight')

            # Display message
            self.statusBar.showMessage(f'Figure saved at: {final_fname}', 10000)
    
    def exportSeismoPlot(self):
        self.exportMplPlot('seismo')

    def exportSetupPlot(self):
        self.exportMplPlot('setup')

    def exportTravelTimePlot(self):
        self.exportMplPlot('traveltime')

#######################################
# Main window
#######################################

def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()