from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal

class EditStockScreen(QWidget):
    """
    An empty screen for the 'Stok Düzenle' view.
    This is a placeholder for future development.
    """
    back_button_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Stok Düzenle Ekranı")
        title.setStyleSheet("""
            font-size: 72px;
            font-weight: bold;
            color: white;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        self.back_button = QPushButton("Geri")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                border-radius: 10px;
                width: 450px;
                height: 80px;
                border: 2px solid white;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(self.back_button)
        self.setLayout(layout)
        self.back_button.clicked.connect(self.back_button_clicked.emit)
