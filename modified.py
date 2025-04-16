import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
from f1api import fetch_all_drivers,compare_cards
from f1_search_nlp import launch_search_ui
# Predefined users
VALID_CREDENTIALS = {}
with open("login.txt") as f:
    for line in f:
        if "," in line:  # Skip lines without commas
            user, pwd = line.strip().split(",")
            VALID_CREDENTIALS[user] = pwd

# Global variable to store drivers data
drivers = []

FONT_LARGE = ("Arial", 24, "bold")
FONT_MEDIUM = ("Arial", 16, "bold")
FONT_SMALL = ("Arial", 12)
COLOR_BG = "#121212"
COLOR_PRIMARY = "#e10600"  # F1 Red
COLOR_SECONDARY = "#ffffff"
COLOR_ACCENT = "#ffd700"  # Gold
COLOR_DARK = "#1e1e1e"

# Load credentials from file
VALID_CREDENTIALS = {}
with open("login.txt") as f:
    for line in f:
        if "," in line:
            user, pwd = line.strip().split(",")
            VALID_CREDENTIALS[user] = pwd

# Global variable to store drivers data
drivers = []



def load_image(parent, file_name, size=None):
    """Load image with error handling and reference storage"""
    if not os.path.exists(file_name):
        print(f"Image not found: {file_name}")
        return None
    
    try:
        img = Image.open(file_name)
        if size:
            img = img.resize(size, Image.LANCZOS)
        photo_img = ImageTk.PhotoImage(img)
        
        # Store reference
        if not hasattr(parent, 'image_references'):
            parent.image_references = {}
        key = f"{file_name}_{size if size else 'original'}"
        parent.image_references[key] = photo_img
        
        return photo_img
    except Exception as e:
        print(f"Error loading {file_name}: {e}")
        return None
def introduce_nlp():
    # Ask user if they want to explore NLP features
    response = messagebox.askyesno("NLP Assistant", "Do you want to explore the NLP features?")
    if response:
        launch_search_ui()  # Redirect to the NLP UI
    else:
        messagebox.showinfo("NLP Assistant", "Alright, hope you enjoy the other features!")
def create_nlp_button(parent,nlp_button):
    nlp_button.bind("<Button-1>", lambda e: introduce_nlp())

# Load images safely with reference storage
# def load_image(parent_widget, file_name, size=None):
#     if not os.path.exists(file_name):
#         print(f"Image not found: {file_name}")
#         return None
#     try:
#         img = Image.open(file_name)
#         if size:
#             img = img.resize(size, Image.LANCZOS)
#         photo_img = ImageTk.PhotoImage(img)
#         # Store reference in the parent widget
#         if not hasattr(parent_widget, 'image_references'):
#             parent_widget.image_references = {}
#         key = f"{file_name}_{size if size else 'original'}"
#         parent_widget.image_references[key] = photo_img
#         return photo_img
#     except Exception as e:
#         print(f"Error loading {file_name}: {e}")
#         return None

# import tkinter as tk


# Fetch all drivers from the database
def fetch_drivers_for_akinator():
    global drivers
    try:
        fetched_data = fetch_all_drivers()
        if not fetched_data:
            messagebox.showerror("Error", "No drivers found in the database for Akinator!", icon='error')
            return False
        required_keys = ["Name", "Nationality", "Team", "championships_won","Retired","teams_raced_for", "most_recent_championship_win"]
        drivers = [d for d in fetched_data if all(k in d for k in required_keys)]
        if not drivers:
            messagebox.showerror("Error", "Fetched drivers lack required attributes for Akinator!", icon='error')
            return False
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch drivers for Akinator: {e}", icon='error')
        return False

# --- Akinator Functions ---

def custom_showinfo(title, message):
    top = tk.Toplevel()
    top.title(title)
    top.configure(bg="black")
    top.grab_set()

    top.geometry("400x150")
    top.resizable(False, False)

    label = tk.Label(
        top, text=message, font=("Arial", 12, "bold"),
        bg="black", fg="white", wraplength=380, justify="center"
    )
    label.pack(pady=20)

    ok_button = tk.Button(
        top, text="OK", font=("Arial", 11, "bold"),
        fg="black", bg="red", width=10,
        command=top.destroy
    )
    ok_button.pack(pady=10)

    top.wait_window()


def custom_askyesno(title, question):
    response = None

    def on_yes():
        nonlocal response
        response = True
        top.destroy()

    def on_no():
        nonlocal response
        response = False
        top.destroy()

    top = tk.Toplevel()
    top.title(title)
    top.configure(bg="black")
    top.grab_set()

    top.geometry("400x150")
    top.resizable(False, False)

    label = tk.Label(
        top, text=question, font=("Arial", 12, "bold"),
        bg="black", fg="white", wraplength=380, justify="center"
    )
    label.pack(pady=20)

    button_frame = tk.Frame(top, bg="black")
    button_frame.pack(pady=10)

    yes_button = tk.Button(
        button_frame, text="Yes", font=("Arial", 11, "bold"),
        fg="black", bg="red", width=10, command=on_yes
    )
    yes_button.grid(row=0, column=0, padx=20)

    no_button = tk.Button(
        button_frame, text="No", font=("Arial", 11, "bold"),
        fg="black", bg="red", width=10, command=on_no
    )
    no_button.grid(row=0, column=1, padx=20)

    top.wait_window()
    return response

