import tkinter as tk
import mysql.connector
import re
from tkinter import messagebox
# DB connection
conn = mysql.connector.connect(
    host="localhost",  # your MySQL host
    user="root",  # replace with your MySQL username
    password="123456",  # replace with your MySQL password
    database="f1db"
)
cursor = conn.cursor()

# Fetch table columns dynamically
cursor.execute("SHOW COLUMNS FROM drivers")
driver_columns = [col[0].lower() for col in cursor.fetchall()]

cursor.execute("SHOW COLUMNS FROM driverstatistics")
stats_columns = [col[0].lower() for col in cursor.fetchall()]

# Fetch all driver names and teams
cursor.execute("SELECT Name FROM drivers")
all_driver_names = [name[0].lower() for name in cursor.fetchall()]

cursor.execute("SELECT DISTINCT Team FROM drivers")
all_teams = [team[0].lower() for team in cursor.fetchall()]

# Synonym mapping for columns
synonym_map = {
    "reflexes": ["reaction", "reflex", "response", "quickness"],
    "wet_condition": ["wet skill", "wet performance", "wet ability", "rain skill"],
    "tactics": ["strategy", "tactic", "gameplay", "approach","knowledge"],
    "focus": ["concentration", "attention", "focus level","focus"],
    "topspeed": ["speed", "top speed", "maximum speed", "velocity","fastest"]
}

# Valid examples to guide the user
valid_examples = [
    "top 3 drivers by reflexes",
    "highest reflexes",
    "slowest driver",
    "worst tactics",
    "best in tactics",
    "most skilled in wet",
    "average wet condition",
    "list drivers from Ferrari",
    "get all the drivers whose name starts with L",
    "what is the nationality of Lewis Hamilton",
    "is there any driver named Lewis",
    "What is max's reflexes+tactics"
]




