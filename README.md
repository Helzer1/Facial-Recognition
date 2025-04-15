# Facial-Recognition

This project implements a facial recognition system using Python. It includes a GUI for live camera feed display, facial recognition logic, and local file storage for images and metadata. The project leverages libraries such as OpenCV, face_recognition, and dlib.

# Features

- **Live Camera Feed:** View real-time video stream with detected faces.
- **Face Recognition:** Identify known faces using stored encodings.
- **Local File Storage:** Save images along with associated names for future recognition.
- **Modular Design:** Separate modules for UI, facial recognition, and file storage.

# Prerequisites

- **Python 3.8** (recommended for compatibility with dlib and face_recognition)
- 64-bit Python installation

# Setup

Clone the Repository:

    git clone https://github.com/your-username/your-repo.git
    cd your-repo
    Create a Virtual Environment:
        python3.8 -m venv venv

    Activate the Virtual Environment:
        On Windows:
            .\venv\Scripts\activate
        On macOS/Linux:
            source venv/bin/activate

    Be sure to have the latest version of pip installed:
        python -m pip install --upgrade pip

    Install Dependencies:
        pip install -r requirements.txt
        If this is not working then pip may not be up to date. Please install latest version.

    Run the Application:
        python ui.py


    Project Structure
        project_directory/
        ├── file_storage.py         # Module for handling local image storage
        ├── facial_recognition.py   # Module for face detection and recognition logic
        ├── ui.py                   # Tkinter-based GUI for camera feed and recognition display
        ├── requirements.txt        # List of project dependencies
        └── README.md               # This file

    Notes
    dlib: Ensure you have a 64-bit Python installation. Precompiled wheels for dlib are available if you encounter build issues.

    IDE Configuration: If using VS Code, make sure to select the correct Python interpreter for your virtual environment.