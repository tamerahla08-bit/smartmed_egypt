"""Stage 3 - Knowledge Base: symptoms, specialties, governorates and IF-THEN rules.
Pure data, no GUI code, so it can be edited and explained easily.
Rule format: all = facts that must ALL be present; any = list of facts of which
at least `min_any` must be present; specialty = suggested specialty key;
weight = strength (1-4); urgent = True shows an urgent-care warning."""

# symptom key: (Arabic, English)
SYMPTOMS = {
    "chest_pain": ("ألم في الصدر", "Chest pain"),
    "shortness_breath": ("ضيق في التنفس", "Shortness of breath"),
    "palpitations": ("خفقان القلب", "Palpitations"),
    "swelling_legs": ("تورم في القدمين", "Leg swelling"),
    "cough": ("سعال", "Cough"),
    "fever": ("حرارة مرتفعة", "Fever"),
    "sore_throat": ("التهاب الحلق", "Sore throat"),
    "runny_nose": ("سيلان الأنف", "Runny nose"),
    "ear_pain": ("ألم في الأذن", "Ear pain"),
    "hearing_loss": ("ضعف السمع", "Hearing loss"),
    "headache": ("صداع", "Headache"),
    "dizziness": ("دوخة", "Dizziness"),
    "numbness_weakness": ("خدر أو ضعف في أحد الجانبين", "Numbness/weakness on one side"),
    "seizure": ("تشنجات", "Seizure"),
    "confusion": ("ارتباك أو تشوش", "Confusion"),
    "vision_blur": ("زغللة في النظر", "Blurred vision"),
    "eye_pain_redness": ("ألم أو احمرار في العين", "Eye pain/redness"),
    "abdominal_pain": ("ألم في البطن", "Abdominal pain"),
    "nausea_vomiting": ("غثيان أو قيء", "Nausea/vomiting"),
    "diarrhea": ("إسهال", "Diarrhea"),
    "heartburn": ("حرقان في المعدة", "Heartburn"),
    "jaundice": ("اصفرار العين أو الجلد", "Jaundice"),
    "joint_pain": ("ألم في المفاصل", "Joint pain"),
    "back_pain": ("ألم في الظهر", "Back pain"),
    "injury_fracture": ("إصابة أو كسر محتمل", "Injury / possible fracture"),
    "burn_injury": ("حرق", "Burn injury"),
    "skin_rash": ("طفح جلدي", "Skin rash"),
    "itching": ("حكة", "Itching"),
    "painful_urination": ("ألم عند التبول", "Painful urination"),
    "frequent_urination": ("كثرة التبول", "Frequent urination"),
    "blood_in_urine": ("دم في البول", "Blood in urine"),
    "excessive_thirst": ("عطش شديد", "Excessive thirst"),
    "weight_loss": ("فقدان وزن غير مبرر", "Unexplained weight loss"),
    "fatigue": ("إرهاق", "Fatigue"),
    "anxiety": ("قلق", "Anxiety"),
    "low_mood": ("حزن أو اكتئاب", "Low mood"),
    "insomnia": ("أرق", "Insomnia"),
    "self_harm_thoughts": ("أفكار لإيذاء النفس", "Thoughts of self-harm"),
    "pregnancy_related": ("حمل مع ألم أو نزيف", "Pregnancy with pain/bleeding"),
}