def natural_to_sql(query):
    query = query.lower()
    # Map synonyms to actual columns
    def get_column_from_synonym(synonym):
        for column, synonyms in synonym_map.items():
            if any(syn in synonym for syn in synonyms):
                return column
        return None

    #race_results
        # Race Results Queries
    match = re.search(r"what position did (.+) get (?:in|on) (\d{4}|[a-z ]+) (?:round|race|gp)? ?(.+)?", query)
    if match:
        name, year_or_race, round_or_name = match.groups()
        name = name.strip().title()
        if year_or_race.isdigit():
            if round_or_name and round_or_name.isdigit():
                return f"SELECT position FROM race_results WHERE (driver_name LIKE '%{name}%' OR constructor_name LIKE '%{name}%') AND season = '{year_or_race}' AND round = '{round_or_name}'"
            else:
                return f"SELECT position FROM race_results WHERE (driver_name LIKE '%{name}%' OR constructor_name LIKE '%{name}%') AND season = '{year_or_race}'"
        else:
            return f"SELECT position FROM race_results WHERE (driver_name LIKE '%{name}%' OR constructor_name LIKE '%{name}%') AND race_name LIKE '%{year_or_race}%'"

    match = re.search(r"who won the race on (.+) in (\d{4})", query)
    if match:
        race_name, season = match.groups()
        return f"SELECT driver_name FROM race_results WHERE race_name LIKE '%{race_name.strip()}%' AND season = '{season}' AND position = 1"

    match = re.search(r"who was last on (.+) in (\d{4})", query)
    if match:
        race_name, season = match.groups()
        return f"SELECT driver_name FROM race_results WHERE race_name LIKE '%{race_name.strip()}%' AND season = '{season}' ORDER BY position DESC LIMIT 1"

    match = re.search(r"highest points scored by (.+) in (\d{4})", query)
    if match:
        name, year = match.groups()
        return f"SELECT MAX(points) FROM race_results WHERE (driver_name LIKE '%{name.strip()}%' OR constructor_name LIKE '%{name.strip()}%') AND season = '{year}'"

    match = re.search(r"top (\d+) (drivers|constructors) in (\d{4})", query)
    if match:
        limit, role, year = match.groups()
        if role.startswith("driver"):
            return f"""
                SELECT driver_name, position, race_name 
                FROM race_results 
                WHERE season = '{year}' 
                AND position <= {limit} 
                ORDER BY position ASC
            """
        else:
            return f"""
                SELECT constructor_name, position, race_name 
                FROM race_results 
                WHERE season = '{year}' 
                AND position <= {limit} 
                ORDER BY position ASC
            """


    match = re.search(r"total points scored by (.+)", query)
    if match:
        name = match.group(1).strip().title()
        return f"SELECT SUM(points) AS total_points FROM race_results WHERE driver_name LIKE '%{name}%' OR constructor_name LIKE '%{name}%'"



    #race_results<>

    #constructer and driver <>
    match = re.search(r'who (won|was) "?(\d+(st|nd|rd|th)?)"? (in|during) "?(\d{4})"?', query)
    if match and "driver" in query:
        position = re.sub(r"(st|nd|rd|th)", "", match.group(2))
        year = match.group(5)
        return f"SELECT driver_name FROM driver_standings WHERE position = {position} AND season = {year}"
    elif match and "constructor" in query:
        position= re.sub(r"(st|nd|rd|th)", "", match.group(2))
        year=match.group(5)
        return f"SELECT constructor_name FROM constructor_standings WHERE position = {position} AND season = {year}"
    


    if "total points" in query and any(w in query for w in ["for", "by"]):
        match = re.search(r"(?:for|by)\s+(.+)", query)
    if match:
        name = match.group(1).strip().title()

        return f"""
        SELECT driver_name AS name, SUM(points) AS total_points
        FROM driver_standings
        WHERE driver_name LIKE '%{name}%'
        GROUP BY driver_name
        UNION
        SELECT constructor_name AS name, SUM(points) AS total_points
        FROM constructor_standings
        WHERE constructor_name LIKE '%{name}%'
        GROUP BY constructor_name;
        """

    # Query for total points in a specific year for a driver
    if "points" in query and "score" in query:
        match = re.search(r"how many points did (\w+ \w+|\w+) score in (\d{4})", query)
        if match:
            driver_name_part = match.group(1).strip().title()
            year = match.group(2)
            return f"SELECT points FROM driver_standings WHERE driver_name LIKE '%{driver_name_part}%' AND season = '{year}'"
    


    # Show records for a specific year
    match = re.search(r"(fetch|show|get).*(records|standings).*('?)(\d{4})('?)( season)?", query)
    if match:
        year = match.group(4)
        if "driver" in query:
            return f"SELECT * FROM driver_standings WHERE season = {year}"
        elif "constructor" in query:
            return f"SELECT * FROM constructor_standings WHERE season = {year}"



    # Who was last in <year> championship
    match = re.search(r'who was last in "?(\d{4})"?', query)
    if match:
        year = match.group(1)
        if "team" in query or "constructor" in query:
            return f"SELECT constructor_name FROM constructor_standings WHERE season = {year} ORDER BY position DESC LIMIT 1"
        elif "driver" in query:
            return f"SELECT driver_name FROM driver_standings WHERE season = {year} ORDER BY position DESC LIMIT 1"
    
    #who was first in <last year> championship
    match = re.search(r'who was first in "?(\d{4})"?', query)
    if match:
        year = match.group(1)
        if "team" in query or "constructor" in query:
            return f"SELECT constructor_name FROM constructor_standings WHERE season = {year} AND position = 1"
        elif "driver" in query:
            return f"SELECT driver_name FROM driver_standings WHERE season = {year} AND position = 1"



    # Who was <year> constructors championship (position = 1)
    match = re.search(r'who was "?(\d{4})"? constructors championship', query)
    if match:
        year = match.group(1)
        return f"SELECT constructor_name FROM constructor_standings WHERE season = {year} AND position = 1"

    
    if "average points" in query and any(w in query for w in ["for", "by"]):
        # Match for a team name (constructor) and an optional year
        match = re.search(r"(?:for|by)\s+([a-zA-Z ]+)\s*(?:in|during)?\s*(\d{4})?", query)
    if match:
            team_name = match.group(1).strip().title()  # Extract team (constructor) name
            year = match.group(2)  # Extract the year if available
            
            # Constructing the SQL query dynamically
            if year:
                # Query for constructor in a specific year
                return f"""
                SELECT constructor_name AS name, AVG(points) AS average_points
                FROM constructor_standings
                WHERE constructor_name LIKE '%{team_name}%' AND season = '{year}'
                GROUP BY constructor_name;
                """
            else:
                # Query for constructor without a specific year
                return f"""
                SELECT constructor_name AS name, AVG(points) AS average_points
                FROM constructor_standings
                WHERE constructor_name LIKE '%{team_name}%'
                GROUP BY constructor_name;
                """

    #constructer and driver<>

    match = re.search(r"top (\d+) drivers by ([a-zA-Z ]+)", query)
    if match:
        limit, attr = match.groups()
        column = get_column_from_synonym(attr.strip())
        return f"SELECT Name, {column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {column} DESC LIMIT {limit}"


    
    match = re.search(r"what is (.+?)'s ([a-z]+)\s*([\+\-\*/])\s*([a-z]+)", query)
    if match:
        name, attr1, operator, attr2 = match.groups()
        col1 = get_column_from_synonym(attr1.strip())
        col2 = get_column_from_synonym(attr2.strip())
        return (
            f"SELECT Name, {col1}, {col2}, "
            f"({col1} {operator} {col2}) AS result "
            f"FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID "
            f"WHERE Name LIKE '%{name.strip()}%'"
        )
            
    match = re.search(r"compare (.+) and (.+)", query)
    if match:
        name1, name2 = match.groups()
        return f"SELECT Name, WetCondition, TopSpeed, Focus, Reflexes, Tactics FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID WHERE Name LIKE '%{name1.strip()}%' OR Name LIKE '%{name2.strip()}%'"

    # Check for reflexes-related queries
    reflex_column = get_column_from_synonym("reflexes")
    if reflex_column:
       
        
        if "best reflexes" in query:
             return f"SELECT Name, {reflex_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {reflex_column} DESC LIMIT 1"

        elif "worst reflexes" in query:
             return f"SELECT Name, {reflex_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {reflex_column} ASC LIMIT 1"

        
        elif "what is" in query and "reflex" in query:
            match = re.search(r"what is (.+)'s reflex", query)
            if match:
                name = match.group(1).strip().title()
                return f"SELECT {reflex_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID WHERE Name LIKE '%{name}%'"

    # Check for speed-related queries
    topspeed_column = get_column_from_synonym("topspeed")
    if topspeed_column:
        if "what is" in query and "speed" in query:
            match = re.search(r"what is (.+)'s speed", query)
            if match:
                name = match.group(1).strip().title()
                return f"SELECT {topspeed_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID WHERE Name LIKE '%{name}%'"
        elif "fastest" in query:
            return f"SELECT Name, {topspeed_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {topspeed_column} DESC LIMIT 1"
        elif "slowest" in query:
            return f"SELECT Name, {topspeed_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {topspeed_column} ASC LIMIT 1"
        elif "average" in query and "speed" in query:
            return f"SELECT AVG({topspeed_column}) AS AverageSpeed FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID"
        elif "best speed" in query:
            return f"SELECT Name, {topspeed_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {topspeed_column} DESC LIMIT 1"
        elif "worst speed" in query:
            return f"SELECT Name, {topspeed_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {topspeed_column} ASC LIMIT 1"

    match = re.search(r"average ([a-zA-Z ]+)", query)
    if match:
        attr = match.group(1).strip()
        column = get_column_from_synonym(attr)
        return f"SELECT AVG({column}) AS Average_{column} FROM driverstatistics"
     

    focus_column = get_column_from_synonym("focus")
    if focus_column:
       
        
        if "best focus" in query:
             return f"SELECT Name, {focus_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {focus_column} DESC LIMIT 1"

        elif "worst focus" in query:
             return f"SELECT Name, {focus_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {focus_column} ASC LIMIT 1"

        
        elif "what is" in query and "reflex" in query:
            match = re.search(r"what is (.+)'s reflex", query)
            if match:
                name = match.group(1).strip().title()
                return f"SELECT {focus_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID WHERE Name LIKE '%{name}%'"

    


    # Check for tactics-related queries
    tactics_column = get_column_from_synonym("tactics")
    if tactics_column:
        if "worst tactics" in query:
            return f"SELECT Name, {tactics_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {tactics_column} ASC LIMIT 1"
        elif "best tactics" in query:
            return f"SELECT Name, {tactics_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {tactics_column} DESC LIMIT 1"
        elif "most skilled" in query and "tactic" in query:
            return f"SELECT Name, {tactics_column} FROM drivers JOIN driverstatistics ON drivers.DriverID = driverstatistics.DriverID ORDER BY {tactics_column} DESC LIMIT 1"

    # Check for nationality-related queries
    match = re.search(r"what is the nationality of (.+)", query)
    if match:
        name = match.group(1).strip().title()
        return f"SELECT Nationality FROM drivers WHERE Name LIKE '%{name}%'"

    # Check if a driver exists by name
    match = re.search(r"is there any driver named (.+)", query)
    if match:
        name = match.group(1).strip().title()
        return f"SELECT Name FROM drivers WHERE Name LIKE '%{name}%'"

    # List drivers by team
    for team in all_teams:
        if team in query:
            return f"SELECT Name FROM drivers WHERE Team LIKE '%{team}%'"

    # List drivers by name starting with specific letter
    match = re.search(r"get all the drivers whose name starts with (.+)", query)
    if match:
        letter = match.group(1).strip().upper()
        return f"SELECT Name FROM drivers WHERE Name LIKE '{letter}%'"

    return None  # If no match found

