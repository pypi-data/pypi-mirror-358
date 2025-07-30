import tkinter as tk
from tkinter import messagebox
import requests
import html
import random
import json
import os
from tkinter import PhotoImage
# ------------------------------
# Constants and styles
# ------------------------------

BG_COLOR = "#f0f4f8"
PANEL_BG = "#ffffff"
ACCENT_COLOR = "#4a90e2"
TEXT_COLOR = "#333333"
CORRECT_COLOR = "#28a745"
WRONG_COLOR = "#dc3545"
FONT_LARGE = ("Segoe UI", 24, "bold")
FONT_MEDIUM = ("Segoe UI", 16)
FONT_SMALL = ("Segoe UI", 12)

STATS_FILE = os.path.join(os.path.expanduser("~"), ".trivia_stats.json")


# ------------------------------
# Rounded Button using Canvas
# ------------------------------

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=200, height=50, radius=20, bg=ACCENT_COLOR, fg="white", font=FONT_MEDIUM):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent["bg"])
        self.command = command
        self.radius = radius
        self.bg = bg
        self.fg = fg
        self.font = font
        self.text = text
        self.width = width
        self.height = height

        self.create_rounded_rect(0, 0, width, height, radius, fill=bg, outline="")
        self.text_id = self.create_text(width // 2, height // 2, text=text, fill=fg, font=font)

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.itemconfig(1, fill="#357ABD")  # Slightly darker on hover

    def _on_leave(self, event):
        self.itemconfig(1, fill=self.bg)


# ------------------------------
# Main Game class
# ------------------------------

class TriviaShow:
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.app = TriviaApp(difficulty)

    def run(self):
        self.app.mainloop()


# ------------------------------
# TriviaApp Main Tk window
# ------------------------------

class TriviaApp(tk.Tk):
    def __init__(self, difficulty):
        super().__init__()
        self.title("QuasttShow")
        self.geometry("1200x800")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.difficulty = difficulty
        self.questions = []
        self.current_q_index = 0
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.paused = False
        self.ai_stats = {"correct_by_category": {}, "questions_answered": 0, "correct_answers": 0}

        self.stats = self.load_stats()

        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.pack(expand=True, fill="both")

        self.frames = {}
        for F in (MenuFrame, GameFrame, StatsFrame, PauseOverlay):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("MenuFrame")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {"games_played": 0, "total_score": 0, "max_score": 0, "max_streak": 0}
        else:
            return {"games_played": 0, "total_score": 0, "max_score": 0, "max_streak": 0}

    def save_stats(self):
        try:
            with open(STATS_FILE, "w") as f:
                json.dump(self.stats, f)
        except Exception:
            pass

    def fetch_questions(self, amount=15, difficulty=None, qtype='multiple'):
        difficulty = difficulty or self.difficulty
        url = f"https://opentdb.com/api.php?amount={amount}&difficulty={difficulty}&type={qtype}"
        try:
            response = requests.get(url)
            data = response.json()
            if data["response_code"] != 0:
                return []
            return data["results"]
        except Exception:
            return []

    def start_new_game(self):
        self.questions = self.fetch_questions()
        if not self.questions:
            messagebox.showerror("Error", "Failed to fetch questions. Check your internet connection.")
            self.show_frame("MenuFrame")
            return
        self.current_q_index = 0
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.ai_stats = {"correct_by_category": {}, "questions_answered": 0, "correct_answers": 0}
        self.paused = False
        self.frames["GameFrame"].load_question()
        self.show_frame("GameFrame")

    def update_game_stats(self, correct, category):
        self.ai_stats['questions_answered'] += 1
        if correct:
            self.ai_stats['correct_answers'] += 1
            self.ai_stats['correct_by_category'][category] = \
                self.ai_stats['correct_by_category'].get(category, 0) + 1

    def end_game(self):
        self.stats["games_played"] += 1
        self.stats["total_score"] += self.score
        self.stats["max_score"] = max(self.stats.get("max_score", 0), self.score)
        self.stats["max_streak"] = max(self.stats.get("max_streak", 0), self.max_streak)
        self.save_stats()
        msg = f"Game Over!\nFinal Score: {self.score}\nMax Streak: {self.max_streak}"
        messagebox.showinfo("Game Over", msg)
        self.show_frame("MenuFrame")


# ------------------------------
# Frames: Menu, Game, Pause, Stats
# ------------------------------

class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        title = tk.Label(self, text="🎲Enter QuasttShow", font=FONT_LARGE, fg=ACCENT_COLOR, bg=BG_COLOR)
        title.pack(pady=(80, 40))
        btn_start = RoundedButton(self, "🏐Start Game", command=self.start_game, width=300, height=60)
        btn_start.pack(pady=20)

        btn_stats = RoundedButton(self, "✨Statistics", command=lambda: controller.show_frame("StatsFrame"), width=300, height=60)
        btn_stats.pack(pady=20)

        btn_exit = RoundedButton(self, "❌Exit", command=controller.destroy, width=300, height=60)
        btn_exit.pack(pady=20)

    def start_game(self):
        self.controller.start_new_game()


class GameFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Question text
        self.question_text = tk.Label(self, text="", font=FONT_MEDIUM, fg=TEXT_COLOR, bg=BG_COLOR, wraplength=1000, justify="center")
        self.question_text.pack(pady=(60, 30))

        # Answers frame (2 columns)
        self.answers_frame = tk.Frame(self, bg=BG_COLOR)
        self.answers_frame.pack(pady=20)

        # Status bar (score, streak)
        self.status_label = tk.Label(self, text="", font=FONT_SMALL, fg=TEXT_COLOR, bg=BG_COLOR)
        self.status_label.pack(pady=10)

        # AI prediction
        self.ai_label = tk.Label(self, text="", font=FONT_SMALL, fg=ACCENT_COLOR, bg=BG_COLOR, justify="center")
        self.ai_label.pack(pady=10)

        # Pause button
        self.pause_btn = RoundedButton(self, "Pause", command=self.show_pause, width=150, height=40)
        self.pause_btn.pack(pady=15)

        self.answer_buttons = []

    def load_question(self):
        self.clear_answer_buttons()
        if self.controller.current_q_index >= len(self.controller.questions):
            self.controller.end_game()
            return

        qdata = self.controller.questions[self.controller.current_q_index]
        question = html.unescape(qdata["question"])
        correct_answer = html.unescape(qdata["correct_answer"])
        incorrect_answers = [html.unescape(ans) for ans in qdata["incorrect_answers"]]
        options = incorrect_answers + [correct_answer]
        random.shuffle(options)

        self.correct_answer = correct_answer
        self.current_category = qdata.get("category", "Unknown")

        self.question_text.config(text=question)

        # Create buttons in 2 columns
        self.answer_buttons = []
        for i, option in enumerate(options):
            btn = RoundedButton(self.answers_frame, option, command=lambda opt=option: self.check_answer(opt), width=540, height=60)
            self.answer_buttons.append(btn)
            btn.grid(row=i//2, column=i%2, padx=20, pady=15)

        self.update_status()
        self.update_ai_prediction()

    def clear_answer_buttons(self):
        for btn in self.answer_buttons:
            btn.destroy()
        self.answer_buttons = []

    def check_answer(self, choice):
        if self.controller.paused:
            return

        correct = choice == self.correct_answer
        if correct:
            self.controller.score += 10
            self.controller.streak += 1
            if self.controller.streak > self.controller.max_streak:
                self.controller.max_streak = self.controller.streak
        else:
            self.controller.streak = 0

        # Update AI stats
        self.controller.update_game_stats(correct, self.current_category)

        # Flash question text color and disable buttons temporarily
        self.flash_feedback(correct)

    def flash_feedback(self, correct):
        color = CORRECT_COLOR if correct else WRONG_COLOR
        self.question_text.config(fg=color)
        for btn in self.answer_buttons:
            btn.unbind("<Button-1>")
        self.after(1200, self.next_question)

    def next_question(self):
        self.question_text.config(fg=TEXT_COLOR)
        self.controller.current_q_index += 1
        self.load_question()

    def update_status(self):
        status = f"Score: {self.controller.score}    Streak: {self.controller.streak}    Max Streak: {self.controller.max_streak}"
        self.status_label.config(text=status)

    def update_ai_prediction(self):
        stats = self.controller.ai_stats
        answered = stats['questions_answered']
        if answered == 0:
            text = "AI Prediction: No data yet."
        else:
            acc = stats['correct_answers'] / answered
            best_cat = max(stats['correct_by_category'], key=stats['correct_by_category'].get) if stats['correct_by_category'] else "N/A"
            text = f"AI Prediction:\nAccuracy: {acc*100:.1f}%\nBest Category: {best_cat}"
        self.ai_label.config(text=text)

    def show_pause(self):
        self.controller.paused = True
        self.controller.show_frame("PauseOverlay")


class PauseOverlay(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#000000")  # semi-transparent black overlay
        self.controller = controller

        panel = tk.Frame(self, bg=PANEL_BG, width=400, height=300)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(panel, text="Game Paused", font=FONT_LARGE, fg=TEXT_COLOR, bg=PANEL_BG)
        title.pack(pady=(40, 30))

        btn_resume = RoundedButton(panel, "Resume", command=self.resume_game)
        btn_resume.pack(pady=15)

        btn_menu = RoundedButton(panel, "Return to Menu", command=self.return_to_menu)
        btn_menu.pack(pady=15)

    def resume_game(self):
        self.controller.paused = False
        self.controller.show_frame("GameFrame")

    def return_to_menu(self):
        self.controller.paused = False
        self.controller.show_frame("MenuFrame")


class StatsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        title = tk.Label(self, text="Statistics", font=FONT_LARGE, fg=ACCENT_COLOR, bg=BG_COLOR)
        title.pack(pady=(60, 40))

        self.stats_text = tk.Label(self, text="", font=FONT_MEDIUM, fg=TEXT_COLOR, bg=BG_COLOR, justify="left")
        self.stats_text.pack(pady=20)

        btn_back = RoundedButton(self, "Back to Menu", command=lambda: controller.show_frame("MenuFrame"), width=300, height=60)
        btn_back.pack(pady=40)

        self.update_stats()

    def update_stats(self):
        s = self.controller.stats
        games = s.get("games_played", 0)
        avg_score = s.get("total_score", 0) / games if games > 0 else 0
        max_score = s.get("max_score", 0)
        max_streak = s.get("max_streak", 0)
        stats_text = (
            f"Games Played: {games}\n"
            f"Average Score: {avg_score:.2f}\n"
            f"Max Score: {max_score}\n"
            f"Max Streak: {max_streak}\n"
        )
        self.stats_text.config(text=stats_text)


# ------------------------------
# Run if main
# ------------------------------

if __name__ == "__main__":
    game = TriviaShow(difficulty="medium")
    game.run()
