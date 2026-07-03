import tkinter as tk
from tkinter import messagebox, filedialog
import random
import json
import os
import csv
import time
import platform

APP_DIR = os.path.dirname(__file__)
LEADERBOARD_FILE = os.path.join(APP_DIR, "leaderboard.json")
SETTINGS_FILE = os.path.join(APP_DIR, "rps_settings.json")

# Game state
player_score = 0
computer_score = 0
round_no = 1
max_rounds = 5
choices = ["Rock", "Paper", "Scissors"]
history = []
last_round = None
playing = False
timer_seconds = 0
timer_job = None

# Default settings and themes
themes = {
    "Neon": {"bg": "#0f1724", "fg": "#e62c2c", "accent": "#00f5d4"},
    "Pastel": {"bg": "#fff8f0", "fg": "#333333", "accent": "#ffb4a2"},
    "Dark": {"bg": "#1e1e2f", "fg": "#f1f5f9", "accent": "#7c3aed"}
}
settings = {"theme": "Neon", "rounds": 5, "timer": 0, "mode": "Single", "difficulty": "Normal", "sound": True, "font_size": 12}

if os.path.exists(SETTINGS_FILE):
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings.update(json.load(f))
    except Exception:
        pass

# Main Window
root = tk.Tk()
root.title("Rock Paper Scissors — CodSoft Internship")
root.geometry("980x640")
root.minsize(900, 600)

player_name = tk.StringVar(value="Player")
player_avatar = tk.StringVar(value="🧑")
font_base = ("Segoe UI", settings.get("font_size", 12))

def save_settings():
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception:
        pass

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_leaderboard(board):
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(board, f, indent=2)
    except Exception:
        pass

leaderboard = load_leaderboard()

# Utility
def play_sound():
    if not settings.get("sound", True):
        return
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.MessageBeep()
        else:
            root.bell()
    except Exception:
        pass

def get_winner(p, c):
    if p == c:
        return "Tie"
    wins = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}
    return "Player" if wins[p] == c else "Computer"

def ai_choice():
    mode = settings.get("difficulty", "Normal")
    if mode == "Easy":
        return random.choice(choices)
    elif mode == "Hard":
        # Try to pick a winning choice against player's last move
        if history:
            last = history[-1].get("player")
            if last in choices and random.random() < 0.75:
                # choose the counter
                counter = {"Rock": "Paper", "Paper": "Scissors", "Scissors": "Rock"}
                return counter[last]
        return random.choice(choices)
    else:
        # Normal: slightly biased against player last move
        if history and random.random() < 0.6:
            last = history[-1].get("player")
            counter = {"Rock": "Paper", "Paper": "Scissors", "Scissors": "Rock"}
            return counter.get(last, random.choice(choices))
        return random.choice(choices)

def apply_theme():
    th = themes.get(settings.get("theme"), themes["Neon"])
    root.config(bg=th["bg"]) 
    for w in root.winfo_children():
        try:
            w.config(bg=th["bg"], fg=th["fg"]) 
        except Exception:
            pass
    try:
        title.config(bg=th["bg"], fg=th["accent"]) 
    except Exception:
        pass
    try:
        footer.config(bg=th["bg"], fg=th["fg"]) 
    except Exception:
        pass

def update_ui_scores():
    score_lbl.config(text=f"{player_avatar.get()} {player_score}   |   💻 {computer_score}")
    round_lbl.config(text=f"Round {round_no}/{max_rounds}")

def unlock_achievement(name):
    if name in achievements: return
    achievements.add(name)
    messagebox.showinfo("Achievement Unlocked!", f"🏅 {name}")

# Game functions
def finish_match():
    global playing
    playing = False
    if player_score > computer_score:
        winner_msg = f"🏆 {player_name.get()} Wins the Match!"
        leaderboard.append({"player": player_name.get(), "score": player_score, "against": computer_score, "time": time.ctime()})
        save_leaderboard(leaderboard)
        unlock_achievement("Champion")
    elif computer_score > player_score:
        winner_msg = "💻 Computer Wins the Match!"
    else:
        winner_msg = "🤝 Match Draw!"
    play_sound()
    messagebox.showinfo("Match Over", winner_msg)
    refresh_leaderboard()

def record_round(p_choice, c_choice, result):
    global last_round
    entry = {"round": round_no, "player": p_choice, "computer": c_choice, "result": result}
    history.append(entry)
    last_round = entry
    try:
        history_list.insert(tk.END, f"R{entry['round']}: {p_choice} vs {c_choice} -> {entry['result']}")
    except Exception:
        pass
    if len(history) > 100:
        history.pop(0)