def ask_question(attribute, value):
    def on_yes():
        nonlocal response
        response = True
        top.destroy()

    def on_no():
        nonlocal response
        response = False
        top.destroy()

    question = f"Is the driver you're thinking of {value}?" if attribute == "Name" else f"Is the driver's {attribute} '{value}'?"

    response = None
    top = tk.Toplevel()
    top.title("Akinator Question")
    top.configure(bg="black")
    top.grab_set()  # Make window modal

    # Center window
    top.geometry("400x150")
    top.resizable(False, False)

    label = tk.Label(
        top, text=question, font=("Arial", 12, "bold"),
        bg="black", fg="white", wraplength=380, justify="center"
    )
    label.pack(pady=20)

    button_frame = tk.Frame(top, bg="black")
    button_frame.pack(pady=10)

    yes_button = tk.Button(
        button_frame, text="Yes", font=("Arial", 11, "bold"),
        fg="black", bg="red", width=10, command=on_yes
    )
    yes_button.grid(row=0, column=0, padx=20)

    

    no_button = tk.Button(
        button_frame, text="No", font=("Arial", 11, "bold"),
        fg="black", bg="red", width=10, command=on_no
    )
    no_button.grid(row=0, column=1, padx=20)

    top.wait_window()
    return response

def filter_drivers(drivers_list, attribute, value, is_positive):
    filtered_drivers = []
    for driver in drivers_list:
        driver_value = driver.get(attribute)
        if is_positive:
            if str(driver_value) == str(value):
                filtered_drivers.append(driver)
        else:
            if str(driver_value) != str(value):
                filtered_drivers.append(driver)
    return filtered_drivers

def play_akinator(remaining_drivers=None, asked_questions=None):
    global drivers
    
    if remaining_drivers is None:
        if not fetch_drivers_for_akinator():
            return
        remaining_drivers = drivers.copy()
        asked_questions = set()
    if not remaining_drivers:
        messagebox.showinfo("Akinator Result", "Hmm, I couldn't narrow it down based on the answers. Let's try again?", icon='info')
        return
    if len(remaining_drivers) == 1:
        guessed_driver = remaining_drivers[0]
        guess_message = f"Okay, I think the driver is {guessed_driver.get('Name', 'Unknown')}!"
        if messagebox.askyesno("Akinator Guess", guess_message, icon='question'):
            messagebox.showinfo("Akinator Result", "Great! I guessed correctly! 🎉", icon='info')
        else:
            messagebox.showinfo("Akinator Result", "Darn! I was wrong. Thanks for playing!", icon='info')
        return
    attribute, value = choose_next_question(remaining_drivers, asked_questions)
    if attribute is None:
        driver = remaining_drivers[0]
        guess_message = f"I'm running out of questions... Is it perhaps {driver.get('Name', 'Unknown')}?"
        if messagebox.askyesno("Akinator Best Guess", guess_message, icon='question'):
            messagebox.showinfo("Akinator Result", "Alright! I guessed correctly!", icon='info')
        else:
            others = ", ".join([d.get('Name', '??') for d in remaining_drivers[1:4]])
            if len(remaining_drivers) > 4:
                others += "..."
            messagebox.showinfo("Akinator Result", f"Oops! My guess was wrong. Maybe it was {others}?", icon='info')
        return
    question_key = f"{attribute}_{value}"
    asked_questions.add(question_key)
    is_positive = ask_question(attribute, value)
    filtered_drivers_list = filter_drivers(remaining_drivers, attribute, value, is_positive)
    if not filtered_drivers_list:
        messagebox.showinfo("Akinator Status", "Interesting! No drivers match that criteria. Let's backtrack slightly or try again.", icon='info')
        play_akinator(filtered_drivers_list, asked_questions)
        return
    play_akinator(filtered_drivers_list, asked_questions)

def choose_next_question(drivers_list, asked_questions):
    if not drivers_list or len(drivers_list) == 1:
        return None, None

    best_score = -1
    best_question = (None, None)

    # Ensure attributes exist in the fetched data
    attributes = ["Nationality", "Team", "championships_won", "teams_raced_for", "most_recent_championship_win"]
    possible_questions = []

    for attribute in attributes:
        # Use .get() with a default value to handle missing keys
        unique_values = set(str(driver.get(attribute, 'N/A')) for driver in drivers_list)
        for value in unique_values:
            if value == 'N/A':  # Skip if value was missing
                continue
            question_key = f"{attribute}_{value}"
            if question_key in asked_questions:
                continue

            # Calculate split
            matches = sum(1 for driver in drivers_list if str(driver.get(attribute, 'N/A')) == str(value))
            non_matches = len(drivers_list) - matches
            if matches == 0 or non_matches == 0:  # Doesn't split the group
                continue

            # Score based on how balanced the split is (closer to 50/50 is better)
            balance_score = 1.0 - abs(matches - non_matches) / len(drivers_list)
            possible_questions.append(((attribute, value), balance_score))

    if not possible_questions:
        # If no attribute questions left, try guessing a name we haven't asked about
        for driver in drivers_list:
            name = driver.get("Name")
            if name:
                question_key = f"Name_{name}"
                if question_key not in asked_questions:
                    return "Name", name  # Ask about a specific driver
        return None, None  # Truly stumped

    # Sort questions by score (higher score is better)
    possible_questions.sort(key=lambda item: item[1], reverse=True)
    best_question = possible_questions[0][0]  # Get the (attribute, value) tuple
    return best_question

