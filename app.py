import random
import customtkinter as ctk

# car basics
def load_facts():
    facts ={}
    topic =None
    text =[]
    path ="data/car_facts.txt"
    try:
        f = open(path,"r")
        while True:
            line =f.readline()
            if not line:
                break
            line =line.strip()
            if not line:
                continue
            if "|" in line:
                if topic:
                    facts[topic] ="\n".join(text)
                    text =[]
                t, part =line.split("|",1)
                topic =t.strip()
                text.append(part.strip())
            else:
                text.append(line)
        if topic:
            facts[topic] ="\n".join(text)
        f.close()
    except FileNotFoundError:
        facts ={"car_facts.txt file missing"}
    return facts


# loan
def calc_monthly(pr,rate,yrs):
    r =(rate/100)/12
    n =yrs*12
    if r ==0:
        return pr/n
    return pr*r*(1+r)**n/((1+r)**n-1)


def total_payment(monthly,months):
    return monthly*months


def to_money(v):
    return "$"+format(v,",.2f")


# quiz
class Question:
    def __init__(self,q,opts,ans):
        self.q =q
        self.opts =opts
        self.ans =ans.strip().upper()


def load_quiz():
    data ={"easy":[], "medium":[], "hard":[]}
    path = "data/quiz_bank.txt"
    try:
        with open(path,"r") as f:
            for line in f:
                s =line.strip()
                if not s or s.startswith("#"):
                    continue
                p =[x.strip() for x in s.split("|")]
                if len(p)<4:
                    continue
                lvl =p[0].lower()
                if lvl not in data:
                    continue
                q =p[1]
                opts =p[2:-1]
                a =p[-1].upper()
                if a not in {"A","B","C"}:
                    continue
                data[lvl].append(Question(q,opts[:4],a))
    except FileNotFoundError:
        data= ["quiz_bank.txt file missing"]
    return data


def get_questions(lvl):
    bank =load_quiz()
    return bank.get(lvl,[])


def save_score(name,score,total):
    path ="data/quiz_results.txt"
    with open(path, "a") as f:
        f.write(f"{name},{score}/{total}\n")


def read_scores():
    try:
        with open("data/quiz_results.txt","r") as f:
            t =f.read().strip()
        return t if t else "No scores yet"
    except FileNotFoundError:
        return "No scores yet"