# specialty key: (Arabic, English)
SPECIALTIES = {
    "cardiology": ("القلب", "Cardiology"),
    "pulmonology": ("الصدر", "Pulmonology"),
    "ent": ("أنف وأذن وحنجرة", "ENT"),
    "neurology": ("المخ والأعصاب", "Neurology"),
    "ophthalmology": ("العيون", "Ophthalmology"),
    "gastroenterology": ("الجهاز الهضمي والكبد", "Gastroenterology"),
    "surgery": ("الجراحة العامة", "General Surgery"),
    "orthopedics": ("العظام", "Orthopedics"),
    "dermatology": ("الجلدية", "Dermatology"),
    "urology": ("المسالك البولية", "Urology"),
    "nephrology": ("الكلى", "Nephrology"),
    "endocrinology": ("الغدد الصماء والسكر", "Endocrinology"),
    "psychiatry": ("الطب النفسي", "Psychiatry"),
    "obgyn": ("النساء والتوليد", "Obstetrics & Gynecology"),
    "pediatrics": ("الأطفال", "Pediatrics"),
    "oncology": ("الأورام", "Oncology"),
    "burns": ("الحروق", "Burns"),
    "internal_medicine": ("الباطنة", "Internal Medicine"),
}

DURATIONS = {  # key: (Arabic, English)
    "lt_24h": ("أقل من 24 ساعة", "Less than 24 hours"),
    "1_7d": ("من يوم إلى أسبوع", "1-7 days"),
    "1_4w": ("من أسبوع إلى 4 أسابيع", "1-4 weeks"),
    "gt_4w": ("أكثر من 4 أسابيع", "More than 4 weeks"),
}
SEVERITIES = {"mild": ("خفيفة", "Mild"), "moderate": ("متوسطة", "Moderate"), "severe": ("شديدة", "Severe")}

GOVERNORATES = {  # English key: Arabic
    "Cairo": "القاهرة", "Giza": "الجيزة", "Alexandria": "الإسكندرية", "Qalyubia": "القليوبية",
    "Port Said": "بورسعيد", "Suez": "السويس", "Damietta": "دمياط", "Dakahlia": "الدقهلية",
    "Sharqia": "الشرقية", "Gharbia": "الغربية", "Monufia": "المنوفية", "Kafr El Sheikh": "كفر الشيخ",
    "Beheira": "البحيرة", "Ismailia": "الإسماعيلية", "Beni Suef": "بني سويف", "Fayoum": "الفيوم",
    "Minya": "المنيا", "Assiut": "أسيوط", "Sohag": "سوهاج", "Qena": "قنا", "Luxor": "الأقصر",
    "Aswan": "أسوان", "Red Sea": "البحر الأحمر", "New Valley": "الوادي الجديد", "Matrouh": "مطروح",
    "North Sinai": "شمال سيناء", "South Sinai": "جنوب سيناء",
}
HOSPITAL_TYPES = {"Government": "حكومي", "Private": "خاص"}

def R(rid, ar, en, specialty, weight, all_=(), any_=(), min_any=1, urgent=False):
    return {"id": rid, "name_ar": ar, "name_en": en, "all": list(all_), "any": list(any_),
            "min_any": min_any, "specialty": specialty, "weight": weight, "urgent": urgent}

