import mysql.connector
import random

# Connect to the MySQL database
try:
    db = mysql.connector.connect(
        host="bxu4dnuioultji19dcki-mysql.services.clever-cloud.com",
        user="ulkndk9aiugwv2eu",
        password="4tR4IAweWMRXAivaeAQP",
        database="bxu4dnuioultji19dcki",
        port="3306"
    )
    print("Connected to the database successfully.")
except mysql.connector.Error as err:
    print(f"Error connecting to the database: {err}")
    exit()

def fetch_race_results():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT season, round, race_name, driver_name, constructor_name, position, points, fastest_lap
            FROM race_results
        """)
        results = cursor.fetchall()
        cursor.close()
        return results
    except mysql.connector.Error as err:
        print(f"Error fetching race results: {err}")
        return []


def get_driver_id(driver_name):
    try:
        buffered_cursor = db.cursor(buffered=True)
        buffered_cursor.execute("SELECT DriverID FROM Drivers WHERE Name = %s", (driver_name,))
        result = buffered_cursor.fetchone()
        buffered_cursor.close()
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"Error fetching DriverID: {err}")
        return None



# Helper function to fetch all drivers and their statistics
def fetch_all_drivers():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.DriverID, d.Name, d.Nationality, d.Team,d.Retired,d.championships_won,d.teams_raced_for,d.most_recent_championship_win,ds.WetCondition, ds.TopSpeed, ds.Focus, ds.Reflexes, ds.Tactics
            FROM Drivers d
            LEFT JOIN DriverStatistics ds ON d.DriverID = ds.DriverID
        """)
        drivers = cursor.fetchall()
        cursor.close()
        return drivers
    except mysql.connector.Error as err:
        print(f"Error fetching drivers: {err}")
        return []

def fetch_driver_statistics():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT season, position, driver_name, team_name, points FROM driver_standings")
        statistics = cursor.fetchall()
        cursor.close()
        return statistics
    except mysql.connector.Error as err:
        print(f"Error fetching driver statistics: {err}")
        return []

def fetch_constructor_standings():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT season, position, constructor_name, points FROM constructor_standings")
        standings = cursor.fetchall()
        cursor.close()
        return standings
    except mysql.connector.Error as err:
        print(f"Error fetching constructor standings: {err}")
        return []


# Compare cards and determine the winner
def compare_cards(user_card, cpu_card, attribute):
    """
    Compares the selected attribute of two cards and determines the winner.
    :param user_card: Dictionary representing the user's card.
    :param cpu_card: Dictionary representing the CPU's card.
    :param attribute: String, the attribute to compare (e.g., 'TopSpeed').
    :return: String, 'user', 'cpu', or 'tie'.
    """
    user_value = user_card[attribute]
    cpu_value = cpu_card[attribute]

    if user_value > cpu_value:
        return "user"
    elif cpu_value > user_value:
        return "cpu"
    else:
        return "tie"

# Initialize the game
def initialize_game():
    """
    Initializes the game by fetching drivers from the database,
    shuffling them, and splitting them into two hands.
    :return: Tuple (user_hand, cpu_hand).
    """
    all_drivers = fetch_all_drivers()
    if not all_drivers:
        print("No active drivers found in the database. Exiting...")
        exit(1)

    random.shuffle(all_drivers)
    mid_point = len(all_drivers) // 2
    user_hand = all_drivers[:mid_point]
    cpu_hand = all_drivers[mid_point:]
    return user_hand, cpu_hand





# Helper function to insert a driver into the Drivers table
def insert_driver(name, nationality, team, retired=False):
    try:
        insert_cursor = db.cursor()
        insert_cursor.execute("""
            INSERT INTO Drivers (Name, Nationality, Team, Retired)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE Nationality=VALUES(Nationality), Team=VALUES(Team), Retired=VALUES(Retired)
        """, (name, nationality, team, retired))
        db.commit()
        driver_id = get_driver_id(name)
        insert_cursor.close()
        return driver_id
    except mysql.connector.Error as err:
        print(f"Error inserting/updating driver: {err}")
        return None



