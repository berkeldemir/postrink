from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QPushButton,
	QLabel, QHBoxLayout, QLineEdit,
	QMessageBox, QScrollArea, QGridLayout,
	QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDateTime, QTimer
from data import AppData

class NewSaleScreen(QWidget):
	"""
	Screen to capture the customer's name and start a new sale.
	"""
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
		self.name_input.textChanged.connect(self._to_uppercase)

	def _to_uppercase(self, text):
		"""Converts the input text to uppercase while preserving the cursor position."""
		cursor_pos = self.name_input.cursorPosition()
		self.name_input.blockSignals(True)
		self.name_input.setText(text.upper())
		self.name_input.blockSignals(False)
		self.name_input.setCursorPosition(cursor_pos)

class CartScreen(QWidget):
	"""
	The main sales screen for the cashier where items will be added and viewed.
	"""
	back_to_menu = Signal()
	item_added = Signal()  # New signal to notify that an item has been added

	def __init__(self, parent=None):
		super().__init__(parent)
		
		# Create a main vertical layout to split the screen in half
		main_layout = QVBoxLayout()
		
		# Top half: Customer name and time
		info_layout = QHBoxLayout()
		info_layout.setAlignment(Qt.AlignTop)
		
		self.customer_label = QLabel("Müşteri: -")
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
		info_layout.addStretch(1)
		info_layout.addWidget(self.date_time_label, 1, Qt.AlignRight)
		
		# QTimer to update the date and time every second
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_date_time)
		self.timer.start(1000)
		
		# Bottom half: Products and cart area
		content_layout = QHBoxLayout()
		
		# Left 1/3 of the bottom half for product buttons
		products_layout_container = QVBoxLayout()
		self.products_container = QWidget()
		self.products_grid_layout = QGridLayout(self.products_container)
		
		self.products_scroll_area = QScrollArea()
		self.products_scroll_area.setWidgetResizable(True)
		self.products_scroll_area.setWidget(self.products_container)
		self.products_scroll_area.setStyleSheet("""
			QScrollArea {
				border: 2px solid #111;
				border-radius: 10px;
				text-align: left;
				background-color: #333;
			}
		""")
		products_layout_container.addWidget(self.products_scroll_area)

		# Middle section: Cart items
		cart_layout_container = QVBoxLayout()
		
		self.cart_items_layout = QVBoxLayout()
		self.cart_items_layout.setAlignment(Qt.AlignTop)
		
		self.cart_scroll_area = QScrollArea()
		self.cart_scroll_area.setWidgetResizable(True)
		cart_items_widget = QWidget()
		cart_items_widget.setLayout(self.cart_items_layout)
		self.cart_scroll_area.setWidget(cart_items_widget)
		self.cart_scroll_area.setStyleSheet("""
			QScrollArea {
				border: 2px solid #111;
				border-radius: 10px;
				background-color: #333;
			}
		""")
		cart_layout_container.addWidget(self.cart_scroll_area)
		
		# Right 2/3 of the bottom half for the cart (placeholder)
		buttons_layout = QVBoxLayout()
		
		self.back_button = QPushButton("Askıya Al")
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

		self.cancel_button = QPushButton("İptal")
		self.cancel_button.setStyleSheet("""
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
		self.cash_button = QPushButton("Nakit")
		self.cash_button.setStyleSheet("""
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
		self.iban_button = QPushButton("IBAN")
		self.iban_button.setStyleSheet("""
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
		self.back_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		buttons_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)
		self.cancel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		buttons_layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)
		self.cash_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		buttons_layout.addWidget(self.cash_button, alignment=Qt.AlignCenter)
		self.iban_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		buttons_layout.addWidget(self.iban_button, alignment=Qt.AlignCenter)
		
		buttons_layout.addStretch(1)

		# Add the three sub-layouts to the main content layout
		content_layout.addLayout(products_layout_container, 3) # Make left part take up 3/8 of the space
		content_layout.addLayout(cart_layout_container, 3) # Make middle part take up 3/8
		content_layout.addLayout(buttons_layout, 2) # Make right part take up 2/8

		# Add the info and content layouts to the main vertical layout with adjusted stretch factors
		main_layout.addLayout(info_layout)
		main_layout.addLayout(content_layout, 1)
		self.setLayout(main_layout)

	def update_date_time(self):
		"""
		Updates the date_time_label with the current date and time.
		"""
		current_datetime = QDateTime.currentDateTime()
		formatted_datetime = current_datetime.toString("dd.MM.yyyy hh:mm:ss")
		self.date_time_label.setText(f"{formatted_datetime}")

	def refresh_data(self, app_data: AppData):
		"""
		Updates the labels with the latest data from the AppData object and loads product buttons.
		"""
		self.customer_label.setText(f"Müşteri: {app_data.curr_customer_name}")
		self.update_date_time()
		self.load_products(app_data)
		self.refresh_cart_items(app_data)

	def wrap_text(self, text, max_chars=15):
		words = text.split(' ')
		lines = []
		current_line = ''
		for word in words:
			if len(current_line + ' ' + word) > max_chars:
				lines.append(current_line)
				current_line = word
			else:
				if current_line:
					current_line += ' ' + word
				else:
					current_line = word
		lines.append(current_line)
		return '\n'.join(lines)
		
	def load_products(self, app_data: AppData):
		"""
		Fetches products from the database and creates buttons for each one.
		"""
		# Clear existing buttons
		for i in reversed(range(self.products_grid_layout.count())):
			widget_to_remove = self.products_grid_layout.itemAt(i).widget()
			if widget_to_remove is not None:
				widget_to_remove.setParent(None)

		products = app_data.database_manager.get_all_products()
		
		row = 0
		col = 0
		for product in products:
			# Convert the sqlite3.Row object to a dictionary to use .get()
			product_dict = dict(product)
			item_name = product_dict.get('item_name', 'Bilinmeyen Ürün')
			
			item_button = QPushButton("")
			wrapped_name = self.wrap_text(item_name, 15)
			item_button.setText(wrapped_name)

				
			item_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
			#item_button.setWordWrap(True)
			item_button.setStyleSheet("""
				QPushButton {
					background-color: #2c3e50;
					color: white;
					font-size: 32px;
					font-weight: bold;
					border: 2px solid #555;
					border-radius: 10px;
				}
				QPushButton:hover {
					background-color: #34495e;
				}
			""")
			
			item_button.clicked.connect(lambda _, id=product['item_id'], ad=app_data: self.handle_product_click(id, ad))
			self.products_grid_layout.addWidget(item_button, row, col)
			col += 1
			if col > 1: # 2 columns
				col = 0
				row += 1

	def handle_product_click(self, item_id, app_data:AppData):
		# Call the database method and check if successful
		if app_data.database_manager.add_item_to_cart(app_data.curr_sale_id, item_id, 1, 0, 0):
			# If successful, refresh the cart on this screen
			self.refresh_cart_items(app_data)
			# Emit a signal to tell other parts of the app to also refresh
			self.item_added.emit()
			
	def refresh_cart_items(self, app_data: AppData):
		"""
		Clears and reloads cart items from the database to display on this screen.
		"""
		# 1. Clear old widgets
		while self.cart_items_layout.count():
			child = self.cart_items_layout.takeAt(0)
			if child.widget():
				child.widget().deleteLater()

		# 2. Fetch latest items
		cart_items = app_data.database_manager.get_cart_items(app_data.curr_sale_id)

		# 3. Populate layout with new items
		for i, item in enumerate(cart_items):
			item_row_widget = QWidget()
			item_row_widget.setStyleSheet("""
				QWidget {
					background-color: #2c3e50;
					margin: 0px 0px 0px 0px;
					color: white;
					border: .3px solid white;
					border-radius: 5px;
					margin-bottom: 5px;
				}
			""")
			
			item_row_layout = QHBoxLayout(item_row_widget)
			item_row_layout.setContentsMargins(5, 5, 5, 5)

			item_number_lbl = QLabel(f"{item['item_count']}")
			item_number_lbl.setStyleSheet("font-size: 28px; font-weight: bold; min-width: 42px;")
			item_number_lbl.setAlignment(Qt.AlignLeft)

			item_name_lbl = QLabel(f"{item['item_name']}")
			item_name_lbl.setStyleSheet("font-size: 28px;")
			item_name_lbl.setAlignment(Qt.AlignLeft)

			item_price_lbl = QLabel(f"{item['item_total'] + item['item_discount_num']} TL")
			item_price_lbl.setStyleSheet("font-size: 28px; font-weight: bold; min-width: 64px;")
			item_price_lbl.setAlignment(Qt.AlignRight)

			item_row_layout.addWidget(item_number_lbl)
			item_row_layout.addSpacing(10)
			item_row_layout.addWidget(item_name_lbl, 1) # Set stretch to expand
			item_row_layout.addWidget(item_price_lbl)
			
			self.cart_items_layout.addWidget(item_row_widget)

		item_row_widget = QWidget()
		item_row_widget.setStyleSheet("""
			QWidget {
				background-color: #2c3e50;
				margin: 0px 0px 0px 0px;
				color: white;
				border: .3px solid white;
				border-radius: 5px;
				margin-bottom: 5px;
			}
		""")

		# --- disc row ---
		disc_row = QWidget()
		disc_row.setStyleSheet("""
			QWidget {
				background-color: #3e502c;
				margin: 0px 0px 0px 0px;
				color: white;
				border: .3px solid white;
				border-radius: 5px;
				margin-bottom: 5px;
			}
		""")
		disc_layout = QHBoxLayout(disc_row)
		disc_layout.setContentsMargins(5, 5, 5, 5)

		disc_layout.addWidget(QLabel(""), 0)
		disc_label = QLabel("İNDİRİM:")
		disc_label.setStyleSheet("font-size: 28px;")
		disc_layout.addWidget(disc_label, 1)

		discount = app_data.database_manager.total_discount_num(app_data.curr_sale_id)
		disc_price = QLabel(f"{discount} TL")
		disc_price.setStyleSheet("font-size: 28px; font-weight: bold; min-width: 64px;")
		disc_layout.addWidget(disc_price)

		self.cart_items_layout.addWidget(disc_row)

		# --- TOTAL row ---
		total_row = QWidget()
		total_row.setStyleSheet(disc_row.styleSheet())
		total_layout = QHBoxLayout(total_row)
		total_layout.setContentsMargins(5, 5, 5, 5)

		total_layout.addWidget(QLabel(""), 0)
		total_label = QLabel("TOTAL:")
		total_label.setStyleSheet("font-size: 28px;")
		total_layout.addWidget(total_label, 1)

		total_amount = app_data.database_manager.total_amount_calculator(app_data.curr_sale_id)
		total_price = QLabel(f"{total_amount} TL")
		total_price.setStyleSheet("font-size: 28px; font-weight: bold; min-width: 64px;")
		total_layout.addWidget(total_price)

		self.cart_items_layout.addWidget(total_row)

class CustomerCartScreen(QWidget):
	"""
	The customer-facing cart screen.
	"""
	def __init__(self, app_data: AppData):
		super().__init__()

		self.app_data = app_data  # keep reference for later

		layout = QVBoxLayout()

		# --- Top info bar ---
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
		info_layout.addStretch(1)
		info_layout.addWidget(self.date_time_label, 1, Qt.AlignRight)

		layout.addLayout(info_layout)

		# --- Cart items area ---
		self.cart_layout = QVBoxLayout()
		self.cart_layout.setAlignment(Qt.AlignTop)

		self.cart_scroll_area = QScrollArea()
		self.cart_scroll_area.setWidgetResizable(True)
		cart_items_widget = QWidget()
		cart_items_widget.setLayout(self.cart_layout)
		self.cart_scroll_area.setWidget(cart_items_widget)
		self.cart_scroll_area.setStyleSheet("""
			QScrollArea {
				border: 2px solid #111;
				border-radius: 10px;
				background-color: #333;
			}
		""")

		layout.addWidget(self.cart_scroll_area)

		self.setLayout(layout)

		# --- Timer to update datetime ---
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_date_time)
		self.timer.start(1000)

		# Initial load
		self.refresh_data(app_data)

	def update_date_time(self):
		"""Updates the date_time_label with the current date and time."""
		current_datetime = QDateTime.currentDateTime()
		formatted_datetime = current_datetime.toString("dd.MM.yyyy hh:mm:ss")
		self.date_time_label.setText(formatted_datetime)

	def refresh_data(self, app_data: AppData):
		"""Refresh both labels and cart items."""
		self.customer_label.setText(f"Hoş geldiniz, {app_data.curr_customer_name}")
		self.update_date_time()
		self.refresh_cart_items(app_data)

	def refresh_cart_items(self, app_data: AppData):
		"""Clear and reload cart items from the database."""
		# 1. Clear old widgets
		while self.cart_layout.count():
			child = self.cart_layout.takeAt(0)
			if child.widget():
				child.widget().deleteLater()

		# 2. Fetch latest items
		cart_items = app_data.database_manager.get_cart_items(app_data.curr_sale_id)

		# 3. Populate layout with new items in a rectangular format
		for i, item in enumerate(cart_items):
			item_row_widget = QWidget()
			item_row_widget.setStyleSheet("""
				QWidget {
					background-color: #2c3e50;
					color: white;
					border: .3px solid white;
					border-radius: 5px;
					margin-bottom: 5px;
				}
			""")
			
			item_row_layout = QHBoxLayout(item_row_widget)
			item_row_layout.setContentsMargins(10, 5, 10, 5)

			item_number_lbl = QLabel(f"{item['item_count']}")
			item_number_lbl.setStyleSheet("font-size: 48px; font-weight: bold; min-width: 56px;")

			item_name_lbl = QLabel(f"{item['item_name']}")
			item_name_lbl.setStyleSheet("font-size: 48px;")

			item_price_lbl = QLabel(f"{item['item_total'] + item['item_discount_num']} TL")
			item_price_lbl.setStyleSheet("font-size: 48px; font-weight: bold; min-width: 96px;")
			item_price_lbl.setAlignment(Qt.AlignRight)

			item_row_layout.addWidget(item_number_lbl)
			item_row_layout.addSpacing(10)
			item_row_layout.addWidget(item_name_lbl, 1)
			item_row_layout.addWidget(item_price_lbl)
			
			self.cart_layout.addWidget(item_row_widget)
		# --- Discount row ---
		disc_row = QWidget()
		disc_row.setStyleSheet("""
			QWidget {
				background-color: #3e502c;
				color: white;
				border: .3px solid white;
				border-radius: 5px;
				margin-bottom: 5px;
			}
		""")
		disc_layout = QHBoxLayout(disc_row)
		disc_layout.setContentsMargins(10, 5, 10, 5)

		disc_label = QLabel("İNDİRİM:")
		disc_label.setStyleSheet("font-size: 48px;")
		disc_layout.addWidget(disc_label, 1)

		discount = app_data.database_manager.total_discount_num(app_data.curr_sale_id)
		disc_price = QLabel(f"{discount} TL")
		disc_price.setStyleSheet("font-size: 48px; font-weight: bold; min-width: 96px;")
		disc_price.setAlignment(Qt.AlignRight)
		disc_layout.addWidget(disc_price)

		self.cart_layout.addWidget(disc_row)

		# --- Total row ---
		total_row = QWidget()
		total_row.setStyleSheet("""
			QWidget {
				background-color: #3e502c;
				color: white;
				border: .3px solid white;
				border-radius: 5px;
				margin-bottom: 5px;
			}
		""")
		total_layout = QHBoxLayout(total_row)
		total_layout.setContentsMargins(10, 5, 10, 5)

		total_label = QLabel("TOTAL:")
		total_label.setStyleSheet("font-size: 48px;")
		total_layout.addWidget(total_label, 1)

		total_amount = app_data.database_manager.total_amount_calculator(app_data.curr_sale_id)
		total_price = QLabel(f"{total_amount} TL")
		total_price.setStyleSheet("font-size: 48px; font-weight: bold; min-width: 96px;")
		total_price.setAlignment(Qt.AlignRight)
		total_layout.addWidget(total_price)

		self.cart_layout.addWidget(total_row)
		scroll_bar = self.cart_scroll_area.verticalScrollBar()
		scroll_bar.setValue(scroll_bar.maximum() + 50)