# Open Akinator Game
def open_akinator_game():
    akinator_window = tk.Toplevel()
    akinator_window.title("F1 Akinator")
    akinator_window.geometry("1080x900")
    akinator_window.configure(bg="black")
    tk.Label(akinator_window, text="F1 Driver Akinator", fg="red", bg="black",
             font=("Arial", 20, "bold")).pack(pady=20)
    tk.Label(akinator_window, text="Think of an F1 driver... I will ask questions to guess who it is!",
             fg="white", bg="black", font=("Arial", 12), justify="center").pack(pady=10)
    tk.Button(akinator_window, text="Start Guessing!", bg="red", fg="black",
              font=("Arial", 14, "bold"), command=lambda: play_akinator(None, None)).pack(pady=20)
  
    
# --- Stat Attack Game (Keep Existing Code Here) ---
def open_stat_attack_game():
    # Your existing stat attack game code...
    # Remember to add icons to messageboxes here too if desired
    # e.g., messagebox.showerror("Error", "...", icon='error')
    # e.g., messagebox.showinfo("Game Over", "...", icon='info')
    # --- PASTE YOUR EXISTING open_stat_attack_game CODE HERE ---
    import tkinter as tk
    from tkinter import messagebox
    import random

    try:
        drivers_stat_attack = fetch_all_drivers() # Fetch fresh data for the game
        if not drivers_stat_attack or len(drivers_stat_attack) < 2: # Need at least 2 cards
             messagebox.showerror("Error", "Not enough driver data in the database to play Stat Attack!", icon='error')
             return
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch driver data: {e}", icon='error')
        return

    # Ensure drivers have necessary stats, provide defaults if missing
    attributes = ["WetCondition", "TopSpeed", "Focus", "Reflexes", "Tactics"]
    valid_drivers = []
    for driver in drivers_stat_attack:
         has_all_stats = True
         for attr in attributes:
              if driver.get(attr) is None:
                   # Option 1: Skip driver
                   # has_all_stats = False
                   # break
                   # Option 2: Assign default (e.g., 50)
                   driver[attr] = 50 # Assign default if missing
         #if has_all_stats: # Use this line if skipping drivers
         valid_drivers.append(driver)

    if len(valid_drivers) < 2: # Need at least 2 valid drivers
        messagebox.showerror("Error", "Not enough drivers with complete stats found to play!", icon='error')
        return

    # Remove duplicate drivers based on names (using valid drivers)
    unique_names = set()
    unique_drivers = []
    for driver in valid_drivers:
        name = driver.get('Name', '')
        if name and name not in unique_names:
            unique_drivers.append(driver)
            unique_names.add(name)

    if len(unique_drivers) < 2:
        messagebox.showerror("Error", "Not enough unique drivers with stats to play!", icon='error')
        return

    random.shuffle(unique_drivers)
    num_cards_each = min(len(unique_drivers) // 2, 5) # Deal up to 5 cards each

    if num_cards_each == 0:
         messagebox.showerror("Error", "Cannot deal cards for the game!", icon='error')
         return

    player_hand = unique_drivers[:num_cards_each]
    cpu_hand = unique_drivers[num_cards_each:num_cards_each*2]
    rounds_to_play = num_cards_each

    round_index = 0
    user_score = 0
    cpu_score = 0

    game_window = tk.Toplevel()
    game_window.title("Stat Attack")
    game_window.geometry("1080x900") # Slightly taller for more info
    game_window.configure(bg="black")

    title_label = tk.Label(game_window, text="F1 Stat Attack!", fg="red", bg="black", font=("Arial", 20, "bold"))
    title_label.pack(pady=10)

    # Frames for layout
    cards_frame = tk.Frame(game_window, bg="black")
    cards_frame.pack(pady=10, fill="x")
    player_card_frame = tk.Frame(cards_frame, bg="#222222", bd=2, relief="sunken")
    player_card_frame.pack(side="left", padx=20, pady=10, expand=True, fill="both")
    cpu_card_frame = tk.Frame(cards_frame, bg="#222222", bd=2, relief="sunken")
    cpu_card_frame.pack(side="right", padx=20, pady=10, expand=True, fill="both")

    control_frame = tk.Frame(game_window, bg="black")
    control_frame.pack(pady=10)

    info_frame = tk.Frame(game_window, bg="black")
    info_frame.pack(pady=10)

    round_info_label = tk.Label(info_frame, text=f"Round 1/{rounds_to_play}", fg="yellow", bg="black", font=("Arial", 14))
    round_info_label.pack(pady=2)

    score_label = tk.Label(info_frame, text="Score - You: 0  |  CPU: 0", fg="red", bg="black", font=("Arial", 16, "bold"))
    score_label.pack(pady=5)

    status_label = tk.Label(info_frame, text="", fg="lightgreen", bg="black", font=("Arial", 12))
    status_label.pack(pady=5)

    # Labels within card frames
    tk.Label(player_card_frame, text="Your Card", fg="cyan", bg="#222222", font=("Arial", 16)).pack(pady=5)
    user_card_label_name = tk.Label(player_card_frame, text="...", fg="white", bg="#222222", font=("Arial", 14, "bold"))
    user_card_label_name.pack(pady=5)
    user_card_labels_stats = {}
    for attr in attributes:
         lbl = tk.Label(player_card_frame, text=f"{attr}: ...", fg="white", bg="#222222", font=("Arial", 12))
         lbl.pack(anchor="w", padx=15)
         user_card_labels_stats[attr] = lbl

    tk.Label(cpu_card_frame, text="CPU Card", fg="orange", bg="#222222", font=("Arial", 16)).pack(pady=5)
    cpu_card_label_name = tk.Label(cpu_card_frame, text="???", fg="grey", bg="#222222", font=("Arial", 14, "bold"))
    cpu_card_label_name.pack(pady=5)
    cpu_card_labels_stats = {}
    for attr in attributes:
         lbl = tk.Label(cpu_card_frame, text=f"{attr}: ???", fg="grey", bg="#222222", font=("Arial", 12))
         lbl.pack(anchor="w", padx=15)
         cpu_card_labels_stats[attr] = lbl


    def update_score():
        score_label.config(text=f"Score - You: {user_score}  |  CPU: {cpu_score}")

    def display_card(card, name_label, stat_labels, reveal=True):
         name_label.config(text=card.get('Name', 'N/A'))
         for attr, label in stat_labels.items():
              value = card.get(attr, '??')
              label.config(text=f"{attr}: {value if reveal else '???'}", fg="white" if reveal else "grey")
         name_label.config(fg="white" if reveal else "grey")


    def next_round_logic():
        nonlocal round_index, user_score, cpu_score, player_hand, cpu_hand

        if round_index >= rounds_to_play:
            winner = "You Win!" if user_score > cpu_score else "CPU Wins!" if cpu_score > user_score else "It's a Draw!"
            messagebox.showinfo(
                "Game Over",
                f"Final Score:\nYou: {user_score}\nCPU: {cpu_score}\n\n🏁 {winner} 🏁",
                icon = 'info' if winner != "CPU Wins!" else 'warning'
            )
            game_window.destroy()
            return

        # Clear previous controls
        for widget in control_frame.winfo_children():
            widget.destroy()

        # Reset CPU card display
        display_card({}, cpu_card_label_name, cpu_card_labels_stats, reveal=False)
        status_label.config(text="")

        if not player_hand or not cpu_hand:
            messagebox.showerror("Error", "Not enough cards to continue the game.", icon='error')
            game_window.destroy()
            return

        user_card = player_hand[0] # Don't pop yet, wait for selection
        cpu_card = cpu_hand[0]

        display_card(user_card, user_card_label_name, user_card_labels_stats, reveal=True)
        round_info_label.config(text=f"Round {round_index + 1}/{rounds_to_play}")


        def do_battle(selected_attr):
            nonlocal user_score, cpu_score, round_index
            # Now pop the cards
            current_user_card = player_hand.pop(0)
            current_cpu_card = cpu_hand.pop(0)

            user_value = current_user_card.get(selected_attr)
            cpu_value = current_cpu_card.get(selected_attr)

            # Reveal CPU card
            display_card(current_cpu_card, cpu_card_label_name, cpu_card_labels_stats, reveal=True)

            # Highlight selected stat
            user_card_labels_stats[selected_attr].config(fg="yellow", font=("Arial", 12, "bold"))
            cpu_card_labels_stats[selected_attr].config(fg="yellow", font=("Arial", 12, "bold"))


            if user_value is None or cpu_value is None:
                messagebox.showwarning("Attribute Error", f"Cannot compare attribute '{selected_attr}'. Skipping round.", icon='warning')
                status_label.config(text="Attribute Error! Skipping round.")
            else:
                # Convert to numbers for comparison if possible
                try:
                    user_value = float(user_value)
                    cpu_value = float(cpu_value)
                    result = compare_cards(current_user_card, current_cpu_card, selected_attr) # Assumes compare_cards handles numbers

                    if result == "user":
                        user_score += 1
                        status_label.config(text=f"You win this round! ({selected_attr}: {user_value} vs {cpu_value})", fg="lightgreen")
                    elif result == "cpu":
                        cpu_score += 1
                        status_label.config(text=f"CPU wins this round! ({selected_attr}: {user_value} vs {cpu_value})", fg="orange")
                    else:
                        status_label.config(text=f"It's a tie! ({selected_attr}: {user_value} vs {cpu_value})", fg="yellow")

                except ValueError:
                     messagebox.showerror("Data Error", f"Cannot compare non-numeric stats for '{selected_attr}'.", icon='error')
                     status_label.config(text="Data Error! Cannot compare.")
                except Exception as e:
                     messagebox.showerror("Comparison Error", f"Error comparing cards: {e}", icon='error')
                     status_label.config(text="Error comparing cards.")

            update_score()
            round_index += 1

            # Disable buttons after choice
            for widget in control_frame.winfo_children():
                 if isinstance(widget, tk.Button):
                      widget.config(state="disabled")

            # Schedule next round
            game_window.after(3000, next_round_logic) # 3 second delay before next round


        # Determine turn
        is_user_turn = (round_index % 2 == 0) # User goes first on even rounds (0, 2, 4)

        if is_user_turn:
            tk.Label(control_frame, text="Your Turn: Choose an Attribute", fg="white", bg="black", font=("Arial", 14)).pack()
            button_frame = tk.Frame(control_frame, bg="black")
            button_frame.pack(pady=5)
            for idx, attr in enumerate(attributes):
                btn = tk.Button(button_frame, text=attr, command=lambda a=attr: do_battle(a), width=12, font=("Arial", 11), bg="#555", fg="white")
                btn.grid(row=0, column=idx, padx=5)
        else:     # CPU Turn
            tk.Label(control_frame, text="CPU Turn: Choosing Attribute...", fg="white", bg="black", font=("Arial", 14)).pack()
            # CPU Strategy: Pick its best stat from the current card
            best_cpu_attr = attributes[0]
            max_val = -1
            for attr in attributes:
                 val = cpu_card.get(attr, 0)
                 try:
                      val = float(val)
                      if val > max_val:
                           max_val = val
                           best_cpu_attr = attr
                 except ValueError:
                      continue # Skip non-numeric

            status_label.config(text=f"CPU chooses {best_cpu_attr}!")
            game_window.after(2000, lambda: do_battle(best_cpu_attr)) # Wait 2s then battle


    # Start the first round
    next_round_logic()

    tk.Button(game_window, text="Quit Game", command=game_window.destroy, bg="darkred", fg="white", font=("Arial", 12, "bold")).pack(pady=15)

# --- End Stat Attack Game ---

# Function to show login screen after loading
def show_login():
    loading_canvas.destroy()
    

        
    # Login Frame (Bezel-Like)
    frame = tk.Frame(root, bg="black", bd=2, relief="ridge", highlightbackground="red", highlightthickness=3)
    frame.place(relx=0.5, rely=0.55, anchor="center", width=350, height=300)  # Increased height for guest button
    
    tk.Label(frame, text="F1 LOGIN", fg="red", bg="black", font=("Arial", 20, "bold")).pack(pady=10)
    tk.Label(frame, text="Username:", fg="white", bg="black", font=("Arial", 14)).pack()
    username_entry = tk.Entry(frame, bg="black", fg="red", font=("Arial", 14), width=25)
    username_entry.pack(pady=5)
    
    tk.Label(frame, text="Password:", fg="white", bg="black", font=("Arial", 14)).pack()
    password_entry = tk.Entry(frame, bg="black", fg="red", font=("Arial", 14), width=25, show="*")
    password_entry.pack(pady=5)
    
    tk.Button(frame, text="LOGIN", bg="red", fg="black", font=("Arial", 14, "bold"), width=15,
              command=lambda: login(username_entry.get().strip(), password_entry.get().strip())).pack(pady=10)
    
    # Guest view button added
    tk.Button(frame, text="GUEST VIEW", bg="gray", fg="black", font=("Arial", 14, "bold"), width=15,
              command=lambda: open_dashboard("Guest", is_guest=True)).pack(pady=5)

def login(username, password):
    if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
        messagebox.showinfo("Login Success", f"Welcome, {username}!")
        open_dashboard(username, is_guest=False)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

# Open Dashboard
def open_dashboard(username, is_guest=False):
    root.destroy()  # Close login window
    dashboard = tk.Tk()
    dashboard.title("F1 Dashboard")
    dashboard.attributes("-fullscreen", True)
    dashboard.bind("<Escape>", lambda e: dashboard.attributes("-fullscreen", False))
    
    # Initialize image references storage
    dashboard.image_references = {}
    
    screen_width, screen_height = dashboard.winfo_screenwidth(), dashboard.winfo_screenheight()
    black_bg = load_image(dashboard, "black.jpg", (screen_width, screen_height))
    
    bg_canvas = tk.Canvas(dashboard, bg="black")
    bg_canvas.pack(fill="both", expand=True)
    
    if black_bg:
        bg_canvas.create_image(0, 0, image=black_bg, anchor="nw")
        
    # Bezel-Like Content Frame
    content_frame = tk.Frame(dashboard, bg="black", bd=5, relief="ridge", highlightbackground="red", highlightthickness=4)
    content_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=650)
    
    nlp_button = tk.Label(bg_canvas, text="Click here to interact with NLP Assistant", bg="red", fg="black", font=("Arial", 14, "bold"))
    nlp_button.pack(pady=10)
    # Logo
    logo_img = load_image(dashboard, "f1_logo.jpg", (300, 150))
    if logo_img:
        logo_label = tk.Label(content_frame, image=logo_img, bg="black")
        logo_label.pack(pady=(20, 10))
        
    # Welcome Message
    welcome_text = f"Welcome, {username}!" + (" (Guest Mode)" if is_guest else "")
    tk.Label(content_frame, text=welcome_text, fg="red", bg="black", font=("Arial", 24, "bold")).pack(pady=10)
    
    # Buttons
    button_frame = tk.Frame(content_frame, bg="black")
    button_frame.pack(pady=20)
    
    btn_style = {
        "bg": "red",
        "fg": "black",
        "font": ("Arial", 16, "bold"),
        "width": 20,
        "height": 2,
        "bd": 0,
        "highlightthickness": 0
    }
    
    # View Database Button
    btn_view_db = tk.Button(button_frame, text="View Database", **btn_style, 
                       command=lambda: open_database_viewer(is_guest))
    btn_view_db.grid(row=0, column=0, padx=10, pady=10)
    
    # Reverse Akinator Button
    btn_reverse_akinator = tk.Button(button_frame, text="F1Akinator", **btn_style,
                                    command=open_akinator_game)
    btn_reverse_akinator.grid(row=1, column=0, padx=10, pady=10)
    
    # Stat Attack Button
    btn_stat_attack = tk.Button(button_frame, text="Stat Attack", **btn_style, command=open_stat_attack_game)
    btn_stat_attack.grid(row=2, column=0, padx=10, pady=10)
    
    create_nlp_button(dashboard,nlp_button)
    dashboard.mainloop()
