import os
import random
import customtkinter as ctk
from PIL import Image

from car_basics import load_facts
from quiz import Question, get_questions_by_level, save_score_to_file, read_past_scores
from loan_calc import calculate_monthly_payment, money, total_payment  # <-- added total_payment


# theme toggle
def is_dark() -> bool: # theme check
    return ctk.get_appearance_mode().lower() == "dark"

def heading_color():  # title color
    return "white" if is_dark() else "black"

def grey_color():   # other color
    return "gray80" if is_dark() else "gray30"


# main app
class CarCoachApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Car Coach")
        self.geometry("1100x720")

        ctk.set_appearance_mode("dark")        
        ctk.set_default_color_theme("blue")   # acsent

        # layout grid
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.topbar = TopBar(self, self.toggle_theme)
        self.topbar.grid(row=0, column=0, sticky="ew")

        self.body = MainBody(self)
        self.body.grid(row=1, column=0, sticky="nsew")

    def toggle_theme(self): # switch theme
        ctk.set_appearance_mode("light" if is_dark() else "dark")
        self.after_idle(self._refresh_all)

    def _refresh_all(self): 
        self.topbar.refresh_theme()
        self.body.refresh_theme()
        self.update_idletasks()


# top bar
class TopBar(ctk.CTkFrame):
    def __init__(self, master, on_toggle):
        super().__init__(master, fg_color=("white", "#1a1a1a"))
        self.theme_switch = ctk.CTkSwitch(self, text="Dark mode", command=on_toggle)
        self.theme_switch.select()    # default dark
        self.theme_switch.pack(side="right", padx=20, pady=10)

    def refresh_theme(self):     # refresh
        self.configure(fg_color=("white", "#1a1a1a"))


# Body
class MainBody(ctk.CTkFrame):
    """Buttons and images"""
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.active_key: str | None = None
        self.active_panel: ctk.CTkFrame | None = None

        # grid
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # header area
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="n", pady=(20, 10))
        self.header.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self.header, text="Car Coach",
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color=heading_color()
        )
        self.title_lbl.grid(row=0, column=0, pady=(5, 2))

        self.subtitle_lbl = ctk.CTkLabel(
            self.header,
            text="Learn • Drive • Plan\nAn interactive car learning dashboard.",
            font=ctk.CTkFont(size=16),
            text_color=grey_color(), justify="center"
        )
        self.subtitle_lbl.grid(row=1, column=0, pady=(0, 8))

        # nav buttons
        self.btn_row = ctk.CTkFrame(self.header, fg_color="transparent")
        self.btn_row.grid(row=2, column=0, pady=(15, 5))

        self.nav: dict[str, ctk.CTkButton] = {}
        for i, (key, text, icon) in enumerate([
            ("basics", "Car Basics", "🚗"),
            ("quiz",   "Road Rules Quiz", "🧠"),
            ("loan",   "Loan Calculator", "💰"),
        ]):
            btn = ctk.CTkButton(
                self.btn_row, text=f"{icon}  {text}",
                width=220, height=50,
                font=ctk.CTkFont(size=15, weight="bold"),
                command=lambda k=key: self._handle_nav(k),
            )
            btn.grid(row=0, column=i, padx=15)
            self.nav[key] = btn

        # Content area
        self.content = ctk.CTkFrame(self, corner_radius=12)
        self.content.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        self.content.grid_propagate(False)

        # Home layer
        self.home = ctk.CTkFrame(self.content, fg_color="transparent")
        self.home.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

        self.hero_pil: Image.Image | None = None
        self.hero_img: ctk.CTkImage | None = None
        self.hero_lbl = ctk.CTkLabel(self.home, text="")
        self.hero_lbl.place(relx=0.5, rely=0.42, anchor="center")

        self.welcome_lbl = ctk.CTkLabel(
            self.home,
            text="Welcome! Choose a Section above to begin.",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4A90E2"
        )
        self.welcome_lbl.place(relx=0.5, rely=0.74, anchor="center")

        self._load_hero_image()
        self.content.bind("<Configure>", self._on_resize)
        self._paint_nav(None)

    # Referesh
    def refresh_theme(self):              
        self.title_lbl.configure(text_color=heading_color())
        self.subtitle_lbl.configure(text_color=grey_color())
        self._paint_nav(self.active_key)

        if self.active_panel:
            self._open_section(self.active_key)
        else:
            self._resize_hero_image()

    def _paint_nav(self, active: str | None):   # nav styling
        for key, btn in self.nav.items():
            if key == active:
                btn.configure(fg_color="#4a90e2", hover_color="#357ABD", text_color="white")
            else:
                btn.configure(
                    fg_color="#2b2b2b" if is_dark() else "#e0e0e0",
                    hover_color="#3a3a3a" if is_dark() else "#d0d0d0",
                    text_color="white" if is_dark() else "black",
                )

    def _handle_nav(self, key: str):  # click button
        if self.active_key == key:
            self._show_home()
        else:
            self._open_section(key)

    # swap panels
    def _show_home(self):                     
        if self.active_panel is not None:
            self.active_panel.destroy()
            self.active_panel = None
        self.active_key = None
        self._paint_nav(None)
        self.home.lift()
        self._resize_hero_image()

    def _open_section(self, key: str):  # open panel
        self.home.lower()
        if self.active_panel is not None:
            self.active_panel.destroy()
            self.active_panel = None

        builders = {"basics": BasicsPanel, "quiz": QuizPanel, "loan": LoanPanel}
        self.active_panel = builders[key](self.content)
        self.active_panel.pack(fill="both", expand=True, padx=20, pady=20)

        self.active_key = key
        self._paint_nav(key)

    # home image
    def _load_hero_image(self):               
        path = "data/home_image.png"
        self.hero_pil = Image.open(path).convert("RGBA")
        self.hero_img = ctk.CTkImage(self.hero_pil, size=(1000, 560))
        self.hero_lbl.configure(image=self.hero_img, text="")

    def _on_resize(self, _event):  # handle resize
        if hasattr(self, "_resize_job"):
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(16, self._resize_hero_image)

    def _resize_hero_image(self):  # scale image
        if self.hero_pil is None or self.active_panel is not None:
            return
        avail_w = max(300, self.content.winfo_width() - 60)
        avail_h = max(220, self.content.winfo_height() - 120)
        iw, ih = self.hero_pil.size
        scale = min(avail_w / iw, avail_h / ih) * 0.95
        new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        self.hero_img.configure(size=new_size)
        self.hero_lbl.configure(image=self.hero_img)


