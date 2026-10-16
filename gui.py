"""Tkinter GUI (Arabic, right-to-left, blue/white medical theme).
Flow: Home -> Patient form -> Symptoms -> Results (everything on ONE screen) ; plus Hospital search and History."""
import tkinter as tk
from tkinter import ttk, messagebox
import knowledge_base as kb
import inference_engine as engine
import hospital_database as db
import report_builder as rb
from knowledge_base import APP_NAME, APP_SUBTITLE

BLUE, DARK, LIGHT, BG = "#1565C0", "#0D47A1", "#E3F2FD", "#F5F9FF"
WHITE, RED, GREEN, GRAY = "#FFFFFF", "#C62828", "#2E7D32", "#546E7A"
FONT = "Segoe UI"
ALL_AR = "الكل"
NONE_AR = "— غير محدد —"

def button(parent, text, cmd, color=BLUE, width=None):
    b = tk.Button(parent, text=text, command=cmd, bg=color, fg=WHITE, font=(FONT, 11, "bold"), relief="flat",
                  padx=16, pady=7, cursor="hand2", activebackground=DARK, activeforeground=WHITE, bd=0)
    if width:
        b.config(width=width)
    b.bind("<Enter>", lambda e: b.config(bg=DARK if color == BLUE else color))
    return b

def card(parent, **kw):
    return tk.Frame(parent, bg=WHITE, highlightbackground="#BBDEFB", highlightthickness=1, **kw)

class Screen(tk.Frame):
    title, icon, step = "", "", ""
    def __init__(self, app):
        super().__init__(app.container, bg=BG)
        self.app = app
        head = tk.Frame(self, bg=BLUE)
        head.pack(fill="x")
        tk.Label(head, text=f"{self.icon}  {self.title}", bg=BLUE, fg=WHITE, font=(FONT, 18, "bold")).pack(side="right", padx=20, pady=12)
        if self.step:
            tk.Label(head, text=self.step, bg=BLUE, fg=LIGHT, font=(FONT, 11)).pack(side="left", padx=20)
        self.footer = tk.Frame(self, bg=BG)
        self.footer.pack(side="bottom", fill="x", padx=20, pady=10)
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True, padx=20, pady=10)
        self.build()
    def label(self, text, parent=None, **kw):
        opts = dict(bg=kw.pop("bg", BG), font=(FONT, 12), anchor="e", justify="right")
        opts.update(kw)
        return tk.Label(parent or self.body, text=text, **opts)
    def nav(self, *buttons):
        for text, cmd, *c in buttons:
            button(self.footer, text, cmd, c[0] if c else BLUE).pack(side="right", padx=5)
    def build(self): pass
    def on_show(self): pass

class HomeScreen(Screen):
    title, icon = APP_NAME, "🩺"
    def build(self):
        box = card(self.body)
        box.pack(fill="both", expand=True, pady=6)
        tk.Label(box, text="🏥", bg=WHITE, font=(FONT, 48)).pack(pady=(14, 0))
        tk.Label(box, text=APP_NAME, bg=WHITE, fg=DARK, font=(FONT, 26, "bold")).pack()
        tk.Label(box, text=APP_SUBTITLE, bg=WHITE, fg=GRAY, font=(FONT, 11)).pack()
        tk.Label(box, text=f"أهلاً بك في {APP_NAME}", bg=WHITE, fg=DARK, font=(FONT, 16, "bold")).pack(pady=(8, 0))
        tk.Label(box, text="سنساعدك في الوصول إلى التخصص الطبي المناسب", bg=WHITE, fg=GRAY, font=(FONT, 14)).pack(pady=4)
        row = tk.Frame(box, bg=WHITE)
        row.pack(pady=14)
        for icon, txt in (("🏥", "مستشفى مقترحة"), ("🔍", "تحليل الأعراض"), ("📝", "بياناتك")):
            c = tk.Frame(row, bg=LIGHT, padx=18, pady=10)
            c.pack(side="right", padx=10)
            tk.Label(c, text=icon, bg=LIGHT, font=(FONT, 26)).pack()
            tk.Label(c, text=txt, bg=LIGHT, fg=DARK, font=(FONT, 11, "bold")).pack()
        tk.Label(box, text="⚠ نظام تعليمي مساعد لاتخاذ القرار، وليس تشخيصاً ولا بديلاً عن الطبيب، ولا يصف أدوية.",
                 bg=WHITE, fg=RED, font=(FONT, 11, "bold"), wraplength=760, justify="center").pack(pady=(6, 2))
        tk.Label(box, text="في الحالات الطارئة اتصل بالإسعاف (123) فوراً ولا تؤخر الرعاية.", bg=WHITE, fg=RED,
                 font=(FONT, 11), wraplength=760).pack(pady=(0, 12))
        self.nav(("ابدأ الآن ▶", self.app.start), ("📁 سجل الحالات", lambda: self.app.show("history"), DARK),
                 ("خروج", self.app.destroy, RED))