def execute_query(nlp_query):
    sql = natural_to_sql(nlp_query)
    if sql is None:
        suggestions = "\n\nDid you mean:\n" + "\n".join(f"- {ex}" for ex in valid_examples)
        return "Sorry, I couldn't understand the question." + suggestions

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        if not rows:
            return "No results found."

        col_names = [desc[0] for desc in cursor.description]
        result = " | ".join(col_names) + "\n" + "-" * 70 + "\n"
        seen = set()
        for row in rows:
            row_key = tuple(row)
            if row_key not in seen:
                result += " | ".join(str(x) for x in row) + "\n"
                seen.add(row_key)
        return result.strip()
    except Exception as e:
        return f"Error: {str(e)}"

instruction_manual = """
Welcome to the F1 Natural Language Search!

Here are some example questions you can ask:

- Top 3 drivers by reflexes
- Best reflexes
-Worst reflexes
-Fastest driver
- Slowest driver
- Most tactics
- average speed
- least tactics
- compare max and charles
- List drivers from Ferrari
- Get all the drivers whose name starts with L
- What is the nationality of Lewis Hamilton
- Is there any driver named Lewis
- What is Lewis's reflexes
- Compare Lewis Hamilton and Max Verstappen
- Top 5 drivers by speed(or any of the attributes)
- who was 1st in 2023 constructor/driver(any position)
- how many points did max score in 2022
- average points for red 2021
- average points for merce
- who was last in 2023 team championship(driver/constructor)
- total points for max
- how many points did charles score in 2022
- fetch driver records in 2022(driver/constructor)
- What position did Max Verstappen get in 2024 round 3?
- What position did Ferrari get in 2023 Monaco Grand Prix?
- Who won the race on bahrain in 2024?
- Who was last on monaco in 2023?
- Highest points scored by Red Bull in 2023
- Total points scored by Charles(driver/constructor)
- Top 3 drivers in 2023(driver/constructor)

Tips:
- Use team names like Ferrari, Red Bull, etc.
- Use first names or last names like "lewis", "max", "charles"
- You can also ask for things like “what is perez’s speed”
"""