# Fetch all drivers and their statistics from the database

# Compare cards and determine the winner
def compare_cards(user_card, cpu_card, attribute):
    """
    Compares the selected attribute of two cards and determines the winner.
    :param user_card: Dictionary representing the user's card.
    :param cpu_card: Dictionary representing the CPU's card.
    :param attribute: String, the attribute to compare (e.g., 'TopSpeed').
    :return: String, 'user', 'cpu', or 'tie'.
    """
    user_value = user_card[attribute]
    cpu_value = cpu_card[attribute]

    if user_value > cpu_value:
        return "user"
    elif cpu_value > user_value:
        return "cpu"
    else:
        return "tie"

# Initialize the game
def initialize_game():
    """
    Initializes the game by fetching drivers from the database,
    shuffling them, and splitting them into two hands.
    :return: Tuple (user_hand, cpu_hand).
    """
    all_drivers = fetch_all_drivers()
    if not all_drivers:
        print("No active drivers found in the database. Exiting...")
        exit(1)

    random.shuffle(all_drivers)
    mid_point = len(all_drivers) // 2
    user_hand = all_drivers[:mid_point]
    cpu_hand = all_drivers[mid_point:]
    return user_hand, cpu_hand


# Update a driver's information in the database
def update_driver(
    conn,
    old_name,               # original name to locate the driver
    new_name,               # new or unchanged name
    nationality,
    team,
    retired,
    championships_won,
    teams_raced_for,
    most_recent_championship_win
):
    try:
        cursor = conn.cursor()

        query = """
            UPDATE drivers
            SET 
                Name = %s,
                Nationality = %s,
                Team = %s,
                Retired = %s,
                championships_won = %s,
                teams_raced_for = %s,
                most_recent_championship_win = %s
            WHERE Name = %s
        """

        values = (
            new_name,
            nationality,
            team,
            retired,
            championships_won,
            teams_raced_for,
            most_recent_championship_win,
            old_name  # this is used in WHERE clause
        )

        cursor.execute(query, values)
        conn.commit()

        return True, f"✅ Driver '{old_name}' successfully updated."

    except Exception as e:
        return False, f"❌ Error updating driver: {e}"


# Delete a driver from the database
def delete_driver(driver_id):
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM DriverStatistics WHERE DriverID = %s", (driver_id,))
        cursor.execute("DELETE FROM Drivers WHERE DriverID = %s", (driver_id,))
        db.commit()
        cursor.close()
        print(f"Deleted driver with ID: {driver_id}")
    except mysql.connector.Error as err:
        print(f"Error deleting driver: {err}")


def insert_driver_statistics(driver_id, wet_condition, top_speed, focus, reflexes, tactics):
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO DriverStatistics (DriverID, WetCondition, TopSpeed, Focus, Reflexes, Tactics)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (driver_id, wet_condition, top_speed, focus, reflexes, tactics))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error inserting driver statistics: {err}")
 
# Delete all records from the database
def delete_all_records():
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM DriverStatistics")
        cursor.execute("DELETE FROM Drivers")
        db.commit()
        cursor.close()
        print("All records deleted successfully.")
    except mysql.connector.Error as err:
        print(f"Error deleting all records: {err}")

# Initialize drivers and their stats dynamically
def initialize_drivers_with_stats():
    # Define default stats for drivers without predefined stats
    default_stats = {
        "wet_condition": 70,
        "top_speed": 70,
        "focus": 70,
        "reflexes": 70,
        "tactics": 70
    }

    # Fetch all drivers from the database
    drivers = fetch_all_drivers()

    for driver in drivers:
        driver_name = driver["Name"]
        driver_nationality = driver["Nationality"]
        driver_team = driver["Team"]

        # Insert or update the driver in the Drivers table
        driver_id = insert_driver(driver_name, driver_nationality, driver_team)

        # Assign stats (use existing stats if available, otherwise use defaults)
        wet_condition = driver.get("WetCondition", default_stats["wet_condition"])
        top_speed = driver.get("TopSpeed", default_stats["top_speed"])
        focus = driver.get("Focus", default_stats["focus"])
        reflexes = driver.get("Reflexes", default_stats["reflexes"])
        tactics = driver.get("Tactics", default_stats["tactics"])

        # Insert or update the driver's stats in the DriverStatistics table
        #insert_driver_statistics(driver_id, wet_condition, top_speed, focus, reflexes, tactics)
