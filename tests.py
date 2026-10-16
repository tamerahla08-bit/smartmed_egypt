"""Run:  python tests.py   (uses a temporary database; does not touch hospitals.db)"""
import os, tempfile, unittest
import hospital_database as db
import inference_engine as eng
import knowledge_base as kb

class DBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.join(tempfile.mkdtemp(), "t.db")
        cls.n = db.seed_database(cls.path)
    def s(self, *a, **k): return db.search_hospitals(*a, db_path=self.path, **k)
    def test_loaded(self): self.assertEqual(len(self.s()), self.n); self.assertGreater(self.n, 30)
    def test_governorate(self):
        r = self.s("Alexandria"); self.assertTrue(r and all(h["governorate"] == "Alexandria" for h in r))
    def test_type(self):
        r = self.s(None, "Government"); self.assertTrue(r and all(h["type"] == "Government" for h in r))
        r = self.s(None, "Private"); self.assertTrue(r and all(h["type"] == "Private" for h in r))
    def test_specialty_only_verified(self):
        r = self.s(None, None, "cardiology")
        self.assertTrue(r and all("cardiology" in h["specialties"] for h in r))
    def test_combined(self):
        r = self.s("Giza", "Private", "cardiology"); self.assertEqual([h["name_en"] for h in r], ["Dar Al Fouad Hospital"])
    def test_empty_result(self): self.assertEqual(self.s("Alexandria", "Government", "cardiology"), [])
    def test_unverified_flag(self):
        r = self.s("Alexandria", "Government", "cardiology", include_unverified_specialty=True)
        self.assertTrue(r and all(h["specialty_status"] == "not_verified" for h in r))
    def test_missing_fields(self):
        h = [x for x in self.s("Cairo") if "Abu El Reesh" in x["name_en"]][0]
        self.assertEqual(h["phone"], ""); self.assertEqual(db.display(h["phone"]), db.NOT_VERIFIED)
        self.assertEqual(h["address"], ""); self.assertEqual(db.display(h["address"]), db.NOT_VERIFIED)
    def test_verified_contacts_added(self):
        for gov in ("Minya", "Beni Suef"):
            h = self.s(gov)[0]; self.assertTrue(h["phone"] and h["address"], gov)
    def test_every_record_has_source(self): self.assertTrue(all(h["source_url"] for h in self.s()))
    def test_cases_crud(self):
        cid = db.save_case(30, "male", ["fever"], "1_7d", "mild", "r", "internal_medicine", self.path)
        self.assertEqual(len(db.list_cases(self.path)), 1)
        self.assertEqual(db.delete_case(cid, self.path), 1); self.assertEqual(db.list_cases(self.path), [])

class InferenceTests(unittest.TestCase):
    def run_(self, **p):
        base = dict(age=30, sex="male", duration="1_7d", severity="moderate"); base.update(p); return eng.infer(base)
    def test_cardiology_urgent(self):
        r = self.run_(symptoms=["chest_pain", "shortness_breath"]); self.assertEqual(r["top_specialty"], "cardiology"); self.assertTrue(r["urgent"])
    def test_pulmonology(self): self.assertEqual(self.run_(symptoms=["cough", "shortness_breath"])["top_specialty"], "pulmonology")
    def test_child_fever(self): self.assertEqual(self.run_(age=5, symptoms=["fever"])["top_specialty"], "pediatrics")
    def test_diabetes_pattern(self): self.assertEqual(self.run_(symptoms=["excessive_thirst", "frequent_urination"])["top_specialty"], "endocrinology")
    def test_neuro_urgent(self):
        r = self.run_(symptoms=["numbness_weakness"]); self.assertEqual(r["top_specialty"], "neurology"); self.assertTrue(r["urgent"])
    def test_fallback(self):
        r = self.run_(symptoms=["fatigue"]); self.assertTrue(r["fallback"]); self.assertFalse(r["urgent"])
    def test_matched_rules_listed(self): self.assertIn("R10", [x["id"] for x in self.run_(symptoms=["ear_pain"])["matched_rules"]])
    def test_self_harm_note(self):
        r = self.run_(symptoms=["self_harm_thoughts"]); self.assertTrue(r["urgent"] and r["extra_notes"])
    def test_kb_consistency(self):
        for r in kb.RULES:
            self.assertIn(r["specialty"], kb.SPECIALTIES)
            for f in r["all"] + r["any"]:
                self.assertTrue(f in kb.SYMPTOMS or f in ("age_child", "age_senior", "severity_severe", "duration_chronic"), (r["id"], f))

