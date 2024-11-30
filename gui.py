from config import *
from backend import Agent

import random

from PySide6.QtCore import Qt, QPointF, QPoint, QEvent, QLine, QLineF
from PySide6.QtGui import QBrush, QPen, QMouseEvent, QKeyEvent, QPainter, QRgba64
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsLineItem,
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
    QGraphicsSceneMouseEvent,
)


class Node(QGraphicsEllipseItem):
    def __init__(self, text, x, y, w, h, colour=NODE_COLOUR):
        super().__init__(0, 0, w, h)
        
        # circle
        scenePos = self.mapToScene(x, y)
        self.setPos(scenePos)
        colour = QRgba64.fromRgba(*colour)
        self.setBrush(QBrush(colour))

        # label
        self.label = QGraphicsTextItem(text, self)
        offset = self.boundingRect().center() - self.label.boundingRect().center()
        self.label.setPos(offset)


class Line(QGraphicsLineItem):
    def __init__(self, end1: Node, end2: Node):
        super().__init__()

        center1 = end1.scenePos() + QPointF(NODE_SIZE / 2, NODE_SIZE / 2)
        center2 = end2.scenePos() + QPointF(NODE_SIZE / 2, NODE_SIZE / 2)
        self.setLine(QLineF(center1, center2))

        self.setZValue(-1)


class StaticText(QGraphicsTextItem):
    def __init__(self, text, x, y, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.base_pos = QPointF(x, y)
        self.setPos(self.base_pos)
        self.setDefaultTextColor(Qt.red)
        self.setZValue(1)

    def update(self, text):
        self.setPlainText(text)
        self.setPos(self.base_pos - self.boundingRect().center())
    
    def clear(self):
        self.update("")


class Gui(QWidget):

    class AutoCenterButton(QPushButton):
        def __init__(self, label: str, parent: QWidget):
            super().__init__(label, parent)
            self.clicked.connect()
        
        def toggle(self):
            self.parent.autocenterflag = not self.parent.autocenterflag

    def __init__(self, debug=False):
        super().__init__()

        # scene
        self.scene = QGraphicsScene(0, 0, WIDTH, 4 * HEIGHT / 5)

        self.display_text = StaticText("", WIDTH / 2, 4 * HEIGHT / 5 - DISPLAY_TEXT_PAD)
        self.scene.addItem(self.display_text)

        # view
        self.view = QGraphicsView(self.scene)
        self.view.viewport().installEventFilter(self)
        self.view.setMouseTracking(True)
        self.view.setRenderHint(QPainter.Antialiasing)

        # interface
        self.textbox = QLineEdit()
        self.textbox.setFixedHeight(HEIGHT / 5)
        self.textbox.setPlaceholderText("Enter your guess: ")
        self.textbox.installEventFilter(self)

        self.autocenterbtn = Gui.AutoCenterButton("Auto-center", self)

        # layout
        self.root = QVBoxLayout()
        self.root.addWidget(self.view)
        self.root.addWidget(self.textbox)
        self.setLayout(self.root)

        # state
        self.mouse_pos = QPointF(0, 0)
        self.items = {}
        self.origin = Node("", 0, 0, 0, 0)
        
        self.autocenterflag = False

        # backend
        self.backend = Agent(tolerance=0.0)
        self.backend.init_core()

        self.add_node(self.backend.start, center=True)

        # debug
        self.debug = debug
        if self.debug:
            print(f"Start word: {self.backend.start}")
            print(f"Target word: {self.backend.target}\n")
    
    def add_item(self, item, key):
        self.items[key] = item
        self.scene.addItem(item)
    
    def get_random_pos(self):
        return (random.randint(0, WIDTH // 2), random.randint(0, HEIGHT // 2))

    def calc_pos(self, word):
        raw_pos = self.backend.get_2d(word)
        norm_pos = self.backend.norm(raw_pos) * (WORLD_WIDTH, WORLD_HEIGHT)
        offset = self.origin.scenePos()
        pos = QPointF(*norm_pos) + offset
        return pos

    def calc_colour(self, word):
        sim = self.backend.get_similarity_to_target(word)
        green_val = self.backend.norm_similarity(sim)
        red_val = 1 - green_val
        colour = (int(255 * red_val), int(255 * green_val), 0, 255)
        return colour

    def _add_node(self, word, pos):
        colour = self.calc_colour(word)
        node = Node(word, pos.x(), pos.y(), NODE_SIZE, NODE_SIZE, colour)
        self.add_item(node, word)
        return node

    def add_node(self, word, center=False, coords=None):
        if coords is None:
            coords = self.calc_pos(word)
        node = self._add_node(word, coords)

        if center:
            self.center_on(node)
    
    def add_line(self, word1, word2):
        label = f'line_{word1}_{word2}'
        line = Line(self.items[word1], self.items[word2])
        self.add_item(line, label)

    def move_all_items(self, dx, dy):
        self.origin.moveBy(dx, dy)
        for item in self.items.values():
            item.moveBy(dx, dy)
    
    def center_on(self, item: QGraphicsItem):
        width, height = self.scene.sceneRect().width(), self.scene.sceneRect().height()
        offset = QPointF((width - NODE_SIZE)/ 2, (height - NODE_SIZE) / 2)
        delta = -item.scenePos() + offset

        self.move_all_items(delta.x(), delta.y())
    
    def display(self, message):
        self.display_text.update(message)

    def successful_guess(self, word, closest_word):
        self.add_node(word, self.center_flag)
        self.add_line(word, closest_word)
        self.display_text.clear()

    def guess(self, word):
        state, message = self.backend.update(word)
        if state == VALID or state == WON:
            self.successful_guess(word, message)            
            if state == WON:
                self.backend.win()
        else:
            self.display(message)
        self.textbox.clear()

    # Events
    def eventFilter(self, source, event: QEvent):
        if (event.type() == QEvent.MouseMove and source is self.view.viewport()):
            self.handle_mouse_move(event)
        elif (event.type() == QEvent.KeyPress):
            self.handle_key_press(event)
        
        # Debug
        elif (event.type() == QEvent.MouseButtonPress and source is self.view.viewport()):
            try:
                if self.debug:
                    for label in self.items:
                        if type(self.items[label]) is Line:
                            print(label, self.items[label].line())
                        else:
                            print(label, self.items[label].pos().x(), self.items[label].pos().y())
            except AttributeError:
                pass

        return QMainWindow.eventFilter(self, source, event) 
    
    def delta_mouse_pos(self, new_pos):
        return new_pos - self.mouse_pos

    def handle_mouse_move(self, event: QMouseEvent):
        new_pos = event.position()
        dpos = self.delta_mouse_pos(new_pos)
        self.mouse_pos = new_pos

        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move_all_items(dpos.x(), dpos.y())
    
    def handle_key_press(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return:
            text = self.textbox.text()
            self.guess(text)
    
    # Settings

if __name__ == '__main__':
    app = QApplication([])
    gui = Gui()
    gui.show()
    app.exec()
