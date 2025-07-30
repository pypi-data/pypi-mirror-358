import cv2
import numpy as np
from cvzone.ColorModule import ColorFinder  # part of cvzone

class ColorRangeSelector:
    def __init__(self, window_name="HSV Selector"):
        self.window_name = window_name
        self.color_finder = ColorFinder(True)

    def select_color_range(self, color="blue"):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            imgColor, mask = self.color_finder.update(frame, color)
            hsv_values = self.color_finder.getColorHSV("blue")

            cv2.imshow("Frame", imgColor)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Exit condition
                break

        cap.release()
        cv2.destroyAllWindows()
        return hsv_values['lower'], hsv_values['upper']  # Dynamically updated bounds
# Run it
if __name__ == "__main__":
    selector = ColorRangeSelector()
    lower, upper = selector.select_color_range()
    print("Final HSV Range:")
    print("Lower:", lower)
    print("Upper:", upper)
