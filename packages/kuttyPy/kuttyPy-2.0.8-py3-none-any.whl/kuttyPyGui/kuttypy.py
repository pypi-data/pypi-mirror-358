import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QIcon


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.running_script = None  # Track a single running script
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Playground Button
        self.playground_btn = QPushButton("Playground")
        self.playground_btn.setIcon(QIcon("playground.jpg"))
        self.playground_btn.setIconSize(self.playground_btn.sizeHint() * 2)
        self.playground_btn.setMinimumHeight(60)
        self.playground_btn.clicked.connect(lambda: self.launch_script("KuttyPyPlus.py"))
        layout.addWidget(self.playground_btn)

        # IDE Button with two icons
        ide_layout = QHBoxLayout()
        self.ide_btn = QPushButton("IDE")
        self.ide_btn.setIcon(QIcon("ide.jpg"))
        self.ide_btn.setIconSize(self.ide_btn.sizeHint() * 2)
        self.ide_btn.setMinimumHeight(60)
        self.ide_btn.clicked.connect(lambda: self.launch_script("KuttyPyIDE.py"))
        ide_layout.addWidget(self.ide_btn)

        self.visual_icon = QPushButton()
        self.visual_icon.setIcon(QIcon("visual_coding.jpg"))
        self.visual_icon.setIconSize(self.visual_icon.sizeHint() * 2)
        self.visual_icon.clicked.connect(lambda: self.launch_script("KuttyPyIDE.py"))
        self.visual_icon.setMinimumHeight(60)
        ide_layout.addWidget(self.visual_icon)

        layout.addLayout(ide_layout)

        self.setLayout(layout)
        self.setWindowTitle("Launcher")
        self.show()

    def launch_script(self, script_name):
        if self.running_script:
            if self.running_script["name"] == script_name and self.running_script["process"].poll() is None:
                return  # Ignore click if the same script is already running

            reply = QMessageBox.question(self, "Process Running",
                                         f"Another script ({self.running_script['name']}) is already running. Close it first?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.running_script["process"].terminate()
                self.running_script["process"].wait()
                self.running_script = None
            else:
                return

        try:
            process = subprocess.Popen([sys.executable, script_name])
            self.running_script = {"name": script_name, "process": process}
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error launching {script_name}: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())