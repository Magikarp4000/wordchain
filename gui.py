import sys

from PySide6.QtCore import Qt, QPointF, QEvent
from PySide6.QtGui import QBrush, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QMainWindow,
)


SPEED = 2


class Node(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPos(100, 100)
        brush = QBrush(Qt.red)
        self.setBrush(brush)


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()

        # scene
        self.scene = QGraphicsScene(0, 0, 600, 450)

        # view
        self.view = QGraphicsView(self.scene)
        self.view.viewport().installEventFilter(self)
        self.view.setMouseTracking(True)
        self.view.setRenderHint(QPainter.Antialiasing)

        # layout
        self.setCentralWidget(self.view)
        
        # state
        self.mouse_pos = QPointF(0, 0)
        self.nodes = []
    
    def move_all_nodes(self, dx, dy):
        for node in self.nodes:
            node.moveBy(dx, dy)
    
    def delta_mouse_pos(self, new_pos):
        return new_pos - self.mouse_pos

    def eventFilter(self, source, event: QEvent):
        if (event.type() == QEvent.MouseMove and source is self.view.viewport()):
            mouse = QMouseEvent(event)
            
            new_pos = mouse.position()
            dpos = self.delta_mouse_pos(new_pos)
            self.mouse_pos = new_pos

            if mouse.buttons() == Qt.MouseButton.LeftButton:
                self.move_all_nodes(dpos.x(), dpos.y())
                print(dpos)
        
        return QMainWindow.eventFilter(self, source, event)


if __name__ == '__main__':
    app = QApplication([])
    gui = Gui()
    gui.show()
    app.exec()