class ImportTests(unittest.TestCase):
    def test_seed_specialties_valid(self):
        from seed_data import HOSPITALS
        for h in HOSPITALS:
            for s, src in h["specialties"]: self.assertIn(s, kb.SPECIALTIES); self.assertTrue(src)


import sqlite3
import report_builder as rb

class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.join(tempfile.mkdtemp(), "r.db"); db.seed_database(cls.path)
    def report(self, **p):
        base = dict(name="أحمد", age=40, sex="male", address="الإسكندرية", phone="", governorate="",
                    duration="1_7d", severity="moderate"); base.update(p)
        return rb.build_report(base, eng.infer(base), db_path=self.path)
    def test_all_sections_present(self):
        r = self.report(symptoms=["chest_pain", "shortness_breath"])
        titles = [t for _, t, _ in r["sections"]]
        for t in ("ملخص بيانات المريض", "الأعراض التي اخترتها", "التقييم حسب قواعد النظام", "التخصص الطبي المناسب",
                  "المستشفيات المقترحة", "فحوصات قد تناقشها مع الطبيب", "رسالة إرشادية"):
            self.assertIn(t, titles)
    def test_hospital_name_shown_not_id(self):
        r = self.report(symptoms=["chest_pain"], address="الجيزة 6 اكتوبر")
        text = rb.report_to_text(r)
        self.assertIn("Dar Al Fouad Hospital", text); self.assertEqual(r["level"], "exact")
    def test_urgent_flag_and_message(self):
        r = self.report(symptoms=["chest_pain", "shortness_breath"])
        self.assertTrue(r["urgent"]); self.assertIn("123", r["urgent_message"])
        self.assertIn("!!اطلب الإسعاف", "\n".join(r["sections"][4][2]))
    def test_not_urgent(self):
        self.assertFalse(self.report(symptoms=["skin_rash"])["urgent"])
    def test_no_hospital_found_fallback_levels(self):
        r = self.report(symptoms=["skin_rash"], address="أسوان")
        self.assertEqual(r["level"], "unverified_specialty")
        r = self.report(symptoms=["skin_rash"], address="")
        self.assertIn(r["level"], ("other_governorates", "none"))
    def test_tests_listed(self):
        self.assertTrue(any("ECG" in l for l in self.report(symptoms=["chest_pain"])["sections"][5][2]))
    def test_guess_governorate(self):
        self.assertEqual(rb.guess_governorate("شارع ... الاسكندرية"), "Alexandria")
        self.assertEqual(rb.guess_governorate("Minya city"), "Minya"); self.assertEqual(rb.guess_governorate("xyz"), "")
    def test_form_validation(self):
        e, c = rb.validate_patient_form("أحمد", "٣٠", "male", "")
        self.assertEqual(e, []); self.assertEqual(c["age"], 30)
        self.assertEqual(len(rb.validate_patient_form("", "abc", "", "12")[0]), 4)
        self.assertEqual(rb.validate_patient_form("سارة", "20", "female", "+20 100 123 4567")[0], [])
    def test_new_case_columns_and_migration(self):
        old = os.path.join(tempfile.mkdtemp(), "old.db")
        con = sqlite3.connect(old)
        con.execute("CREATE TABLE cases(id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT, age INTEGER, sex TEXT, symptoms TEXT, duration TEXT, severity TEXT, report TEXT, top_specialty TEXT)")
        con.commit(); con.close()
        db.init_db(old)
        cid = db.save_case(30, "male", ["fever"], "1_7d", "mild", "r", "internal_medicine", old, name="علي", phone="0100", address="x", governorate="Cairo")
        c = db.list_cases(old)[0]; self.assertEqual((c["name"], c["phone"], c["governorate"]), ("علي", "0100", "Cairo"))
        self.assertEqual(db.delete_case(cid, old), 1)


import io, urllib.parse as _up

