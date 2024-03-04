import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import oracledb
import re


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setFixedHeight(300)
        self.setFixedWidth(300)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.show_registration)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        # Handle login button click here
        username = self.username_input.text()
        password = self.password_input.text()

        # Check login credentials in the database
        if self.check_login(username, password):
            cursor = connection.cursor()

            query = "SELECT account_id FROM ACCOUNTS WHERE USERNAME = :username AND ACCOUNT_PASSWORD = :password"
            cursor.execute(query, {'username': username, 'password': password})
            userID = cursor.fetchone()

            print("Login successful!")

            query = "SELECT type FROM ACCOUNTS WHERE USERNAME = :username AND ACCOUNT_PASSWORD = :password"
            cursor.execute(query, {'username': username, 'password': password})
            result = cursor.fetchone()

            if(result[0] == 'CUSTOMER'):
                widget.setCurrentIndex(widget.currentIndex() + 2)
            else:
                widget.setCurrentIndex(widget.currentIndex() + 4)
        else:
            self.show_error_prompt("Username or password incorrect")

    def check_login(self, username, password):
        cursor = connection.cursor()

        # Execute a query to check login credentials
        query = "SELECT COUNT(*) FROM ACCOUNTS WHERE USERNAME = :username AND ACCOUNT_PASSWORD = :password"
        cursor.execute(query, {'username': username, 'password': password})

        result = cursor.fetchone()
        return result[0] > 0  # If count > 0, credentials are valid

    def show_registration(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def show_error_prompt(self, message):
        error_prompt = QMessageBox()
        error_prompt.setIcon(QMessageBox.Warning)
        error_prompt.setText(message)
        error_prompt.setWindowTitle("Error")
        error_prompt.exec_()


class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Registration")
        self.setFixedHeight(500)
        self.setFixedWidth(300)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create widgets for registration interface
        self.password_label = QLabel("Password:")
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.username_label = QLabel('Username:')
        self.username_entry = QLineEdit()
        self.email_label = QLabel('Email:')
        self.location_label = QLabel('County:')
        self.email_entry = QLineEdit()
        self.county_entry = QLineEdit()
        self.city_entry = QLineEdit()
        self.street_entry = QLineEdit()
        self.street_number_entry = QLineEdit()
        self.register_button = QPushButton('Register')
        self.city_label = QLabel('City:')
        self.street_label = QLabel('Street:')
        self.street_number_label = QLabel('Street number:')

        # Create layout for registration interface
        registration_layout = QVBoxLayout()
        registration_layout.addWidget(self.username_label)
        registration_layout.addWidget(self.username_entry)
        registration_layout.addWidget(self.password_label)
        registration_layout.addWidget(self.password_entry)
        registration_layout.addWidget(self.email_label)
        registration_layout.addWidget(self.email_entry)
        registration_layout.addWidget(self.location_label)
        registration_layout.addWidget(self.county_entry)
        registration_layout.addWidget(self.city_label)
        registration_layout.addWidget(self.city_entry)
        registration_layout.addWidget(self.street_label)
        registration_layout.addWidget(self.street_entry)
        registration_layout.addWidget(self.street_number_label)
        registration_layout.addWidget(self.street_number_entry)
        registration_layout.addWidget(self.register_button)

        self.register_button.clicked.connect(self.register)

        self.setLayout(registration_layout)

    def register(self):
        # Get values from input fields
        username = self.username_entry.text()
        password = self.password_entry.text()
        email = self.email_entry.text()
        county = self.county_entry.text()
        city = self.city_entry.text()
        street = self.street_entry.text()
        street_number = self.street_number_entry.text()

        # Check conditions for registration
        if (
                len(username) > 5
                and len(password) > 5
                and all(location != "" for location in [county, city, street, street_number])
                and re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)
        ):
            if self.perform_registration(username, password, email, county, city, street, street_number):
                print("Registration successful!")
                self.show_info_prompt("Registration successful!")
                widget.setCurrentIndex(widget.currentIndex() - 1)
            else:
                self.show_error_prompt("Error inserting into the database.")
        else:
            # Display appropriate prompt
            error_message = "Invalid registration details. Please ensure:\n"
            error_message += "- Username and password are each at least 6 characters long.\n"
            error_message += "- All location fields are filled.\n"
            error_message += "- Email is in a valid format."
            self.show_error_prompt(error_message)

    def perform_registration(self, username, password, email, county, city, street, street_number):
        try:
            cursor = connection.cursor()

            # Get the next available account_id
            cursor.execute("SELECT MAX(account_id) FROM ACCOUNTS")
            result = cursor.fetchone()
            next_account_id = result[0] + 1 if result[0] is not None else 1

            # Insert into the ACCOUNTS table
            cursor.execute("""
                INSERT INTO ACCOUNTS (account_id, type, username, account_password, email)
                VALUES (:account_id, 'CUSTOMER', :username, :password, :email)
            """, {'account_id': next_account_id, 'username': username, 'password': password, 'email': email})

            # Get the next available location_id
            cursor.execute("SELECT MAX(location_id) FROM LOCATIONS")
            result = cursor.fetchone()
            next_location_id = result[0] + 1 if result[0] is not None else 1

            # Insert into the LOCATIONS table
            cursor.execute("""
                INSERT INTO LOCATIONS (location_id, customer_id, county, city, street, street_number)
                VALUES (:location_id, :customer_id, :county, :city, :street, :street_number)
            """, {'location_id': next_location_id, 'customer_id': next_account_id,
                  'county': county, 'city': city, 'street': street, 'street_number': street_number})

            # Commit the transaction
            connection.commit()

            return True
        except oracledb.Error as error:
            print(f"Error performing registration: {error}")
            return False

    def show_error_prompt(self, message):
        error_prompt = QMessageBox()
        error_prompt.setIcon(QMessageBox.Warning)
        error_prompt.setText(message)
        error_prompt.setWindowTitle("Error")
        error_prompt.exec_()


class ItemListApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Create the main layout
        main_layout = QHBoxLayout()

        # Create a table widget
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(4)  # Removed one column for "Item ID"
        self.table_widget.setHorizontalHeaderLabels(["Name", "Manufacturer", "Stock", "Price Per Unit"])

        # Populate the table with data from the database
        self.populate_table()

        # Create a vertical layout for combo box, text box, label, order button, and change location button
        right_layout = QVBoxLayout()

        # Create a horizontal layout for combo box and text box
        combo_amount_layout = QHBoxLayout()

        # Create a combo box for product names
        self.name_combo = QComboBox(self)
        self.populate_combo()

        # Create a label for the text box
        amount_label = QLabel("Amount:", self)

        # Create a text box for entering the amount
        self.amount_edit = QLineEdit(self)

        # Add the combo box and text box to the horizontal layout
        combo_amount_layout.addWidget(self.name_combo)
        combo_amount_layout.addWidget(amount_label)
        combo_amount_layout.addWidget(self.amount_edit)

        # Create a button for ordering
        self.order_button = QPushButton("Order", self)
        self.order_button.clicked.connect(self.order_button_clicked)

        # Create a button for changing location
        self.change_location_button = QPushButton("Change Location", self)
        self.change_location_button.clicked.connect(self.change_location_button_clicked)

        # Add the horizontal layout, order button, and change location button to the vertical layout
        right_layout.addLayout(combo_amount_layout)
        right_layout.addWidget(self.order_button)
        right_layout.addWidget(self.change_location_button)

        # Add the table widget and the vertical layout to the main layout
        main_layout.addWidget(self.table_widget)
        main_layout.addLayout(right_layout)

        # Set the main layout for the window
        self.setLayout(main_layout)

        # Set window properties
        self.setWindowTitle('Item List')
        self.setGeometry(300, 300, 800, 400)

    def populate_table(self):
        # Assume `connection` is a valid database connection
        cursor = connection.cursor()

        # Execute a query to retrieve items from the database
        cursor.execute("SELECT name, manufacturer, stock, price_per_unit FROM INVENTORY")
        items = cursor.fetchall()

        # Set the number of rows in the table
        self.table_widget.setRowCount(len(items))

        # Populate the table with data
        for row, item in enumerate(items):
            for col, value in enumerate(item):
                item_data = QTableWidgetItem(str(value))
                self.table_widget.setItem(row, col, item_data)

    def populate_combo(self):

        self.name_combo.clear()

        for row in range(self.table_widget.rowCount()):
            name_item = self.table_widget.item(row, 0)
            if name_item is not None:
                self.name_combo.addItem(name_item.text())

    def show_error_prompt(self, message):
        error_prompt = QMessageBox()
        error_prompt.setIcon(QMessageBox.Warning)
        error_prompt.setText(message)
        error_prompt.setWindowTitle("Error")
        error_prompt.exec_()

    def order_button_clicked(self):
        # Simulate order button click
        selected_product = self.name_combo.currentText()
        order_amount = self.amount_edit.text()
        cursor = connection.cursor()

        # Execute a query to check login credentials
        query = "SELECT STOCK FROM INVENTORY WHERE NAME = :productname"
        cursor.execute(query, {'productname': selected_product})
        result = cursor.fetchone()

        if int(order_amount) < result[0]:

            # obtain next id
            cursor.execute("SELECT MAX(order_id) FROM ORDERS")
            result = cursor.fetchone()
            next_order_id = result[0] + 1 if result[0] is not None else 1

            # obtain item id
            query = "SELECT item_id FROM INVENTORY WHERE NAME = :productname"
            cursor.execute(query, {'productname': selected_product})
            result = cursor.fetchone()
            ordereditem_id = result[0]

            query = "INSERT INTO ORDERS(order_id, ordered_item_id, order_amount, order_destination_id, order_date, customer_id) VALUES (:next_order_id, :ordereditem_id, :order_amount, :userID, SYSDATE,:userID)"
            cursor.execute(query, {'next_order_id': next_order_id, 'ordereditem_id': ordereditem_id,
                                   'order_amount': int(order_amount),
                                   'userID': userID})

            connection.commit()

            print("Order set succesfully")

        else:
            self.show_error_prompt("Demand exceeds stock")

    def change_location_button_clicked(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)