# car basics panel
class BasicsPanel(ctk.CTkFrame):
    """Search box with info display"""
    def __init__(self, master):
        super().__init__(master)

        # data
        self.facts: dict[str, str] = load_facts()
        self.all_topics = sorted(self.facts.keys(), key=str.casefold)
        self.filtered = list(self.all_topics)

        # heading
        ctk.CTkLabel(self, text="Car Basics",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=heading_color()).pack(anchor="w")
        ctk.CTkLabel(self, text="Search and pick a topic from the dropdown.",
                     text_color=grey_color()).pack(anchor="w", pady=(0, 8))

        # search row
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text="Search:", width=70, anchor="w",
                     text_color=heading_color()).pack(side="left", padx=(0, 6))

        self.search_var = ctk.StringVar(value="")
        ent = ctk.CTkEntry(row, width=360, textvariable=self.search_var, placeholder_text="Type to filter…")
        ent.pack(side="left")
        ent.bind("<KeyRelease>", self._on_search_change)
        ent.bind("<FocusIn>", lambda _: self._open_dropdown())

        # dropdown
        self.dropdown = ctk.CTkScrollableFrame(self, height=200, fg_color=("#ffffff", "#1e1e1e"), corner_radius=10)
        self.dropdown.pack(fill="x", pady=(6, 0))
        self.dropdown_open = True
        self._fill_dropdown(self.filtered)

        # info box
        self.box = ctk.CTkTextbox(self, width=900, height=260)
        self.box.pack(pady=10, fill="x")
        self.box.configure(state="disabled")
        self._hint("Select a topic from the list, or type to search.")

    def _hint(self, msg: str):  # hints
        self.box.configure(state="normal")
        self.box.delete("0.0", "end")
        self.box.insert("0.0", msg)
        self.box.configure(state="disabled")

    def _open_dropdown(self):  # list
        if not self.dropdown_open:
            self.dropdown.pack(fill="x", pady=(6, 0))
            self.dropdown_open = True

    def _clear_dropdown(self): # clear list
        for w in self.dropdown.winfo_children():
            w.destroy()

    def _fill_dropdown(self, topics: list[str]): # fill list
        self._clear_dropdown()
        if not topics:
            ctk.CTkLabel(self.dropdown, text="No matches", text_color=grey_color()).pack(anchor="w", padx=10, pady=6)
            return
        for topic in topics:
            ctk.CTkButton(
                self.dropdown, text=topic, anchor="w",
                fg_color=("white", "#2b2b2b"), text_color=("black", "white"),
                hover_color=("#e6e6e6", "#3a3a3a"), corner_radius=6,
                command=lambda t=topic: self._choose_topic(t)
            ).pack(fill="x", padx=10, pady=4)

    def _on_search_change(self, _=None):  # filter on the go
        q = self.search_var.get().casefold().strip()
        self.filtered = [t for t in self.all_topics if q in t.casefold()] if q else list(self.all_topics)
        self._open_dropdown()
        self._fill_dropdown(self.filtered)
        if not q:
            self._hint("Select a topic from the list, or type to search.")

    def _choose_topic(self, topic: str): # show info
        self.search_var.set(topic)
        text = self.facts.get(topic, "No info available.")
        self.box.configure(state="normal")
        self.box.delete("0.0", "end")
        self.box.insert("0.0", f"{topic}\n\n{text}")
        self.box.configure(state="disabled")