class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import webapp
        cls.webapp = webapp
        cls.old = db.DB_PATH
        db.DB_PATH = os.path.join(tempfile.mkdtemp(), "web.db"); db.seed_database()
    @classmethod
    def tearDownClass(cls): db.DB_PATH = cls.old
    def call(self, method, path, data=None, cookie=""):
        path, _, qs = path.partition("?")
        body = _up.urlencode(data or [], doseq=True).encode()
        env = {"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": qs, "CONTENT_LENGTH": str(len(body)),
               "wsgi.input": io.BytesIO(body), "HTTP_COOKIE": cookie, "wsgi.url_scheme": "http"}
        out = {}
        def sr(status, headers): out["status"], out["headers"] = status, dict((k, v) for k, v in headers)
        text = b"".join(self.webapp.application(env, sr)).decode("utf-8")
        return out["status"], out["headers"], text
    CASE = [("name", "أحمد"), ("age", "55"), ("sex", "male"), ("gov", "Giza"), ("address", "6 أكتوبر"), ("phone", ""),
            ("s", "chest_pain"), ("s", "shortness_breath"), ("duration", "1_7d"), ("severity", "severe")]
    def test_pages_and_welcome(self):
        st, h, t = self.call("GET", "/"); self.assertTrue(st.startswith("200")); self.assertIn("أهلاً بك في SmartMed Egypt", t); self.assertIn("An Expert System for Medical Specialty and Hospital Recommendation", t)
        self.assertIn('dir="rtl"', t); self.assertIn("width=device-width", t)
        for p in ("/patient", "/hospitals", "/history", "/health"): self.assertTrue(self.call("GET", p)[0].startswith("200"), p)
    def test_404_405(self):
        self.assertTrue(self.call("GET", "/nope")[0].startswith("404")); self.assertTrue(self.call("GET", "/results")[0].startswith("405"))
    def test_patient_validation_and_next_step(self):
        st, h, t = self.call("POST", "/patient", [("name", ""), ("age", "x"), ("sex", "")]); self.assertIn("الاسم مطلوب", t)
        st, h, t = self.call("POST", "/patient", self.CASE[:6]); self.assertIn('name="s"', t); self.assertIn('name="name" value="أحمد"', t)
    def test_results_one_screen(self):
        st, h, t = self.call("POST", "/results", self.CASE)
        for needle in ("ملخص بيانات المريض", "أحمد", "ألم في الصدر", "R01", "التخصص المقترح", "Dar Al Fouad Hospital",
                       "فحوصات قد تناقشها", "رسالة إرشادية", "banner", "123"):
            self.assertIn(needle, t, needle)
    def test_results_requires_symptom(self):
        st, h, t = self.call("POST", "/results", [x for x in self.CASE if x[0] != "s"]); self.assertIn("اختر عرضاً واحداً", t)
    def test_xss_escaped(self):
        data = [("name", "<script>alert(1)</script>")] + self.CASE[1:]
        st, h, t = self.call("POST", "/results", data)
        self.assertNotIn("<script>alert(1)</script>", t); self.assertIn("&lt;script&gt;", t)
    def test_security_headers(self):
        h = self.call("GET", "/")[1]; self.assertIn("default-src 'none'", h["Content-Security-Policy"]); self.assertIn("HttpOnly", h["Set-Cookie"])
    def test_history_is_private_per_browser(self):
        a, b = "cid=" + "a" * 32, "cid=" + "b" * 32
        st, h, _ = self.call("POST", "/save", self.CASE, a); self.assertTrue(st.startswith("303"))
        _, _, ta = self.call("GET", "/history?msg=saved", cookie=a); _, _, tb = self.call("GET", "/history", cookie=b)
        self.assertIn("أحمد", ta); self.assertIn("تم حفظ الحالة", ta); self.assertNotIn("أحمد", tb)
        cid = db.list_cases(owner="a" * 32)[0]["id"]
        self.assertTrue(self.call("GET", f"/history/{cid}", cookie=a)[0].startswith("200"))
        self.assertTrue(self.call("GET", f"/history/{cid}", cookie=b)[0].startswith("404"))
        self.assertTrue(self.call("POST", f"/history/{cid}/delete", cookie=b)[0].startswith("404"))
        self.assertTrue(self.call("POST", f"/history/{cid}/delete", cookie=a)[0].startswith("303"))
        self.assertEqual(db.list_cases(owner="a" * 32), [])
    def test_delete_all_only_own(self):
        a, b = "cid=" + "c" * 32, "cid=" + "d" * 32
        self.call("POST", "/save", self.CASE, a); self.call("POST", "/save", self.CASE, b)
        self.call("POST", "/history/delete-all", cookie=a)
        self.assertEqual(db.list_cases(owner="c" * 32), []); self.assertEqual(len(db.list_cases(owner="d" * 32)), 1)
    def test_hospital_filters_on_web(self):
        _, _, t = self.call("GET", "/hospitals?g=Giza&t=Private&s=cardiology"); self.assertIn("Dar Al Fouad Hospital", t); self.assertIn("عدد النتائج: 1", t)
        _, _, t = self.call("GET", "/hospitals?g=Alexandria&t=Government&s=cardiology"); self.assertIn("لا توجد نتائج", t)
        _, _, t = self.call("GET", "/hospitals?g=Alexandria&t=Government&s=cardiology&u=1"); self.assertIn("Armed Forces Hospital", t)
        _, _, t = self.call("GET", "/hospitals?g=evil'--"); self.assertIn("عدد النتائج: 40", t)

if __name__ == "__main__":
    unittest.main(verbosity=2)
