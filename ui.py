import tkinter as tk
import cv2
from PIL import Image, ImageTk
# Import the new facial_recognition class
from facial_recognition import FacialRecognition  

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Facial Recognition")
        self.root.geometry("1250x750")
        
        # UI elements setup
        tk.Label(self.root, text="Detected People:").place(x=1000, y=60)
        self.detected_people_text = tk.Text(self.root, height=30, width=40)
        self.detected_people_text.place(x=875, y=80)
        
        # Initializes start button
        self.start_button = tk.Button(self.root, text="Start Feed", command=self.start_stop_feed)
        self.start_button.place(x=350, y=600)
        
        # Initializes the feed label to "Off"
        self.feed_label = tk.Label(self.root, text="Feed Off")
        self.feed_label.place(x=350, y=50)
        
        # Initializes the frame on the UI
        tk.Frame(self.root, bg="lightgray", width=685, height=395).place(x=50, y=75)
        
        self.feed_widget = tk.Label(self.root)
        self.feed_widget.place(x=75, y=90)
        
        # Setting up the camera
        self.cap = cv2.VideoCapture(0)
        width, height = 450, 400  # Camera dimensions
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Initializes the feed status to false for start_stop_feed to enable
        self.feed_active = False  

        # Initialize FacialRecognition for face detection and recognition
        self.recognition = FacialRecognition()

    def open_camera(self):
        if self.feed_active:
            ret, frame = self.cap.read()
            if ret:
                # Get face locations and names from the recognition module
                face_locations, face_names = self.recognition.recognize_faces(frame)

                # Draw rectangles around faces and display names
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

                # Update the detected people text box
                self.detected_people_text.delete(1.0, tk.END)
                for name in face_names:
                    self.detected_people_text.insert(tk.END, name + "\n")
                
                # Convert the frame to a format that can be displayed in Tkinter
                opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                captured_image = Image.fromarray(opencv_image)
                photo_image = ImageTk.PhotoImage(image=captured_image)
                
                # Update the feed widget with the new image
                self.feed_widget.photo_image = photo_image
                self.feed_widget.configure(image=photo_image)
                
                # Schedule the next frame capture after 10 milliseconds
                self.feed_widget.after(10, self.open_camera)
            else:
                print("Failed to capture frame. Stopping feed.")
                # Stopping the feed here keeps the print statement from infinite loop
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
                width, height = 450, 400  # Camera dimensions
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                
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


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