def play_round(player_choice=None, pvp_second=False):
    global player_score, computer_score, round_no, playing, timer_job
    if settings.get("mode") == "PvP":
        # PvP: players take turns; if second selected, compute second player move
        if not pvp_second:
            player_choice_lbl.config(text=f"{player_avatar.get()} chose: {player_choice}")
            # store first player's choice in temp
            root.first_choice = player_choice
            result_lbl.config(text="Now Player 2 choose")
            return
        else:
            p1 = getattr(root, "first_choice", None)
            p2 = player_choice
            if not p1:
                return
            c_choice = p2
            result = get_winner(p1, c_choice)
            if result == "Player":
                player_score += 1
            elif result == "Computer":
                computer_score += 1
            record_round(p1, c_choice, result)
            result_lbl.config(text=f"{result} wins the round")
    else:
        if round_no > max_rounds:
            return
        if player_choice is None:
            player_choice = random.choice(choices)
        computer_choice = ai_choice()
        player_choice_lbl.config(text=f"{player_avatar.get()} {player_name.get()} chose: {player_choice}")
        computer_choice_lbl.config(text=f"💻 Computer chose: {computer_choice}")
        result = get_winner(player_choice, computer_choice)
        if result == "Player":
            player_score += 1
        elif result == "Computer":
            computer_score += 1
        record_round(player_choice, computer_choice, result)
        result_lbl.config(text=("🎉 You Win This Round!" if result=="Player" else ("😔 Computer Wins This Round!" if result=="Computer" else "🤝 It's a Tie!")))
        round_no += 1
        update_ui_scores()
        if round_no > max_rounds:
            finish_match()
        else:
            flash_result()

def reset_game():
    global player_score, computer_score, round_no, history, last_round, playing
    player_score = 0
    computer_score = 0
    round_no = 1
    history = []
    last_round = None
    playing = True
    try:
        history_list.delete(0, tk.END)
    except Exception:
        pass
    score_lbl.config(text=f"{player_avatar.get()} 0   |   💻 0")
    round_lbl.config(text=f"Round 1/{max_rounds}")
    result_lbl.config(text="Choose Your Move")

def undo_last():
    global player_score, computer_score, round_no
    if not history:
        messagebox.showinfo("Undo", "No rounds to undo")
        return
    last = history.pop()
    if last["result"] == "Player":
        player_score -= 1
    elif last["result"] == "Computer":
        computer_score -= 1
    round_no = max(1, last["round"])
    try:
        history_list.delete(0, tk.END)
        for h in history:
            history_list.insert(tk.END, f"R{h['round']}: {h['player']} vs {h['computer']} -> {h['result']}")
    except Exception:
        pass
    update_ui_scores()
    result_lbl.config(text="Last round undone")

def export_csv():
    if not history:
        messagebox.showinfo("Export", "No rounds to export")
        return
    path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
    if not path: return
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["Round","Player","Computer","Result"])
        for h in history:
            w.writerow([h['round'], h['player'], h['computer'], h['result']])
    messagebox.showinfo("Export", "History exported to CSV")

def share_result():
    root.clipboard_clear()
    root.clipboard_append(f"{player_name.get()} {player_score} - Computer {computer_score}")
    messagebox.showinfo("Share", "Result copied to clipboard")

# UI Layout
title = tk.Label(root, text="🎮 ROCK PAPER SCISSORS — CodSoft Internship 🎮", font=("Segoe UI", 20, "bold"))
title.pack(pady=10)

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=12)

left = tk.Frame(top_frame)
left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

right = tk.Frame(top_frame, width=320)
right.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=8)

# Left: Game area
name_frame = tk.Frame(left)
name_frame.pack(anchor='w')

tk.Label(name_frame, text="Player Name:", font=font_base).pack(side=tk.LEFT)
tk.Entry(name_frame, textvariable=player_name, font=font_base, width=18).pack(side=tk.LEFT, padx=6)
tk.Label(name_frame, text="Avatar:", font=font_base).pack(side=tk.LEFT, padx=(12,0))
tk.Entry(name_frame, textvariable=player_avatar, font=font_base, width=4).pack(side=tk.LEFT)

round_lbl = tk.Label(left, text=f"Round 1/{max_rounds}", font=("Segoe UI", 14, "bold"))
round_lbl.pack(pady=6)

score_lbl = tk.Label(left, text=f"{player_avatar.get()} 0   |   💻 0", font=("Segoe UI", 18, "bold"))
score_lbl.pack()

result_lbl = tk.Label(left, text="Choose Your Move", font=("Segoe UI", 16))
result_lbl.pack(pady=8)

btn_frame = tk.Frame(left)
btn_frame.pack(pady=12)

