from random import choices
import tkinter as tk
import cv2
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from mongo_storage import MongoStorage 
from export_storage import ExportStorage
from confidence_recognition import ConfidenceRecognition
import time
import os
from dotenv import load_dotenv
load_dotenv()


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Facial Recognition")
        self.root.geometry("1250x750")

        # MongoDB setup
        MONGO_URI = os.getenv("MONGO_URI")

        # UI Elements
        self.dark_mode_var = tk.BooleanVar()
        self.check_dark_mode = tk.Checkbutton(self.root, text="Dark Mode", variable=self.dark_mode_var, command=self.dark_mode)
        self.check_dark_mode.place(x=1150, y=725)

        self.detect_label = tk.Label(self.root, text="Detected People:")
        self.detect_label.place(x=1000, y=60)

        self.det_people_frame = tk.Frame(self.root, bg="darkgray", width=375, height=525)
        self.det_people_frame.place(x=850, y=80)

        self.detected_people_text = tk.Text(self.root, height=30, width=40)
        self.detected_people_text.place(x=875, y=100)

        self.start_button = tk.Button(self.root, text="Start Feed", width=10, height=2, command=self.start_stop_feed)
        self.start_button.place(x=190, y=550)

        self.feed_label = tk.Label(self.root, text="Feed Off")
        self.feed_label.place(x=350, y=50)

        self.create_user_button = tk.Button(self.root, text="Create User", width=10, height=2)
        self.create_user_button.place(x=190, y=625)

        self.create_user_frame = tk.Frame(self.root, bg="darkgray", width=325, height=200)
        self.create_user_frame.place(x=300, y=500)

        self.cap_image_button = tk.Button(self.root, text="Capture Image", width=20, height=2, command=self.capture_image)
        self.cap_image_button.place(x=395, y=550)

        self.name_cap = tk.Text(self.root, height=2, width=35)
        self.name_cap.place(x=320, y=625)
        self.name_label = tk.Label(self.root, text="Enter name of User:")
        self.name_label.place(x=321, y=605)

        self.refresh_button = tk.Button(self.root, text="Refresh List", width=10, height=2, command=self.refresh)
        self.refresh_button.place(x=925, y=615)

        self.export_button = tk.Button(self.root, text="Export List", width=10, height=2, command=self.handle_export)
        self.export_button.place(x=925, y=615)

        self.choices = ["txt", "csv", "json"]
        self.export_label = tk.Label(self.root, text="Export Type:")
        self.export_label.place(x=925, y=650)
        self.export_dropdown = ttk.Combobox(self.root, values=self.choices)
        self.export_dropdown.place(x=925, y=675)

        self.vid_frame = tk.Frame(self.root, bg="darkgray", width=685, height=395)
        self.vid_frame.place(x=50, y=75)
        self.feed_widget = tk.Label(self.root)
        self.feed_widget.place(x=75, y=90)

        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.width, self.height = 500, 350
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)  # NEW: Request 30 FPS
        self.last_frame_time = time.time()  # For FPS tracking


        if not self.cap.isOpened():
            print("Error: Camera not initialized!")
            messagebox.showerror("Camera Error", "Could not open the camera.")
            return

        self.feed_active = False
        self.recognition = ConfidenceRecognition(self.cap, self.name_cap)
        self.storage = MongoStorage(MONGO_URI, self.cap, self.name_cap, self.recognition)
        self.start_stop_feed()

    def capture_image(self):
        # Call MongoDB-based image capture and storage
        uid, _ = self.storage.take_picture()
        
        if uid:
            # Reload the known face encodings from MongoDB after adding a new one
            self.storage.load_known_faces()
        
        # Clear the name entry box
        self.name_cap.delete("0.0", tk.END)


    def handle_export(self):
        export_type = self.export_dropdown.get()
        self.export_list(export_type)

    def export_list(self, choice):
        exporter = ExportStorage(self.recognition, choice)
        if choice == "txt":
            exporter.export_to_txt()
        elif choice == "csv":
            exporter.export_to_csv()
        elif choice == "json":
            exporter.export_to_json()
        else:
            print("Error: Invalid export type.")
            messagebox.showerror("Export Error", "Invalid export type.")

    def open_camera(self):
        if self.feed_active:
            ret, frame = self.cap.read()

            # Only process every Nth frame (skip every other for speed)
            if hasattr(self, "frame_count"):
                self.frame_count += 1
            else:
                self.frame_count = 1

            if self.frame_count % 2 != 0:
                self.feed_widget.after(10, self.open_camera)
                return

            if ret:
                frame = cv2.resize(frame, (self.width, self.height))

                # Optional: show FPS overlay
                now = time.time()
                fps = 1 / (now - self.last_frame_time)
                self.last_frame_time = now
                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)

                # Face recognition
                face_locations, face_names = self.recognition.recognize_faces(frame)
                confidence_scores = self.recognition.get_last_confidence_scores()

                for (top, right, bottom, left), name, score in zip(face_locations, face_names, confidence_scores):
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

                    if score >= 70:
                        conf_color = (0, 255, 0)
                    elif score >= 50:
                        conf_color = (0, 255, 255)
                    else:
                        conf_color = (0, 0, 255)

                    confidence_text = f"{score:.1f}%"
                    cv2.putText(frame, confidence_text, (left, top - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, conf_color, 2)

                self.detected_people_text.delete(1.0, tk.END)
                # Get unique names and highest confidence per person
                name_conf_map = {}
                for name, score in zip(face_names, confidence_scores):
                    if name not in name_conf_map or score > name_conf_map[name]:
                        name_conf_map[name] = score

                # Write unique names and their best confidence
                for name, score in name_conf_map.items():
                    confidence_level = "HIGH" if score >= 70 else "MEDIUM" if score >= 50 else "LOW"
                    self.detected_people_text.insert(tk.END, f"{name}\n")
                    self.detected_people_text.insert(tk.END, f"Confidence: {score:.1f}% ({confidence_level})\n\n")


                opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                captured_image = Image.fromarray(opencv_image)
                photo_image = ImageTk.PhotoImage(image=captured_image)

                self.feed_widget.photo_image = photo_image
                self.feed_widget.configure(image=photo_image)
                self.feed_widget.after(10, self.open_camera)

            else:
                print("Failed to capture frame. Stopping feed.")
                self.feed_active = False
                self.feed_label.config(text="Feed Off")
                self.start_button.config(text="Start Feed")
                if self.cap.isOpened():
                    self.cap.release()
                cv2.destroyAllWindows()
                self.feed_widget.config(image='')


    def start_stop_feed(self):
        if not self.feed_active:
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.feed_active = True
            self.feed_label.config(text="Feed On")
            self.start_button.config(text="Stop Feed")
            self.open_camera()
        else:
            self.feed_active = False
            self.feed_label.config(text="Feed Off")
            self.start_button.config(text="Start Feed")
            if self.cap.isOpened():
                self.cap.release()
            cv2.destroyAllWindows()
            self.feed_widget.config(image='')

    def refresh(self):
        self.detected_people_text.delete("0.0", tk.END)

    def dark_mode(self):
        if self.dark_mode_var.get():
            self.root.configure(bg="gray18")
            self.detect_label.configure(bg='gray60', fg="gray99")
            self.feed_label.configure(bg='gray60', fg="gray99")
            self.name_label.configure(bg='gray60', fg="gray99")
            self.det_people_frame.configure(bg='gray27')
            self.create_user_frame.configure(bg='gray27')
            self.vid_frame.configure(bg='gray27')
            self.detected_people_text.configure(bg='gray60', fg="gray99")
            self.name_cap.configure(bg='gray60', fg="gray99")
            self.start_button.configure(bg='gray60', fg="gray99")
            self.create_user_button.configure(bg='gray60', fg="gray99")
            self.cap_image_button.configure(bg='gray60', fg="gray99")
            self.refresh_button.configure(bg='gray60', fg="gray99")
            self.export_button.configure(bg='gray60', fg="gray99")
            self.check_dark_mode.configure(bg='gray60', fg="gray99")
        else:
            self.root.configure(bg="SystemButtonFace")
            self.detect_label.configure(bg='SystemButtonFace', fg="black")
            self.feed_label.configure(bg='SystemButtonFace', fg="black")
            self.name_label.configure(bg='SystemButtonFace', fg="black")
            self.det_people_frame.configure(bg='darkgray')
            self.create_user_frame.configure(bg='darkgray')
            self.vid_frame.configure(bg='darkgray')
            self.detected_people_text.configure(bg='SystemButtonFace', fg="black")
            self.name_cap.configure(bg='SystemButtonFace', fg="black")
            self.start_button.configure(bg='SystemButtonFace', fg="black")
            self.create_user_button.configure(bg='SystemButtonFace', fg="black")
            self.cap_image_button.configure(bg='SystemButtonFace', fg="black")
            self.refresh_button.configure(bg='SystemButtonFace', fg="black")
            self.export_button.configure(bg='SystemButtonFace', fg="black")
            self.check_dark_mode.configure(bg='SystemButtonFace', fg="black")

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
