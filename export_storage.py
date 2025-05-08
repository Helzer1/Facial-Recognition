import json
import csv
import os
import datetime

class ExportStorage:
    def __init__(self, recognition_instance, choice):
        self.choice = choice
        self.names = recognition_instance.known_face_names
        self.export_dir = "exported_data"

        # Ensure the export directory exists
        os.makedirs(self.export_dir, exist_ok=True)

    def _generate_filename(self, extension):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.export_dir, f"names_{timestamp}.{extension}")

    def export_to_txt(self, filename=None):
        path = filename or self._generate_filename("txt")
        with open(path, 'w') as f:
            for name in self.names:
                f.write(str(name) + '\n')

    def export_to_csv(self, filename=None):
        path = filename or self._generate_filename("csv")
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            #writer.writerow(["Name"])
            for name in self.names:
                writer.writerow([name])

    def export_to_json(self, filename=None):
        path = filename or self._generate_filename("json")
        with open(path, 'w') as f:
            json.dump(self.names, f, indent=4)
