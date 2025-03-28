import os
import uuid
import json
import shutil
from typing import Optional

class LocalImageStorage:
    def __init__(self, storage_dir='image_data', metadata_file='metadata.json'):
        self.storage_dir = storage_dir
        self.metadata_file = os.path.join(storage_dir, metadata_file)
        os.makedirs(self.storage_dir, exist_ok=True)
        self._load_metadata()

    def _load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def _save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=4)

    def save_image(self, image_path: str, person_name: str) -> str:
        ext = os.path.splitext(image_path)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        dest_path = os.path.join(self.storage_dir, unique_filename)
        shutil.copy2(image_path, dest_path)

        self.metadata[unique_filename] = person_name
        self._save_metadata()

        return unique_filename

    def get_person_name(self, image_filename: str) -> Optional[str]:
        return self.metadata.get(image_filename)

    def list_images(self):
        return [(fname, self.metadata[fname]) for fname in self.metadata]

    def delete_image(self, image_filename: str) -> bool:
        path = os.path.join(self.storage_dir, image_filename)
        if os.path.exists(path):
            os.remove(path)
            self.metadata.pop(image_filename, None)
            self._save_metadata()
            return True
        return False

# Example usage:
# storage = LocalImageStorage()
# saved_file = storage.save_image('path/to/image.jpg', 'John Doe')
# print(storage.get_person_name(saved_file))
# print(storage.list_images())
