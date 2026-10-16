"""Builds the single-screen result report (patient summary, symptoms, rule-based assessment,
specialty, recommended hospitals, tests to discuss, guidance). No GUI code, so it is testable."""
import re
import knowledge_base as kb
import hospital_database as db

SEX_AR = {"male": "ذكر", "female": "أنثى"}
_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

def _norm(text):
    t = (text or "").lower().translate(_AR_DIGITS)
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي")):
        t = t.replace(a, b)
    return t

def guess_governorate(text):
    """Find a governorate name (Arabic or English) inside a free-text address. '' if none."""
    t = _norm(text)
    if not t:
        return ""
    for en, ar in kb.GOVERNORATES.items():
        if _norm(ar) in t or en.lower() in t:
            return en
    aliases = {"اسكندريه": "Alexandria", "6 اكتوبر": "Giza", "السادس من اكتوبر": "Giza",
               "المهندسين": "Giza", "مدينه نصر": "Cairo", "المعادي": "Cairo", "التجمع": "Cairo"}
    for k, v in aliases.items():
        if k in t:
            return v
    return ""

def validate_patient_form(name, age_text, sex, phone=""):
    """Returns (errors, cleaned). Phone is optional."""
    errors, cleaned = [], {}
    name = (name or "").strip()
    if len(name) < 2:
        errors.append("الاسم مطلوب (حرفان على الأقل).")
    cleaned["name"] = name
    try:
        age = int(str(age_text).strip().translate(_AR_DIGITS))
        if not 0 <= age <= 120:
            raise ValueError
        cleaned["age"] = age
    except ValueError:
        errors.append("السن يجب أن يكون رقما صحيحا بين 0 و 120.")
    if sex not in SEX_AR:
        errors.append("اختر النوع (ذكر / أنثى).")
    cleaned["sex"] = sex
    phone = (phone or "").strip().translate(_AR_DIGITS)
    digits = re.sub(r"[\s\-+()]", "", phone)
    if phone and not (digits.isdigit() and 7 <= len(digits) <= 15):
        errors.append("رقم الهاتف غير صحيح (اتركه فارغا إن لم ترغب في إدخاله).")
    cleaned["phone"] = phone
    return errors, cleaned

def hospital_line(h):
    name = h["name_ar"] or h["name_en"]
    parts = [f"##🏥 {name}"]
    place = kb.GOVERNORATES.get(h["governorate"], h["governorate"])
    if h["city"]:
        place += " - " + h["city"]
    parts.append(f"المحافظة/المدينة: {place}  |  النوع: {kb.HOSPITAL_TYPES.get(h['type'], db.NOT_VERIFIED)}")
    parts.append(f"العنوان: {db.display(h['address'])}")
    parts.append(f"الهاتف: {db.display(h['phone'])}")
    if h["website"]:
        parts.append(f"الموقع: {h['website']}")
    if h["specialties"]:
        parts.append("التخصصات الموثقة: " + "، ".join(kb.SPECIALTIES[s][0] for s in h["specialties"]))
    else:
        parts.append("~~تخصصات هذه المستشفى غير موثقة في قاعدة البيانات؛ اتصل بها للتأكد.")
    parts.append(f"~~المصدر: {h['source_url']}")
    return parts

