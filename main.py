import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QListWidget, QFileDialog, QLabel, QLineEdit, QGridLayout,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
import paramiko
from pathlib import Path

class SSHFileUploader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PIP Server Uploader")
        self.setGeometry(100, 100, 600, 500)
        self.setWindowIcon(QIcon("icon.png"))
        self.selected_files = []
        self.init_ui()

    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_widget.setLayout(main_layout)

        # Apply modern stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f4f8;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #007bff;
                background-color: #e6f0fa;
            }
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                background-color: #007bff;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #003d80;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #ffffff;
                padding: 5px;
                font-size: 14px;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 5px;
            }
        """)

        # Server connection inputs
        conn_frame = QFrame()
        conn_frame.setFrameShape(QFrame.Shape.StyledPanel)
        conn_layout = QGridLayout()
        conn_layout.setSpacing(10)
        conn_frame.setLayout(conn_layout)
        main_layout.addWidget(conn_frame)

        # Set modern font
        font = QFont("Arial", 12)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Server Host (e.g., 192.168.1.100)")
        self.host_input.setText("192.168.18.50")
        self.host_input.setFont(font)
        conn_layout.addWidget(QLabel("Host:"), 0, 0)
        conn_layout.addWidget(self.host_input, 0, 1)

        self.username_input = QLineEdit()
        self.username_input.setText("adminit")
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFont(font)
        conn_layout.addWidget(QLabel("Username:"), 1, 0)
        conn_layout.addWidget(self.username_input, 1, 1)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(font)
        conn_layout.addWidget(QLabel("Password:"), 2, 0)
        conn_layout.addWidget(self.password_input, 2, 1)

        self.remote_path_input = QLineEdit()
        self.remote_path_input.setText("/home/adminit/Downloads")  # Set default remote path
        self.remote_path_input.setPlaceholderText("/home/adminit/Downloads")
        self.remote_path_input.setFont(font)
        conn_layout.addWidget(QLabel("Remote Path:"), 3, 0)
        conn_layout.addWidget(self.remote_path_input, 3, 1)

        # File selection button with icon
        self.select_button = QPushButton("Select Files")
        self.select_button.setIcon(QIcon.fromTheme("document-open"))
        self.select_button.clicked.connect(self.select_files)
        self.select_button.setFont(font)
        main_layout.addWidget(self.select_button)

        # File list
        self.file_list = QListWidget()
        self.file_list.setFont(font)
        main_layout.addWidget(self.file_list)

        # Upload button with icon
        self.upload_button = QPushButton("Upload Files")
        self.upload_button.setIcon(QIcon.fromTheme("network-transmit"))
        self.upload_button.clicked.connect(self.upload_files)
        self.upload_button.setFont(font)
        main_layout.addWidget(self.upload_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(font)
        main_layout.addWidget(self.status_label)

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
            self.progress_bar.setValue(0)

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

            # Create remote directory if it doesn't exist
            try:
                sftp.stat(remote_path)
            except FileNotFoundError:
                sftp.mkdir(remote_path)

            # Upload files with progress
            total_files = len(self.selected_files)
            for index, file_path in enumerate(self.selected_files, 1):
                file_name = Path(file_path).name
                remote_file_path = os.path.join(remote_path, file_name)
                sftp.put(file_path, remote_file_path)
                self.status_label.setText(f"Status: Uploaded {file_name}")
                self.progress_bar.setValue(int((index / total_files) * 100))

            sftp.close()
            ssh.close()
            self.status_label.setText("Status: All files uploaded successfully")
            self.progress_bar.setValue(100)

        except Exception as e:
            self.status_label.setText(f"Status: Error - {str(e)}")
            self.progress_bar.setValue(0)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for a modern look
    window = SSHFileUploader()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()