# quiz panel
class QuizPanel(ctk.CTkFrame):
    """save with different levels"""
    def __init__(self, master):
        super().__init__(master)
        self.player = ""
        self.level = "easy"
        self.questions: list[Question] = []
        self.choices: list[ctk.StringVar] = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_intro()

    # first page intro
    def _build_intro(self):
        for w in self.winfo_children():
            w.destroy()

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        ctk.CTkLabel(hdr, text="Road Rules Quiz",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=heading_color()).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Enter your name and choose a difficulty.",
                     text_color=grey_color()).pack(anchor="w")

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, sticky="nw", pady=(6, 0))

        ctk.CTkLabel(form, text="Name:", width=70, anchor="w",
                     text_color=heading_color()).grid(row=0, column=0, padx=(0, 8), pady=2, sticky="w")
        self.name_var = ctk.StringVar(value="")
        ctk.CTkEntry(form, width=240, textvariable=self.name_var, placeholder_text="Your name").grid(row=0, column=1, pady=2, sticky="w")

        ctk.CTkLabel(form, text="Level:", width=70, anchor="w",
                     text_color=heading_color()).grid(row=1, column=0, padx=(0, 8), pady=2, sticky="w")
        self.level_var = ctk.StringVar(value="easy")
        ctk.CTkOptionMenu(form, values=["easy", "medium", "hard"], variable=self.level_var, width=120).grid(row=1, column=1, sticky="w")

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ctk.CTkButton(btns, text="Start Quiz", command=self._start).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btns, text="View Past Scores", command=self._show_scores).pack(side="left")

    def _show_scores(self): # shows all scores
        top = ctk.CTkToplevel(self)
        top.title("Past Scores")
        top.geometry("520x360")
        box = ctk.CTkTextbox(top, width=480, height=300)
        box.pack(padx=16, pady=16, fill="both", expand=True)
        box.insert("0.0", read_past_scores())
        box.configure(state="disabled")

    # quiz
    def _start(self):        
        self.player = self.name_var.get().strip() or "Anonymous"
        self.level = self.level_var.get().strip().lower()

        bank = get_questions_by_level(self.level)
        if len(bank) < 5:
            bank = (get_questions_by_level("easy")
                    + get_questions_by_level("medium")
                    + get_questions_by_level("hard"))

        self.questions = random.sample(bank, k=min(5, len(bank)))
        self.choices = [ctk.StringVar(value="") for _ in self.questions]

        for w in self.winfo_children():
            w.destroy()

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(hdr, text=f"Quiz ({self.level.title()} • 5 Questions)",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=heading_color()).pack(anchor="w")
        ctk.CTkLabel(hdr, text=f"Name: {self.player}",
                     text_color=grey_color()).pack(anchor="w")

        self.scroll = ctk.CTkScrollableFrame(self, height=380)
        self.scroll.grid(row=1, column=0, sticky="nsew", pady=(6, 6))

        for i, q in enumerate(self.questions):
            self._render_q(self.scroll, i, q)

        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=2, column=0, sticky="w", pady=(2, 8))
        ctk.CTkButton(foot, text="Submit", command=self._submit).pack(side="left")

        self.result = ctk.CTkTextbox(self, width=900, height=180)
        self.result.grid(row=3, column=0, sticky="nsew")
        self.result.configure(state="disabled")

    def _render_q(self, parent, idx: int, q: Question):  # render question
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(wrap, text=f"Q{idx+1}. {q.prompt}",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=heading_color(),
                     wraplength=900, anchor="w", justify="left").pack(anchor="w", pady=(0, 4))

        for i in range(4):
            if i < len(q.options):
                text = q.options[i]
                letter = text.split(")")[0].strip() if ")" in text else chr(ord('A') + i)
                ctk.CTkRadioButton(wrap, text=text, variable=self.choices[idx], value=letter).pack(anchor="w", pady=2)

    def _submit(self):  # Save and show results
        score = 0
        mistakes: list[tuple[int, Question, str]] = []
        for i, q in enumerate(self.questions):
            chosen = (self.choices[i].get() or "").upper()
            if chosen == q.answer.upper():
                score += 1
            else:
                mistakes.append((i + 1, q, chosen))

        lines = [f"Score: {score}/{len(self.questions)}\n"]
        if mistakes:
            lines.append("Mistakes:")
            for num, q, chosen in mistakes:
                lines.append(f"  Q{num}: {q.prompt}")
                lines.append(f"    Your answer: {chosen if chosen else '—'}")
                lines.append(f"    Correct:     {q.answer}")
        else:
            lines.append("Perfect! 🎉")

        self.result.configure(state="normal")
        self.result.delete("0.0", "end")
        self.result.insert("0.0", "\n".join(lines))
        self.result.configure(state="disabled")
        self.result.yview_moveto(0.0)

        save_score_to_file(self.player, score, len(self.questions))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=4, column=0, sticky="w", pady=(6, 0))
        ctk.CTkButton(btns, text="Restart Quiz", command=self._build_intro).pack(side="left", padx=6)

    def refresh_theme(self):  # refresh
        for w in self.winfo_children():
            w.destroy()
        self._build_intro()


