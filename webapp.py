"""Web version (WSGI, Python standard library only). Same knowledge base, inference engine,
report builder and hospitals.db as the desktop app. Stateless steps: data travels in the forms.
History is private per browser (anonymous cookie id). Run locally: python run_web.py"""
import html, os, re, secrets, urllib.parse
from http import cookies
import knowledge_base as kb
import inference_engine as engine
import hospital_database as db
import report_builder as rb
from knowledge_base import APP_NAME, APP_SUBTITLE

e = lambda s: html.escape(str(s if s is not None else ""), quote=True)
MSGS = {"saved": "✅ تم حفظ الحالة.", "deleted": "✅ تم حذف الحالة.", "cleared": "✅ تم حذف جميع حالاتك."}
CSS = """
:root{--b:#1565C0;--d:#0D47A1;--l:#E3F2FD;--r:#C62828;--g:#2E7D32;--t:#546E7A}
*{box-sizing:border-box}body{margin:0;background:#F5F9FF;color:#1b2733;font-family:Tahoma,"Segoe UI",Arial,sans-serif;font-size:17px;line-height:1.7}
header{background:var(--b);color:#fff;padding:12px 16px}header .in{max-width:900px;margin:auto;display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center;justify-content:space-between}
header a{color:#fff;text-decoration:none;font-weight:bold;padding:4px 8px;border-radius:8px}header a:hover{background:var(--d)}
main{max-width:900px;margin:auto;padding:14px}.card{background:#fff;border:1px solid #BBDEFB;border-radius:14px;padding:16px;margin:12px 0}
h1{color:var(--d);margin:.2em 0}h2{background:var(--b);color:#fff;border-radius:10px;padding:6px 12px;font-size:19px;margin:0 0 10px}
.btn{display:inline-block;background:var(--b);color:#fff;border:0;border-radius:10px;padding:12px 20px;font:inherit;font-weight:bold;cursor:pointer;text-decoration:none;margin:4px 0 4px 8px}
.btn:hover{background:var(--d)}.btn.g{background:var(--g)}.btn.r{background:var(--r)}.btn.s{background:var(--t)}
label{display:block;font-weight:bold;color:var(--d);margin-top:12px}input[type=text],input[type=tel],input[type=number],select{width:100%;padding:11px;border:1px solid #90A4AE;border-radius:10px;font:inherit;background:#fff}
.opts{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:6px}.opts label{font-weight:normal;color:inherit;margin:0;background:var(--l);padding:10px;border-radius:10px;cursor:pointer}
.row{display:flex;flex-wrap:wrap;gap:12px}.row>div{flex:1 1 200px}.feat{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}.feat div{background:var(--l);border-radius:12px;padding:12px 20px;text-align:center;font-weight:bold;color:var(--d)}
.big{font-size:44px;text-align:center}.center{text-align:center}.banner{background:var(--r);color:#fff;font-weight:bold;border-radius:12px;padding:14px;margin:12px 0;font-size:19px}
.err{background:#FFEBEE;border:1px solid var(--r);color:var(--r);border-radius:10px;padding:10px;margin:10px 0}.ok{background:#E8F5E9;border:1px solid var(--g);color:var(--g);border-radius:10px;padding:10px;margin:10px 0;font-weight:bold}
.b{font-weight:bold;color:var(--d);margin:.3em 0}.warn{font-weight:bold;color:var(--r);margin:.3em 0}.muted{color:var(--t);font-size:14px;margin:.2em 0;word-break:break-word}p{margin:.25em 0}.gap{height:8px}
a{color:var(--b)}.steps{color:#E3F2FD;font-size:14px}.pre{white-space:pre-wrap}footer{max-width:900px;margin:auto;padding:12px;color:var(--t);font-size:14px;text-align:center}
"""

def layout(title, body):
    page = f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} | {APP_NAME}</title><style>{CSS}</style></head><body>
