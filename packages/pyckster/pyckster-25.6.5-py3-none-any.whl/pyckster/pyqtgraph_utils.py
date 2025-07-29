import pyqtgraph as pqg
from PyQt5 import QtGui

#######################################
# Monkey patching the _getFillPath in PlotCurveItem to allow for filling when plotting traces vertically
# This is a temporary fix until the issue is resolved in pyqtgraph
#######################################
def _getFillPath(self):
    if self.fillPath is not None:
        return self.fillPath

    path = QtGui.QPainterPath(self.getPath())
    self.fillPath = path
    if self.opts['fillLevel'] == 'enclosed':
        return path

    baseline = self.opts['fillLevel']
    x, y = self.getData()
    lx, rx = x[[0, -1]]
    ly, ry = y[[0, -1]]

    if ry != baseline:
        path.lineTo(rx, baseline) # Last point to baseline at same y
    # path.lineTo(lx, baseline) 
    if ly != baseline:
        path.lineTo(baseline, ly) # baseline at last point y to baseline at first point y (new line)
        path.lineTo(lx, ly) # baseline at first point y to first point

    return path

pqg.PlotCurveItem._getFillPath = _getFillPath