# main app
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Car Coach")
        self.geometry("850x650")

        top =ctk.CTkFrame(self)
        top.pack(fill="x", pady=5)
        ctk.CTkLabel(top,text="Car Coach",font=("Arial",20,"bold")).pack(side="left")
        ctk.CTkLabel(top,text="Learn • Drive • Plan",font=("Arial", 12)).pack(side="left",padx=8)

        self.dark =ctk.StringVar(value="On")
        ctk.CTkSwitch(top,text="Dark mode",variable=self.dark,
                      onvalue="On",offvalue="Off",command=self.change_mode).pack(side="right")

        bar =ctk.CTkFrame(self)
        bar.pack(pady=6)
        ctk.CTkButton(bar,text="Car Basics",width=150,command=self.show_basics).pack(side="left")
        ctk.CTkButton(bar,text="Quiz",width=150,command=self.show_quiz).pack(side="left",padx=5)
        ctk.CTkButton(bar,text="Loan",width=150,command=self.show_loan).pack(side="left",padx=5)

        self.page =ctk.CTkFrame(self)
        self.page.pack(fill="both",expand=True)
        self.current =None

    def change_mode(self):
        if self.dark.get() =="On":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def swap(self,frame_cls):
        if self.current:
            self.current.destroy()
        self.current =frame_cls(self.page)
        self.current.pack(fill="both",expand=True)

    # car basics
    def show_basics(self):
        info =load_facts()
        topics =sorted(info.keys())

        class Basics(ctk.CTkFrame):
            def __init__(self,parent):
                super().__init__(parent)
                ctk.CTkLabel(self,text="Car Basics",font=("Arial",14,"bold")).pack(anchor="w")

                row =ctk.CTkFrame(self)
                row.pack(fill="x")
                self.query =ctk.StringVar()
                ctk.CTkLabel(row,text="Search:").pack(side="left")
                e = ctk.CTkEntry(row,width=250,textvariable=self.query)
                e.pack(side="left")
                e.bind("<KeyRelease>",self.search)

                self.listbox =ctk.CTkScrollableFrame(self)
                self.listbox.pack(fill="both",expand=True)
                self.textbox =ctk.CTkTextbox(self,height=250)
                self.textbox.pack(fill="x",padx=8,pady=6)
                self.textbox.insert("0.0","Select a topic from above.")
                self.textbox.configure(state="disabled")
                self.fill(topics)

            def fill(self,lst):
                for w in self.listbox.winfo_children():
                    w.destroy()
                for t in lst:
                    ctk.CTkButton(self.listbox,text=t,anchor="w",
                                  command=lambda tt=t: self.show_text(tt)).pack(fill="x",padx=4,pady=2)

            def search(self,_=None):
                q =self.query.get().lower().strip()
                lst =[t for t in topics if q in t.lower()] if q else topics
                self.fill(lst)

            def show_text(self,topic):
                self.query.set(topic)
                txt =info.get(topic,"No info found")
                self.textbox.configure(state="normal")
                self.textbox.delete("0.0","end")
                self.textbox.insert("0.0",f"{topic}\n\n{txt}")
                self.textbox.configure(state="disabled")

        self.swap(Basics)

    # quiz
    def show_quiz(self):
        class Quiz(ctk.CTkFrame):
            def __init__(self,parent):
                super().__init__(parent)
                ctk.CTkLabel(self,text="Road Rules Quiz",font=("Arial",14,"bold"))
                form =ctk.CTkFrame(self)
                form.grid(row=1,column=0,columnspan=2,sticky="w")
                self.name =ctk.StringVar()
                self.level =ctk.StringVar(value="easy")
                ctk.CTkLabel(form,text="Name:").grid(row=0,column=0)
                ctk.CTkEntry(form,width=180,textvariable=self.name).grid(row=0,column=1)
                ctk.CTkLabel(form,text="Level:").grid(row=1,column=0)
                ctk.CTkOptionMenu(form,values=["easy","medium","hard"], variable=self.level,width=90).grid(row=1,column=1)

                self.columnconfigure(0,weight=1)
                self.columnconfigure(1,weight=1)
                self.rowconfigure(2,weight=1)

                self.left =ctk.CTkScrollableFrame(self)
                self.left.grid(row=2,column=0,sticky="nsew")
                self.right =ctk.CTkFrame(self)
                self.right.grid(row=2,column=1,sticky="nsew")

                self.out =ctk.CTkTextbox(self.right)
                self.out.pack(fill="both",expand=True)
                self.out.insert("0.0","Results here.")
                self.out.configure(state="disabled")

                btns = ctk.CTkFrame(self)
                btns.grid(row=3,column=0,columnspan=2,sticky="w")
                ctk.CTkButton(btns,text="Start",command=self.start).pack(side="left")
                ctk.CTkButton(btns,text="Scores",command=self.show_scores).pack(side="left",padx=4)

            def start(self):
                for w in self.left.winfo_children():w.destroy()
                qs = get_questions(self.level.get())
                if len(qs)<5:
                    qs =get_questions("easy")+get_questions("medium")+get_questions("hard")
                self.qs =random.sample(qs,k=min(5,len(qs)))
                self.vars =[]
                for i, q in enumerate(self.qs):
                    box = ctk.CTkFrame(self.left)
                    box.pack(fill="x")
                    ctk.CTkLabel(box,text=f"Q{i+1}.{q.q}",wraplength=360).pack(anchor="w")
                    v =ctk.StringVar(value="")
                    self.vars.append(v)
                    for opt in q.opts:
                        letter =opt.split(")")[0].strip()
                        ctk.CTkRadioButton(box,text=opt,variable=v,value=letter).pack(anchor="w")
                ctk.CTkButton(self.right,text="Submit",command=self.submit).pack(anchor="e")

            def submit(self):
                score =0
                wrong =[]
                for i,q in enumerate(self.qs):
                    choice =(self.vars[i].get() or "").upper()
                    if choice ==q.ans:
                        score +=1
                    else:
                        wrong.append((i+1, q,choice))
                lines = [f"Score: {score}/{len(self.qs)}"]
                if wrong:
                    lines.append("Mistakes:")
                    for n,qq,ch in wrong:
                        lines.append(f"Q{n}:{qq.q}")
                        lines.append(f" Your: {ch or'-'} Correct:{qq.ans}")
                else:
                    lines.append("Perfect!")
                self.out.configure(state="normal")
                self.out.delete("0.0","end")
                self.out.insert("0.0","\n".join(lines))
                self.out.configure(state="disabled")
                save_score(self.name.get()or"Blank",score,len(self.qs))

            def show_scores(self):
                win = ctk.CTkToplevel(self)
                win.title("Past scores")
                win.geometry("400x300")
                box = ctk.CTkTextbox(win)
                box.pack(fill="both",expand=True)
                box.insert("0.0",read_scores())
                box.configure(state="disabled")

        self.swap(Quiz)

    # loan
    def show_loan(self):
        class Loan(ctk.CTkFrame):
            def __init__(self, parent):
                super().__init__(parent)
                ctk.CTkLabel(self,text="Loan Calculator",font=("Arial",14,"bold")).pack(anchor="w")

                def field(lbl):
                    f = ctk.CTkFrame(self); f.pack(anchor="w")
                    ctk.CTkLabel(f,text=lbl,width=120).pack(side="left")
                    e = ctk.CTkEntry(f,width=120); e.pack(side="left")
                    return e

                self.price =field("Price ($):")
                self.dep =field("Deposit ($):")
                self.rate =field("Rate (%):")
                self.years =field("Years:")
                self.out =ctk.CTkTextbox(self, height=100); self.out.pack(fill="x")
                ctk.CTkButton(self, text="Calculate", command=self.calc).pack(anchor="w")

            def calc(self):
                try:
                    p =float(self.price.get()) -float(self.dep.get())
                    r =float(self.rate.get())
                    y =int(self.years.get())
                    m =calc_monthly(p,r,y)
                    t =total_payment(m,y*12)
                    txt =f"Loan: {to_money(p)}\nMonth: {to_money(m)}\nTotal: {to_money(t)}\nInterest: {to_money(t-p)}"
                except Exception as e:
                    txt = "Error:"+str(e)
                self.out.configure(state="normal")
                self.out.delete("0.0","end")
                self.out.insert("0.0",txt)
                self.out.configure(state="disabled")

        self.swap(Loan)


if __name__ =="__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    App().mainloop()
    
# Reference - "https://customtkinter.tomschimansky.com/documentation/"