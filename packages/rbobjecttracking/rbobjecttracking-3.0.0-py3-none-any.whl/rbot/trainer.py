import os
import time
import numpy as np
from skimage.io import imread
from skimage.transform import resize
from skimage.feature import hog
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib  # For saving/loading the SVM model


class ObjectDataset:
    def __init__(self, dataset_path, img_size=(128, 128)):
        self.img_size = img_size
        self.object_dir = os.path.join(dataset_path, "object")
        self.not_object_dir = os.path.join(dataset_path, "not_objects")
        self.X = []
        self.y = []
        self.load_data()

    @staticmethod
    def extract_features(img_path, img_size=(128, 128)):
        image = imread(img_path, as_gray=True)
        image = resize(image, img_size)
        features, _ = hog(image, pixels_per_cell=(8, 8), cells_per_block=(2, 2), visualize=True)
        return features

    def load_data(self):
        for folder, label in [(self.object_dir, 1), (self.not_object_dir, 0)]:
            for file in os.listdir(folder):
                path = os.path.join(folder, file)
                try:
                    features = ObjectDataset.extract_features(path, self.img_size)
                    self.X.append(features)
                    self.y.append(label)
                except Exception as e:
                    print(f"⚠️ Skipping {path}: {e}")
        self.X = np.array(self.X)
        self.y = np.array(self.y)

class Trainer:
    """Trains an SVM on extracted HOG features."""
    def __init__(self, dataset_path, model_path="svm_model.joblib", img_size=(128, 128)):
        self.dataset = ObjectDataset(dataset_path, img_size=img_size)
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

        # Save model
        joblib.dump(self.model, self.model_path)
        print(f"💾 Model saved to {self.model_path}")

    def predict(self, image_path):
        features = self.dataset.extract_features(image_path)
        start = time.time()
        prediction = self.model.predict([features])[0]
        end = time.time()
        print("🔍 Predicted class:", "A" if prediction == 0 else "B")
        print(f"⏱️ Prediction time: {end - start:.4f} seconds")


if __name__ == "__main__":
    trainer = Trainer(r"S:\python\rbot\testing\scissors", model_path="svm_model.joblib")
    trainer.train()
    trainer.predict(r'S:\python\rbot\testing\scissors\img_1.jpg')