# loan panel
class LoanPanel(ctk.CTkFrame):
    """Simple EMI calculator."""
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Loan Calculator",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=heading_color()).pack(anchor="w")
        ctk.CTkLabel(self, text="Enter price, deposit, rate and years.",
                     text_color=grey_color()).pack(anchor="w", pady=(0, 8))

        self.price_ent  = self._entry_row("Car price ($):")
        self.dep_ent    = self._entry_row("Deposit ($):")
        self.rate_ent   = self._entry_row("Interest rate (%):")
        self.years_ent  = self._entry_row("Loan term (years):")

        ctk.CTkButton(self, text="Calculate", command=self._calc).pack(pady=8)

        self.out = ctk.CTkTextbox(self, width=900, height=100)
        self.out.pack()
        self.out.configure(state="disabled")

    def _entry_row(self, label: str) -> ctk.CTkEntry:  # labeled entry
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(anchor="w", pady=2)
        ctk.CTkLabel(row, text=label, width=160, anchor="w",
                     text_color=heading_color()).pack(side="left", padx=(0, 8))
        ent = ctk.CTkEntry(row, width=160)
        ent.pack(side="left")
        return ent

    def _calc(self):  # computing EMI
        try:
            principal = float(self.price_ent.get()) - float(self.dep_ent.get())
            if principal < 0:
                raise ValueError("Deposit cannot exceed price.")
            rate = float(self.rate_ent.get())
            years = int(self.years_ent.get())

            monthly = calculate_monthly_payment(principal, rate, years)
            total = total_payment(monthly, 12 * years) 
            interest = total - principal

            txt = (
                f"Loan amount: {money(principal)}\n"
                f"Monthly repayment: {money(monthly)}\n"
                f"Total over {years} yrs: {money(total)}\n"
                f"Total interest paid: {money(interest)}"
            )
            ok = True
        except Exception as e:
            txt = f"Error: {e}\nPlease enter valid values"
            ok = False

        self.out.configure(state="normal")
        self.out.delete("0.0", "end")
        self.out.insert("0.0", txt)
        self.out.configure(state="disabled")
        self.out.configure(fg_color=("#1E2A1E" if ok else "#2A1E1E") if is_dark() else None)

if __name__ == "__main__":
    app = CarCoachApp()
    app.mainloop()