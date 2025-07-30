import os
import cv2
import ast
import joblib
import numpy as np
from concurrent.futures import ThreadPoolExecutor


class ColorDetector:
    def __init__(self, color_range_str):
        self.color_range = self.parse_color_range(color_range_str)

    def parse_color_range(self, color_range_str):
        color_values = ast.literal_eval(color_range_str)
        return color_values

    def filter_color(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([
            self.color_range['hmin'],
            self.color_range['smin'],
            self.color_range['vmin']
        ])
        upper_bound = np.array([
            self.color_range['hmax'],
            self.color_range['smax'],
            self.color_range['vmax']
        ])
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
        return mask

    def get_bounding_boxes(self, frame, minimum_contour_size, maximum_contour_size):
        mask = self.filter_color(frame)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(c) for c in contours]
        bounding_boxes = [
            cv2.boundingRect(contours[i]) for i in range(len(contours))
            if minimum_contour_size < areas[i] < maximum_contour_size
        ]
        return bounding_boxes

    def extract_rois(self, frame, minimum_contour_size, maximum_contour_size, target_size=(64, 64), x_offset=30, y_offset=30):
        bounding_boxes = self.get_bounding_boxes(frame, minimum_contour_size, maximum_contour_size)
        height, width = frame.shape[:2]
        rois = [
            cv2.resize(frame[max(0, y - y_offset):min(height, y + h + y_offset),
                       max(0, x - x_offset):min(width, x + w + x_offset)],
                       target_size)
            for x, y, w, h in bounding_boxes
        ] if bounding_boxes else []
        return rois, bounding_boxes


class RBOT:
    def __init__(self, hsvValues, image_size=(64, 64), minimum_contour_size=500, maximum_contour_size=10000,
                 minimum_confidence=0.8, model_path="svm_model.joblib", multithread=True, block_size=(16, 16), block_stride=(8, 8), cell_size=(8, 8)):
        self.image_size = image_size
        self.color_detector = ColorDetector(hsvValues)
        self.minimum_contour_size = minimum_contour_size
        self.maximum_contour_size = maximum_contour_size
        self.minimum_confidence = minimum_confidence
        self.model = self.load_model(model_path)
        self.multithread = multithread

        # Optimized HOG descriptor
        self.hog = cv2.HOGDescriptor(
            _winSize=self.image_size,
            _blockSize=block_size,
            _blockStride=block_stride,
            _cellSize=cell_size,
            _nbins=9
        )

    def load_model(self, model_path):
        print(f"📥 Loading SVM model from {model_path}")
        model = joblib.load(model_path)
        print("✅ Model loaded successfully!")
        return model

    def extract_hog(self, roi):
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, self.image_size)
        features = self.hog.compute(resized)
        return features.flatten()

    def detect_object(self, frame, target_size=(64, 64), x_offset=30, y_offset=30):
        return self.color_detector.extract_rois(
            frame,
            minimum_contour_size=self.minimum_contour_size,
            maximum_contour_size=self.maximum_contour_size,
            target_size=target_size,
            x_offset=x_offset,
            y_offset=y_offset
        )

    def get_object(self, frame, target_size=(64, 64), x_offset=30, y_offset=30):
        rois, bounding_boxes = self.detect_object(frame, target_size, x_offset, y_offset)
        if not rois:
            return "Object not detected", "Object not detected"

        if self.multithread:
            with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                preprocessed = list(executor.map(
                    lambda roi: cv2.resize(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), self.image_size),
                    rois
                ))
                features_list = list(executor.map(self.hog.compute, preprocessed))
                features_list = [f.flatten() for f in features_list]
        else:
            features_list = [self.extract_hog(roi) for roi in rois]

        probs = self.model.predict_proba(features_list)
        best_idx = np.argmax([p[1] for p in probs])
        best_prediction = probs[best_idx]

        if best_prediction[1] > self.minimum_confidence:
            return rois[best_idx], bounding_boxes[best_idx]

        return "Object not detected", "Object not detected"

    def track_object(self, frame, color=(0, 255, 0), width=2, x_offset=30, y_offset=30, bx_offset=15, by_offset=15):
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
