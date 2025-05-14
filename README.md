# Facial Recognition System with MongoDB and GUI

A real-time facial recognition system using Python, OpenCV, and dlib, featuring a Tkinter-based GUI and scalable cloud storage via MongoDB Atlas.

---

## 🔍 Features

- **Live Camera Feed:** Real-time webcam stream with facial detection.
- **Face Recognition:** Match captured faces against stored encodings.
- **MongoDB Cloud Storage:** Stores user face encodings, names, timestamps, and image paths.
- **Export Options:** Export detected users to `.txt`, `.csv`, or `.json` format.
- **Dark Mode UI:** Easily toggle between light and dark themes.

---

## 📦 Technologies Used

- Python 3.8
- [OpenCV](https://opencv.org/)
- [dlib](http://dlib.net/)
- [face_recognition](https://github.com/ageitgey/face_recognition)
- MongoDB Atlas (Cloud NoSQL Database)
- Tkinter (GUI)
- Pillow (image handling)
- `python-dotenv` (environment variable handling)

---

## 🛠️ Setup Instructions

### 1. Clone the Repository


git clone https://github.com/Helzer1/facial-recognition.git
cd facial-recognition

### 2. Create a Virtual Environment

python3.8 -m venv venv
# Activate it:
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

3. Install Requirements

pip install --upgrade pip
pip install -r requirements.txt

4. Add MongoDB Credentials
Create a .env file in the root of the project:

MONGO_URI=your-mongodb-connection-string
⚠️ Never share your actual .env file publicly. You can use .env.example to guide collaborators.

5. Run the Application
python ui.py

🗂️ Project Structure

facial-recognition/
├── ui.py                  # Main GUI application
├── mongo_storage.py       # MongoDB-based storage backend
├── facial_recognition.py  # Core face recognition logic
├── confidence_recognition.py # Adds confidence scores to matches
├── export_storage.py      # Handles export to txt/csv/json
├── requirements.txt
├── .env                   # MongoDB URI (excluded from Git)
├── README.md