def handle_move(choice):
    # Wrap play_round to support PvP turn logic: first press stores, second press resolves
    try:
        if settings.get('mode') == 'PvP':
            first = getattr(root, 'first_choice', None)
            if first is None:
                play_round(choice, pvp_second=False)
            else:
                play_round(choice, pvp_second=True)
                root.first_choice = None
        else:
            play_round(choice)
    except Exception:
        play_round(choice)

rock_btn = tk.Button(btn_frame, text="🪨 Rock", font=font_base, width=12, height=2, command=lambda: handle_move("Rock"))
rock_btn.grid(row=0, column=0, padx=6)
paper_btn = tk.Button(btn_frame, text="📄 Paper", font=font_base, width=12, height=2, command=lambda: handle_move("Paper"))
paper_btn.grid(row=0, column=1, padx=6)
scissor_btn = tk.Button(btn_frame, text="✂️ Scissors", font=font_base, width=12, height=2, command=lambda: handle_move("Scissors"))
scissor_btn.grid(row=0, column=2, padx=6)

player_choice_lbl = tk.Label(left, text="", font=font_base)
player_choice_lbl.pack(pady=6)
computer_choice_lbl = tk.Label(left, text="", font=font_base)
computer_choice_lbl.pack()

controls = tk.Frame(left)
controls.pack(pady=10)
tk.Button(controls, text="🔄 New Match", command=lambda: (set_rounds_from_settings(), reset_game()), font=font_base).pack(side=tk.LEFT, padx=6)
tk.Button(controls, text="↶ Undo", command=undo_last, font=font_base).pack(side=tk.LEFT, padx=6)
tk.Button(controls, text="⬇ Export CSV", command=export_csv, font=font_base).pack(side=tk.LEFT, padx=6)
tk.Button(controls, text="📋 Share", command=share_result, font=font_base).pack(side=tk.LEFT, padx=6)

canvas = tk.Canvas(left, height=140)
canvas.pack(fill=tk.X, pady=8)

# Right: Settings, history, stats
tk.Label(right, text="Settings", font=("Segoe UI", 14, "bold")).pack(anchor='w')
settings_frame = tk.Frame(right)
settings_frame.pack(fill=tk.X, pady=6)

tk.Label(settings_frame, text="Theme:", font=font_base).grid(row=0, column=0, sticky='w')
theme_var = tk.StringVar(value=settings.get('theme'))
tk.OptionMenu(settings_frame, theme_var, *themes.keys(), command=lambda v: (settings.update({'theme':v}), apply_theme(), save_settings())).grid(row=0, column=1, sticky='w')

tk.Label(settings_frame, text="Rounds:", font=font_base).grid(row=1, column=0, sticky='w')
rounds_var = tk.IntVar(value=settings.get('rounds',5))
tk.Spinbox(settings_frame, from_=1, to=25, textvariable=rounds_var, width=5, command=lambda: settings.update({'rounds':rounds_var.get()}) or save_settings()).grid(row=1, column=1, sticky='w')

tk.Label(settings_frame, text="Mode:", font=font_base).grid(row=2, column=0, sticky='w')
mode_var = tk.StringVar(value=settings.get('mode','Single'))
tk.OptionMenu(settings_frame, mode_var, 'Single', 'PvP', command=lambda v: settings.update({'mode':v}) or save_settings()).grid(row=2, column=1, sticky='w')

tk.Label(settings_frame, text="Difficulty:", font=font_base).grid(row=3, column=0, sticky='w')
diff_var = tk.StringVar(value=settings.get('difficulty','Normal'))
tk.OptionMenu(settings_frame, diff_var, 'Easy', 'Normal', 'Hard', command=lambda v: settings.update({'difficulty':v}) or save_settings()).grid(row=3, column=1, sticky='w')

sound_var = tk.BooleanVar(value=settings.get('sound', True))
tk.Checkbutton(settings_frame, text='Sound', variable=sound_var, command=lambda: settings.update({'sound':sound_var.get()}) or save_settings()).grid(row=4, column=0, sticky='w')

tk.Label(settings_frame, text="Timer (s):", font=font_base).grid(row=5, column=0, sticky='w')
timer_var = tk.IntVar(value=settings.get('timer',0))
tk.Spinbox(settings_frame, from_=0, to=30, textvariable=timer_var, width=5, command=lambda: settings.update({'timer':timer_var.get()}) or save_settings()).grid(row=5, column=1, sticky='w')

tk.Button(right, text="View Leaderboard", command=lambda: show_leaderboard(), font=font_base).pack(fill=tk.X, pady=(8,4))

tk.Label(right, text="History", font=("Segoe UI", 12, "bold")).pack(anchor='w', pady=(10,0))
history_list = tk.Listbox(right, height=10)
history_list.pack(fill=tk.BOTH, expand=True)

