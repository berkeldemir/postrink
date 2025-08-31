from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QHBoxLayout, QStackedWidget
)
from PySide6.QtCore import Qt, Signal

class OnHoldOrdersScreen(QWidget):
	back_to_menu = Signal()

	def __init__(self, app_data):
		super().__init__(parent)
		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignCenter)

		title = QLabel("Askıdaki İşlemler:")
		title.setStyleSheet("""
			font-size: 72px;
			font-weight: bold;
			color: white;
		""")
		title.setAlignment(Qt.AlignCenter)

		back_button = QPushButton("Geri")
		back_button.setStyleSheet("""
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
		layout.addWidget(back_button)
		self.setLayout(layout)

		self.back_button = back_button
		self.back_button.clicked.connect(self.back_to_menu.emit)
