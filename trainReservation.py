import pymysql
from datetime import datetime

# Replace these variables with your MySQL database credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root@123',
    'database': 'train_db',
}

# Connect to the MySQL database
conn = pymysql.connect(**db_config)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL
)
''')

# Create Trains table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Trains (
    TrainID INT AUTO_INCREMENT PRIMARY KEY,
    TrainName VARCHAR(255) NOT NULL,
    DepartureCity VARCHAR(255) NOT NULL,
    ArrivalCity VARCHAR(255) NOT NULL,
    DepartureTime TIME NOT NULL,
    ArrivalTime TIME NOT NULL,
    AvailableSeats INT NOT NULL
)
''')

# Commit changes
conn.commit()

# Create Reservations table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Reservations (
    ReservationID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    TrainID INT,
    NumTickets INT NOT NULL,
    ReservationDate DATETIME NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (TrainID) REFERENCES Trains(TrainID)
)
''')

# Create Payments table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    ReservationID INT,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentDate DATETIME NOT NULL,
    FOREIGN KEY (ReservationID) REFERENCES Reservations(ReservationID)
)
''')

# Close the connection
conn.close()




# Replace these variables with your MySQL database credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root@123',
    'database': 'train_db',
}

def register_user():
    # Connect to the MySQL database
    conn = pymysql.connect(**db_config)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    try:
        # Get user inputs
        username = input("Enter your desired username: ")
        password = input("Enter your password: ")
        email = input("Enter your email address: ")

        # Check if the username is already taken
        cursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            print("Username already taken. Please choose a different username.")
            return

        # Insert user registration
        cursor.execute('''
            INSERT INTO Users (Username, Password, Email)
            VALUES (%s, %s, %s)
        ''', (username, password, email))

        # Commit changes
        conn.commit()

        print("\nRegistration successful! You can now log in.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        conn.close()

def create_reservation():
    # Connect to the MySQL database
    conn = pymysql.connect(**db_config)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    try:
        # Get user inputs
        username = input("Enter your username: ")

        # Display available trains
        cursor.execute("SELECT TrainID, TrainName, DepartureCity, ArrivalCity FROM Trains")
        trains = cursor.fetchall()

        if not trains:
            print("No trains available.")
            return

        print("\nAvailable Trains:")
        for train in trains:
            train_id, train_name, departure_city, arrival_city = train
            print(f"{train_id}. {train_name} - {departure_city} to {arrival_city}")

        # Get user inputs for train reservation
        train_id = int(input("Enter the Train ID for reservation: "))

        # Get user ID
        cursor.execute("SELECT UserID FROM Users WHERE Username = %s", (username,))
        user_id = cursor.fetchone()
        if not user_id:
            print("User not found. Please register first.")
            return

        # Get train information
        cursor.execute("SELECT AvailableSeats, DepartureTime, ArrivalTime FROM Trains WHERE TrainID = %s", (train_id,))
        train_info = cursor.fetchone()

        if not train_info:
            print("Train not found.")
            return

        available_seats, departure_time, arrival_time = train_info

        print(f"\nTrainID: {train_id}")
        print(f"Available Seats: {available_seats}")
        print(f"Departure Time: {departure_time}")
        print(f"Arrival Time: {arrival_time}")

        # Get the number of tickets
        num_tickets = int(input("Enter the number of tickets: "))

        if num_tickets > available_seats:
            print("Not enough available seats for the requested number of tickets.")
            return

        # Insert reservation
        reservation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO Reservations (UserID, TrainID, NumTickets, ReservationDate)
            VALUES (%s, %s, %s, %s)
        ''', (user_id[0], train_id, num_tickets, reservation_date))

        # Update available seats
        updated_seats = available_seats - num_tickets
        cursor.execute("UPDATE Trains SET AvailableSeats = %s WHERE TrainID = %s", (updated_seats, train_id))

        # Simulate payment (you can customize this part based on your needs)
        amount = num_tickets * 50  # Assuming $50 per ticket
        payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO Payments (ReservationID, Amount, PaymentDate)
            VALUES (LAST_INSERT_ID(), %s, %s)
        ''', (amount, payment_date))

        # Commit changes
        conn.commit()

        print("\nReservation successful!")
        print("+" + "-" * 33 + "+")
        print(f"| Username: {username: <20} |")
        print(f"| Train ID: {train_id: <22} |")
        print(f"| Num Tickets: {num_tickets: <20} |")
        print(f"| Amount Paid: ${amount: <19} |")
        print("+" + "-" * 33 + "+")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        conn.close()

def check_reservations_by_username(username):
    try:
        # Connect to the MySQL database
        conn = pymysql.connect(**db_config)

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Check if the username exists
        cursor.execute("SELECT UserID FROM Users WHERE Username = %s", (username,))
        user_id = cursor.fetchone()

        if not user_id:
            print("User not found.")
            return

        # Retrieve pre-booked reservations for the user
        cursor.execute('''
            SELECT R.ReservationID, T.TrainName, R.NumTickets, R.ReservationDate
            FROM Reservations R
            JOIN Trains T ON R.TrainID = T.TrainID
            WHERE R.UserID = %s
        ''', (user_id[0],))

        reservations = cursor.fetchall()

        if not reservations:
            print("No pre-booked reservations for the user.")
            return

        print("\nPre-booked Reservations:")
        print("+-------------------------+")
        print("|   Train Name   | Tickets |   Reservation Date   |")
        print("+-------------------------+")

        for reservation in reservations:
            reservation_id, train_name, num_tickets, reservation_date = reservation
            print(f"| {train_name: <15} | {num_tickets: <7} | {reservation_date} |")

        print("+-------------------------+")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        conn.close()

# Provide a menu for the user
while True:
    print("\n1. Register\n2. Create Train Reservation\n3. Check Pre-booked Reservations\n4. Exit")
    choice = input("Enter your choice (1, 2, 3, or 4): ")

    if choice == '1':
        register_user()
    elif choice == '2':
        create_reservation()
    elif choice == '3':
        username = input("Enter your username: ")
        check_reservations_by_username(username)
    elif choice == '4':
        print("Exiting the program. Goodbye!")
        break
    else:
        print("Invalid choice. Please enter 1, 2, 3, or 4.")