tk.Label(right, text="Stats", font=("Segoe UI", 12, "bold")).pack(anchor='w', pady=(8,0))
stats_lbl = tk.Label(right, text="Wins: 0  Losses: 0  Ties: 0  Win%: 0%", wraplength=300, justify='left')
stats_lbl.pack(anchor='w')

achievements = set()

def refresh_stats():
    wins = sum(1 for h in history if h['result']=='Player')
    losses = sum(1 for h in history if h['result']=='Computer')
    ties = sum(1 for h in history if h['result']=='Tie')
    total = max(1, len(history))
    winp = int((wins/total)*100)
    stats_lbl.config(text=f"Wins: {wins}  Losses: {losses}  Ties: {ties}  Win%: {winp}%")

def refresh_leaderboard():
    # simple viewer
    b = load_leaderboard()
    if not b:
        messagebox.showinfo('Leaderboard', 'No scores yet')
        return
    s = '\n'.join([f"{i+1}. {e['player']} {e['score']} - {e['against']} ({e['time']})" for i,e in enumerate(sorted(b, key=lambda x:-x.get('score',0))[:20])])
    messagebox.showinfo('Leaderboard', s)

def show_leaderboard():
    refresh_leaderboard()

def set_rounds_from_settings():
    global max_rounds
    max_rounds = int(rounds_var.get())
    settings['rounds'] = max_rounds
    save_settings()

def flash_result(count=0):
    # simple color flash
    if count>4: return
    try:
        if count%2==0:
            result_lbl.config(fg=themes[settings['theme']]['accent'])
        else:
            result_lbl.config(fg=themes[settings['theme']]['fg'])
        root.after(180, lambda: flash_result(count+1))
    except Exception:
        pass

def confetti():
    # simple confetti animation
    colors = ['#ff3b3b','#ffd23f','#6effc8','#9ad0f5','#c77dff']
    pieces = []
    for i in range(30):
        x = random.randint(10, max(20, canvas.winfo_width()-10))
        y = random.randint(0, 40)
        c = canvas.create_oval(x, y, x+6, y+6, fill=random.choice(colors), outline='')
        pieces.append((c, random.uniform(1,3)))
    def animate():
        for obj, speed in pieces:
            canvas.move(obj, 0, speed)
            if canvas.coords(obj)[1] > 140:
                canvas.coords(obj, random.randint(10, max(20, canvas.winfo_width()-10)), 0, 6, 6)
        root.after(40, animate)
    animate()

# Keyboard shortcuts
def bind_keys():
    root.bind('<r>', lambda e: play_round('Rock'))
    root.bind('<p>', lambda e: play_round('Paper'))
    root.bind('<s>', lambda e: play_round('Scissors'))
    root.bind('<n>', lambda e: (set_rounds_from_settings(), reset_game()))

bind_keys()
apply_theme()
set_rounds_from_settings()
reset_game()

def periodic_refresh():
    refresh_stats()
    root.after(2000, periodic_refresh)

periodic_refresh()

root.protocol('WM_DELETE_WINDOW', lambda: (save_settings(), root.destroy()))

footer = tk.Label(root, text="CodSoft Internship Project | Python + Tkinter — Enhanced", font=("Segoe UI", 9))
footer.pack(side='bottom', pady=6)

# Allow a headless test mode via environment variable RPS_HEADLESS=1
if os.environ.get('RPS_HEADLESS') == '1':
    # simulate some button actions without launching GUI
    try:
        # monkeypatch messagebox / filedialog for headless
        messagebox.showinfo = lambda title, msg=None: print(f"MSG: {title} - {msg}")
        filedialog.asksaveasfilename = lambda **k: os.path.join(APP_DIR, 'headless_export.csv')

        settings['mode'] = 'Single'
        set_rounds_from_settings()
        reset_game()

        # simulate UI buttons: New Match, Rock, Paper, Scissors, Undo, Export, Share, Leaderboard
        print('HEADLESS TEST RUN START')
        print('-> New Match')
        set_rounds_from_settings(); reset_game()
        print('-> Press Rock')
        handle_move('Rock')
        print('-> Press Paper')
        handle_move('Paper')
        print('-> Press Scissors')
        handle_move('Scissors')
        print('-> Undo last')
        undo_last()
        print('-> Export CSV')
        export_csv()
        print('-> Share result')
        share_result()
        print('-> Show Leaderboard')
        show_leaderboard()

        # print summary to stdout for automated run
        print('HEADLESS TEST RUN SUMMARY')
        print('Player:', player_name.get())
        print('Score:', player_score, 'Computer:', computer_score)
        print('History:')
        for h in history:
            print(f"R{h['round']}: {h['player']} vs {h['computer']} -> {h['result']}")
    except Exception as e:
        print('HEADLESS ERROR', e)
else:
    bind_keys()
    root.mainloop()