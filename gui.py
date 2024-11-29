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


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()

        # graphics
        self.scene = QGraphicsScene(0, 0, 600, 450)

        self.node = QGraphicsEllipseItem(0, 0, 50, 50)
        self.node.setPos(100, 100)

        brush = QBrush(Qt.red)
        self.node.setBrush(brush)

        self.scene.addItem(self.node)

        self.view = QGraphicsView(self.scene)
        self.view.viewport().installEventFilter(self)
        self.view.setMouseTracking(True)
        self.view.setRenderHint(QPainter.Antialiasing)

        # layout
        self.setCentralWidget(self.view)
        
        # state
        self.mouse_pos = QPointF(0, 0)
    
    def eventFilter(self, source, event: QEvent):
        if (event.type() == QEvent.MouseMove and source is self.view.viewport()):
            mouse = QMouseEvent(event)
            
            old_pos = self.mouse_pos
            new_pos = mouse.position()
            dpos = new_pos - old_pos
            self.mouse_pos = new_pos

            if mouse.buttons() == Qt.MouseButton.LeftButton:
                self.node.moveBy(dpos.x(), dpos.y())
                print(dpos)
        
        return QMainWindow.eventFilter(self, source, event)


if __name__ == '__main__':
    app = QApplication([])
    gui = Gui()
    gui.show()
    app.exec()