def open_database_viewer(is_guest=False):
    def show_selection_menu():
        for widget in db_window.winfo_children():
            widget.destroy()

        tk.Label(db_window, text="Select View", fg="red", bg="black", font=("Arial", 24, "bold")).pack(pady=30)

        options = [
            ("Driver Standings", show_driver_standings),
            ("Constructor Standings", show_constructor_standings),
            ("Race Results", show_race_results)
        ]

        for text, command in options:
            tk.Button(db_window, text=text, font=("Arial", 16, "bold"), width=25,
                      bg="red", fg="black", command=command).pack(pady=10)

    def show_driver_standings():
        from f1api import fetch_driver_statistics, insert_driver_standing, update_driver_standing, delete_driver_standing

        def load_data(year):
            for row in tree.get_children():
                tree.delete(row)
            for stat in fetch_driver_statistics():
                if str(stat["season"]) == year:
                    tree.insert("", "end", values=[
                        stat["season"], stat["position"], stat["driver_name"], stat["team_name"], stat["points"]
                    ])

        for widget in db_window.winfo_children():
            widget.destroy()

        # --- Top Control Bar ---
        top_frame = tk.Frame(db_window, bg="black")
        top_frame.pack(anchor="nw", fill="x", padx=10, pady=10)

        # Back Button
        tk.Button(top_frame, text="← Back", bg="gray", fg="black", font=("Arial", 12, "bold"),
                command=show_selection_menu).pack(side="left")

        # Year Dropdown
        years = sorted(set(str(d["season"]) for d in fetch_driver_statistics()))
        selected_year = tk.StringVar(value=years[-1] if years else "")
        year_box = ttk.Combobox(top_frame, textvariable=selected_year, values=years,
                                state="readonly", width=10)
        year_box.pack(side="left", padx=10)

        # Load Button
        tk.Button(top_frame, text="Load", command=lambda: load_data(selected_year.get()),
                bg="red", fg="black", font=("Arial", 10, "bold")).pack(side="left")

        # --- CRUD Buttons (Admins Only) ---
        if not is_guest:
            def open_form(mode="add"):
                form = tk.Toplevel(db_window)
                form.title(f"{mode.capitalize()} Driver Standing")
                form.geometry("400x400")
                form.configure(bg="black")

                fields = ["season", "position", "driver_name", "team_name", "points"]
                entries = {}

                values = tree.item(tree.selection()[0])["values"] if mode == "edit" and tree.selection() else [""] * 5

                for i, field in enumerate(fields):
                    tk.Label(form, text=field.replace("_", " ").title(), bg="black", fg="white", font=("Arial", 12)).grid(row=i, column=0, sticky="e", padx=10, pady=5)
                    entry = tk.Entry(form, width=25, font=("Arial", 12))
                    entry.grid(row=i, column=1, pady=5)
                    entry.insert(0, values[i])
                    entries[field] = entry

                def submit():
                    try:
                        data = {
                            "season": int(entries["season"].get()),
                            "position": int(entries["position"].get()),
                            "driver_name": entries["driver_name"].get(),
                            "team_name": entries["team_name"].get(),
                            "points": float(entries["points"].get())
                        }

                        if mode == "add":
                            insert_driver_standing(**data)
                        else:
                            update_driver_standing(data["season"], data["driver_name"], data["position"], data["team_name"], data["points"])

                        messagebox.showinfo("Success", f"{mode.capitalize()} successful!")
                        load_data(str(data["season"]))
                        form.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))

                tk.Button(form, text="Submit", command=submit, bg="red", fg="black", font=("Arial", 12, "bold")).grid(row=len(fields), column=0, columnspan=2, pady=15)
