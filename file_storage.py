import os, time, json, cv2, tkinter as tk
from tkinter import messagebox
import face_recognition

IMAGE_DIR = "stored_images" # folder for JPEGs
JSON_PATH = "image_data/user_data.json"
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)

class Storage:
    def __init__(self, capture, name_cap, recognizer=None):
        self.capture  = capture
        self.name_cap = name_cap
        self.recognition = recognizer
        self.storage_dir = IMAGE_DIR

    # ------------------------------------------------------------------ helpers
    def load_metadata(self):
        if os.path.exists(JSON_PATH):
            try:
                with open(JSON_PATH, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass # start fresh if the file is garbled
        return []
    
    def list_images(self):
        """
        Return [(filename, person_name), …] for every image recorded
        in user_data.json.  If the JSON file is empty we return [].
        """
        records = self.load_metadata() # list of dicts
        out = []
        for rec in records:
            fname = os.path.basename(rec["image_path"])
            out.append((fname, rec["name"]))
        return out

    def save_metadata(self, data):
        with open(JSON_PATH, "w") as f:
            json.dump(data, f, indent=4)

    def get_name(self):
        name = self.name_cap.get("1.0", tk.END).strip()
        if not name:
            messagebox.showerror("Name Error", "Please enter a name")
            return None
        return name

    # ------------------------------------------------------------------ main API
    def take_picture(self):
        name = self.get_name()
        if not name:
            return None, None

        uid = str(int(time.time()))
        ok, frame = self.capture.read()
        if not ok:
            messagebox.showerror("Camera Error", "Couldn’t capture a frame.")
            return None, None

        # --- ensure a face exists ------------------------------------------
        if not face_recognition.face_locations(frame):
            messagebox.showwarning("No Face", "No face detected – try again.")
            return None, None

        # --- convert & detect on RGB first -------------------------------
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)        # BGR → RGB
        locs = face_recognition.face_locations(rgb)         # detect on RGB
        if not locs:
            messagebox.showwarning("No Face", "No face detected—try again.")
            return None, None

        # --- save the original BGR frame as JPEG ------------------------
        img_path = os.path.join(IMAGE_DIR, f"user_{uid}.jpg")
        cv2.imwrite(img_path, frame)
        print(f"✔ saved {img_path}")

        # --- encode only those exact RGB boxes --------------------------
        encs = face_recognition.face_encodings(rgb, locs, num_jitters=0)
        if not encs:
            messagebox.showerror("Encode Error", "Face detected but encoding failed.")
            return None, None

        # --- immediately update in‑memory recognizer ----------------------
        self.recognition.known_face_encodings.append(encs[0])
        self.recognition.known_face_names.append(name)

        print(f"✔ saved {img_path}")

        # --- update JSON ----------------------------------------------------
        data = self.load_metadata()
        data.append({"user_id": uid, "name": name, "image_path": img_path})
        self.save_metadata(data)
        print(f"✔ metadata appended → {JSON_PATH}")

        return uid, img_path

    # stubs you can flesh out later
    def refresh_button(self): pass
    def export_button(self):  pass
