from config import *
from utils import *
from backend import Agent

import random
import math

from PySide6.QtCore import Qt, QPointF, QPoint, QEvent, QLine, QLineF
from PySide6.QtGui import QBrush, QPen, QMouseEvent, QKeyEvent, QResizeEvent, QPainter, QRgba64, QPixmap, QColor
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
    QGraphicsPixmapItem,
    QSizePolicy,
)


class Node(QGraphicsEllipseItem):
    def __init__(self, text, x, y, w, h, colour=NODE_COLOUR):
        super().__init__(0, 0, w, h)
        self.edges = set()
        
        # circle
        scenePos = self.mapToScene(x, y)
        self.setPos(scenePos)
        colour = QRgba64.fromRgba(*colour)
        self.setBrush(QBrush(colour))
        self.setPen(QColor(Qt.white))

        # label
        self.label = QGraphicsTextItem(text, self)
        offset = self.boundingRect().center() - self.label.boundingRect().center()
        self.label.setPos(offset)
    
    def add_edge(self, edge):
        self.edges.add(edge)
    
    def is_connected(self, edge):
        return edge in self.edges


class Line(QGraphicsLineItem):
    def __init__(self, end1: Node, end2: Node):
        super().__init__()
        self.end1 = end1
        self.end2 = end2
        end1.add_edge(self)
        end2.add_edge(self)

        center1 = end1.scenePos() + QPointF(NODE_SIZE / 2, NODE_SIZE / 2)
        center2 = end2.scenePos() + QPointF(NODE_SIZE / 2, NODE_SIZE / 2)
        self.setPen(QColor(Qt.white))
        self.setLine(QLineF(center1, center2))

        self.setZValue(-1)
    
    def is_connected(self, node):
        return (
            node is self.end1 or
            node is self.end2 or
            self.end1.is_connected(node) or
            self.end2.is_connected(node)
        )


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
    def __init__(self, model_name='v1', debug=False, mouse_debug=False):
        super().__init__()

        # scene
        self.scene = QGraphicsScene(0, 0, WIDTH, 4 * HEIGHT / 5)

        self.display_text = StaticText("", WIDTH / 2, 4 * HEIGHT / 5 - DISPLAY_TEXT_PAD)
        self.scene.addItem(self.display_text)

        bkgrd_pixmap = QPixmap(f'{DIR_PATH}/assets/dark-blue-background.jpg')
        self.bkgrd = QGraphicsPixmapItem(bkgrd_pixmap)
        self.bkgrd.setZValue(-1000)
        self.bkgrd.setScale(5)
        self.scene.addItem(self.bkgrd)

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

        self.autocenterbtn = QPushButton("Auto-center")
        self.autocenterbtn.clicked.connect(self.toggle_autocenter)
        self.autocenterbtn.setCheckable(True)
        self.autocenterbtn.resize(0.2 * WIDTH, 0.1 * HEIGHT)
        self.scene.addWidget(self.autocenterbtn)

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
        self.backend = Agent(model_name=model_name, tolerance=TOLERANCE, algo='default')
        self.backend.init_core()

        start_node = self.add_node(self.backend.start, coords=QPointF(0, 0), center_flag=True)
        self.prev_node = start_node

        # debug
        self.debug = debug
        self.mouse_debug = mouse_debug

        if self.debug:
            print(f"Start word: {self.backend.start}")
            print(f"Target word: {self.backend.target}\n")
    
    def add_item(self, item, key):
        self.items[key] = item
        self.scene.addItem(item)
    
    def remove_item(self, key):
        item = self.items[key]
        self.scene.removeItem(item)
        self.items.pop(key)
    
    def random_pos(self):
        return (random.randint(0, WIDTH // 2), random.randint(0, HEIGHT // 2))
    
    def random_dir(self):
        theta = random.uniform(0, 2 * math.pi)
        return QPointF(math.cos(theta), math.sin(theta))    
    
    def norm(self, x, minX, maxX, norm_minX, norm_maxX):
        x = min(maxX, max(minX, x))
        return norm_minX + (x - minX) * (norm_maxX - norm_minX) / (maxX - minX)
    
    def norm_colour(self, x):
        return 1 / (1 + math.exp(-10 * (x - 0.5)))

    def calc_line_len(self, word, closest_word):
        sim = self.backend.get_similarity(word, closest_word, adjust=True)
        raw_len = self.norm(MAX_SIM_POS - sim, 0, MAX_SIM_POS, MIN_LINE_LENGTH, MAX_LINE_LENGTH)
        line_len = raw_len + NODE_SIZE
        return line_len
    
    def calc_pos(self, anchor, line_len):
        line_vec = line_len * self.random_dir()
        pos = self.items[anchor].pos() + line_vec
        return pos
    
    def calc_pos_2d(self, word):
        raw_pos = self.backend.get_2d(word)
        norm_pos = self.backend.norm(raw_pos) * (WORLD_WIDTH, WORLD_HEIGHT)
        offset = self.origin.scenePos()
        pos = QPointF(*norm_pos) + offset
        return pos

    def calc_colour(self, word):
        raw_sim = self.backend.get_similarity_to_target(word, adjust=False)
        sim = self.norm_colour(raw_sim)
        green_val = self.norm(sim, MIN_SIM, MAX_SIM, 0, 1)
        red_val = 1 - green_val
        colour = (int(255 * red_val), int(255 * green_val), 0, 255)
        return colour

    def _add_node(self, word, coords, colour):
        node = Node(word, coords.x(), coords.y(), NODE_SIZE, NODE_SIZE, colour)
        self.add_item(node, word)
        return node
    
    def _add_line(self, word1, word2):
        line = Line(self.items[word1], self.items[word2])
        self.add_item(line, f'line_{word1}_{word2}')
        return line
    
    def collide(self, src: QGraphicsItem):
        for other in self.items.values():
            if other is src or src.is_connected(other):
                continue
            if src.collidesWithItem(other):
                return True
        return False

    def add_node_no_collision(self, word, closest_word=None, coords=None):
        colour = self.calc_colour(word)

        if closest_word is None:
            return self._add_node(word, coords, colour)
        
        line_len = self.calc_line_len(word, closest_word)
        for try_num in range(MAX_TRIES):
            pos = self.calc_pos(closest_word, line_len)
            node = self._add_node(word, pos, colour)
            line = self._add_line(word, closest_word)
            
            print(node.pos())
            if not self.collide(node) and not self.collide(line):
                return node
            elif try_num + 1 < MAX_TRIES:
                self.remove_item(word)
                self.remove_item(f'line_{word}_{closest_word}')
        print('exhausted')
        return node

    def add_node(self, word, closest_word=None, coords=None, center_flag=None):
        node = self.add_node_no_collision(word, closest_word, coords)
        self.prev_node = node
        if center_flag:
            self.center_on(node)
        return node

    def move_all_items(self, dx, dy):
        self.origin.moveBy(dx, dy)
        for item in self.items.values():
            item.moveBy(dx, dy)
    
    def center_on(self, item: QGraphicsItem):
        width, height = self.scene.sceneRect().width(), self.scene.sceneRect().height()
        offset = QPointF((width - NODE_SIZE)/ 2, (height - NODE_SIZE) / 2)
        delta = -item.scenePos() + offset

        self.move_all_items(delta.x(), delta.y())

    def win(self):
        self.display_text.update("Congratulations! You won!")
        self.display_text.setDefaultTextColor(QColor(Qt.green))
    
    def display(self, message):
        self.display_text.update(message)
        self.display_text.setDefaultTextColor(QColor(Qt.red))

    def successful_guess(self, word, closest_word):
        self.add_node(word, closest_word, center_flag=self.autocenterflag)
        self.display_text.clear()

    def guess(self, word):
        state, message = self.backend.update(word)
        if state == VALID or state == WON:
            self.successful_guess(word, message)
            if state == WON:
                self.win()
            # Debug
            if self.debug:
                print(f"Similarity: {self.backend.get_similarity(word, message, adjust=True)}")
        else:
            self.display(message)
        self.textbox.clear()

    # Events
    def eventFilter(self, source, event: QEvent):
        if (event.type() == QEvent.MouseMove and source is self.view.viewport()):
            self.handle_mouse_move(event)
        elif (event.type() == QEvent.KeyPress):
            self.handle_key_press(event)
        elif (event.type() == QEvent.Resize):
            self.handle_resize_event(event)
        
        # Debug
        elif (event.type() == QEvent.MouseButtonPress and source is self.view.viewport()):
            try:
                if self.mouse_debug:
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
    
    def handle_resize_event(self, event: QResizeEvent):
        size = event.size()
        self.scene.setSceneRect(0, 0, size.width(), size.height())
    
    # Settings
    def toggle_autocenter(self):
        self.autocenterflag = not self.autocenterflag
        if self.autocenterflag:
            self.center_on(self.prev_node)

if __name__ == '__main__':
    app = QApplication([])
    gui = Gui(model_name='v1', debug=True)
    gui.show()
    app.exec()
