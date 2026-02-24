import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from summarizer import summarize_url

import re
import tkinter as tk
import tkinter.font as tkfont
from tkinter.scrolledtext import ScrolledText

class MarkdownText(ScrolledText):
    def __init__(self, master, **kwargs):
        super().__init__(master, wrap="word", **kwargs)
        base = tkfont.nametofont("TkDefaultFont")
        base_size = int(base.cget("size"))

        def bigger(delta: int) -> int:
            # Tk sizes can be negative on Windows (pixel-based)
            return base_size - delta if base_size < 0 else base_size + delta

        # Keep references on self so they are not garbage-collected
        self._font_h1 = base.copy()
        self._font_h1.configure(size=bigger(6), weight="bold")

        self._font_h2 = base.copy()
        self._font_h2.configure(size=bigger(4), weight="bold")

        self._font_h3 = base.copy()
        self._font_h3.configure(size=bigger(2), weight="bold")

        self._font_bold = base.copy()
        self._font_bold.configure(weight="bold")

        self._font_code = tkfont.nametofont("TkFixedFont").copy()
        self._font_codeblock = tkfont.nametofont("TkFixedFont").copy()

        self.tag_configure("h1", font=self._font_h1, spacing3=8)
        self.tag_configure("h2", font=self._font_h2, spacing3=6)
        self.tag_configure("h3", font=self._font_h3, spacing3=4)
        self.tag_configure("bold", font=self._font_bold)
        self.tag_configure("code", font=self._font_code, background="#f5f5f5")
        self.tag_configure("codeblock", font=self._font_codeblock, background="#f5f5f5", lmargin1=10, lmargin2=10)

    def set_markdown(self, md: str):
        self.configure(state="normal")
        self.delete("1.0", tk.END)

        lines = md.splitlines()
        in_code = False
        code_buf = []

        for line in lines:
            if line.strip().startswith("```"):
                if not in_code:
                    in_code = True
                    code_buf = []
                else:
                    in_code = False
                    self._insert_tagged("\n".join(code_buf) + "\n\n", "codeblock")
                continue

            if in_code:
                code_buf.append(line)
                continue

            if line.startswith("# "):
                self._insert_tagged(line[2:].rstrip() + "\n", "h1")
                continue
            if line.startswith("## "):
                self._insert_tagged(line[3:].rstrip() + "\n", "h2")
                continue
            if line.startswith("### "):
                self._insert_tagged(line[4:].rstrip() + "\n", "h3")
                continue

            line = re.sub(r"^\s*[\-\*]\s+", "• ", line)
            line = re.sub(r"^\s*(\d+)[\.\)]\s+", r"\1. ", line)

            self._insert_inline(line + "\n")

        if in_code and code_buf:
            self._insert_tagged("\n".join(code_buf) + "\n", "codeblock")

        self.configure(state="disabled")

    def _insert_tagged(self, text: str, tag: str):
        self.insert(tk.END, text, (tag,))

    def _insert_inline(self, s: str):
        i = 0
        while i < len(s):
            if s[i] == "`":
                j = s.find("`", i + 1)
                if j != -1:
                    self._insert_tagged(s[i+1:j], "code")
                    i = j + 1
                    continue
            if s.startswith("**", i):
                j = s.find("**", i + 2)
                if j != -1:
                    self._insert_tagged(s[i+2:j], "bold")
                    i = j + 2
                    continue

            nxt = self._next_special(s, i)
            self.insert(tk.END, s[i:nxt])
            i = nxt

    @staticmethod
    def _next_special(s: str, start: int) -> int:
        cands = [x for x in (s.find("**", start), s.find("`", start)) if x != -1]
        return min(cands) if cands else len(s)

class RepoSummarizerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Repo Summarizer")

        tk.Label(self.root, text="Insert URL:").pack(anchor="w", padx=10, pady=(10, 2))

        self.url_var = tk.StringVar()
        self.entry = tk.Entry(self.root, textvariable=self.url_var, width=120)
        self.entry.pack(fill="x", padx=10, pady=(0, 8))
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda _e: self.on_summarize())

        self.btn = tk.Button(self.root, text="Summarize", command=self.on_summarize)
        self.btn.pack(anchor="w", padx=10, pady=(0, 8))

        self.status = tk.Label(self.root, text="", anchor="w")
        self.status.pack(fill="x", padx=10, pady=(0, 6))

        self.output = MarkdownText(self.root, height=28)
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.busy = False

    def set_busy(self, busy: bool):
        self.busy = busy
        state = "disabled" if busy else "normal"
        self.btn.config(state=state)
        self.entry.config(state=state)

    def set_status(self, msg: str):
        self.status.config(text=msg)

    def set_output(self, text: str):
        self.output.set_markdown(text)

    def on_summarize(self):
        if self.busy:
            return

        url = self.url_var.get().strip()
        if not url:
            self.set_status("Please enter a GitHub URL")
            self.entry.focus_set()
            return

        self.set_busy(True)
        self.set_status("Working...")
        self.set_output("")

        def worker():
            try:
                result = summarize_url(url)
                if result is None:
                    result = "(Your run() prints output. If you want it displayed here, make run() return the summary string.)"

                self.root.after(0, lambda: self.set_output(str(result)))
                self.root.after(0, lambda: self.set_status("Done. Enter another URL."))
            except Exception as e:
                self.root.after(0, lambda: self.set_output(f"Error:\n{e}"))
                self.root.after(0, lambda: self.set_status("Failed. Try again."))
            finally:
                def finish():
                    self.set_busy(False)
                    self.url_var.set("")
                    self.entry.focus_set()
                self.root.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def run(self):
        self.root.mainloop()