<header><div class="in"><strong>🩺 {APP_NAME}</strong><nav><a href="/">الرئيسية</a><a href="/patient">حالة جديدة</a><a href="/hospitals">المستشفيات</a><a href="/history">سجل الحالات</a></nav></div></header>
<main>{body}</main><footer>⚠ نظام تعليمي مساعد لاتخاذ القرار، وليس تشخيصاً ولا بديلاً عن الطبيب، ولا يصف أدوية. في الطوارئ اتصل بالإسعاف (123).</footer></body></html>"""
    return page

def linkify(text):
    return re.sub(r"https?://[^\s<]+", lambda m: f'<a dir="ltr" href="{m.group(0)}" rel="noopener noreferrer" target="_blank">{m.group(0)}</a>', e(text))

def first(form, k): return (form.get(k) or [""])[0].strip()

def patient_from(form):
    errors, p = rb.validate_patient_form(first(form, "name"), first(form, "age"), first(form, "sex"), first(form, "phone"))
    p["name"], p["phone"] = p.get("name", "")[:80], p.get("phone", "")[:30]
    p["address"] = first(form, "address")[:200]
    g = first(form, "gov")
    p["governorate"] = g if g in kb.GOVERNORATES else ""
    return errors, p

def case_from(form):
    errors, p = patient_from(form)
    chosen = set(form.get("s", []))
    p["symptoms"] = [k for k in kb.SYMPTOMS if k in chosen]
    d, s = first(form, "duration"), first(form, "severity")
    p["duration"] = d if d in kb.DURATIONS else "1_7d"
    p["severity"] = s if s in kb.SEVERITIES else "moderate"
    return errors, p

def hidden(p, with_case=False):
    items = [("name", p.get("name", "")), ("age", p.get("age", "")), ("sex", p.get("sex", "")), ("gov", p.get("governorate", "")),
             ("address", p.get("address", "")), ("phone", p.get("phone", ""))]
    if with_case:
        items += [("s", k) for k in p.get("symptoms", [])] + [("duration", p["duration"]), ("severity", p["severity"])]
    return "".join(f'<input type="hidden" name="{n}" value="{e(v)}">' for n, v in items)

def errs(errors): return "".join(f'<div class="err">⚠ {e(x)}</div>' for x in errors)

# ---------------- pages ----------------
def page_home():
    return layout("الرئيسية", f"""<div class="card center"><div class="big">🏥</div><h1>{APP_NAME}</h1>
<p class="muted" dir="ltr" style="font-size:16px">{APP_SUBTITLE}</p>
<p><strong>أهلاً بك في {APP_NAME}</strong><br>سنساعدك في الوصول إلى التخصص الطبي المناسب</p>
<div class="feat"><div>📝<br>بياناتك</div><div>🔍<br>تحليل الأعراض</div><div>🏥<br>مستشفى مقترحة</div></div><p></p>
<p class="warn">⚠ هذا النظام تعليمي وليس تشخيصاً، ولا يغني عن الطبيب، ولا يصف أدوية.<br>في الحالات الطارئة اتصل بالإسعاف (123) فوراً.</p>
<a class="btn g" href="/patient">ابدأ الآن ◀</a><a class="btn" href="/history">📁 سجل الحالات</a></div>""")

def page_patient(p=None, errors=()):
    p = p or {}
    gov = "".join(f'<option value="{k}"{" selected" if k == p.get("governorate") else ""}>{e(v)}</option>' for k, v in kb.GOVERNORATES.items())
    sx = lambda v: " checked" if p.get("sex") == v else ""
    return layout("البيانات الشخصية", f"""<div class="card"><h2>📝 الخطوة 1 من 3: البيانات الشخصية</h2>{errs(errors)}
