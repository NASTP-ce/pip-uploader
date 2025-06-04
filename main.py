import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QListWidget, QFileDialog, QLabel, QLineEdit, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import paramiko
from pathlib import Path

class SSHFileUploader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PIP Server File Uploader")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon("icon.png"))
        self.selected_files = []
        self.init_ui()

    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Server connection inputs
        conn_layout = QGridLayout()
        layout.addLayout(conn_layout)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Server Host")
        conn_layout.addWidget(QLabel("Host:"), 0, 0)
        conn_layout.addWidget(self.host_input, 0, 1)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        conn_layout.addWidget(QLabel("Username:"), 1, 0)
        conn_layout.addWidget(self.username_input, 1, 1)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        conn_layout.addWidget(QLabel("Password:"), 2, 0)
        conn_layout.addWidget(self.password_input, 2, 1)

        self.remote_path_input = QLineEdit()
        self.remote_path_input.setPlaceholderText("/path/to/remote/directory")
        conn_layout.addWidget(QLabel("Remote Path:"), 3, 0)
        conn_layout.addWidget(self.remote_path_input, 3, 1)

        # File selection button
        self.select_button = QPushButton("Select Files")
        self.select_button.clicked.connect(self.select_files)
        layout.addWidget(self.select_button)

        # File list
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # Upload button
        self.upload_button = QPushButton("Upload Files")
        self.upload_button.clicked.connect(self.upload_files)
        layout.addWidget(self.upload_button)

        # Status label
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Upload", "",
            "All Files (*);;Text Files (*.txt);;Images (*.png *.jpg)"
        )
        if files:
            self.selected_files = files
            self.file_list.clear()
            for file in files:
                self.file_list.addItem(file)
            self.status_label.setText(f"Status: {len(files)} files selected")

    def upload_files(self):
        if not self.selected_files:
            self.status_label.setText("Status: No files selected")
            return

        host = self.host_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        remote_path = self.remote_path_input.text()

        if not all([host, username, password, remote_path]):
            self.status_label.setText("Status: Please fill all connection details")
            return

        try:
            # Initialize SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=username, password=password)

            # Initialize SFTP
            sftp = ssh.open_sftp()

            # Upload files
            for file_path in self.selected_files:
                file_name = Path(file_path).name
                remote_file_path = os.path.join(remote_path, file_name)
                sftp.put(file_path, remote_file_path)
                self.status_label.setText(f"Status: Uploaded {file_name}")

            sftp.close()
            ssh.close()
            self.status_label.setText("Status: All files uploaded successfully")

        except Exception as e:
            self.status_label.setText(f"Status: Error - {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = SSHFileUploader()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()