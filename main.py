import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QRubberBand, QFrame, QSizeGrip
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import QTimer, QRect, QEvent
from PyQt5.QtCore import Qt


class ResizableWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.SubWindow)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.drag_start = None

        self.sizeGrip = QSizeGrip(self)
        self.sizeGrip.setVisible(True)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = event.pos()
            self.rubberBand.setGeometry(event.pos().x(), event.pos().y(), 0, 0)
            self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if self.drag_start:
            self.rubberBand.setGeometry(QRect(self.drag_start, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = None
            self.rubberBand.hide()


class CaptureArea(ResizableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 200)  # Set initial size of the widget
        self.setStyleSheet("border: 2px solid red;")  # Set border style
        self.setFrameStyle(QFrame.Box | QFrame.Plain)  # Set frame style

class CaptureArea(QFrame):
    def __init__(self):
        super().__init__()

        # Set initial size and position of the capture area
        self.setGeometry(100, 100, 500, 500)

        # Make the widget transparent and without a frame
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        # Set the widget's background to be translucent
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Set the border properties directly
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(10)
        self.setStyleSheet("border-color: red;")

        # Add resize grip
        self.resize_grip = ResizableWidget(self)
        self.resize_grip.setGeometry(self.width() - 20, self.height() - 20, 20, 20)
        # self.resize_grip.setStyleSheet("background-color: blue;")  # Adjust style as needed

        # Install event filter
        self.installEventFilter(self)

        self.mouse_press_pos = None
        self.mouse_is_pressed = False

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




class ScreenShareApp(QMainWindow):
    def __init__(self, capture_area):
        super().__init__()

        # Store the capture area
        self.capture_area = capture_area

        # Set the size of the window to be the same as the capture area
        self.setGeometry(self.capture_area.geometry())

        # Set up a timer to capture the screen every 100ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Capture the screen
        screen_capture = QApplication.primaryScreen().grabWindow(0,
                                                                 self.capture_area.geometry().x(),
                                                                 self.capture_area.geometry().y(),
                                                                 self.capture_area.geometry().width(),
                                                                 self.capture_area.geometry().height())

        # Calculate the scale factor for the captured image
        scale_factor = min(self.width() / screen_capture.width(), self.height() / screen_capture.height())

        # Scale the captured image to fit the window
        screen_capture = screen_capture.scaled(self.width() * scale_factor, self.height() * scale_factor,
                                               Qt.KeepAspectRatio)

        # Calculate the position to center the captured image in the window
        x = (self.width() - screen_capture.width()) / 2
        y = (self.height() - screen_capture.height()) / 2

        # Draw the captured image
        painter.drawPixmap(x, y, screen_capture)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    capture_area = CaptureArea()
    capture_area.show()

    window = ScreenShareApp(capture_area)
    window.show()

    sys.exit(app.exec_())
