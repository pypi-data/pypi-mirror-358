import os
import cv2
import customtkinter as ctk
import threading

class DataCollector(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RBOT Data Collector")
        self.geometry("600x400")

        self.dataset_dir_var = ctk.StringVar()
        self.image_numbers = [0, 0]
        self.cap = cv2.VideoCapture(0)  # Open webcam feed

        # UI Elements
        self.label_dir = ctk.CTkLabel(self, text="Enter Dataset Directory:")
        self.label_dir.pack(pady=5)

        self.entry_dir = ctk.CTkEntry(self, textvariable=self.dataset_dir_var)
        self.entry_dir.pack(pady=5)

        self.capture_button_object = ctk.CTkButton(self, text="Capture Object Image", command=self.capture_object)
        self.capture_button_object.pack(pady=5)

        self.capture_button_background = ctk.CTkButton(self, text="Capture Background Image and objects with same color", command=self.capture_background)
        self.capture_button_background.pack(pady=5)

        self.frame_label = ctk.CTkLabel(self, text="")
        self.frame_label.pack(pady=5)

        # Start the webcam feed in a separate thread
        threading.Thread(target=self.display_webcam, daemon=True).start()

    def get_dataset_dir(self, subfolder):
        """Retrieve dataset directory from input and create necessary subdirectories"""
        dataset_dir = self.dataset_dir_var.get().strip()
        if not dataset_dir:
            print("Error: Please specify a dataset directory.")
            return None
        target_dir = os.path.join(dataset_dir, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    def capture_object(self):
        """Capture and save object image"""
        save_dir = self.get_dataset_dir("object")
        if save_dir:
            self.save_image(save_dir, "object")

    def capture_background(self):
        """Capture and save background image without filtering"""
        save_dir = self.get_dataset_dir("not_objects")
        if save_dir:
            self.save_image(save_dir, "not_object")

    def save_image(self, save_dir, category):
        """Saves the current webcam frame when button is clicked"""
        ret, frame = self.cap.read()
        if ret:
            self.image_numbers[0 if category == "object" else 1] += 1
            img_path = os.path.join(save_dir, f"img_{self.image_numbers[0 if category == 'object' else 1]}.jpg")
            cv2.imwrite(img_path, frame)
            print(f"Saved: {img_path}")
        else:
            print("Failed to capture image.")

    def display_webcam(self):
        """Continuously displays webcam feed in the UI window"""
        while True:
            ret, frame = self.cap.read()
            if ret:
                cv2.imshow("Live Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def collectData(self):
        """Starts the GUI for collecting data."""
        self.mainloop()

# Usage
if __name__ == "__main__":
    collector = DataCollector()
    collector.collectData()