RULES = [
    R("R01", "ألم صدر مع أعراض مصاحبة", "Chest pain + associated symptom", "cardiology", 3,
      ["chest_pain"], ["shortness_breath", "palpitations", "dizziness", "swelling_legs", "age_senior"], urgent=True),
    R("R02", "ألم صدر شديد", "Severe chest pain", "cardiology", 2, ["chest_pain", "severity_severe"], urgent=True),
    R("R03", "خفقان مع دوخة", "Palpitations + dizziness", "cardiology", 2, ["palpitations", "dizziness"]),
    R("R04", "تورم القدمين مع ضيق تنفس", "Leg swelling + breathlessness", "cardiology", 2, ["swelling_legs", "shortness_breath"]),
    R("R45", "ألم في الصدر (علامة تحذيرية)", "Chest pain alone (warning sign)", "cardiology", 2, ["chest_pain"], urgent=True),
    R("R46", "ضيق في التنفس", "Shortness of breath alone", "pulmonology", 2, ["shortness_breath"]),
    R("R05", "سعال مع ضيق تنفس", "Cough + shortness of breath", "pulmonology", 3, ["cough", "shortness_breath"]),
    R("R06", "سعال مزمن", "Chronic cough", "pulmonology", 2, ["cough", "duration_chronic"]),
    R("R07", "ضيق تنفس شديد", "Severe shortness of breath", "pulmonology", 2, ["shortness_breath", "severity_severe"], urgent=True),
    R("R08", "حرارة مع سعال", "Fever + cough", "pulmonology", 1, ["fever", "cough"]),
    R("R09", "التهاب حلق مع سيلان أنف", "Sore throat + runny nose", "ent", 2, ["sore_throat", "runny_nose"]),
    R("R10", "ألم الأذن", "Ear pain", "ent", 2, ["ear_pain"]),
    R("R11", "ضعف السمع", "Hearing loss", "ent", 2, ["hearing_loss"]),
    R("R12", "صداع مع أعراض عصبية", "Headache + neurological sign", "neurology", 3,
      ["headache"], ["numbness_weakness", "vision_blur", "confusion", "seizure"], urgent=True),
    R("R13", "صداع مع دوخة", "Headache + dizziness", "neurology", 2, ["headache", "dizziness"]),
    R("R14", "تشنجات", "Seizure", "neurology", 3, ["seizure"], urgent=True),
    R("R15", "خدر أو ضعف في جانب واحد", "One-sided numbness/weakness", "neurology", 3, ["numbness_weakness"], urgent=True),
    R("R16", "صداع مزمن", "Chronic headache", "neurology", 2, ["headache", "duration_chronic"]),
    R("R17", "ارتباك أو تشوش", "Confusion", "neurology", 2, ["confusion"], urgent=True),
    R("R18", "ألم أو احمرار العين", "Eye pain/redness", "ophthalmology", 3, ["eye_pain_redness"]),
    R("R19", "زغللة النظر", "Blurred vision", "ophthalmology", 2, ["vision_blur"]),
    R("R20", "ألم بطن مع غثيان", "Abdominal pain + nausea/vomiting", "gastroenterology", 2, ["abdominal_pain", "nausea_vomiting"]),
    R("R21", "حرقان المعدة", "Heartburn", "gastroenterology", 3, ["heartburn"]),
    R("R22", "إسهال مع ألم بطن", "Diarrhea + abdominal pain", "gastroenterology", 2, ["diarrhea", "abdominal_pain"]),
    R("R23", "اصفرار العين أو الجلد", "Jaundice", "gastroenterology", 3, ["jaundice"]),
    R("R24", "ألم بطن شديد", "Severe abdominal pain", "surgery", 2, ["abdominal_pain", "severity_severe"], urgent=True),
    R("R25", "ألم المفاصل", "Joint pain", "orthopedics", 2, ["joint_pain"]),
    R("R26", "ألم الظهر", "Back pain", "orthopedics", 2, ["back_pain"]),
    R("R27", "إصابة أو كسر محتمل", "Injury / possible fracture", "orthopedics", 3, ["injury_fracture"]),
    R("R28", "إصابة شديدة", "Severe injury", "orthopedics", 1, ["injury_fracture", "severity_severe"], urgent=True),
    R("R29", "حرق", "Burn injury", "burns", 4, ["burn_injury"], urgent=True),
    R("R30", "طفح جلدي", "Skin rash", "dermatology", 3, ["skin_rash"]),
    R("R31", "حكة", "Itching", "dermatology", 2, ["itching"]),
    R("R32", "أعراض بولية", "Urinary symptoms", "urology", 2, [], ["painful_urination", "frequent_urination"]),
    R("R33", "دم في البول", "Blood in urine", "urology", 3, ["blood_in_urine"]),
    R("R34", "دم في البول (كلى)", "Blood in urine (kidney check)", "nephrology", 1, ["blood_in_urine"]),
    R("R35", "عطش شديد مع كثرة تبول", "Excessive thirst + frequent urination", "endocrinology", 4, ["excessive_thirst", "frequent_urination"]),
    R("R36", "فقدان وزن مع إرهاق", "Weight loss + fatigue", "internal_medicine", 2, ["weight_loss", "fatigue"]),
    R("R37", "حرارة مع إرهاق", "Fever + fatigue", "internal_medicine", 2, ["fever", "fatigue"]),
    R("R38", "قلق/حزن/أرق (عرضان أو أكثر)", "Two or more of anxiety/low mood/insomnia", "psychiatry", 3,
      [], ["anxiety", "low_mood", "insomnia"], min_any=2),
    R("R39", "حزن مزمن", "Chronic low mood", "psychiatry", 2, ["low_mood", "duration_chronic"]),
    R("R40", "أفكار لإيذاء النفس", "Thoughts of self-harm", "psychiatry", 4, ["self_harm_thoughts"], urgent=True),
    R("R41", "حمل مع ألم أو نزيف", "Pregnancy with pain/bleeding", "obgyn", 4, ["pregnancy_related"], urgent=True),
    R("R42", "طفل (أقل من 12 سنة)", "Child under 12", "pediatrics", 2, ["age_child"]),
    R("R43", "طفل مع حرارة", "Child + fever", "pediatrics", 3, ["age_child", "fever"]),
    R("R44", "طفل مع حرارة وأعراض شديدة", "Child + fever + severe", "pediatrics", 1, ["age_child", "fever", "severity_severe"], urgent=True),
]

