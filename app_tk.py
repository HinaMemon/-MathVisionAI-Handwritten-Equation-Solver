# app_tk.py
# MathVision AI — Gemini image + typed input, improved UI and step-by-step display

import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import google.generativeai as genai

# ----------------- CONFIG -----------------
GEMINI_API_KEY = "AIzaSyCkuUhRPoUwsCpb5k2NS5WEOm6x9DdCv6I"  # <-- replace with your Gemini key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ----------------- APP -----------------
class MathVisionAI:
    def __init__(self, root):
        self.root = root
        self.root.title("📘 MathVision AI – Handwritten Equation Solver")
        self.root.geometry("980x700")
        self.root.configure(bg="#0f172a")

        self.question_count = 0
        # keep references for inserted PhotoImage objects (prevent GC)
        self._image_refs = []

        # Header
        hdr = tk.Frame(root, bg="#0f172a")
        hdr.pack(fill="x", pady=(8,6))
        tk.Label(hdr, text="MathVision AI", font=("Georgia", 28, "bold"), fg="#facc15", bg="#0f172a").pack()
        tk.Label(hdr, text="Upload image OR type question — get clear, student-friendly step-by-step solutions.",
                 font=("Segoe UI", 10), fg="#93c5fd", bg="#0f172a").pack()

        # Main frame: left controls + preview, right output
        main = tk.Frame(root, bg="#0f172a")
        main.pack(fill="both", expand=True, padx=12, pady=10)

        # Left: controls & preview
        left = tk.Frame(main, width=280, bg="#071029")
        left.pack(side="left", fill="y", padx=(0,12), pady=4)
        left.pack_propagate(False)

        btn_frame = tk.Frame(left, bg="#071029")
        btn_frame.pack(pady=12)

        self.upload_btn = tk.Button(btn_frame, text="📤 Upload Image",
                                    command=self.upload_image, bg="#16a34a", fg="white",
                                    font=("Arial", 11, "bold"), width=20, height=2, relief="flat", cursor="hand2")
        self.upload_btn.grid(row=0, column=0, padx=6, pady=6)

        self.type_btn = tk.Button(btn_frame, text="⌨️ Type Question",
                                  command=self.open_type_window, bg="#2563eb", fg="white",
                                  font=("Arial", 11, "bold"), width=20, height=2, relief="flat", cursor="hand2")
        self.type_btn.grid(row=1, column=0, padx=6, pady=6)

        self.clear_btn = tk.Button(btn_frame, text="🧹 Clear All",
                                   command=self.clear_all, bg="#dc2626", fg="white",
                                   font=("Arial", 11, "bold"), width=20, height=2, relief="flat", cursor="hand2")
        self.clear_btn.grid(row=2, column=0, padx=6, pady=6)

        # preview label (fixed size) — small thumbnail, won't expand
        preview_box = tk.LabelFrame(left, text="Preview", fg="#93c5fd", bg="#071029", bd=0, font=("Segoe UI", 10, "bold"))
        preview_box.pack(fill="both", expand=False, padx=8, pady=12)
        self.preview_label = tk.Label(preview_box, bg="#0f172a", width=30, height=12)
        self.preview_label.pack(padx=8, pady=8)

        # Info label
        tk.Label(left, text="Tip: Upload photos of handwritten math or type it directly.",
                 wraplength=240, fg="#c7d2fe", bg="#071029", font=("Segoe UI", 9)).pack(padx=8, pady=(6,12))

        # Right: output area (large)
        right = tk.Frame(main, bg="#0f172a")
        right.pack(side="left", fill="both", expand=True)

        # Output scrolled text
        self.output = scrolledtext.ScrolledText(right, wrap=tk.WORD, font=("Consolas", 12),
                                                bg="#0b1220", fg="#e6eef8", insertbackground="white")
        self.output.pack(fill="both", expand=True, padx=(0,6), pady=(0,6))

        # configure tags for styling
        self.output.tag_configure("qheader", font=("Georgia", 14, "bold"), foreground="#ffd166")
        self.output.tag_configure("qmeta", font=("Segoe UI", 10, "italic"), foreground="#93c5fd")
        self.output.tag_configure("question", font=("Segoe UI", 11, "bold"), foreground="#a5b4fc")
        self.output.tag_configure("step", font=("Consolas", 11), lmargin1=18, lmargin2=30, foreground="#dbeafe")
        self.output.tag_configure("final", font=("Consolas", 12, "bold"), foreground="#4ade80")
        self.output.tag_configure("separator", foreground="#374151")
        self.output.tag_configure("error", foreground="#fca5a5", font=("Consolas", 11, "bold"))

        # state
        self.current_file = None

    # ---------- Helpers ----------
    def _insert_image_inline(self, pil_image, maxsize=(140,140)):
        """Return a PhotoImage (kept in refs) ready to be inserted in the Text widget."""
        # resize while keeping aspect
        img = pil_image.copy()
        img.thumbnail(maxsize)
        photo = ImageTk.PhotoImage(img)
        self._image_refs.append(photo)
        return photo

    # ---------- Upload + Preview ----------
    def upload_image(self):
        path = filedialog.askopenfilename(title="Select image",
                                          filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not path:
            return
        self.current_file = path
        # show small thumbnail in preview area (fixed)
        try:
            pil = Image.open(path)
            thumb = pil.copy()
            thumb.thumbnail((220, 220))
            tkthumb = ImageTk.PhotoImage(thumb)
            # keep ref
            self._image_refs.append(tkthumb)
            self.preview_label.configure(image=tkthumb, text="")
            self.preview_label.image = tkthumb
            # enable solve immediately: same as uploading triggers solve-by-image step below
            # Do not auto-solve: let user click "Type" followed by Solve (as before). We'll solve on demand.
            messagebox.showinfo("Image loaded", f"Loaded: {os.path.basename(path)}\nClick 'Type Question' to type or press 'Upload Image' again to change.")
        except Exception as ex:
            messagebox.showerror("Preview error", f"Could not preview image: {ex}")

    # ---------- Type window ----------
    def open_type_window(self):
        tw = tk.Toplevel(self.root)
        tw.title("Type math question")
        tw.geometry("560x260")
        tw.configure(bg="#081029")

        tk.Label(tw, text="Type your math question (e.g. d/dx x^2 or integrate(x^2, x))",
                 bg="#081029", fg="#c7d2fe", font=("Segoe UI", 10)).pack(pady=(12,6))
        txt = tk.Text(tw, height=6, width=60, font=("Consolas", 12))
        txt.pack(pady=(0,8), padx=12)

        def submit_typed():
            question = txt.get("1.0", tk.END).strip()
            if not question:
                messagebox.showwarning("Empty", "Please type a question.")
                return
            tw.destroy()
            # show thumbnail if existing to the left, but here mark typed question
            self._append_question_block(question_text=question, image_path=None, source="typed")

        btn = tk.Button(tw, text="✅ Solve Typed Question", bg="#16a34a", fg="white",
                        font=("Arial", 11, "bold"), command=submit_typed)
        btn.pack(pady=(0,12))

    # ---------- Append question & call Gemini ----------
    def _append_question_block(self, question_text=None, image_path=None, source="image"):
        """
        Appends header + (optional) thumbnail then sends to Gemini and appends the formatted step-by-step solution.
        source: "image" or "typed"
        """
        self.question_count += 1
        qnum = self.question_count
        # Header
        self.output.insert(tk.END, f"\n\n=== Question {qnum} ===\n", "qheader")

        # if image path present insert thumbnail inline and short caption
        if image_path:
            try:
                pil = Image.open(image_path)
                photo = self._insert_image_inline(pil, maxsize=(120,120))
                # insert image into text widget
                self.output.image_create(tk.END, image=photo)
                self.output.insert(tk.END, "   ")  # small gap
                # caption: filename
                self.output.insert(tk.END, f"{os.path.basename(image_path)}\n", "qmeta")
            except Exception:
                self.output.insert(tk.END, f"(image: {os.path.basename(image_path)})\n", "qmeta")
            # prepare prompt for image
            prompt_intro = ("You are a patient math teacher. Read the handwritten math problem from the image I provide, "
                            "then solve it step-by-step in simple English. Use clear numbered steps: Step 1:, Step 2:, ... "
                            "Finish with a line starting 'Final Answer:' containing the final answer. Explain each step briefly.")
            # upload and call Gemini
            try:
                self.output.insert(tk.END, "🔍 Solving (image) — please wait...\n", "qmeta")
                self.output.see(tk.END)
                img_obj = genai.upload_file(path=image_path)
                response = model.generate_content([prompt_intro, img_obj])
                raw = response.text or ""
            except Exception as e:
                self.output.insert(tk.END, f"\n[ERROR] Gemini image solve failed: {e}\n", "error")
                return
        else:
            # typed question
            self.output.insert(tk.END, "🖊️ (typed question)\n", "qmeta")
            prompt_intro = ("You are a patient math teacher. Read the math question below, then solve it step-by-step in simple English. "
                            "Use clear numbered steps: Step 1:, Step 2:, ... Finish with a line starting 'Final Answer:' containing the final answer. "
                            "Explain each step briefly.")
            full_prompt = f"{prompt_intro}\n\nQuestion: {question_text}"
            self.output.insert(tk.END, f"{question_text}\n", "question")
            self.output.insert(tk.END, "🔍 Solving (typed) — please wait...\n", "qmeta")
            self.output.see(tk.END)
            try:
                response = model.generate_content(full_prompt)
                raw = response.text or ""
            except Exception as e:
                self.output.insert(tk.END, f"\n[ERROR] Gemini typed solve failed: {e}\n", "error")
                return

        # ----------------- format Gemini output -----------------
        if not raw.strip():
            self.output.insert(tk.END, "\n[No result from Gemini]\n", "error")
            return

        # split into lines and apply tags:
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip() != ""]
        # If the model returned everything in a single paragraph, try split by sentences or by "Step"
        if len(lines) == 1:
            # try splitting by 'Step ' or by sentences
            if "Step" in lines[0] or "Final Answer" in lines[0]:
                # try to split by 'Step'
                parts = []
                tmp = lines[0]
                for chunk in tmp.split("Step"):
                    chunk = chunk.strip()
                    if chunk:
                        parts.append("Step " + chunk if not chunk.startswith("Step") else chunk)
                lines = parts if parts else [lines[0]]
            else:
                # split into smaller sentences by period
                import re
                sents = re.split(r'(?<=[.!?])\s+', lines[0])
                lines = [s.strip() for s in sents if s.strip()]

        # Insert lines with tags:
        for ln in lines:
            lower_ln = ln.lower()
            if lower_ln.startswith("step") or ln.lstrip().startswith("•") or ln.lstrip().startswith("-"):
                # Step line
                # put numbered bullet
                self.output.insert(tk.END, f"{ln}\n", "step")
            elif "final answer" in lower_ln or lower_ln.startswith("final:") or lower_ln.startswith("answer"):
                self.output.insert(tk.END, f"{ln}\n", "final")
            else:
                # generic explanatory line
                self.output.insert(tk.END, f"{ln}\n", "step")
        # add a separator
        self.output.insert(tk.END, "\n" + ("-" * 72) + "\n", "separator")
        self.output.see(tk.END)

    # ---------- Public actions ----------
    def solve_with_current_image(self):
        if not self.current_file:
            messagebox.showwarning("No image", "Please upload an image first.")
            return
        # Append question block and solve
        self._append_question_block(image_path=self.current_file, source="image")

    # typed submission is handled by open_type_window -> _append_question_block called directly

    def clear_all(self):
        self.output.delete("1.0", tk.END)
        self.preview_label.configure(image="", text="")
        self._image_refs.clear()
        self.question_count = 0
        self.current_file = None

# ----------------- RUN -----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MathVisionAI(root)

    # Add a small solve button under preview for convenience
    solve_small = tk.Button(root, text="🧮 Solve Uploaded Image", bg="#7c3aed", fg="white",
                            font=("Arial", 11, "bold"), relief="flat",
                            command=app.solve_with_current_image)
    solve_small.place(x=18, y=600, width=240, height=36)  # position near the left panel

    root.mainloop()















