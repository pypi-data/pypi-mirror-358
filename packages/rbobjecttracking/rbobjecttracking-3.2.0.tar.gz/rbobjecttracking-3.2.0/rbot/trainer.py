import os
import time
import numpy as np
import cv2
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib  # For saving/loading the SVM model
import ast


class ColorDetector:
    def __init__(self, color_range_str):
        self.color_range = self.parse_color_range(color_range_str)

    def parse_color_range(self, color_range_str):
        return ast.literal_eval(color_range_str)

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


class ObjectDataset:
    def __init__(self, dataset_path, img_size=(64, 64), block_size=(16, 16), cell_size=(8, 8),
                 block_stride=(8, 8), color_range=None, x_offset=30, y_offset=30):
        self.img_size = img_size
        self.object_dir = os.path.join(dataset_path, "object")
        self.not_object_dir = os.path.join(dataset_path, "not_objects")
        self.X = []
        self.y = []
        self.color_detector = ColorDetector(color_range) if color_range else None
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.hog = cv2.HOGDescriptor(
            _winSize=self.img_size,
            _blockSize=block_size,
            _blockStride=block_stride,
            _cellSize=cell_size,
            _nbins=9
        )
        self.load_data()

    def extract_features_from_image(self, img_path, is_object):
        image = cv2.imread(img_path)
        if image is None:
            raise ValueError(f"Image not found: {img_path}")

        if self.color_detector and is_object:
            rois, _ = self.color_detector.extract_rois(
                image,
                minimum_contour_size=200,
                maximum_contour_size=10000,
                target_size=self.img_size,
                x_offset=self.x_offset,
                y_offset=self.y_offset
            )
            if rois:
                gray = cv2.cvtColor(rois[0], cv2.COLOR_BGR2GRAY)
            else:
                print(f"⚠️ No ROI found in {img_path}, using fallback full image.")
                gray = cv2.cvtColor(cv2.resize(image, self.img_size), cv2.COLOR_BGR2GRAY)
        else:
            gray = cv2.cvtColor(cv2.resize(image, self.img_size), cv2.COLOR_BGR2GRAY)

        features = self.hog.compute(gray)
        return features.flatten()

    def load_data(self):
        for folder, label in [(self.object_dir, 1), (self.not_object_dir, 0)]:
            for file in os.listdir(folder):
                path = os.path.join(folder, file)
                try:
                    features = self.extract_features_from_image(path, is_object=(label == 1))
                    self.X.append(features)
                    self.y.append(label)
                except Exception as e:
                    print(f"⚠️ Skipping {path}: {e}")

        self.X = np.array(self.X)
        self.y = np.array(self.y)


class Trainer:
    def __init__(self, dataset_path, model_path="svm_model.joblib", img_size=(64, 64), color_range=None, x_offset=30, y_offset=30):
        self.dataset = ObjectDataset(
            dataset_path,
            img_size=img_size,
            color_range=color_range,
            x_offset=x_offset,
            y_offset=y_offset
        )
        self.model = SVC(kernel="linear", probability=True)
        self.model_path = model_path

    def train(self):
        X_train, X_test, y_train, y_test = train_test_split(self.dataset.X, self.dataset.y, test_size=0.2)

        print("⚙️ Training SVM...")
        start = time.time()
        self.model.fit(X_train, y_train)
        end = time.time()
        print(f"✅ Training completed in {end - start:.4f} seconds.")

        y_pred = self.model.predict(X_test)
        print("🎯 Accuracy:", accuracy_score(y_test, y_pred))

        joblib.dump(self.model, self.model_path)
        print(f"💾 Model saved to {self.model_path}")

    def predict(self, image_path):
        features = self.dataset.extract_features_from_image(image_path, is_object=True)
        start = time.time()
        prediction = self.model.predict([features])[0]
        end = time.time()
        print("🔍 Predicted class:", "Object" if prediction == 1 else "Not Object")
        print(f"⏱️ Prediction time: {end - start:.4f} seconds")


if __name__ == "__main__":
    hsv_range = "{'hmin': 20, 'hmax': 45, 'smin': 50, 'smax': 255, 'vmin': 50, 'vmax': 255}"
    trainer = Trainer(
        dataset_path=r"S:\python\rbot\testing\scissors",
        model_path="svm_model.joblib",
        img_size=(64, 64),
        color_range=hsv_range
    )
    trainer.train()
    trainer.predict(r'S:\python\rbot\testing\scissors\img_1.jpg')