URGENT_SYMPTOM_NOTES = {
    "self_harm_thoughts": "إذا كانت لديك أفكار لإيذاء نفسك فتواصل فورا مع شخص تثق به أو اتصل بالإسعاف (123).",
}

# Educational list of tests a patient MAY discuss with the doctor (the doctor alone decides).
# Written by the project author for teaching purposes; it is NOT derived from the hospital sources.
TESTS_TO_DISCUSS = {
    "cardiology": ["رسم قلب (ECG)", "تحاليل إنزيمات القلب", "سونار على القلب (إيكو)"],
    "pulmonology": ["أشعة على الصدر", "قياس وظائف التنفس", "قياس نسبة الأكسجين في الدم"],
    "ent": ["فحص الأذن والأنف والحلق", "قياس السمع"],
    "neurology": ["فحص عصبي", "أشعة مقطعية أو رنين مغناطيسي على المخ", "رسم مخ (EEG)"],
    "ophthalmology": ["قياس النظر", "قياس ضغط العين", "فحص قاع العين"],
    "gastroenterology": ["تحاليل وظائف الكبد", "سونار على البطن", "منظار الجهاز الهضمي إذا رأى الطبيب ذلك"],
    "surgery": ["سونار على البطن", "تحاليل دم"],
    "orthopedics": ["أشعة سينية (X-ray) على المنطقة المصابة"],
    "dermatology": ["فحص الجلد", "تحاليل حساسية إذا رأى الطبيب ذلك"],
    "urology": ["تحليل بول", "سونار على المسالك البولية"],
    "nephrology": ["تحليل بول", "وظائف الكلى"],
    "endocrinology": ["سكر صائم وتراكمي", "وظائف الغدة الدرقية"],
    "psychiatry": ["تقييم نفسي بالمقابلة مع الطبيب"],
    "obgyn": ["سونار", "تحاليل حمل ومتابعة"],
    "pediatrics": ["فحص إكلينيكي وقياس النمو", "تحاليل دم حسب رأي الطبيب"],
    "oncology": ["فحوصات يحددها الطبيب بعد الفحص السريري"],
    "burns": ["تقييم الطبيب لمساحة وعمق الحرق"],
    "internal_medicine": ["صورة دم كاملة", "تحليل سكر", "وظائف الكلى والكبد"],
}

APP_NAME = "SmartMed Egypt"
APP_SUBTITLE = "An Expert System for Medical Specialty and Hospital Recommendation"
