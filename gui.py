from config import *

import random

from PySide6.QtCore import Qt, QPointF, QEvent
from PySide6.QtGui import QBrush, QMouseEvent, QKeyEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QStackedLayout,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QLineEdit,
)


class Node(QGraphicsEllipseItem):
    def __init__(self, text, x, y, w, h):
        super().__init__(x, y, w, h)
        self.setBrush(QBrush(Qt.red))
        self.setPos(x, y)
        self.label = QGraphicsTextItem(text, self)


class Gui(QWidget):
    def __init__(self):
        super().__init__()

        # scene
        self.scene = QGraphicsScene(0, 0, WIDTH, HEIGHT)

        # view
        self.view = QGraphicsView(self.scene)
        self.view.viewport().installEventFilter(self)
        self.view.setMouseTracking(True)
        self.view.setRenderHint(QPainter.Antialiasing)

        # text input
        self.textbox = QLineEdit()
        self.textbox.setFixedHeight(HEIGHT / 5)
        self.textbox.setPlaceholderText("Enter your guess: ")
        self.textbox.installEventFilter(self)

        # layout
        self.root = QVBoxLayout()
        self.root.addWidget(self.textbox)
        self.root.addWidget(self.view)
        self.setLayout(self.root)
        
        # state
        self.mouse_pos = QPointF(0, 0)
        self.nodes = []
    
    def get_random_pos(self):
        return (random.randint(0, WIDTH // 2), random.randint(0, HEIGHT // 2))

    def add_node(self, node):
        self.nodes.append(node)
        self.scene.addItem(node)

    def move_all_nodes(self, dx, dy):
        for node in self.nodes:
            node.moveBy(dx, dy)
    
    def delta_mouse_pos(self, new_pos):
        return new_pos - self.mouse_pos

    def handle_mouse_move(self, event: QMouseEvent):
        new_pos = event.position()
        dpos = self.delta_mouse_pos(new_pos)
        self.mouse_pos = new_pos

        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move_all_nodes(dpos.x(), dpos.y())
            print(dpos)
    
    def handle_key_press(self, event: QKeyEvent):
        text = self.textbox.text()
        if event.key() == Qt.Key_Return:
            self.add_node(Node(text, *self.get_random_pos(), 50, 50))
            print(self.nodes)

    def eventFilter(self, source, event: QEvent):
        if (event.type() == QEvent.MouseMove and source is self.view.viewport()):
            self.handle_mouse_move(event)
        elif (event.type() == QEvent.KeyPress):
            self.handle_key_press(event)

        return QMainWindow.eventFilter(self, source, event)


if __name__ == '__main__':
    app = QApplication([])
    gui = Gui()
    gui.show()
    app.exec()
