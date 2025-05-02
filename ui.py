import tkinter as tk
import cv2
from tkinter import messagebox
from PIL import Image, ImageTk
from facial_recognition import FacialRecognition # Import the facial_recognition class
from file_storage import Storage

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Facial Recognition")
        self.root.geometry("1250x750")

        # Dark Mode Check Box
        self.dark_mode_var = tk.BooleanVar()
        self.check_dark_mode=tk.Checkbutton(self.root, text="Dark Mode", variable=self.dark_mode_var, command=self.dark_mode)
        self.check_dark_mode.place(x=1150, y=725)
        # UI elements setup
        self.detect_label = tk.Label(self.root, text="Detected People:")
        self.detect_label.place(x=1000, y=60)

        self.det_people_frame = tk.Frame(self.root, bg="darkgray", width=375, height=525)
        self.det_people_frame.place(x=850, y=80)

        self.detected_people_text = tk.Text(self.root, height=30, width=40)
        self.detected_people_text.place(x=875, y=100)
        
        # Initializes start button
        self.start_button = tk.Button(self.root, text="Start Feed", width=10, height = 2, command=self.start_stop_feed)
        self.start_button.place(x=190, y=550)
        
        # Initializes the feed label to "Off"
        self.feed_label = tk.Label(self.root, text="Feed Off")
        self.feed_label.place(x=350, y=50)
        
        # Create User UI Elements
        self.create_user_button = tk.Button(self.root, text="Create User", width=10, height = 2) # Have to add ", command=create_user" and make create_user function
        self.create_user_button.place(x=190,y=625)

        self.create_user_frame = tk.Frame(self.root, bg="darkgray", width=325, height=200)
        self.create_user_frame.place(x=300, y=500)

        # Capture image button
        self.cap_image_button = tk.Button(self.root, text="Capture Image", width=20, height = 2, command = self.capture_image) # Have to add ", command=cap_image" and create cap_image function
        self.cap_image_button.place(x=395,y=550)

        # Username entry box
        self.name_cap = tk.Text(self.root, height=2,width=35) # Have to write function to take user written text from the text box
        self.name_cap.place(x=320,y=625)
        self.name_label = tk.Label(self.root, text="Enter name of User:")
        self.name_label.place(x=321, y=605)

        # Export/Refresh Buttons
        self.refresh_button = tk.Button(self.root, text="Refresh List", width=10, height = 2, command = self.refresh) # Have to add ", command=refresh_list" and create refresh_list function
        self.refresh_button.place(x=925, y=615)

        self.export_button = tk.Button(self.root, text="Export List", width=10, height = 2, command = Storage.export_button(self)) # Have to add ", command=export_list" and create export_list function
        self.export_button.place(x=1075, y=615)


        # Initializes the frame on the UI
        self.vid_frame = tk.Frame(self.root, bg="darkgray", width=685, height=395)
        self.vid_frame.place(x=50, y=75)
        self.feed_widget = tk.Label(self.root)
        self.feed_widget.place(x=75, y=90)
        
        # Setting up the camera
        self.cap = cv2.VideoCapture(0)
        self.width, self.height = 500, 350  
        # Camera dimensions that stretch in box for macOS is 625w x 350h
        # Camera dimensions that fit in box for macOS is 500w x 350h
        # This is stretched though and should probably fit the window better
        # Maybe a different UI window based on operating system?
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Check if the camera is opened correctly
        if not self.cap.isOpened():
            print("Error: Camera not initialized!")
            messagebox.showerror("Camera Error", "Could not open the camera.")
            return
        
        # Initializes the feed status to false for start_stop_feed to enable
        self.feed_active = False  

        # Initialize FacialRecognition for face detection and recognition
        self.recognition = FacialRecognition(self.cap, self.name_cap)

        # Initialize Storage for handling user data, passing capture and name_cap
        self.storage = Storage(self.cap, self.name_cap, self.recognition)  # Now passing both arguments

        self.start_stop_feed()

    def capture_image(self):
        # Now use the method correctly via `self.storage.take_picture()`
        uid, _ = self.storage.take_picture()
        if uid:
            self.recognition.load_known_faces()

    def open_camera(self):
        #print(self.recognition.known_face_names) # Debug

        if self.feed_active:
            ret, frame = self.cap.read()
            if ret:
                # Resize the frame
                frame = cv2.resize(frame, (self.width, self.height))

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
                #width, height = 325, 200  # Camera dimensions
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
            #Set Background to Dark Mode
            self.root.configure(bg="gray18") 
            #Set Labels to Dark Mode
            self.detect_label.configure(bg='gray60', fg="gray99")
            self.feed_label.configure(bg='gray60', fg="gray99")
            self.name_label.configure(bg='gray60', fg="gray99")
            #Set Frames to Dark Mode
            self.det_people_frame.configure(bg='gray27')
            self.create_user_frame.configure(bg='gray27')
            self.vid_frame.configure(bg='gray27')
            #Set Text Boxes to Dark Mode
            self.detected_people_text.configure(bg='gray60', fg="gray99")
            self.name_cap.configure(bg='gray60', fg="gray99")
            #Set Buttons to Dark Mode
            self.start_button.configure(bg='gray60', fg="gray99")
            self.create_user_button.configure(bg='gray60', fg="gray99")
            self.cap_image_button.configure(bg='gray60', fg="gray99")
            self.refresh_button.configure(bg='gray60', fg="gray99")
            self.export_button.configure(bg='gray60', fg="gray99")
            self.check_dark_mode.configure(bg='gray60', fg="gray99")

        else:
            #Set Background to Light Mode
            self.root.configure(bg="SystemButtonFace")
            #Set Labels to Light Mode
            self.detect_label.configure(bg='SystemButtonFace', fg="black")
            self.feed_label.configure(bg='SystemButtonFace', fg="black")
            self.name_label.configure(bg='SystemButtonFace', fg="black")
            #Set Frames to Light Mode
            self.det_people_frame.configure(bg='darkgray')
            self.create_user_frame.configure(bg='darkgray')
            self.vid_frame.configure(bg='darkgray')
            #Set Text Boxes to Light Mode
            self.detected_people_text.configure(bg='SystemButtonFace', fg="black")
            self.name_cap.configure(bg='SystemButtonFace', fg="black")
            #Set Buttons to Light Mode 
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
