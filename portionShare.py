import sys
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QLabel, QSizeGrip, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import QTimer, Qt, QRect, pyqtSignal, QEvent, QThread


class CaptureArea(QFrame):
    # Define sizeChanged signal with QRect parameter
    sizeChanged = pyqtSignal(QRect)

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
        self.resize_origin = None

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
            if self.resize_grip.geometry().contains(event.pos()):
                self.mouse_press_pos = event.globalPos()
                self.resize_origin = self.geometry().bottomRight()
            else:
                self.mouse_press_pos = event.globalPos() - self.frameGeometry().topLeft()
                self.mouse_is_pressed = True

    def mouseMoveEvent(self, event):
        if self.mouse_is_pressed:
            self.move(event.globalPos() - self.mouse_press_pos)
        elif self.resize_origin is not None:
            diff = event.globalPos() - self.mouse_press_pos
            self.setGeometry(QRect(self.geometry().topLeft(), self.resize_origin + diff).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_is_pressed = False
            self.resize_origin = None

    def resizeEvent(self, event):
        self.resize_grip.setGeometry(self.width() - 20, self.height() - 20, 20, 20)
        self.indicator_label.move(self.width() - 25, self.height() - 25)

        # Emit a signal indicating that the size has changed
        self.sizeChanged.emit(self.geometry())

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            # Forward resize event to resizeEvent method
            self.resizeEvent(event)
        return super().eventFilter(obj, event)


class ScreenWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.screen_label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.screen_label)
        self.setLayout(layout)

    def update_screen(self, screen_capture):
        self.screen_label.setPixmap(screen_capture)

class ScreenCaptureThread(QThread):
    screenCaptured = pyqtSignal(QPixmap)

    def __init__(self, capture_area):
        super().__init__()
        self.capture_area = capture_area
        self.stopped = False

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            try:
                screen_capture = QApplication.primaryScreen().grabWindow(
                    0,
                    self.capture_area.geometry().x(),
                    self.capture_area.geometry().y(),
                    self.capture_area.geometry().width(),
                    self.capture_area.geometry().height()
                )
                self.screenCaptured.emit(screen_capture)
                time.sleep(0.1)  # Adjust capture frequency as needed
            except Exception as e:
                print("Error during screen capturing:", e)

class ScreenShareApp(QMainWindow):
    def __init__(self, capture_area):
        super().__init__()

        # Store the capture area
        self.capture_area = capture_area

        # Set the size of the window to be the same as the capture area
        self.setGeometry(self.capture_area.geometry())

        # Hide window buttons (close, minimize, maximize)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowTitleHint)

        # Make the window transparent to mouse events
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Create a screen widget to display the captured screen
        self.screen_widget = ScreenWidget(self)

        # Create and start the screen capture thread
        self.capture_thread = ScreenCaptureThread(self.capture_area)
        self.capture_thread.screenCaptured.connect(self.update_screen)
        self.capture_thread.start()

        # Connect the resizeEvent of the CaptureArea to the adjust_size method
        self.capture_area.sizeChanged.connect(self.adjust_size)

    def adjust_size(self, geometry):
        # Set the size of the ScreenShareApp to be the same as the capture area
        self.setGeometry(geometry)
        # Adjust the size of the screen widget
        self.screen_widget.setGeometry(0, 0, self.width(), self.height())

    def update_screen(self, screen_capture):
        self.screen_widget.update_screen(screen_capture)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                self.showMinimized()
                self.capture_area.show()
            elif self.isMaximized():
                self.showMaximized()
                self.capture_area.show()
            else:
                self.showNormal()
                self.capture_area.show()

    def closeEvent(self, event):
        self.capture_thread.stop()
        self.capture_thread.wait()
if __name__ == "__main__":
    app = QApplication(sys.argv)

    capture_area = CaptureArea()
    capture_area.setStyleSheet("border-color: white;")

    capture_area.show()

    window = ScreenShareApp(capture_area)
    window.show()

    sys.exit(app.exec_())