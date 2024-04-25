import cv2
import pyautogui
import numpy as np

# Initial frame size
frame_width, frame_height = 640, 480

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (frame_width, frame_height))

# Function to draw resizable frame
def draw_frame(frame, width, height):
    frame_copy = frame.copy()
    cv2.rectangle(frame_copy, (0, 0), (width, height), (255, 0, 0), 3)
    return frame_copy

while True:
    # Take a screenshot
    img = pyautogui.screenshot()

    # Convert the screenshot to an array
    frame = np.array(img)

    # Resize the frame
    frame = cv2.resize(frame, (frame_width, frame_height))

    # Draw resizable frame
    frame_with_frame = draw_frame(frame, frame_width, frame_height)

    # Write the screenshot to the video file
    out.write(frame)

    # Display the screenshot with resizable frame
    cv2.imshow('Screen Capture', frame_with_frame)

    # Check for keyboard input
    key = cv2.waitKey(1) & 0xFF

    # Resize frame if '+' or '-' is pressed
    if key == ord('+'):
        frame_width += 100
        frame_height += 100
    elif key == ord('-'):
        frame_width -= 100
        frame_height -= 100
        if frame_width <= 0 or frame_height <= 0:
            frame_width = max(frame_width, 1)
            frame_height = max(frame_height, 1)

    # Check for 'q' key press to exit
    elif key == ord('q'):
        break

# Release the video writer and close OpenCV windows
out.release()
cv2.destroyAllWindows()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
