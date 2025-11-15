# mental_bot.py — compact + shows matched happy keywords
import re, threading, datetime, tkinter as tk, nltk
from tkinter import scrolledtext, messagebox, filedialog
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# ---------- Setup ----------
try: nltk.data.find("sentiment/vader_lexicon.zip")
except: nltk.download("vader_lexicon", quiet=True)
sia = SentimentIntensityAnalyzer()

CRISIS = ["suicide","kill myself","want to die","end my life","self harm","panic attack"]
HAPPY = ["happy","good","great","fine","awesome","well","better","joy","excited","relieved","calm","okay","ok","fantastic","wonderful"]

RESP = {
  "general":"I hear you. Try grounding: name 5 things you see, 4 you can touch, 3 you hear.",
  "negative":"Sorry you're struggling. Try 5 slow breaths: inhale 4s, hold 4s, exhale 6s.",
  "crisis":"This sounds like serious distress. If in danger call emergency services or contact someone now."
}

def find_keywords(text, keywords):
    found = [k for k in keywords if re.search(r"\b"+re.escape(k)+r"\b", text, re.I)]
    return found

def analyze(text):
    s = sia.polarity_scores(text)["compound"]
    if s>=0.05: sentiment="positive"
    elif s<=-0.05: sentiment="negative"
    else: sentiment="neutral"
    intent = "crisis" if any(re.search(r"\b"+re.escape(k)+r"\b", text, re.I) for k in CRISIS) else "general"
    happy_found = find_keywords(text, HAPPY)
    return sentiment, s, intent, happy_found

# ---------- UI & Logic ----------
class App:
    def __init__(self, root):
        root.title("Mental Wellness Bot"); root.geometry("640x560"); root.resizable(False,False)
        self.chat = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Segoe UI",13))
        self.chat.place(x=12,y=12,width=616,height=420)
        self.entry = tk.Entry(root, font=("Segoe UI",14))
        self.entry.place(x=12,y=440,width=480,height=42); self.entry.bind("<Return>", lambda e: self.send())
        tk.Button(root, text="Send", command=self.send, width=10).place(x=502,y=440,height=42)
        self.status = tk.Label(root, text="Sentiment: —", anchor='w', font=("Segoe UI",11))
        self.status.place(x=12,y=492,width=400,height=28)
        tk.Button(root, text="Breath", command=lambda:self._bot("Breathing: inhale 4s, hold 4s, exhale 6s. Repeat 5x")).place(x=420,y=492,width=100)
        tk.Button(root, text="Save", command=self.save).place(x=532,y=492,width=96)
        self._bot("Hi — I'm here to listen. Type how you feel. Type 'exit' to quit.")

    def _append(self, who, text):
        self.chat.configure(state='normal')
        prefix = "You: " if who=="user" else "Bot: "
        self.chat.insert(tk.END, f"{prefix}{text}\n\n")
        self.chat.configure(state='disabled'); self.chat.yview(tk.END)

    def _bot(self, text):
        self._append("bot", text)

    def send(self):
        msg = self.entry.get().strip()
        if not msg: return
        self._append("user", msg); self.entry.delete(0,tk.END)
        if msg.lower() in ("exit","quit","bye"):
            self._bot("Take care — reach out if you need to.")
            root.after(700, root.destroy); return
        threading.Thread(target=self._handle, args=(msg,), daemon=True).start()

    def _handle(self, msg):
        sentiment, score, intent, happy_found = analyze(msg)
        # update status with keywords if any
        kws = ", ".join(happy_found) if happy_found else "—"
        self.status.config(text=f"Sentiment: {sentiment} ({score:.2f})  |  Happy keywords: {kws}")
        if intent=="crisis" or (sentiment=="negative" and score<=-0.6):
            self._bot(RESP["crisis"])
            messagebox.showwarning("Crisis detected", "Serious distress detected. If in danger, call emergency services now.")
            return
        if sentiment=="negative": reply=RESP["negative"]
        elif sentiment=="positive": reply="I'm glad to hear that. Tell me more if you'd like."
        else: reply=RESP["general"]
        self._bot(reply)

    def save(self):
        txt = self.chat.get("1.0", tk.END).strip()
        if not txt: messagebox.showinfo("Save","Nothing to save"); return
        f = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"chat_{int(datetime.datetime.now().timestamp())}.txt")
        if f:
            open(f,"w",encoding="utf-8").write(txt); messagebox.showinfo("Saved",f"Saved to {f}")

if __name__=="__main__":
    root = tk.Tk(); App(root); root.mainloop()