class locationChange(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Create the main layout
        layout = QVBoxLayout()

        # Create text boxes for County, City, Street, and Street Number
        self.county_edit = QLineEdit(self)
        self.city_edit = QLineEdit(self)
        self.street_edit = QLineEdit(self)
        self.street_number_edit = QLineEdit(self)

        # Add labels for better clarity
        layout.addWidget(QLabel("County:"))
        layout.addWidget(self.county_edit)

        layout.addWidget(QLabel("City:"))
        layout.addWidget(self.city_edit)

        layout.addWidget(QLabel("Street:"))
        layout.addWidget(self.street_edit)

        layout.addWidget(QLabel("Street Number:"))
        layout.addWidget(self.street_number_edit)

        # Create a button for committing changes
        commit_button = QPushButton("Commit Changes", self)
        commit_button.clicked.connect(self.commit_changes_clicked)

        # Add the button to the layout
        layout.addWidget(commit_button)

        # Set the main layout for the window
        self.setLayout(layout)

        # Set window properties
        self.setWindowTitle('Location Change')
        self.setGeometry(400, 400, 300, 200)

    def commit_changes_clicked(self):
        # Add your logic for handling the "Commit Changes" button click
        county = self.county_edit.text()
        city = self.city_edit.text()
        street = self.street_edit.text()
        street_number = int(self.street_number_edit.text())

        cursor = connection.cursor()
        query = "UPDATE LOCATIONS SET county = :county, city = :city, street = :street, street_number = :street_number WHERE customer_id = :userID"
        cursor.execute(query, {'county': county, 'city': city, 'street': street, 'street_number': street_number,
                               'userID': userID})

        connection.commit()

        widget.setCurrentIndex(widget.currentIndex() - 1)


class adminPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Create the main layout
        main_layout = QHBoxLayout()

        # Create a table widget
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(4)  # Removed one column for "Item ID"
        self.table_widget.setHorizontalHeaderLabels(["Name", "Manufacturer", "Stock", "Price Per Unit"])

        # Populate the table with data from the database
        self.populate_table()

        # Create a vertical layout for combo box, text box, label, order button, and change location button
        right_layout = QVBoxLayout()

        # Create a horizontal layout for combo box and text box
        combo_amount_layout = QHBoxLayout()

        # Create a combo box for product names
        self.name_combo = QComboBox(self)
        self.populate_combo()

        # Create a label for the text box
        amount_label = QLabel("Amount:", self)

        # Create a text box for entering the amount
        self.amount_edit = QLineEdit(self)

        # Add the combo box and text box to the horizontal layout
        combo_amount_layout.addWidget(self.name_combo)
        combo_amount_layout.addWidget(amount_label)
        combo_amount_layout.addWidget(self.amount_edit)

        # Create a button for ordering
        self.changestock_button = QPushButton("ChangeStock", self)
        self.changestock_button.clicked.connect(self.changestock)

        # Create a button for changing location
        self.add_item_button = QPushButton("Add item", self)
        self.add_item_button.clicked.connect(self.add_item)

        self.delete_button =  QPushButton("Delete item", self)
        self.delete_button.clicked.connect(self.delete_item)

        # Add the horizontal layout, order button, and change location button to the vertical layout
        right_layout.addLayout(combo_amount_layout)
        right_layout.addWidget(self.changestock_button)
        right_layout.addWidget(self.add_item_button)
        right_layout.addWidget(self.delete_button)

        # Add the table widget and the vertical layout to the main layout
        main_layout.addWidget(self.table_widget)
        main_layout.addLayout(right_layout)

        # Set the main layout for the window
        self.setLayout(main_layout)

        # Set window properties
        self.setWindowTitle('Item List')
        self.setGeometry(300, 300, 800, 400)

    def populate_table(self):
        # Assume `connection` is a valid database connection
        cursor = connection.cursor()

        # Execute a query to retrieve items from the database
        cursor.execute("SELECT name, manufacturer, stock, price_per_unit FROM INVENTORY")
        items = cursor.fetchall()

        # Set the number of rows in the table
        self.table_widget.setRowCount(len(items))

        # Populate the table with data
        for row, item in enumerate(items):
            for col, value in enumerate(item):
                item_data = QTableWidgetItem(str(value))
                self.table_widget.setItem(row, col, item_data)

    def populate_combo(self):
        # Populate the combo box with product names from the table
        for row in range(self.table_widget.rowCount()):
            name_item = self.table_widget.item(row, 0)  # Assuming the "Name" column is at index 0
            if name_item is not None:
                self.name_combo.addItem(name_item.text())

    def changestock(self):
        newstock = int(self.amount_edit.text())
        product_changed = self.name_combo.currentText()

        cursor = connection.cursor()
        query = "UPDATE INVENTORY SET stock = :newstock WHERE name = :product_changed"
        cursor.execute(query, {'newstock': newstock, 'product_changed': product_changed})
        connection.commit()

        self.populate_table()
        self.populate_combo()

    def add_item(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)


    def delete_item(self):
        product_changed = self.name_combo.currentText()
        cursor = connection.cursor()

        querry = "SELECT ITEM_ID FROM inventory WHERE NAME = :product_changed"
        cursor.execute(querry, {'product_changed': product_changed})
        result = cursor.fetchone()
        itemID = result[0]

        querry = "DELETE FROM ORDERS WHERE ORDERED_ITEM_ID = :itemID"
        cursor.execute(querry, {'itemID': itemID})

        querry = "DELETE FROM INVENTORY WHERE name = :product_changed"
        cursor.execute(querry, {'product_changed': product_changed})

        connection.commit()

        self.populate_table()
        self.populate_combo()

class AddItemApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Create the main layout
        layout = QVBoxLayout()

        # Create text boxes for Name, Manufacturer, Stock, and Price
        self.name_edit = QLineEdit(self)
        self.manufacturer_edit = QLineEdit(self)
        self.stock_edit = QLineEdit(self)
        self.price_edit = QLineEdit(self)

        # Add labels for better clarity
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Manufacturer:"))
        layout.addWidget(self.manufacturer_edit)

        layout.addWidget(QLabel("Stock:"))
        layout.addWidget(self.stock_edit)

        layout.addWidget(QLabel("Price:"))
        layout.addWidget(self.price_edit)

        # Create a button for adding the item
        add_item_button = QPushButton("Add Item", self)
        add_item_button.clicked.connect(self.add_item_clicked)

        # Add the button to the layout
        layout.addWidget(add_item_button)

        # Set the main layout for the window
        self.setLayout(layout)

        # Set window properties
        self.setWindowTitle('Add Item')
        self.setGeometry(400, 400, 300, 200)

    def add_item_clicked(self):
        # Add your logic for handling the "Add Item" button click
        name = self.name_edit.text()
        manufacturer = self.manufacturer_edit.text()
        stock = self.stock_edit.text()
        price = self.price_edit.text()

        cursor = connection.cursor()
        # obtain next id
        cursor.execute("SELECT MAX(order_id) FROM ORDERS")
        result = cursor.fetchone()
        next_order_id = result[0] + 1 if result[0] is not None else 1

        querry = "INSERT INTO INVENTORY(item_id, name, manufacturer, stock, price_per_unit) VALUES (:next_order_id, :name, :manufacturer, :stock, :price_per_unit)"
        cursor.execute(querry, {'next_order_id': next_order_id, 'name': name, 'manufacturer': manufacturer, 'stock': stock, 'price_per_unit': price})
        connection.commit()

        widget.setCurrentIndex(widget.currentIndex() - 1)


if __name__ == '__main__':
    connection = oracledb.connect(user="bd011", password="bd011",
                                  dsn=f"{"bd-dc.cs.tuiasi.ro"}:{1539}/{"orcl"}")

    userID = 3
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    registration_window = RegistrationWindow()
    login_window = LoginWindow()
    adminP = adminPanel()
    itemlist = ItemListApp()
    changeLoc = locationChange()
    addItem = AddItemApp()

    widget.addWidget(login_window)
    widget.addWidget(registration_window)
    widget.addWidget(itemlist)
    widget.addWidget(changeLoc)
    widget.addWidget(adminP)
    widget.addWidget(addItem)

    widget.show()

    sys.exit(app.exec_())
