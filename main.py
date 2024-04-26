import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QLabel, QSizeGrip
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import QTimer, Qt, QObject, QThread, pyqtSignal

class CaptureArea(QFrame):
    def __init__(self):
        super().__init__()

        # Set initial size and position of the capture area
        self.setGeometry(100, 100, 500, 500)

        # Make the widget transparent and without a frame
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Set the border properties directly
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(10)
        self.setStyleSheet("border-color: red;")

        # Install event filter
        self.installEventFilter(self)

        self.mouse_press_pos = None
        self.mouse_is_pressed = False

        # Add resize grip
        self.resize_grip = QSizeGrip(self)
        self.resize_grip.setVisible(True)

        # Add indicator label
        self.indicator_label = QLabel(self)
        self.indicator_label.setGeometry(5, 5, 20, 20)
        self.indicator_label.setStyleSheet("background-color: red; border-radius: 50px;")
        self.indicator_label.setVisible(False)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.mouse_press_pos = event.pos()
            self.mouse_is_pressed = True

    def mouseMoveEvent(self, event):
        if self.mouse_is_pressed:
            delta = event.pos() - self.mouse_press_pos
            new_pos = self.pos() + delta
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_is_pressed = False

    def resizeEvent(self, event):
        self.resize_grip.setGeometry(self.width() - 20, self.height() - 20, 20, 20)
        self.indicator_label.move(self.width() - 25, self.height() - 25)

class ScreenShareWorker(QObject):
    signal = pyqtSignal(QPixmap)

    def __init__(self, capture_area):
        super().__init__()
        self.capture_area = capture_area

    def run(self):
        while True:
            # Capture the screen
            screen_capture = QApplication.primaryScreen().grabWindow(0,
                                                                        self.capture_area.geometry().x(),
                                                                        self.capture_area.geometry().y(),
                                                                        self.capture_area.geometry().width(),
                                                                        self.capture_area.geometry().height())
            # Emit signal with the captured screen
            self.signal.emit(screen_capture)
            # Wait for 100ms before capturing again
            QThread.msleep(100)

class ScreenShareApp(QMainWindow):
    def __init__(self, capture_area):
        super().__init__()

        # Store the capture area
        self.capture_area = capture_area

        # Set the size of the window to be the same as the capture area
        self.setGeometry(self.capture_area.geometry())

        # Create a thread for capturing the screen
        self.thread = QThread()
        self.worker = ScreenShareWorker(capture_area)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.signal.connect(self.update_pixmap)
        self.thread.start()

    def update_pixmap(self, pixmap):
        # Update the captured pixmap
        self.pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if hasattr(self, 'pixmap'):
            # Draw the captured pixmap
            painter.drawPixmap(self.rect(), self.pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    capture_area = CaptureArea()
    capture_area.show()

    window = ScreenShareApp(capture_area)
    window.show()

    sys.exit(app.exec_())