<form method="post" action="/patient"><label>الاسم *</label><input type="text" name="name" maxlength="80" value="{e(p.get('name'))}" required>
<div class="row"><div><label>السن *</label><input type="number" name="age" min="0" max="120" value="{e(p.get('age'))}" required></div>
<div><label>النوع *</label><label style="font-weight:normal"><input type="radio" name="sex" value="female"{sx('female')}> أنثى 👩</label>
<label style="font-weight:normal"><input type="radio" name="sex" value="male"{sx('male')}> ذكر 👨</label></div></div>
<label>المحافظة</label><select name="gov"><option value="">— غير محدد —</option>{gov}</select>
<label>العنوان</label><input type="text" name="address" maxlength="200" value="{e(p.get('address'))}">
<label>رقم الهاتف (اختياري)</label><input type="tel" name="phone" maxlength="30" value="{e(p.get('phone'))}">
<p class="muted">* حقول مطلوبة. لا تُدخل بيانات حقيقية إذا كنت تجرّب النسخة على الإنترنت.</p>
<button class="btn g" type="submit">التالي ◀</button><a class="btn s" href="/">الرئيسية</a></form></div>""")

def page_symptoms(p, errors=()):
    chosen = set(p.get("symptoms", []))
    boxes = "".join(f'<label><input type="checkbox" name="s" value="{k}"{" checked" if k in chosen else ""}> {e(ar)}</label>' for k, (ar, _) in kb.SYMPTOMS.items())
    dur = "".join(f'<option value="{k}"{" selected" if k == p.get("duration", "1_7d") else ""}>{e(v[0])}</option>' for k, v in kb.DURATIONS.items())
    sev = "".join(f'<label style="font-weight:normal;display:inline-block;margin-left:14px"><input type="radio" name="severity" value="{k}"{" checked" if k == p.get("severity", "moderate") else ""}> {e(v[0])}</label>' for k, v in kb.SEVERITIES.items())
    return layout("الأعراض", f"""<div class="card"><h2>🔍 الخطوة 2 من 3: الأعراض</h2>{errs(errors)}
<form method="post" action="/results">{hidden(p)}<p class="b">اختر عرضاً أو أكثر:</p><div class="opts">{boxes}</div>
<label>مدة ظهور الأعراض</label><select name="duration">{dur}</select><label>شدة الأعراض</label><div>{sev}</div><p></p>
<button class="btn g" type="submit">🔍 تحليل الأعراض</button></form>
<form method="post" action="/patient">{hidden(p)}<button class="btn s" type="submit" name="back" value="1">▶ رجوع</button></form></div>""")

def render_sections(report):
    out = ""
    if report["urgent"]:
        out += f'<div class="banner">🚨 {e(report["urgent_message"])}</div>'
    for icon, title, lines in report["sections"]:
        out += f'<section class="card"><h2>{icon} {e(title)}</h2>'
        for ln in lines:
            if not ln:
                out += '<div class="gap"></div>'; continue
            cls = "p"
            for prefix, c in (("##", "b"), ("!!", "warn"), ("~~", "muted")):
                if ln.startswith(prefix):
                    ln, cls = ln[2:], c; break
            out += f'<p class="{cls}">{linkify(ln)}</p>'
        out += "</section>"
    return out

def page_results(p):
    result = engine.infer(p)
    report = rb.build_report(p, result)
    q = urllib.parse.urlencode({"g": report["governorate"], "s": report["specialty"]})
    return layout("النتيجة", f"""<h1>📊 نتيجة التحليل <span class="steps" style="color:#546E7A">(الخطوة 3 من 3)</span></h1>{render_sections(report)}
<div class="card center"><form method="post" action="/save" style="display:inline">{hidden(p, True)}<button class="btn g" type="submit">💾 حفظ الحالة</button></form>
<a class="btn" href="/hospitals?{q}">🏥 بحث متقدم عن مستشفى</a><a class="btn s" href="/patient">🆕 حالة جديدة</a></div>"""), result, report

def hospital_card(h):
    place = kb.GOVERNORATES.get(h["governorate"], h["governorate"]) + (" - " + h["city"] if h["city"] else "")
    specs = "، ".join(kb.SPECIALTIES[s][0] for s in h["specialties"]) or db.NOT_VERIFIED
    web = f'<p>الموقع: {linkify(h["website"])}</p>' if h["website"] else ""
    note = f'<p class="muted">ملاحظات: {e(h["notes"])}</p>' if h["notes"] else ""
    ar = "" if h["name_ar"] else '<span class="muted"> (الاسم العربي غير موثق)</span>'
    return f"""<section class="card"><p class="b">🏥 {e(h['name_ar'] or h['name_en'])}{ar}</p><p>{e(h['name_en']) if h['name_ar'] else ''}</p>