class PatientScreen(Screen):
    title, icon, step = "البيانات الشخصية", "📝", "الخطوة 1 من 3"
    def build(self):
        self.v = {k: tk.StringVar() for k in ("name", "age", "address", "phone", "gov")}
        self.sex = tk.StringVar(value="")
        self.gov_map = {v: k for k, v in kb.GOVERNORATES.items()}
        box = card(self.body)
        box.pack(fill="x", pady=6, ipadx=10, ipady=10)
        box.grid_columnconfigure(0, weight=1)
        def row(r, text, widget):
            tk.Label(box, text=text, bg=WHITE, font=(FONT, 12, "bold"), fg=DARK, anchor="e").grid(row=r, column=1, sticky="e", padx=14, pady=7)
            widget.grid(row=r, column=0, sticky="e", padx=14, pady=7)
        ent = lambda var, w=38: tk.Entry(box, textvariable=var, font=(FONT, 12), justify="right", width=w, relief="solid", bd=1)
        row(0, "الاسم *", ent(self.v["name"]))
        row(1, "السن *", ent(self.v["age"], 10))
        sx = tk.Frame(box, bg=WHITE)
        for val, txt in (("female", "أنثى 👩"), ("male", "ذكر 👨")):
            tk.Radiobutton(sx, text=txt, variable=self.sex, value=val, bg=WHITE, font=(FONT, 12)).pack(side="right", padx=10)
        row(2, "النوع *", sx)
        self.gov_box = ttk.Combobox(box, textvariable=self.v["gov"], state="readonly", justify="right", width=28,
                                    values=[NONE_AR] + list(kb.GOVERNORATES.values()))
        row(3, "المحافظة", self.gov_box)
        row(4, "العنوان", ent(self.v["address"]))
        row(5, "رقم الهاتف (اختياري)", ent(self.v["phone"], 24))
        self.label("* حقول مطلوبة. بياناتك تُحفظ على جهازك فقط داخل قاعدة بيانات SQLite عند الضغط على «حفظ الحالة».", fg=GRAY, wraplength=800).pack(fill="x")
        self.nav(("التالي ◀", self.next), ("الرئيسية", lambda: self.app.show("home"), DARK))
        self.reset()
    def reset(self):
        for var in self.v.values(): var.set("")
        self.v["gov"].set(NONE_AR); self.sex.set("")
    def next(self):
        errors, clean = rb.validate_patient_form(self.v["name"].get(), self.v["age"].get(), self.sex.get(), self.v["phone"].get())
        if errors:
            return messagebox.showwarning("⚠ تنبيه", "\n".join(errors))
        clean["address"] = self.v["address"].get().strip()
        clean["governorate"] = self.gov_map.get(self.v["gov"].get(), "")
        self.app.patient.update(clean)
        self.app.show("symptoms")