def launch_search_ui():
    root = tk.Tk()
    root.title("F1 Natural Language Search")
    root.geometry("1080x900")
    root.configure(bg="#1E1E1E") 

    # Toggle Frame for Instruction Manual
    toggle_frame = tk.Frame(root, bg="#1E1E1E")
    toggle_frame.pack(pady=10)

    # Instruction Text Box
    instruction_text = tk.Text(
        root, height=20, width=110, font=("Calibri", 10), 
        bg="#333333", fg="#FFFFFF", bd=0, padx=10, pady=10
    )
    instruction_text.insert(tk.END, instruction_manual)
    instruction_text.config(state="disabled")
    instruction_text.pack(pady=5)

    def toggle_manual():
        if instruction_text.winfo_ismapped():
            instruction_text.pack_forget()
            toggle_button.config(text="Show Instructions")
        else:
            instruction_text.pack(pady=5)
            toggle_button.config(text="Hide Instructions")

    toggle_button = tk.Button(
        toggle_frame, text="Hide Instructions", command=toggle_manual, 
        bg="#E10600", fg="#FFFFFF", font=("Segoe UI", 10, "bold"), 
        activebackground="#A80400", activeforeground="#FFFFFF"
    )
    toggle_button.pack()

    # Query Label
    tk.Label(
        root, text="Ask a question:", fg="#FFFFFF", bg="#1E1E1E", 
        font=("Segoe UI", 14, "bold")
    ).pack(pady=5)

    # Query Entry Box
    query_entry = tk.Entry(
        root, width=70, font=("Segoe UI", 12), bg="#333333", fg="#FFFFFF", 
        insertbackground="#FFFFFF", relief="flat"
    )
    query_entry.pack(pady=10)

    # Result Display Box
    result_text = tk.Text(
        root, width=110, height=11, font=("Consolas", 11), 
        bg="#333333", fg="#FFFFFF", bd=0, padx=10, pady=10
    )
    result_text.pack(pady=10)

    # Handle Query Function
    def handle_query():
        nlp_query = query_entry.get().strip()
        if not nlp_query:
            messagebox.showwarning("Input Error", "Please enter a question.")
            return
        result = execute_query(nlp_query)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, result)

    # Ask Button
    tk.Button(
        root, text="Ask", command=handle_query, 
        bg="#E10600", fg="#FFFFFF", font=("Segoe UI", 12, "bold"), 
        activebackground="#A80400", activeforeground="#FFFFFF", width=12
    ).pack(pady=5)

    # Exit Button
    tk.Button(
        root, text="Exit", command=root.destroy, 
        bg="#333333", fg="#FFFFFF", font=("Segoe UI", 12, "bold"), 
        activebackground="#555555", activeforeground="#FFFFFF", width=12
    ).pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    launch_search_ui()