#it gets over here
            def delete_selected():
                if not tree.selection():
                    return messagebox.showwarning("Select", "Please select a row to delete.")
                values = tree.item(tree.selection()[0])["values"]
                if messagebox.askyesno("Confirm", f"Delete {values[2]} from {values[0]}?"):
                    delete_driver_standing(values[0], values[2])
                    load_data(str(values[0]))
                    messagebox.showinfo("Deleted", "Entry removed.")

            tk.Button(top_frame, text="Add", bg="green", fg="black", font=("Arial", 10, "bold"),
                    command=lambda: open_form("add")).pack(side="right", padx=5)
            tk.Button(top_frame, text="Edit", bg="orange", fg="black", font=("Arial", 10, "bold"),
                    command=lambda: open_form("edit")).pack(side="right", padx=5)
            tk.Button(top_frame, text="Delete", bg="darkred", fg="white", font=("Arial", 10, "bold"),
                    command=delete_selected).pack(side="right", padx=5)

        # --- Section Title ---
        tk.Label(db_window, text="Driver Standings", fg="red", bg="black",
                font=("Arial", 20, "bold")).pack(pady=(10, 5))

        # --- Treeview Styling ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="black",
                        foreground="white",
                        fieldbackground="black",
                        font=("Arial", 12),
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background="red",
                        foreground="black",
                        font=("Arial", 13, "bold"))
        style.map("Treeview", background=[("selected", "darkred")])

        # --- Treeview ---
        cols = ("Season", "Position", "Driver Name", "Team Name", "Points")
        tree = ttk.Treeview(db_window, columns=cols, show="headings", height=20, style="Treeview")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        # --- Auto-load latest year on open ---
        if years:
            load_data(years[-1])

    

    def show_constructor_standings():
        from f1api import fetch_constructor_standings, insert_constructor_standing, update_constructor_standing, delete_constructor_standing

        def load_data(year):
            for row in tree.get_children():
                tree.delete(row)
            for stat in fetch_constructor_standings():
                if str(stat["season"]) == year:
                    tree.insert("", "end", values=[
                        stat["season"], stat["position"], stat["constructor_name"], stat["points"]
                    ])

        for widget in db_window.winfo_children():
            widget.destroy()

        # --- Top Controls ---
        top_frame = tk.Frame(db_window, bg="black")
        top_frame.pack(anchor="nw", fill="x", padx=10, pady=10)

        # Back button
        tk.Button(top_frame, text="← Back", bg="gray", fg="black", font=("Arial", 12, "bold"),
                command=show_selection_menu).pack(side="left")

        years = sorted(set(str(c["season"]) for c in fetch_constructor_standings()))
        selected_year = tk.StringVar(value=years[-1] if years else "")
        ttk.Combobox(top_frame, textvariable=selected_year, values=years,
                    state="readonly", width=10).pack(side="left", padx=10)

        tk.Button(top_frame, text="Load", command=lambda: load_data(selected_year.get()),
                bg="red", fg="black", font=("Arial", 10, "bold")).pack(side="left")

        # --- CRUD Buttons (Admins Only) ---
        if not is_guest:
            def open_form(mode="add"):
                form = tk.Toplevel(db_window)
                form.title(f"{mode.capitalize()} Constructor Standing")
                form.geometry("400x300")
                form.configure(bg="black")

                fields = ["season", "position", "constructor_name", "points"]
                entries = {}

                values = tree.item(tree.selection()[0])["values"] if mode == "edit" and tree.selection() else [""] * 4

                for i, field in enumerate(fields):
                    tk.Label(form, text=field.replace("_", " ").title(), bg="black", fg="white", font=("Arial", 12)).grid(row=i, column=0, sticky="e", padx=10, pady=5)
                    entry = tk.Entry(form, width=25, font=("Arial", 12))
                    entry.grid(row=i, column=1, pady=5)
                    entry.insert(0, values[i])
                    entries[field] = entry

                def submit():
                    try:
                        data = {
                            "season": int(entries["season"].get()),
                            "position": int(entries["position"].get()),
                            "constructor_name": entries["constructor_name"].get(),
                            "points": float(entries["points"].get())
                        }

                        if mode == "add":
                            insert_constructor_standing(**data)
                        else:
                            update_constructor_standing(data["season"], data["constructor_name"], data["position"], data["points"])

                        messagebox.showinfo("Success", f"{mode.capitalize()} successful!")
                        load_data(str(data["season"]))
                        form.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))

                tk.Button(form, text="Submit", command=submit, bg="red", fg="black", font=("Arial", 12, "bold")).grid(row=len(fields), column=0, columnspan=2, pady=15)

            def delete_selected():
                if not tree.selection():
                    return messagebox.showwarning("Select", "Please select a row to delete.")
                values = tree.item(tree.selection()[0])["values"]
                if messagebox.askyesno("Confirm", f"Delete {values[2]} from {values[0]}?"):
                    delete_constructor_standing(values[0], values[2])
                    load_data(str(values[0]))
                    messagebox.showinfo("Deleted", "Entry removed.")

            tk.Button(top_frame, text="Add", bg="green", fg="black", font=("Arial", 10, "bold"),
                    command=lambda: open_form("add")).pack(side="right", padx=5)
            tk.Button(top_frame, text="Edit", bg="orange", fg="black", font=("Arial", 10, "bold"),
                    command=lambda: open_form("edit")).pack(side="right", padx=5)
            tk.Button(top_frame, text="Delete", bg="darkred", fg="white", font=("Arial", 10, "bold"),
                    command=delete_selected).pack(side="right", padx=5)

        # --- Title ---
        tk.Label(db_window, text="Constructor Standings", fg="red", bg="black",
                font=("Arial", 20, "bold")).pack(pady=(10, 5))

        # --- Treeview Style ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="black",
                        foreground="white",
                        fieldbackground="black",
                        font=("Arial", 12),
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background="red",
                        foreground="black",
                        font=("Arial", 13, "bold"))
        style.map("Treeview", background=[("selected", "darkred")])

        # --- Treeview ---
        cols = ("Season", "Position", "Constructor Name", "Points")
        tree = ttk.Treeview(db_window, columns=cols, show="headings", height=20, style="Treeview")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        # --- Auto-load most recent year ---
        if years:
            load_data(years[-1])



    def show_race_results():
        from f1api import fetch_race_results, insert_race_result, update_race_result, delete_race_result

        race_data = fetch_race_results()

        def update_race_dropdown(*args):
            selected = season_var.get()
            filtered = sorted(set(r["race_name"] for r in race_data if str(r["season"]) == selected))
            race_var.set(filtered[0] if filtered else "")
            race_menu["values"] = filtered

        def load_data():
            season = season_var.get()
            race_name = race_var.get()

            results = [r for r in race_data if str(r["season"]) == season and r["race_name"] == race_name]
            results.sort(key=lambda r: (r["position"] if r["position"] is not None else 999))

            for row in tree.get_children():
                tree.delete(row)
            for result in results:
                tree.insert("", "end", values=[
                    result["season"],
                    result["round"],
                    result["race_name"],
                    result["driver_name"],
                    result["constructor_name"],
                    result["position"],
                    result["points"],
                    result["fastest_lap"]
                ])

        for widget in db_window.winfo_children():
            widget.destroy()

        # --- Top Bar ---
        top_frame = tk.Frame(db_window, bg="black")
        top_frame.pack(anchor="nw", fill="x", padx=10, pady=10)

        tk.Button(top_frame, text="← Back", bg="gray", fg="black", font=("Arial", 12, "bold"),
                command=show_selection_menu).pack(side="left")

        tk.Label(top_frame, text="Season", fg="white", bg="black", font=("Arial", 12)).pack(side="left", padx=5)
        season_var = tk.StringVar()
        seasons = sorted(set(str(r["season"]) for r in race_data))
        season_menu = ttk.Combobox(top_frame, textvariable=season_var, values=seasons, state="readonly", width=10)
        season_menu.pack(side="left", padx=5)

        tk.Label(top_frame, text="Race", fg="white", bg="black", font=("Arial", 12)).pack(side="left", padx=5)
        race_var = tk.StringVar()
        race_menu = ttk.Combobox(top_frame, textvariable=race_var, values=[], state="readonly", width=20)
        race_menu.pack(side="left", padx=5)

        tk.Button(top_frame, text="Load Results", command=load_data,
                bg="red", fg="black", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        # --- CRUD Buttons (Admins Only) ---
        if not is_guest:
            def open_form(mode="add"):
                form = tk.Toplevel(db_window)
                form.title(f"{mode.capitalize()} Race Result")
                form.geometry("500x500")
                form.configure(bg="black")

                fields = ["season", "round", "race_name", "driver_name", "constructor_name", "position", "points", "fastest_lap"]
                entries = {}

                values = tree.item(tree.selection()[0])["values"] if mode == "edit" and tree.selection() else [""] * len(fields)

                for i, field in enumerate(fields):
                    tk.Label(form, text=field.replace("_", " ").title(), bg="black", fg="white", font=("Arial", 12)).grid(row=i, column=0, sticky="e", padx=10, pady=5)
                    entry = tk.Entry(form, width=30, font=("Arial", 12))
                    entry.grid(row=i, column=1, pady=5)
                    entry.insert(0, values[i])
                    entries[field] = entry

                def submit():
                    try:
                        data = {
                            "season": int(entries["season"].get()),
                            "round_num": int(entries["round"].get()),
                            "race_name": entries["race_name"].get(),
                            "driver_name": entries["driver_name"].get(),
                            "constructor_name": entries["constructor_name"].get(),
                            "position": int(entries["position"].get()),
                            "points": float(entries["points"].get()),
                            "fastest_lap": entries["fastest_lap"].get()
                        }

                        if mode == "add":
                            insert_race_result(**data)
                        else:
                            update_race_result(**data)

                        messagebox.showinfo("Success", f"{mode.capitalize()} successful!")
                        race_data.clear()
                        race_data.extend(fetch_race_results())  # reload for dropdowns
                        update_race_dropdown()
                        load_data()
                        form.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))

                tk.Button(form, text="Submit", command=submit, bg="red", fg="black", font=("Arial", 12, "bold")).grid(row=len(fields), column=0, columnspan=2, pady=20)

            def delete_selected():
                if not tree.selection():
                    return messagebox.showwarning("Select", "Please select a row to delete.")
                values = tree.item(tree.selection()[0])["values"]
                if messagebox.askyesno("Confirm", f"Delete result for {values[3]} in {values[2]}?"):
                    delete_race_result(values[0], values[1], values[2], values[3])
                    race_data.clear()
                    race_data.extend(fetch_race_results())
                    update_race_dropdown()
                    load_data()
                    messagebox.showinfo("Deleted", "Entry removed.")

            tk.Button(top_frame, text="Add", bg="green", fg="black", font=("Arial", 10, "bold"),
                    command=lambda: open_form("add")).pack(side="right", padx=5)
            tk.Button(top_frame, text="Edit", bg="orange", fg="black", font=("Arial", 10, "bold"),
                    command=lambda: open_form("edit")).pack(side="right", padx=5)
            tk.Button(top_frame, text="Delete", bg="darkred", fg="white", font=("Arial", 10, "bold"),
                    command=delete_selected).pack(side="right", padx=5)

        # --- Label ---
        tk.Label(db_window, text="Race Results", fg="red", bg="black",
                font=("Arial", 20, "bold")).pack(pady=(10, 5))

        # --- Treeview Style ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="black",
                        foreground="white",
                        fieldbackground="black",
                        font=("Arial", 12),
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background="red",
                        foreground="black",
                        font=("Arial", 13, "bold"))
        style.map("Treeview", background=[("selected", "darkred")])

        # --- Table ---
        cols = ("Season", "Round", "Race", "Driver", "Constructor", "Position", "Points", "Fastest Lap")
        tree = ttk.Treeview(db_window, columns=cols, show="headings", height=20, style="Treeview")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        season_var.trace_add("write", update_race_dropdown)

        if seasons:
            season_var.set(seasons[-1])






    # Create the base window
    db_window = tk.Toplevel()
    db_window.title("F1 Database Viewer")
    db_window.geometry("1080x900")
    db_window.configure(bg="black")
    db_window.image_references = {}

    show_selection_menu()

# Main application start
if __name__ == "__main__":
    # Initialize image references dictionary in root
    root = tk.Tk()
    root.title("F1 Application")
    root.configure(bg="black")
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    root.image_references = {}
    
    # Loading Screen
    loading_canvas = tk.Canvas(root, bg="black", highlightthickness=0)
    loading_canvas.pack(fill="both", expand=True)
    
    loading_logo = load_image(root, "f1_logo.jpg", (800, 400))
    if loading_logo:
        loading_canvas.create_image(root.winfo_screenwidth()//2, root.winfo_screenheight()//2, anchor="center", image=loading_logo)
    
    root.after(3000, show_login)  # Show login after 3 seconds
    root.mainloop()