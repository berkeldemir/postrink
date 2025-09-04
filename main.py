### main.py

import sys
from PySide6.QtWidgets import (
	QApplication, QMainWindow, QWidget,
	QVBoxLayout, QPushButton, QLabel,
	QHBoxLayout, QStackedWidget, QLineEdit,
	QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal
import random 
import time

from data import AppData, DatabaseManager

from new_sale import NewSaleScreen, CartScreen, CustomerCartScreen
from view_sales import SalesScreen, WelcomeScreen
from edit_stock import EditStockScreen
from onhold_orders import OnHoldOrdersScreen

class Window1(QMainWindow):
	"""
	The main POS window for the employee.
	"""
	def __init__(self, controller, second_window):
		super().__init__()
		self.setWindowTitle("Main Window")
		self.controller = controller
		self.second_window = second_window

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
		
		self.main_menu_widget = self._create_main_menu()
		self.stacked_widget.addWidget(self.main_menu_widget)
		
		self.new_sale_screen = NewSaleScreen()
		self.stacked_widget.addWidget(self.new_sale_screen)
		
		self.sales_screen = SalesScreen()
		self.stacked_widget.addWidget(self.sales_screen)
		
		self.cart_screen = CartScreen()
		self.stacked_widget.addWidget(self.cart_screen)

		self.edit_stock_screen = EditStockScreen()
		self.stacked_widget.addWidget(self.edit_stock_screen)

		self.onhold_screen = OnHoldOrdersScreen(controller)
		self.stacked_widget.addWidget(self.onhold_screen)
		
		self.new_sale_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
		self.sales_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
		self.stock_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
		self.onhold_button.clicked.connect(lambda: [
			self.onhold_screen.refresh_onhold_sales(),
			self.stacked_widget.setCurrentIndex(5)
		])
		self.quit_button.clicked.connect(QApplication.instance().quit)
		
		self.new_sale_screen.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
		self.new_sale_screen.next_button.clicked.connect(self.start_sale_and_show_cart)

		self.sales_screen.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
		self.cart_screen.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
		self.onhold_screen.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
		self.onhold_screen.continue_sale.connect(self.continue_sale)
		self.cart_screen.cancel_button.clicked.connect(self.handle_cancel)
		#self.cart_screen.cancel_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
		self.edit_stock_screen.back_button_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

		# Connect the cart screen's item_added signal to the customer display update
		self.cart_screen.item_added.connect(self.second_window.show_cart)

		# Connect the new payment buttons to their handlers
		self.cart_screen.cash_button.clicked.connect(self.handle_cash_payment)
		self.cart_screen.iban_button.clicked.connect(self.handle_iban_payment)

		self.showFullScreen()

	def handle_cash_payment(self):
		"""Handles the cash payment and completes the sale."""
		if self.controller.curr_sale_id:
			self.controller.database_manager.update_sale_payment_info(self.controller.curr_sale_id, "Nakit")
			self.stacked_widget.setCurrentIndex(0)
			self.second_window.show_welcome()

	def handle_iban_payment(self):
		"""Handles the IBAN payment and gets sender info."""
		if self.controller.curr_sale_id:
			sender_name, ok = QInputDialog.getText(self, "IBAN Bilgisi", "Göndericinin Adı:")
			if ok and sender_name:
				self.controller.database_manager.update_sale_payment_info(self.controller.curr_sale_id, "IBAN", sender_name)
				self.stacked_widget.setCurrentIndex(0)
				self.second_window.show_welcome()
			else:
				# Handle the case where the user cancels the input or enters nothing
				msg_box = QMessageBox()
				msg_box.setWindowTitle("Uyarı")
				msg_box.setText("IBAN işlemi iptal edildi veya gönderici adı girilmedi.")
				msg_box.setIcon(QMessageBox.Warning)
				msg_box.exec()

	def handle_cancel(self):
		self.controller.database_manager.remove_cart_of_sale(self.controller.curr_sale_id)
		self.stacked_widget.setCurrentIndex(0)
		self.second_window.show_welcome()

	def _create_main_menu(self):
		main_menu_widget = QWidget()
		main_menu_layout = QVBoxLayout()
		main_menu_layout.setAlignment(Qt.AlignCenter)

		self.new_sale_button = QPushButton("Yeni Satış")
		self.sales_button = QPushButton("Satışlar")
		self.stock_button = QPushButton("Stoklar")
		self.onhold_button = QPushButton("Askıdakiler")
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
		onhold_style = """
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
		self.onhold_button.setStyleSheet(onhold_style)
		self.quit_button.setStyleSheet(quit_style)

		self.new_sale_button.setShortcut("n")
		self.sales_button.setShortcut("v")
		self.stock_button.setShortcut("s")
		self.onhold_button.setShortcut("o")
		self.quit_button.setShortcut("q")

		main_menu_layout.addStretch()
		main_menu_layout.addWidget(self.new_sale_button)
		main_menu_layout.addWidget(self.sales_button)
		main_menu_layout.addWidget(self.stock_button)
		main_menu_layout.addWidget(self.onhold_button)
		main_menu_layout.addWidget(self.quit_button)
		main_menu_layout.addStretch()
		
		main_menu_widget.setLayout(main_menu_layout)
		return main_menu_widget

	def start_sale_and_show_cart(self):
		"""
		Starts a new sale, stores the customer name and sale ID,
		and then shows the cart screen.
		"""
		customer_name = self.new_sale_screen.name_input.text().strip()
		
		if not customer_name:
			msg_box = QMessageBox()
			msg_box.setWindowTitle("Hata")
			msg_box.setText("Lütfen müşteri adını girin.")
			msg_box.setIcon(QMessageBox.Warning)
			msg_box.exec()
			return

		self.controller.curr_customer_name = customer_name
		self.controller.curr_sale_id = self.controller.database_manager.start_new_sale(customer_name)

		# Refresh both the employee and customer cart screens when a new sale starts
		self.cart_screen.refresh_data(self.controller)
		self.stacked_widget.setCurrentIndex(3)
		self.second_window.show_cart()

	def continue_sale(self, selected_id):
		try:
			cursor = self.controller.database_manager.conn.cursor()
			cursor.execute("""
				SELECT customer_name FROM
				sales
				WHERE sale_id = ?
			""", (selected_id, ))
			cust_name = cursor.fetchone()
			if cust_name:
				self.controller.curr_customer_name = cust_name[0]
			else:
				print(f"Sale {selected_id} not found in sales table!")
				return
			self.controller.curr_customer_name = cust_name[0]
			self.controller.curr_sale_id = selected_id
			self.cart_screen.refresh_data(self.controller)
			self.stacked_widget.setCurrentIndex(3)
			self.second_window.show_cart()
		except Exception as e:
			print(f"ERROR   : {e}")

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
		self.stacked_widget.addWidget(self.welcome_screen)
		
		from new_sale import CustomerCartScreen
		self.customer_cart_screen = CustomerCartScreen(controller)
		self.stacked_widget.addWidget(self.customer_cart_screen)

		self.showFullScreen()
	
	def show_welcome(self):
		self.stacked_widget.setCurrentIndex(0)

	def show_cart(self):
		# This method is now called whenever the main cart is updated
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
