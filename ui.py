import tkinter as tk
import cv2
from PIL import Image, ImageTk

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Facial Recognition")
        self.root.geometry("1250x750")
        
        # UI elements setup
        tk.Label(self.root, text="Detected People:").place(x=1000, y=60)
        tk.Text(self.root, height=30, width=40).place(x=875, y=80)
        
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
        
        # Initalizes the feed status to false for start_stop_feed to enable
        self.feed_active = False  

    def open_camera(self):
        if self.feed_active:
            ret, frame = self.cap.read()
            if ret:
                # Convert frame color from BGR to RGBA
                opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                captured_image = Image.fromarray(opencv_image)
                photo_image = ImageTk.PhotoImage(image=captured_image)
                
                # Update the feed widget with the new image
                self.feed_widget.photo_image = photo_image
                self.feed_widget.configure(image=photo_image)
                
                # Schedule the next frame capture after 10 milliseconds
                self.feed_widget.after(10, self.open_camera)
            else:
                # If capturing the frame fails, stop the feed
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
            # Reinitialize camera if it's not opened
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
