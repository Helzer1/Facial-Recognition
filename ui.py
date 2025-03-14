import tkinter as tk
import cv2
from PIL import Image, ImageTk


#Function for displaying webcam on the UI
def open_camera(): 
    # Capture the video frame by frame 
    _, frame = cap.read() 
  
    # Convert image from one color space to other 
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 
  
    # Capture the latest frame and transform to image 
    captured_image = Image.fromarray(opencv_image) 
  
    # Convert captured image to photoimage 
    photo_image = ImageTk.PhotoImage(image=captured_image) 
  
    # Displaying photoimage in the label 
    feed_widget.photo_image = photo_image 
  
    # Configure image in the label 
    feed_widget.configure(image=photo_image) 
  
    # Repeat the same process after every 10 seconds 
    feed_widget.after(10, open_camera) 



#Function for the Start/Stop button
def startStopFeed(start_button, feed_label):
    global cap
    
    button_text = start_button.cget("text")
    if button_text == "Start Feed":
        feed_label.config(text="Feed On")
        start_button.config(text="Stop Feed")
        open_camera()
   
    else:
        feed_label.config(text="Feed Off")
        start_button.config(text="Start Feed")
        cap.release()
        cv2.destroyAllWindows()
        # Clear the feed_widget image
        feed_widget.config(image='')
        
      
#Create App Window
root = tk.Tk()
root.title("Facial Recognition")
root.geometry("1250x750")

#UI Elements
label = tk.Label(root, text="Detected People:").place(x=1000, y=60)
output_text = tk.Text(root, height=30, width=40).place(x=875, y=80)

start_button = tk.Button(root, text="Start Feed", command=lambda: startStopFeed(start_button, feed_label))
start_button.place(x=350,y=600)

feed_label = tk.Label(root, text="Feed Off")
feed_label.place(x=350, y=50)

frame = tk.Frame(root, bg="lightgray", width=685, height=395).place(x=50, y=75)
#feed = tk.Label(root).place(x=50, y=75)


#Setting up camera for the UI
cap = cv2.VideoCapture(0)
width, height =  450,400 # Width of camera, #Height of Camera 
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) 
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height) 

feed_widget = tk.Label(root) 
feed_widget.place(x=75,y=90) 

#Run application
root.mainloop()