class SymptomScreen(Screen):
    title, icon, step = "اختيار الأعراض", "🔍", "الخطوة 2 من 3"
    def build(self):
        self.label("اختر عرضاً أو أكثر من الأعراض التي تشعر بها:", font=(FONT, 12, "bold"), fg=DARK).pack(fill="x")
        self.vars = {k: tk.BooleanVar() for k in kb.SYMPTOMS}
        self.count = tk.StringVar()
        wrap = card(self.body)
        wrap.pack(fill="both", expand=True, pady=6)
        canvas = tk.Canvas(wrap, bg=WHITE, highlightthickness=0, height=250)
        sb = ttk.Scrollbar(wrap, command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="left", fill="y")
        canvas.pack(side="right", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=WHITE)
        canvas.create_window((0, 0), window=inner, anchor="ne", tags="w")
        canvas.bind("<Configure>", lambda e: canvas.coords("w", e.width, 0))
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(int(-ev.delta / 120), "units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        for i, (k, (ar, _)) in enumerate(kb.SYMPTOMS.items()):
            tk.Checkbutton(inner, text=ar, variable=self.vars[k], bg=WHITE, font=(FONT, 11), anchor="e", width=30,
                           command=self.update_count, activebackground=LIGHT).grid(row=i // 2, column=1 - (i % 2), sticky="e", padx=6, pady=2)
        opts = card(self.body)
        opts.pack(fill="x", pady=6, ipady=6)
        self.severity = tk.StringVar(value="moderate")
        r1 = tk.Frame(opts, bg=WHITE); r1.pack(fill="x", padx=12, pady=4)
        tk.Label(r1, text="مدة ظهور الأعراض:", bg=WHITE, font=(FONT, 11, "bold"), fg=DARK).pack(side="right")
        self.dur_box = ttk.Combobox(r1, state="readonly", justify="right", width=26, values=[v[0] for v in kb.DURATIONS.values()])
        self.dur_box.current(1)
        self.dur_box.pack(side="right", padx=8)
        r2 = tk.Frame(opts, bg=WHITE); r2.pack(fill="x", padx=12, pady=4)
        tk.Label(r2, text="شدة الأعراض:", bg=WHITE, font=(FONT, 11, "bold"), fg=DARK).pack(side="right")
        for k in ("severe", "moderate", "mild"):
            tk.Radiobutton(r2, text=kb.SEVERITIES[k][0], variable=self.severity, value=k, bg=WHITE, font=(FONT, 11)).pack(side="right", padx=8)
        tk.Label(r2, textvariable=self.count, bg=WHITE, fg=GREEN, font=(FONT, 11, "bold")).pack(side="left", padx=8)
        self.nav(("🔍 تحليل الأعراض", self.analyze, GREEN), ("◀ رجوع", lambda: self.app.show("patient"), DARK),
                 ("مسح الاختيار", self.reset, GRAY))
        self.reset()
    def update_count(self):
        n = sum(v.get() for v in self.vars.values())
        self.count.set(f"عدد الأعراض المختارة: {n}")
    def reset(self):
        for v in self.vars.values(): v.set(False)
        self.severity.set("moderate"); self.dur_box.current(1); self.update_count()
    def analyze(self):
        chosen = [k for k, v in self.vars.items() if v.get()]
        if not chosen:
            return messagebox.showwarning("⚠ تنبيه", "اختر عرضاً واحداً على الأقل.")
        self.app.patient.update(symptoms=chosen, duration=list(kb.DURATIONS)[self.dur_box.current()], severity=self.severity.get())
        self.app.result = engine.infer(self.app.patient)
        self.app.saved_id = None
        self.app.show("results")

class ResultScreen(Screen):
    title, icon, step = "نتيجة التحليل", "📊", "الخطوة 3 من 3"
    def build(self):
        self.banner = tk.Label(self.body, bg=RED, fg=WHITE, font=(FONT, 13, "bold"), wraplength=820, justify="center", pady=10)
        self.holder = tk.Frame(self.body, bg=WHITE, highlightbackground="#BBDEFB", highlightthickness=1)
        self.holder.pack(fill="both", expand=True)
        self.text = tk.Text(self.holder, wrap="word", font=(FONT, 12), bg=WHITE, relief="flat", padx=8, pady=8)
        sb = ttk.Scrollbar(self.holder, command=self.text.yview)
        self.text.configure(yscrollcommand=sb.set)
        sb.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)
        common = dict(justify="right", rmargin=12, lmargin1=12, lmargin2=12)
        self.text.tag_configure("title", font=(FONT, 14, "bold"), foreground=WHITE, background=BLUE, spacing1=10, spacing3=4, **common)
        self.text.tag_configure("body", font=(FONT, 12), spacing1=2, **common)
        self.text.tag_configure("bold", font=(FONT, 12, "bold"), foreground=DARK, spacing1=4, **common)
        self.text.tag_configure("warn", font=(FONT, 12, "bold"), foreground=RED, spacing1=4, **common)
        self.text.tag_configure("muted", font=(FONT, 10), foreground=GRAY, **common)
        self.report = None
        self.nav(("💾 حفظ الحالة", self.save, GREEN), ("🏥 بحث متقدم عن مستشفى", lambda: self.app.show("hospitals")),
                 ("◀ رجوع", lambda: self.app.show("symptoms"), DARK), ("🆕 حالة جديدة", self.app.start, DARK),
                 ("الرئيسية", lambda: self.app.show("home"), DARK))
    def render(self, report):
        t = self.text
        t.config(state="normal"); t.delete("1.0", "end")
        for icon, title, lines in report["sections"]:
            t.insert("end", f" {icon}  {title}\n", "title")
            for ln in lines:
                tag = "body"
                for prefix, name in (("##", "bold"), ("!!", "warn"), ("~~", "muted")):
                    if ln.startswith(prefix):
                        ln, tag = ln[2:], name
                        break
                t.insert("end", ln + "\n", tag)
            t.insert("end", "\n", "body")
        t.config(state="disabled")
        t.yview_moveto(0)
    def on_show(self):
        if not self.app.result:
            return
        self.report = rb.build_report(self.app.patient, self.app.result)
        self.app.report = self.report
        self.banner.pack_forget()
        if self.report["urgent"]:
            self.banner.config(text="🚨 " + self.report["urgent_message"])
            self.banner.pack(fill="x", pady=(0, 8), before=self.holder)
        self.render(self.report)
    def save(self):
        if self.app.saved_id:
            return messagebox.showinfo("ℹ معلومة", "هذه الحالة محفوظة بالفعل.")
        p, r = self.app.patient, self.app.result
        self.app.saved_id = db.save_case(p["age"], p["sex"], p["symptoms"], p["duration"], p["severity"],
                                         rb.report_to_text(self.report), r["top_specialty"], name=p.get("name", ""),
                                         address=p.get("address", ""), phone=p.get("phone", ""), governorate=p.get("governorate", ""))
        messagebox.showinfo("✅ تم الحفظ", "تم حفظ الحالة على جهازك. يمكنك مشاهدتها أو حذفها من «سجل الحالات».")

class HospitalScreen(Screen):
    title, icon = "البحث المتقدم عن مستشفى", "🏥"
    def build(self):
        f = card(self.body)
        f.pack(fill="x", pady=4, ipady=6)
        self.gov = ttk.Combobox(f, state="readonly", width=16, justify="right", values=[ALL_AR] + list(kb.GOVERNORATES.values()))
        self.typ = ttk.Combobox(f, state="readonly", width=10, justify="right", values=[ALL_AR] + list(kb.HOSPITAL_TYPES.values()))
        self.spec = ttk.Combobox(f, state="readonly", width=22, justify="right", values=[ALL_AR] + [v[0] for v in kb.SPECIALTIES.values()])
        for box, lbl in ((self.gov, "المحافظة"), (self.typ, "النوع"), (self.spec, "التخصص")):
            tk.Label(f, text=lbl, bg=WHITE, font=(FONT, 10, "bold")).pack(side="right", padx=(10, 2), pady=6)
            box.current(0)
            box.pack(side="right")
        self.unver = tk.BooleanVar()
        tk.Checkbutton(self.body, text="أظهر أيضاً المستشفيات التي لم تُوثّق تخصصاتها (قد لا تقدم هذا التخصص)", variable=self.unver,
                       bg=BG, font=(FONT, 10)).pack(anchor="e", pady=4)
        button(self.body, "🔎 بحث", self.search).pack(anchor="e")
        cols = ("spec", "phone", "type", "city", "name")
        self.tree = ttk.Treeview(self.body, columns=cols, show="headings", height=8)
        for c, t, w in (("spec", "التخصصات الموثقة", 170), ("phone", "الهاتف", 130), ("type", "النوع", 70),
                        ("city", "المحافظة / المدينة", 150), ("name", "اسم المستشفى", 260)):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="e")
        self.tree.pack(fill="both", expand=True, pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.show_details)
        self.detail = tk.Label(self.body, text="", bg=BG, font=(FONT, 10), justify="right", anchor="e", wraplength=820)
        self.detail.pack(fill="x")
        self.rows = {}
        self.nav(("◀ النتيجة", lambda: self.app.show("results"), DARK), ("الرئيسية", lambda: self.app.show("home"), DARK))
    def on_show(self):
        if self.app.result:
            self.spec.set(kb.SPECIALTIES[self.app.result["top_specialty"]][0])
        gov = self.app.patient.get("governorate") or rb.guess_governorate(self.app.patient.get("address", ""))
        if gov:
            self.gov.set(kb.GOVERNORATES[gov])
        self.search()
    def search(self):
        g = {v: k for k, v in kb.GOVERNORATES.items()}.get(self.gov.get())
        t = {v: k for k, v in kb.HOSPITAL_TYPES.items()}.get(self.typ.get())
        s = {v[0]: k for k, v in kb.SPECIALTIES.items()}.get(self.spec.get())
        res = db.search_hospitals(g, t, s, self.unver.get())
        self.tree.delete(*self.tree.get_children())
        self.rows = {}
        for h in res:
            specs = "، ".join(kb.SPECIALTIES[x][0] for x in h["specialties"]) or db.NOT_VERIFIED
            iid = self.tree.insert("", "end", values=(specs, db.display(h["phone"]), kb.HOSPITAL_TYPES.get(h["type"], db.NOT_VERIFIED),
                                   f"{kb.GOVERNORATES.get(h['governorate'], h['governorate'])} / {h['city']}", h["name_ar"] or h["name_en"]))
            self.rows[iid] = h
        self.detail.config(text="لا توجد نتائج مطابقة في قاعدة البيانات الحالية." if not res else f"عدد النتائج: {len(res)} — اختر مستشفى لعرض التفاصيل.")
    def show_details(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        h = self.rows[sel[0]]
        self.detail.config(text=(f"{h['name_en']}" + ("" if h["name_ar"] else "  (الاسم العربي غير موثق)") +
                                 f"\nالعنوان: {db.display(h['address'])}\nالموقع: {db.display(h['website'])}\nالمصدر: {h['source_url']}" +
                                 (f"\nملاحظات: {h['notes']}" if h["notes"] else "")))

class HistoryScreen(Screen):
    title, icon = "سجل الحالات المحفوظة", "📁"
    def build(self):
        self.tree = ttk.Treeview(self.body, columns=("spec", "sev", "age", "name", "date", "id"), show="headings", height=10)
        for c, t, w in (("spec", "التخصص المقترح", 160), ("sev", "الشدة", 70), ("age", "السن", 50), ("name", "الاسم", 150),
                        ("date", "التاريخ", 130), ("id", "#", 40)):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="e")
        self.tree.pack(fill="both", expand=True)
        self.cases = {}
        self.nav(("👁 عرض", self.view), ("🗑 حذف المحدد", self.delete, RED), ("حذف الكل", self.delete_all, RED),
                 ("الرئيسية", lambda: self.app.show("home"), DARK))
    def on_show(self):
        self.tree.delete(*self.tree.get_children())
        self.cases = {}
        for c in db.list_cases():
            iid = self.tree.insert("", "end", values=(kb.SPECIALTIES.get(c["top_specialty"], ("",))[0], kb.SEVERITIES.get(c["severity"], ("",))[0],
                                   c["age"], c.get("name") or "-", c["created"], c["id"]))
            self.cases[iid] = c
    def selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("ℹ معلومة", "اختر حالة من القائمة أولاً.")
            return None
        return self.cases[sel[0]]
    def view(self):
        c = self.selected()
        if not c:
            return
        win = tk.Toplevel(self)
        win.title(f"تفاصيل الحالة #{c['id']}")
        win.geometry("700x560")
        t = tk.Text(win, wrap="word", font=(FONT, 12), padx=10, pady=10)
        t.tag_configure("r", justify="right")
        t.insert("end", f"الاسم: {c.get('name') or '-'}   |   الهاتف: {c.get('phone') or '-'}   |   {c['created']}\n\n" + (c["report"] or ""), "r")
        t.config(state="disabled")
        t.pack(fill="both", expand=True)
    def delete(self):
        c = self.selected()
        if c and messagebox.askyesno("تأكيد", "هل تريد حذف هذه الحالة؟"):
            db.delete_case(c["id"])
            self.on_show()
            messagebox.showinfo("✅ تم", "تم حذف الحالة.")
    def delete_all(self):
        if messagebox.askyesno("تأكيد", "هل تريد حذف جميع الحالات المحفوظة؟"):
            db.delete_all_cases()
            self.on_show()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} - {APP_SUBTITLE}")
        self.geometry("980x720")
        self.minsize(900, 640)
        self.configure(bg=BG)
        self.option_add("*TCombobox*Listbox.font", (FONT, 11))
        db.init_db()
        self.patient, self.result, self.report, self.saved_id = {}, None, None, None
        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.screens = {n: c(self) for n, c in (("home", HomeScreen), ("patient", PatientScreen), ("symptoms", SymptomScreen),
                                                 ("results", ResultScreen), ("hospitals", HospitalScreen), ("history", HistoryScreen))}
        for s in self.screens.values():
            s.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.show("home")
    def report_callback_exception(self, exc, val, tb):
        messagebox.showerror("خطأ", f"حدث خطأ غير متوقع:\n{val}")
    def start(self):
        """Begin a new case with empty forms."""
        self.patient, self.result, self.report, self.saved_id = {}, None, None, None
        self.screens["patient"].reset()
        self.screens["symptoms"].reset()
        self.show("patient")
    def show(self, name):
        s = self.screens[name]
        s.on_show()
        s.tkraise()

def run():
    App().mainloop()
