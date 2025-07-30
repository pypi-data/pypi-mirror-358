import os
import cv2
import ast
import joblib
import numpy as np
from skimage.transform import resize
from skimage.feature import hog
from .trainer import ObjectDataset  # Assumes trainer.py contains ObjectDataset with @staticmethod


class ColorDetector:
    def __init__(self, color_range_str):
        self.color_range = self.parse_color_range(color_range_str)

    def parse_color_range(self, color_range_str):
        color_values = ast.literal_eval(color_range_str)
        return color_values

    def filter_color(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([self.color_range['hmin'], self.color_range['smin'], self.color_range['vmin']])
        upper_bound = np.array([self.color_range['hmax'], self.color_range['smax'], self.color_range['vmax']])
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
        return mask

    def get_bounding_boxes(self, frame, minimum_contour_size, maximum_contour_size):
        mask = self.filter_color(frame)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bounding_boxes = []
        for contour in contours:
            if maximum_contour_size > cv2.contourArea(contour) > minimum_contour_size:
                x, y, w, h = cv2.boundingRect(contour)
                bounding_boxes.append((x, y, w, h))
        return bounding_boxes

    def extract_rois(self, frame, minimum_contour_size, maximum_contour_size, target_size=(128, 128), x_offset=30, y_offset=30):
        bounding_boxes = self.get_bounding_boxes(frame, minimum_contour_size, maximum_contour_size)
        height, width = frame.shape[:2]
        rois = [cv2.resize(frame[max(0, y - y_offset):min(height, y + h + y_offset),
                           max(0, x - x_offset):min(width, x + w + x_offset)], target_size)
                for x, y, w, h in bounding_boxes] if bounding_boxes else []
        return rois, bounding_boxes


class RBOT:
    def __init__(self, hsvValues, image_size=(128, 128), minimum_contour_size=500, maximum_contour_size=10000,
                 minimum_confidence=0.8, model_path="svm_model.joblib"):
        self.image_size = image_size
        self.color_detector = ColorDetector(hsvValues)
        self.minimum_contour_size = minimum_contour_size
        self.maximum_contour_size = maximum_contour_size
        self.minimum_confidence = minimum_confidence
        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        print(f"📥 Loading SVM model from {model_path}")
        model = joblib.load(model_path)
        print("✅ Model loaded successfully!")
        return model

    def extract_hog(self, roi):
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roi_resized = cv2.resize(roi_gray, self.image_size)
        features = hog(roi_resized, pixels_per_cell=(8, 8), cells_per_block=(2, 2), visualize=False)
        return features

    def detect_object(self, frame, target_size=(128, 128), x_offset=30, y_offset=30):
        return self.color_detector.extract_rois(
            frame,
            minimum_contour_size=self.minimum_contour_size,
            maximum_contour_size=self.maximum_contour_size,
            target_size=target_size,
            x_offset=x_offset,
            y_offset=y_offset
        )

    def get_object(self, frame, target_size=(128, 128), x_offset=30, y_offset=30):
        rois, bounding_boxes = self.detect_object(frame, target_size, x_offset, y_offset)
        if not rois:
            return "Object not detected", "Object not detected"

        predictions = []
        for roi in rois:
            features = self.extract_hog(roi)
            prob = self.model.predict_proba([features])[0]
            predictions.append(prob)

        best_idx = np.argmax([pred[1] for pred in predictions])
        best_prediction = predictions[best_idx]

        if best_prediction[1] > self.minimum_confidence:
            return rois[best_idx], bounding_boxes[best_idx]

        return "Object not detected", "Object not detected"

    def track_object(self, frame, color, width, x_offset=30, y_offset=30, bx_offset=15, by_offset=15):
        ROI, bounding_box = self.get_object(frame, self.image_size, x_offset, y_offset)
        if not isinstance(ROI, str):
            x, y, w, h = bounding_box
            bounding_box_frame = cv2.rectangle(
                frame,
                (x - bx_offset, y - by_offset),
                (x + w + bx_offset, y + h + by_offset),
                color, width
            )
            return bounding_box_frame, bounding_box

        return frame, bounding_box
