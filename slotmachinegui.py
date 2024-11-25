import sys
import random
import mysql.connector as ms
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer


class SlotMachine(QWidget):
    def __init__(self):
        super().__init__()
        self.connection = ms.connect(host="localhost", user="root", password="varad@mysql", database="slotmachine")
        self.cursor = self.connection.cursor()
        self.current_user = None
        self.balance = 0

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Python Slots")
        self.setGeometry(100, 100, 400, 600)


        self.header_label = QLabel("🎰 Welcome to Python Slots 🎰")
        self.balance_label = QLabel("Balance: $0")
        self.slot_row = QLabel("🍒 | 🍉 | 🍋")
        self.bet_input = QLineEdit()
        self.spin_button = QPushButton("Spin")
        self.play_again_button = QPushButton("Play Again")
        self.quit_button = QPushButton("Quit")
        self.login_button = QPushButton("Login/Register")

        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
            QLineEdit {
                font-size: 20px;
                padding: 5px;
                border: 2px solid #3498db;
                border-radius: 5px;
            }
            QPushButton {
                font-size: 18px;
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.header_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.balance_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.slot_row, alignment=Qt.AlignCenter)
        layout.addWidget(self.bet_input, alignment=Qt.AlignCenter)
        layout.addWidget(self.spin_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.play_again_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.quit_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        
        self.login_button.clicked.connect(self.check_account)
        self.spin_button.clicked.connect(self.spin_slots)
        self.play_again_button.clicked.connect(self.reset_game)
        self.quit_button.clicked.connect(self.close_game)

        self.play_again_button.setEnabled(False)
        self.spin_button.setEnabled(False)

    def check_account(self):
        acc, ok = QInputDialog.getText(self, "Account Check", "Do you have an account? (y/n):")

        if ok:
            if acc.lower() == 'y':
                user, ok1 = QInputDialog.getText(self, "Login", "Enter Username:")
                if not ok1:
                    return
                password, ok2 = QInputDialog.getText(self, "Login", "Enter Password:", QLineEdit.Password)
                if not ok2:
                    return

                
                query = "SELECT name FROM user WHERE name = %s"
                self.cursor.execute(query, (user,))
                real_user = self.cursor.fetchall()

                if real_user:
                    query = "SELECT passwrd FROM user WHERE name = %s"
                    self.cursor.execute(query, (user,))
                    real_pass = self.cursor.fetchall()

                    if real_pass and real_pass[0][0] == password:
                        self.current_user = user
                        self.balance = self.get_balance()
                        self.update_balance_label()
                        QMessageBox.information(self, "Login Successful", "Welcome back!")
                        self.spin_button.setEnabled(True)
                    else:
                        QMessageBox.critical(self, "Error", "Invalid password!")
                else:
                    QMessageBox.critical(self, "Error", "Invalid username!")

            elif acc.lower() == 'n':
                new_user, ok1 = QInputDialog.getText(self, "Register", "Enter New Username:")
                if not ok1:
                    return
                new_pass, ok2 = QInputDialog.getText(self, "Register", "Enter Password:", QLineEdit.Password)
                if not ok2:
                    return
                deposit, ok3 = QInputDialog.getInt(self, "Deposit", "Enter Initial Deposit Amount:")
                if not ok3:
                    return

                
                query = "INSERT INTO user(name, passwrd, deposit) VALUES (%s, %s, %s)"
                self.cursor.execute(query, (new_user, new_pass, deposit))
                self.connection.commit()
                QMessageBox.information(self, "Sign-Up Successful", "Account created successfully!")
                self.current_user = new_user
                self.balance = deposit
                self.update_balance_label()
                self.spin_button.setEnabled(True)

    def get_balance(self):
        query = "SELECT deposit FROM user WHERE name = %s"
        self.cursor.execute(query, (self.current_user,))
        balance = self.cursor.fetchone()
        return balance[0] if balance else 0

    def update_balance_label(self):
        self.balance_label.setText(f"Balance: ${self.balance}")

    def spin_slots(self):
        bet = self.bet_input.text()
        if not bet.isdigit():
            QMessageBox.warning(self, "Invalid Bet", "Please enter a valid bet amount.")
            return

        bet = int(bet)
        if bet > self.balance:
            QMessageBox.warning(self, "Insufficient Funds", "You don't have enough balance.")
            return

        self.balance -= bet
        self.update_balance_label()

        
        row = self.spin_row()
        self.slot_row.setText(" | ".join(row))

        payout = self.get_payout(row, bet)
        if payout > 0:
            QMessageBox.information(self, "Congratulations!", f"You won ${payout}!")
        else:
            QMessageBox.information(self, "Try Again", "You lost this round.")

        self.balance += payout
        self.update_balance_label()

        if self.balance <= 0:
            QMessageBox.warning(self, "Game Over", "You ran out of balance!")
            self.spin_button.setEnabled(False)
        else:
            self.play_again_button.setEnabled(True)

    def spin_row(self):
        symbols = ['🍒', '🍉', '🍋', '🔔', '⭐']
        return [random.choice(symbols) for _ in range(3)]

    def get_payout(self, row, bet):
        if row[0] == row[1] == row[2]:
            if row[0] == '🍒':
                return bet * 3
            elif row[0] == '🍉':
                return bet * 4
            elif row[0] == '🍋':
                return bet * 5
            elif row[0] == '🔔':
                return bet * 10
            elif row[0] == '⭐':
                return bet * 20
        return 0

    def reset_game(self):
        self.bet_input.clear()
        self.slot_row.setText("🍒 | 🍉 | 🍋")
        self.play_again_button.setEnabled(False)

    def close_game(self):
        self.update_balance_in_db()
        self.connection.close()
        self.close()

    def update_balance_in_db(self):
        if self.current_user:
            query = "UPDATE user SET deposit = %s WHERE name = %s"
            self.cursor.execute(query, (self.balance, self.current_user))
            self.connection.commit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    slot_machine = SlotMachine()
    slot_machine.show()
    sys.exit(app.exec_())
