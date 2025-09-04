from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from data import AppData

class OnHoldOrdersScreen(QWidget):
    back_to_menu = Signal()
    continue_sale = Signal(str)

    def __init__(self, app_data, parent=None):
        super().__init__(parent)
        self.app_data = app_data

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)

        # Top spacer
        top_spacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(top_spacer)

        # Title
        title = QLabel("Askıdaki İşlemler:")
        title.setStyleSheet("""
            font-size: 72px;
            font-weight: bold;
            color: white;
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Scroll area for sales buttons
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        main_layout.addWidget(self.scroll_area)

        # Container for sales buttons
        self.sales_buttons_container = QVBoxLayout()
        self.sales_buttons_container.setAlignment(Qt.AlignTop)
        container_widget = QWidget()
        container_widget.setLayout(self.sales_buttons_container)
        self.scroll_area.setWidget(container_widget)

        # Back button
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
        back_button.clicked.connect(self.back_to_menu.emit)
        main_layout.addWidget(back_button)
        self.back_button = back_button

        # Bottom spacer
        bottom_spacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(bottom_spacer)

        # Initial load
        self.refresh_onhold_sales()

    def refresh_onhold_sales(self):
        # Clear previous buttons
        for i in reversed(range(self.sales_buttons_container.count())):
            widget = self.sales_buttons_container.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Fetch current on-hold sales
        onhold_sales = self.app_data.database_manager.get_onhold_sales()

        for row in onhold_sales:
            sale_id = row["sale_id"]
            customer_name = row["customer_name"]
            total_amount = row["total_amount"]

            # Create button
            btn = QPushButton(f"{sale_id}\n{customer_name}\n{total_amount:.2f} ₺")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495e;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    padding: 20px;
                    border-radius: 10px;
                    border: 2px solid white;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2c3e50;
                }
            """)
            btn.setFixedSize(500, 120)
            btn.clicked.connect(lambda checked, s=sale_id: self.load_sale(s))
            self.sales_buttons_container.addWidget(btn)

    def load_sale(self, sale_id):
        # Update app_data to point to this sale
        self.app_data.curr_sale_id = sale_id

        # Fetch customer name
        cur = self.app_data.database_manager.conn.cursor()
        cur.execute("SELECT customer_name FROM sales WHERE sale_id = ?", (sale_id,))
        row = cur.fetchone()
        if row:
            self.app_data.curr_customer_name = row["customer_name"]

        print(f"OLD SALE: {sale_id} for {self.app_data.curr_customer_name}")

        # Emit signal to continue sale
        self.continue_sale.emit(sale_id)