def fetch_driver_statistics():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT season, position, driver_name, team_name, points FROM driver_standings")
        statistics = cursor.fetchall()
        cursor.close()
        return statistics
    except mysql.connector.Error as err:
        print(f"Error fetching driver statistics: {err}")
        return []

def insert_driver_standing(season, position, driver_name, team_name, points):
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO driver_standings (season, position, driver_name, team_name, points)
            VALUES (%s, %s, %s, %s, %s)
        """, (season, position, driver_name, team_name, points))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error inserting driver standing: {err}")

def update_driver_standing(season, driver_name, position, team_name, points):
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE driver_standings
            SET position = %s, team_name = %s, points = %s
            WHERE season = %s AND driver_name = %s
        """, (position, team_name, points, season, driver_name))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error updating driver standing: {err}")

def delete_driver_standing(season, driver_name):
    try:
        cursor = db.cursor()
        cursor.execute("""
            DELETE FROM driver_standings WHERE season = %s AND driver_name = %s
        """, (season, driver_name))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error deleting driver standing: {err}")

def insert_driver_standing(season, position, driver_name, team_name, points):
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO driver_standings (season, position, driver_name, team_name, points)
            VALUES (%s, %s, %s, %s, %s)
        """, (season, position, driver_name, team_name, points))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error inserting driver standing: {err}")

def update_driver_standing(season, driver_name, position, team_name, points):
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE driver_standings
            SET position = %s, team_name = %s, points = %s
            WHERE season = %s AND driver_name = %s
        """, (position, team_name, points, season, driver_name))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error updating driver standing: {err}")

def delete_driver_standing(season, driver_name):
    try:
        cursor = db.cursor()
        cursor.execute("""
            DELETE FROM driver_standings
            WHERE season = %s AND driver_name = %s
        """, (season, driver_name))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error deleting driver standing: {err}")


def insert_constructor_standing(season, position, constructor_name, points):
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO constructor_standings (season, position, constructor_name, points)
            VALUES (%s, %s, %s, %s)
        """, (season, position, constructor_name, points))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error inserting constructor standing: {err}")

def update_constructor_standing(season, constructor_name, position, points):
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE constructor_standings
            SET position = %s, points = %s
            WHERE season = %s AND constructor_name = %s
        """, (position, points, season, constructor_name))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error updating constructor standing: {err}")

def delete_constructor_standing(season, constructor_name):
    try:
        cursor = db.cursor()
        cursor.execute("""
            DELETE FROM constructor_standings
            WHERE season = %s AND constructor_name = %s
        """, (season, constructor_name))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error deleting constructor standing: {err}")


def insert_race_result(season, round_num, race_name, driver_name, constructor_name, position, points, fastest_lap):
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO race_results (season, round, race_name, driver_name, constructor_name, position, points, fastest_lap)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (season, round_num, race_name, driver_name, constructor_name, position, points, fastest_lap))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error inserting race result: {err}")

def update_race_result(season, round_num, race_name, driver_name, constructor_name, position, points, fastest_lap):
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE race_results
            SET position = %s, points = %s, fastest_lap = %s
            WHERE season = %s AND round = %s AND race_name = %s AND driver_name = %s AND constructor_name = %s
        """, (position, points, fastest_lap, season, round_num, race_name, driver_name, constructor_name))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error updating race result: {err}")

def delete_race_result(season, round_num, race_name, driver_name):
    try:
        cursor = db.cursor()
        cursor.execute("""
            DELETE FROM race_results
            WHERE season = %s AND round = %s AND race_name = %s AND driver_name = %s
        """, (season, round_num, race_name, driver_name))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error deleting race result: {err}")


if __name__ == "__main__":
    initialize_drivers_with_stats()
    print("Driver initialization with stats completed!")