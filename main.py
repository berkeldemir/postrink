import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QPushButton, QLabel,
    QHBoxLayout, QStackedWidget, QLineEdit,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
import random # Used for mocking a sale ID
import time # Used for mocking a sale ID

# Import shared data from its own module
from data import AppData, DatabaseManager

# Import screen modules
from new_sale import NewSaleScreen, CartScreen, CustomerCartScreen
from view_sales import SalesScreen, WelcomeScreen
from edit_stock import EditStockScreen

class Window1(QMainWindow):
    """
    The main POS window for the employee.
    """
    def __init__(self, controller, second_window):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.controller = controller
        # Store a reference to the second window to control it
        self.second_window = second_window

        # Use a QStackedWidget to manage different views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #111;
            }
            QWidget {
                background-color: #111;
            }
        """)
        
        # --- Main Menu Screen ---
        self.main_menu_widget = self._create_main_menu()
        self.stacked_widget.addWidget(self.main_menu_widget) # Index 0
        
        # --- Other Screens ---
        self.new_sale_screen = NewSaleScreen()
        self.stacked_widget.addWidget(self.new_sale_screen) # Index 1
        
        self.sales_screen = SalesScreen()
        self.stacked_widget.addWidget(self.sales_screen) # Index 2
        
        self.cart_screen = CartScreen()
        self.stacked_widget.addWidget(self.cart_screen) # Index 3

        self.edit_stock_screen = EditStockScreen()
        self.stacked_widget.addWidget(self.edit_stock_screen) # Index 4
        
        # --- Connect signals to screen-switching slots ---
        self.new_sale_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.sales_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.stock_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        self.quit_button.clicked.connect(QApplication.instance().quit)
        
        # Connections for NewSaleScreen
        self.new_sale_screen.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.new_sale_screen.next_button.clicked.connect(self.start_sale_and_show_cart)

        # Connections for other screens
        self.sales_screen.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.cart_screen.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.edit_stock_screen.back_button_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        self.showFullScreen()
        
    def _create_main_menu(self):
        main_menu_widget = QWidget()
        main_menu_layout = QVBoxLayout()
        main_menu_layout.setAlignment(Qt.AlignCenter)

        self.new_sale_button = QPushButton("Yeni Satış")
        self.sales_button = QPushButton("Satışlar")
        self.stock_button = QPushButton("Stoklar")
        self.campaign_button = QPushButton("Kampanyalar")
        self.quit_button = QPushButton("Çıkış")
        
        new_sale_style = """
            QPushButton {
                background-color: #27ae60; 
                border: 2px solid #229954; 
                color: white;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                border-radius: 10px;
                width: 500px;
                height: 80px;
            }
            QPushButton:hover {
                border: 5px solid #999;
            }
        """
        
        sales_style = """
            QPushButton {
                background-color: #f39c12; 
                border: 2px solid #e67e22; 
                color: white;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                border-radius: 10px;
                width: 500px;
                height: 80px;
            }
            QPushButton:hover {
                border: 5px solid #999;
            }
        """

        stock_style = """
            QPushButton {
                background-color: #3498db; 
                border: 2px solid #2980b9; 
                color: white;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                border-radius: 10px;
                width: 500px;
                height: 80px;
            }
            QPushButton:hover {
                border: 5px solid #999;
            }
        """
        campaign_style = """
            QPushButton {
                background-color: #C27D0E; 
                border: 2px solid #c0392b; 
                color: white;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                border-radius: 10px;
                width: 500px;
                height: 80px;
            }
            QPushButton:hover {
                border: 5px solid #999;
            }
        """

        quit_style = """
            QPushButton {
                background-color: #e74c3c; 
                border: 2px solid #c0392b; 
                color: white;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                border-radius: 10px;
                width: 500px;
                height: 80px;
            }
            QPushButton:hover {
                border: 5px solid #999;
            }
        """

        self.new_sale_button.setStyleSheet(new_sale_style)
        self.sales_button.setStyleSheet(sales_style)
        self.stock_button.setStyleSheet(stock_style)
        self.campaign_button.setStyleSheet(campaign_style)
        self.quit_button.setStyleSheet(quit_style)

        self.new_sale_button.setShortcut("n")
        self.sales_button.setShortcut("v")
        self.stock_button.setShortcut("s")
        self.campaign_button.setShortcut("c")
        self.quit_button.setShortcut("q")

        main_menu_layout.addStretch()
        main_menu_layout.addWidget(self.new_sale_button)
        main_menu_layout.addWidget(self.sales_button)
        main_menu_layout.addWidget(self.stock_button)
        main_menu_layout.addWidget(self.campaign_button)
        main_menu_layout.addWidget(self.quit_button)
        main_menu_layout.addStretch()
        
        main_menu_widget.setLayout(main_menu_layout)
        return main_menu_widget

    def start_sale_and_show_cart(self):
        """
        Starts a new sale, stores the customer name and sale ID,
        and then shows the cart screen.
        """
        # Get the customer name from the input field
        customer_name = self.new_sale_screen.name_input.text().strip()
        
        # Perform validation FIRST.
        #if not customer_name:
        #    msg_box = QMessageBox()
        #    msg_box.setWindowTitle("Hata")
        #    msg_box.setText("Lütfen müşteri adını girin.")
        #    msg_box.setIcon(QMessageBox.Warning)
        #    msg_box.exec()
        #    return # Exit the function if validation fails

        # ONLY if validation passes, proceed with updates
        # 1. Update the shared AppData object
        self.controller.curr_customer_name = customer_name
        self.controller.curr_sale_id = self.controller.db.start_new_sale()

        # 2. Refresh the cashier's cart screen with the new data
        self.cart_screen.refresh_data(self.controller)
        
        # 3. Switch the cashier's screen to the cart screen
        self.stacked_widget.setCurrentIndex(3)

        # 4. Refresh the customer screen with the new data and show the cart
        self.second_window.show_cart()

class Window2(QMainWindow):
    """
    The customer-facing display window.
    """
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("Customer Display")
        self.controller = controller
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.setStyleSheet("background-color: #111;")
        
        self.welcome_screen = WelcomeScreen()
        self.stacked_widget.addWidget(self.welcome_screen) #0
        
        from new_sale import CustomerCartScreen
        self.customer_cart_screen = CustomerCartScreen()
        self.stacked_widget.addWidget(self.customer_cart_screen) #1

        self.showFullScreen()
    
    def show_welcome(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_cart(self):
        self.customer_cart_screen.refresh_data(self.controller)
        self.stacked_widget.setCurrentIndex(1)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    data = AppData()

    second_window = Window2(data)
    main_window = Window1(data, second_window)

    main_window.new_sale_button.clicked.connect(second_window.show_welcome)

    main_window.new_sale_screen.back_button.clicked.connect(second_window.show_welcome)
    main_window.sales_screen.back_button.clicked.connect(second_window.show_welcome)
    main_window.cart_screen.back_button.clicked.connect(second_window.show_welcome)
    main_window.edit_stock_screen.back_button_clicked.connect(second_window.show_welcome)

    sys.exit(app.exec())
