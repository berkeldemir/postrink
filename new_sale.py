from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QHBoxLayout, QLineEdit,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal, QDateTime, QTimer
# The AppData import has been moved to a separate data.py file
from data import AppData

class NewSaleScreen(QWidget):
    """
    Screen to capture the customer's name and start a new sale.
    """
    # Define a signal that will be emitted when the 'Devam' button is clicked.
    # This signal carries no data, just indicates a click.
    continue_sale = Signal()
    back_to_menu = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Müşteri Adı:")
        title.setStyleSheet("""
            font-size: 72px;
            font-weight: bold;
            color: white;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("örn: 946 Berk Eldemir")
        self.name_input.setStyleSheet("""
            QLineEdit {
                font-size: 48px;
                padding: 15px;
                background-color: #34495e;
                color: white;
                border: 2px solid white;
                border-radius: 10px;
            }
        """)
        # Set the maximum length of the input to 32 characters
        self.name_input.setMaxLength(32)
        self.name_input.setFixedSize(750, 80)
        
        self.next_button = QPushButton("Devam")
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #55cc55;
                color: white;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                margin-top: 5px;
                border-radius: 10px;
                height: 60px;
                border: 2px solid white;
            }
        """)
        self.back_button = QPushButton("Geri")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                border-radius: 10px;
                height: 60px;
                border: 2px solid white;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(self.name_input)
        layout.addWidget(self.next_button)
        layout.addWidget(self.back_button)
        
        self.setLayout(layout)
        
        # Connect the buttons to the signals
        self.next_button.clicked.connect(self.continue_sale.emit)
        self.back_button.clicked.connect(self.back_to_menu.emit)

class CartScreen(QWidget):
    """
    The main sales screen for the cashier where items will be added.
    """
    back_to_menu = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        
        info_layout = QHBoxLayout()
        info_layout.setAlignment(Qt.AlignTop)

        self.customer_label = QLabel("Müşteri: Yok")
        self.date_time_label = QLabel("Tarih: Yok")
        
        label_style = """
            font-size: 36px;
            color: white;
            padding: 10px;
        """
        self.customer_label.setStyleSheet(label_style)
        self.date_time_label.setStyleSheet(label_style)
        
        info_layout.addWidget(self.customer_label, 1, Qt.AlignLeft)
        info_layout.addStretch(1) # Stretch to push the widgets to the edges
        info_layout.addWidget(self.date_time_label, 1, Qt.AlignRight)

        # Back button
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
        self.back_button.clicked.connect(self.back_to_menu.emit)
        
        layout.addLayout(info_layout)
        layout.addStretch(1) # Add a stretch to push content up
        layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # QTimer to update the date and time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000)

    def update_date_time(self):
        """
        Updates the date_time_label with the current date and time.
        """
        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("dd.MM.yyyy hh:mm:ss")
        self.date_time_label.setText(f"{formatted_datetime}")
    
    def refresh_data(self, app_data: AppData):
        """
        Updates the labels with the latest data from the AppData object.
        """
        self.customer_label.setText(f"Müşteri: {app_data.curr_customer_name}")
        # The date and time are now handled by the QTimer
        self.update_date_time()

class CustomerCartScreen(QWidget):
    """
    The customer-facing cart screen.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        
        info_layout = QHBoxLayout()
        info_layout.setAlignment(Qt.AlignTop)
        
        self.customer_label = QLabel("Hoş geldiniz, ")
        self.date_time_label = QLabel("-")
        
        label_style = """
            font-size: 28px;
            color: white;
            padding: 10px;
            font-weight: bold;
        """
        self.customer_label.setStyleSheet(label_style)
        self.date_time_label.setStyleSheet(label_style)

        info_layout.addWidget(self.customer_label, 1, Qt.AlignLeft)
        info_layout.addStretch(1) # Stretch to push the widgets to the edges
        info_layout.addWidget(self.date_time_label, 1, Qt.AlignRight)
        
        layout.addLayout(info_layout)
        layout.addStretch(1) # Add a stretch to push content up

        self.setLayout(layout)
        
        # QTimer to update the date and time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000)

    def update_date_time(self):
        """
        Updates the date_time_label with the current date and time.
        """
        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("dd.MM.yyyy hh:mm:ss")
        self.date_time_label.setText(f"{formatted_datetime}")
    
    def refresh_data(self, app_data: AppData):
        """
        Updates the labels with the latest data from the AppData object.
        """
        self.customer_label.setText(f"Hoş geldiniz, {app_data.curr_customer_name}")
        # The date and time are now handled by the QTimer
        self.update_date_time()
