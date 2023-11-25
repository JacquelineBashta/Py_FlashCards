import os
import random as r
import tkinter as tk
import pandas as pd


LEFT = 0
RIGHT = 1
BG_COLOR = "#B1DDC6"  # rbg(179, 222, 198)

LANGUAGE = "Spanish"
TRANS_LANGUAGE = "English"

MAX_SEEN_FREQ = 1000
SECONDS_TO_FLIP = 5
DB_LOC = "data/spanish_1000_words.csv"
# ---------------------------------- class Button ---------------------------------------######


class Button:
    def __init__(self, root, side, img, command, w=100, h=100) -> None:
        if side == LEFT:
            self.column = 0
        else:
            self.column = 1
        self.img = img
        self.command = command
        self.root = root
        self.create(w, h)

    def create(self, w, h):
        self.btn_img = tk.PhotoImage(file=self.img)
        self.btn = tk.Button(self.root, image=self.btn_img, command=self.command, borderwidth=0, highlightthickness=0)
        self.btn.config(width=h, height=w, background=BG_COLOR)

    def show(self):
        self.btn.grid(column=self.column, row=1)

    def hide(self):
        self.btn.grid_remove()

# ---------------------------------- class Card ---------------------------------------######


class Card:
    def __init__(self, img) -> None:
        self.img = img
        self.create()

    def create(self):
        self.card = tk.Canvas(width=800, height=526, background=BG_COLOR,
                              highlightthickness=0)
        self.card_img = tk.PhotoImage(file=self.img)
        self.card.create_image(400, 263, image=self.card_img)
        self.lbl_1 = self.card.create_text(400, 150, font=("Courier", 40, "italic"), text="")
        self.lbl_2 = self.card.create_text(400, 263, font=("Courier", 60, "bold"), text="")

    def hide(self):
        self.card.grid_remove()

    def show(self, lbl_1, lbl_2):
        self.card.itemconfigure(self.lbl_1, text=lbl_1)
        self.card.itemconfigure(self.lbl_2, text=lbl_2)
        self.card.grid(column=0, row=0, columnspan=2)

# ---------------------------------- class FlashCard ---------------------------------------######


class FlashCard:
    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.title("flashy")
        self.window.config(background=BG_COLOR, padx=50, pady=50)
        self.front_card = Card("images/card_front.png")
        self.back_card = Card("images/card_back.png")
        self.start_btn = Button(self.window, RIGHT, "images/start.png", self._start_pressed, 90, 198)
        self.end_btn = Button(self.window, RIGHT, "images/end.png", self._end_pressed, 90, 198)

        self.yes_btn = Button(self.window, RIGHT, "images/right.png", self._yes_pressed)
        self.no_btn = Button(self.window, LEFT, "images/wrong.png", self._no_pressed)

        self.count_down_job = None
        self.data = pd.read_csv(DB_LOC)
        self.random_index = 0
        self.the_word = self.data.loc[self.random_index]
        self.end_game = False

    def start(self):
        # 1. show welcome page with start button
        self.back_card.show("Welcome to flashy game.\nAre you ready?", "")
        self.start_btn.show()
        self.window.mainloop()

    def reset(self):
        self.data.loc[:, ["seen_freq"]] = 0
        if os.path.isfile(DB_LOC):
            os.remove(DB_LOC)
        self.data.to_csv(DB_LOC, index=False)

    def _choose_a_word(self, ):
        # 3. choose random word with seen_freq != MAX_SEEN
        random_index = r.randint(0, self.data.shape[0])
        random_word = self.data.loc[random_index]
        if random_word.seen_freq == MAX_SEEN_FREQ:
            self._choose_a_word()
        else:
            self.random_index = random_index
            self.the_word = self.data.loc[self.random_index]

    def _show_the_word(self):
        # 4. show word (in foreign lang) on front card
        self.back_card.hide()
        self.start_btn.hide()
        self.yes_btn.hide()
        self.no_btn.hide()
        self.end_btn.show()
        self.front_card.show(LANGUAGE, self.the_word.spanish)
        # 5. wait for x timer
        self._count_down(SECONDS_TO_FLIP)

    def _count_down(self, tmr_sec):
        if tmr_sec > 0:
            self.count_down_job = self.window.after(
                1000, self._count_down, tmr_sec - 1)
        else:
            self._show_trans_word()

    def _show_trans_word(self):
        # 6. show back card with the word ( in english)
        self.front_card.hide()
        self.end_btn.hide()
        self.back_card.show(TRANS_LANGUAGE, self.the_word.english)
        # show btns
        self.yes_btn.show()
        self.no_btn.show()

    def show_summary(self):
        total_max_seen = self.data.query("seen_freq == 1000").seen_freq.count()
        total_seen = self.data.query("seen_freq != 0").seen_freq.count()
        self.back_card.hide()
        self.yes_btn.hide()
        self.no_btn.hide()
        self.back_card.show(f"Total words seen = {total_seen} \nTotal words learned = {total_max_seen} ", "")

    def _main_seq(self):
        if not self.end_game:
            # 3. choose random word with seen_freq != MAX_SEEN
            self._choose_a_word()
            self._show_the_word()
        else:
            # 10. if user press "End", save final data to csv and show summary.
            if os.path.isfile(DB_LOC):
                os.remove(DB_LOC)
            self.data.to_csv(DB_LOC, index=False)
            self.show_summary()

    def _start_pressed(self):
        # 2. listen on start button
        self._main_seq()

    def _end_pressed(self):
        if self.count_down_job:
            self.window.after_cancel(self.count_down_job)
        self.end_game = True
        self.end_btn.hide()
        self._main_seq()

    def _yes_pressed(self):
        # 8. if user click (✔) ,set seen_freq = 1000 + repeat from 3
        self.data.loc[self.random_index, ["seen_freq"]] = MAX_SEEN_FREQ
        self._main_seq()

    def _no_pressed(self):
        # 7. wait on user response + inc seen_freq for word
        # 9. if user click (✖) ,repeat from 3
        self.data.loc[self.random_index, ["seen_freq"]] += 1
        self._main_seq()


my_game = FlashCard()
my_game.start()