def build_report(patient, result, db_path=None):
    spec = result["top_specialty"]
    spec_ar, spec_en = kb.SPECIALTIES[spec]
    gov = patient.get("governorate") or guess_governorate(patient.get("address", ""))
    hospitals, level = db.recommend_hospitals(gov, spec, db_path=db_path)
    gov_ar = kb.GOVERNORATES.get(gov, "")
    sections = []

    # 1. patient summary
    s = [f"الاسم: {patient.get('name') or '-'}",
         f"السن: {patient.get('age', '-')}  |  النوع: {SEX_AR.get(patient.get('sex'), '-')}",
         f"العنوان: {patient.get('address') or '-'}" + (f" ({gov_ar})" if gov_ar else ""),
         f"الهاتف: {patient.get('phone') or '-'}"]
    sections.append(("👤", "ملخص بيانات المريض", s))

    # 2. symptoms
    sym = ["• " + kb.SYMPTOMS[k][0] for k in patient.get("symptoms", [])]
    sym.append(f"المدة: {kb.DURATIONS[patient['duration']][0]}  |  الشدة: {kb.SEVERITIES[patient['severity']][0]}")
    sections.append(("🩺", "الأعراض التي اخترتها", sym))

    # 3. rule-based assessment
    a = []
    if result["matched_rules"]:
        a.append("القواعد التي تحققت في النظام:")
        for r in result["matched_rules"]:
            a.append(f"• {r['id']}: {r['name_ar']} ← {kb.SPECIALTIES[r['specialty']][0]} (الوزن {r['weight']})")
    else:
        a.append("لم تنطبق أي قاعدة محددة على هذه الأعراض؛ يُقترح البدء بطبيب الباطنة/العام.")
    a.append("~~هذا تقييم مبني على قواعد تعليمية وليس تشخيصا مؤكدا.")
    sections.append(("📋", "التقييم حسب قواعد النظام", a))

    # 4. specialty
    sp = [f"##التخصص المقترح: {spec_ar} ({spec_en})"]
    others = [k for k, _ in result["scores"][1:4]]
    if others:
        sp.append("تخصصات أخرى محتملة: " + "، ".join(kb.SPECIALTIES[k][0] for k in others))
    sp.append("~~التخصص المقترح ليس تشخيصا؛ الطبيب هو من يحدد التشخيص.")
    sections.append(("⚕️", "التخصص الطبي المناسب", sp))

    # 5. hospitals (names come straight from the database)
    h = []
    if result["urgent"]:
        h.append("!!اطلب الإسعاف (123) أو توجه لأقرب طوارئ الآن، ولا تنتظر البحث عن مستشفى. المستشفيات التالية للعلم فقط:")
    msgs = {
        "exact": f"مستشفيات {('في ' + gov_ar + ' ') if gov_ar else ''}مسجل لها تخصص {spec_ar} في قاعدة البيانات:",
        "unverified_specialty": f"لا توجد مستشفى موثق لها تخصص {spec_ar} في {gov_ar}. هذه مستشفيات في المحافظة لم تُوثّق تخصصاتها (قد لا تقدم هذا التخصص):",
        "other_governorates": f"لا توجد مستشفيات موثقة لتخصص {spec_ar} في محافظتك (أو لم تُحدَّد محافظة). المتاح في قاعدة البيانات من محافظات أخرى:",
        "same_governorate_any": f"لا توجد بيانات تخصص موثقة لـ{spec_ar}. هذه مستشفيات في {gov_ar} (التخصص غير مؤكد):",
        "none": "لا توجد مستشفيات مطابقة في قاعدة البيانات الحالية. اسأل طبيبك أو اتصل بالإسعاف (123) عند الحاجة.",
    }
    h.append(msgs[level])
    for hosp in hospitals:
        h.append("")
        h.extend(hospital_line(hosp))
    h.append("")
    h.append("~~البيانات من مصادر مذكورة لكل مستشفى وقد تكون قديمة؛ تأكد بالاتصال قبل الذهاب.")
    sections.append(("🏥", "المستشفيات المقترحة", h))

    # 6. tests to discuss
    t = [f"• {x}" for x in kb.TESTS_TO_DISCUSS.get(spec, [])]
    t.append("~~للعلم فقط: قد يناقشها المريض مع الطبيب، والطبيب وحده يقرر ما يلزم. لا يصف النظام أدوية أو علاجا.")
    sections.append(("🔬", "فحوصات قد تناقشها مع الطبيب", t))

    # 7. guidance
    g = []
    if result["urgent"]:
        g.append("!!" + result["urgent_message"])
    for n in result["extra_notes"]:
        g.append("!!" + n)
    if not result["urgent"]:
        if patient.get("severity") == "severe":
            g.append("الشدة التي اخترتها شديدة؛ لا تؤجل الكشف، وتوجه للطبيب اليوم أو للطوارئ إذا ساءت الأعراض.")
        elif result["fallback"]:
            g.append("ابدأ بالكشف عند طبيب عام أو باطنة، وراجعه إذا استمرت الأعراض أو ازدادت.")
        else:
            g.append(f"يُنصح بحجز كشف عند طبيب {spec_ar} في أقرب وقت مناسب، وتوجه للطوارئ إذا ازدادت الأعراض.")
        g.append("اذكر للطبيب مدة الأعراض وأي أمراض مزمنة أو أدوية تتناولها حاليا.")
    g.append("~~" + result["disclaimer"])
    sections.append(("💡", "رسالة إرشادية", g))

    return {"urgent": result["urgent"], "urgent_message": result["urgent_message"], "sections": sections,
            "hospitals": hospitals, "level": level, "governorate": gov, "specialty": spec}

def report_to_text(report):
    """Plain-text version saved with the case in SQLite."""
    out = []
    if report["urgent"]:
        out += ["!!! " + report["urgent_message"], ""]
    for icon, title, lines in report["sections"]:
        out.append(f"== {title} ==")
        out += [ln.lstrip("#!~") for ln in lines]
        out.append("")
    return "\n".join(out)