<p>المحافظة/المدينة: {e(place)} | النوع: {e(kb.HOSPITAL_TYPES.get(h['type'], db.NOT_VERIFIED))}</p><p>العنوان: {e(db.display(h['address']))}</p>
<p>الهاتف: {e(db.display(h['phone']))}</p>{web}<p>التخصصات الموثقة: {e(specs)}</p><p class="muted">المصدر: {linkify(h['source_url'])}</p>{note}</section>"""

def page_hospitals(q):
    g, t, s, u = first(q, "g"), first(q, "t"), first(q, "s"), first(q, "u") == "1"
    g = g if g in kb.GOVERNORATES else ""; t = t if t in kb.HOSPITAL_TYPES else ""; s = s if s in kb.SPECIALTIES else ""
    opt = lambda items, cur: "".join(f'<option value="{k}"{" selected" if k == cur else ""}>{e(v)}</option>' for k, v in items)
    res = db.search_hospitals(g or None, t or None, s or None, u)
    msg = f"<p class='b'>عدد النتائج: {len(res)}</p>" if res else '<div class="err">لا توجد نتائج مطابقة في قاعدة البيانات الحالية.</div>'
    return layout("المستشفيات", f"""<div class="card"><h2>🏥 البحث عن مستشفى</h2><form method="get" action="/hospitals"><div class="row">
<div><label>المحافظة</label><select name="g"><option value="">الكل</option>{opt([(k, v) for k, v in kb.GOVERNORATES.items()], g)}</select></div>
<div><label>النوع</label><select name="t"><option value="">الكل</option>{opt(kb.HOSPITAL_TYPES.items(), t)}</select></div>
<div><label>التخصص</label><select name="s"><option value="">الكل</option>{opt([(k, v[0]) for k, v in kb.SPECIALTIES.items()], s)}</select></div></div>
<label style="font-weight:normal"><input type="checkbox" name="u" value="1"{' checked' if u else ''}> أظهر أيضاً المستشفيات التي لم تُوثّق تخصصاتها (قد لا تقدم هذا التخصص)</label>
<button class="btn" type="submit">🔎 بحث</button></form></div>{msg}{''.join(hospital_card(h) for h in res)}""")

def page_history(owner, flash=""):
    cases = db.list_cases(owner=owner)
    rows = "".join(f"""<section class="card"><p class="b">{e(c.get('name') or '-')} — {e(kb.SPECIALTIES.get(c['top_specialty'], ('',))[0])}</p>
<p class="muted">{e(c['created'])} | السن {e(c['age'])} | الشدة: {e(kb.SEVERITIES.get(c['severity'], ('',))[0])}</p>
<a class="btn" href="/history/{c['id']}">👁 عرض</a><a class="btn r" href="/history/{c['id']}/delete">🗑 حذف</a></section>""" for c in cases)
    empty = '<div class="card center">لا توجد حالات محفوظة على هذا المتصفح.</div>' if not cases else ""
    clear = '<a class="btn r" href="/history/delete-all">حذف جميع حالاتي</a>' if cases else ""
    ok = f'<div class="ok">{MSGS[flash]}</div>' if flash in MSGS else ""
    return layout("سجل الحالات", f'<h1>📁 سجل الحالات</h1><p class="muted">كل متصفح يرى حالاته فقط.</p>{ok}{empty}{rows}{clear}')

def page_case(c):
    return layout("تفاصيل الحالة", f"""<div class="card"><h2>تفاصيل الحالة #{c['id']}</h2><p class="muted">{e(c['created'])} | الهاتف: {e(c.get('phone') or '-')}</p>
<div class="pre">{e(c['report'])}</div><a class="btn" href="/history">◀ رجوع</a></div>""")

def page_confirm(text, action, back):
    return layout("تأكيد", f"""<div class="card center"><h2>تأكيد</h2><p>{e(text)}</p><form method="post" action="{action}"><button class="btn r" type="submit">نعم، احذف</button>
