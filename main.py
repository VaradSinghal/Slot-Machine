import random
import mysql.connector as ms


c = ms.connect(host="localhost", user="root", password="varad@mysql", database="slotmachine")
cursor = c.cursor()

current_user = None

def get_bal():
    query = "SELECT deposit FROM user WHERE name = %s"
    cursor.execute(query, (current_user,))
    balL = cursor.fetchall()
    bal = balL[0][0] if balL else 0
    return bal

def spin_row():
    symbols = ['🍒', '🍉', '🍋', '🔔', '⭐']
    result = [random.choice(symbols) for _ in range(3)]
    return result

def print_row(row):
    print("--------------")
    print(" | ".join(row))
    print("--------------")

def get_payout(row, bet):
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

def check_acc():
    global current_user
    acc = input("Do you have an account? (y/n): ")
    if acc == 'y':
        user = input("Enter the username: ")
        passwrd = input("Enter the password: ")
        print("Verifying...")
        
        
        query = "SELECT name FROM user WHERE name = %s"
        cursor.execute(query, (user,))
        real_user = cursor.fetchall()
        
        if real_user:
            query1 = "SELECT passwrd FROM user WHERE name = %s"
            cursor.execute(query1, (user,))
            real_pass = cursor.fetchall()
            
            if real_pass and real_pass[0][0] == passwrd:
                print("Login successful!")
                current_user = user  
                return 1
            else:
                print("Invalid password!")
                exit(1)
        else:
            print("Invalid username!")
            exit(1)
    else:
        print("Create an account to play")
        new_user = input("Enter the username: ")
        new_pass = input("Enter the password: ")
        amt = int(input("Enter the amount you want to deposit: "))
        

        query = "INSERT INTO user(name, passwrd, deposit) VALUES (%s, %s, %s)"
        data = (new_user, new_pass, amt)
        cursor.execute(query, data)
        c.commit()
        print("Sign-up successful!")
        current_user = new_user  

def bal_update(balance):
    global current_user
    query = "UPDATE user SET deposit = %s WHERE name = %s"
    data = (balance, current_user)
    cursor.execute(query, data)
    c.commit()
    print(f"Balance updated for {current_user}")

def main():
    print("---------------------------")
    print(" Welcome to Python Slots  ")
    print(" Symbols: 🍒 🍉 🍋 🔔 ⭐ ")
    print("---------------------------")
    
    check_acc()  
    balance = get_bal()  

    while balance > 0:
        print(f"Current balance: ${balance}")
        bet = input("Place your bet amount: ")

        if not bet.isdigit():
            print("Please enter a valid number")
            continue
        bet = int(bet)
        if bet > balance:
            print("Insufficient Balance")
            continue
        if bet <= 0:
            print("Bet must be greater than 0")
            continue
        balance -= bet  

        row = spin_row()
        print("Spinning....\n")
        print_row(row)
        payout = get_payout(row, bet)

        if payout > 0:
            print(f"You won ${payout}")
        else:
            print("Sorry, you lost this round")
        balance += payout  

        play_again = input("Do you want to play again? (Y/N): ").upper()
        if play_again != 'Y':
            bal_update(balance)  
            break

    print(f"Game Over! Your final balance is ${balance}")

if __name__ == "__main__":
    main()
