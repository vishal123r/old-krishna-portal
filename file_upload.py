import os
from werkzeug.utils import secure_filename

class UploadHandler:
    def __init__(self, upload_folder):
        # Folder where files will be stored
        self.upload_folder = upload_folder
        self.allowed_extensions = {'xls', 'xlsx'}  # Allowed Excel file types

        # Make sure the upload folder exists
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def allowed_file(self, filename):
        """Check if the uploaded file is allowed."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def save_file(self, file):
        """Save the uploaded file to the specified folder."""
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Secure the filename
            file_path = os.path.join(self.upload_folder, filename)  # Full path for the file
            file.save(file_path)  # Save the file to the folder
            return file_path
        return None