<a class="btn s" href="{back}">إلغاء</a></form></div>""")

def page_error(code, text):
    return layout(text, f'<div class="card center"><div class="big">⚠</div><h1>{code}</h1><p>{e(text)}</p><a class="btn" href="/">الرئيسية</a></div>')

# ---------------- WSGI plumbing ----------------
def parse_body(environ):
    try: n = min(int(environ.get("CONTENT_LENGTH") or 0), 50_000)
    except ValueError: n = 0
    return urllib.parse.parse_qs(environ["wsgi.input"].read(n).decode("utf-8", "replace"), keep_blank_values=True)

def get_owner(environ):
    c = cookies.SimpleCookie(environ.get("HTTP_COOKIE", ""))
    cid = c["cid"].value if "cid" in c else ""
    if re.fullmatch(r"[0-9a-f]{32}", cid):
        return cid, False
    return secrets.token_hex(16), True

def application(environ, start_response):
    method, path = environ["REQUEST_METHOD"], environ.get("PATH_INFO", "/") or "/"
    owner, new_cookie = get_owner(environ)
    q = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
    status, extra, body = "200 OK", [], ""
    def redirect(to): return "303 See Other", [("Location", to)], ""
    try:
        form = parse_body(environ) if method == "POST" else {}
        m = re.fullmatch(r"/history/(\d+)(/delete)?", path)
        if path == "/health": body = "ok"
        elif path == "/" and method == "GET": body = page_home()
        elif path == "/patient" and method == "GET": body = page_patient()
        elif path == "/patient" and method == "POST":
            errors, p = patient_from(form)
            if "back" in form:
                body = page_patient(p)
            elif errors: body = page_patient(p, errors)
            else: _, p = case_from(form); body = page_symptoms(p)
        elif path == "/results" and method == "POST":
            errors, p = case_from(form)
            if errors: body = page_patient(p, errors)
            elif not p["symptoms"]: body = page_symptoms(p, ["اختر عرضاً واحداً على الأقل."])
            else: body = page_results(p)[0]
        elif path == "/save" and method == "POST":
            errors, p = case_from(form)
            if errors or not p["symptoms"]: status, body = "400 Bad Request", page_error(400, "بيانات غير مكتملة")
            else:
                result = engine.infer(p); report = rb.build_report(p, result)
                db.save_case(p["age"], p["sex"], p["symptoms"], p["duration"], p["severity"], rb.report_to_text(report),
                             result["top_specialty"], name=p["name"], address=p["address"], phone=p["phone"],
                             governorate=p["governorate"], owner=owner)
                status, extra, body = redirect("/history?msg=saved")
        elif path == "/hospitals" and method == "GET": body = page_hospitals(q)
        elif path == "/history" and method == "GET": body = page_history(owner, first(q, "msg"))
        elif path == "/history/delete-all":
            if method == "POST": db.delete_all_cases(owner=owner); status, extra, body = redirect("/history?msg=cleared")
            else: body = page_confirm("هل تريد حذف جميع حالاتك المحفوظة؟", "/history/delete-all", "/history")
        elif m and method in ("GET", "POST"):
            cid = int(m.group(1)); c = db.get_case(cid, owner=owner)
            if not c: status, body = "404 Not Found", page_error(404, "الحالة غير موجودة")
            elif m.group(2) and method == "POST": db.delete_case(cid, owner=owner); status, extra, body = redirect("/history?msg=deleted")
            elif m.group(2): body = page_confirm("هل تريد حذف هذه الحالة؟", f"/history/{cid}/delete", "/history")
            elif method == "GET": body = page_case(c)
            else: status, body = "405 Method Not Allowed", page_error(405, "طريقة غير مسموحة")
        elif path in ("/", "/patient", "/results", "/save", "/hospitals", "/history"):
            status, body = "405 Method Not Allowed", page_error(405, "طريقة غير مسموحة")
        else: status, body = "404 Not Found", page_error(404, "الصفحة غير موجودة")
    except Exception:  # never show internals to the visitor
        status, body = "500 Internal Server Error", page_error(500, "حدث خطأ غير متوقع")
    headers = [("Content-Type", "text/plain; charset=utf-8" if path == "/health" else "text/html; charset=utf-8"),
               ("X-Content-Type-Options", "nosniff"), ("Referrer-Policy", "no-referrer"), ("Cache-Control", "no-store"),
               ("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")] + extra
    if new_cookie:
        secure = "; Secure" if environ.get("wsgi.url_scheme") == "https" or environ.get("HTTP_X_FORWARDED_PROTO") == "https" else ""
        headers.append(("Set-Cookie", f"cid={owner}; Path=/; Max-Age=31536000; HttpOnly; SameSite=Lax{secure}"))
    data = body.encode("utf-8")
    headers.append(("Content-Length", str(len(data))))
    start_response(status, headers)
    return [data]

# create/upgrade the database at start-up
if not os.path.exists(db.DB_PATH):
    db.seed_database()
else:
    db.init_db()
