"""Stage 5 & 6 data layer (SQLite): hospital search + saved patient cases."""
import os, sqlite3, datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hospitals.db")
NOT_VERIFIED = "غير متوفر (لم يتم التحقق منه)"

SCHEMA = """
CREATE TABLE IF NOT EXISTS hospitals(
  id INTEGER PRIMARY KEY AUTOINCREMENT, name_ar TEXT DEFAULT '', name_en TEXT NOT NULL,
  governorate TEXT NOT NULL, city TEXT DEFAULT '', type TEXT DEFAULT '' CHECK(type IN ('Government','Private','')),
  address TEXT DEFAULT '', phone TEXT DEFAULT '', website TEXT DEFAULT '', source_url TEXT NOT NULL, notes TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS hospital_specialties(
  hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
  specialty TEXT NOT NULL, source_url TEXT NOT NULL, PRIMARY KEY(hospital_id, specialty));
CREATE TABLE IF NOT EXISTS cases(
  id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT NOT NULL, age INTEGER, sex TEXT, symptoms TEXT,
  duration TEXT, severity TEXT, report TEXT, top_specialty TEXT,
  name TEXT DEFAULT '', address TEXT DEFAULT '', phone TEXT DEFAULT '', governorate TEXT DEFAULT '', owner TEXT DEFAULT '');
"""

def connect(db_path=None):
    con = sqlite3.connect(db_path or DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_db(db_path=None):
    """Create tables; add new case columns to an older database (safe to call every start)."""
    with connect(db_path) as con:
        con.executescript(SCHEMA)
        cols = {r["name"] for r in con.execute("PRAGMA table_info(cases)")}
        for c in ("name", "address", "phone", "governorate", "owner"):
            if c not in cols:
                con.execute(f"ALTER TABLE cases ADD COLUMN {c} TEXT DEFAULT ''")

def seed_database(db_path=None, reset=True):
    """(Re)build the hospital tables from seed_data.HOSPITALS. Saved cases are kept."""
    from seed_data import HOSPITALS
    init_db(db_path)
    with connect(db_path) as con:
        if reset:
            con.execute("DELETE FROM hospital_specialties"); con.execute("DELETE FROM hospitals")
        for h in HOSPITALS:
            cur = con.execute(
                "INSERT INTO hospitals(name_ar,name_en,governorate,city,type,address,phone,website,source_url,notes)"
                " VALUES(?,?,?,?,?,?,?,?,?,?)",
                (h["name_ar"], h["name_en"], h["governorate"], h["city"], h["type"], h["address"],
                 h["phone"], h["website"], h["source_url"], h["notes"]))
            for spec, src in h["specialties"]:
                con.execute("INSERT OR IGNORE INTO hospital_specialties VALUES(?,?,?)", (cur.lastrowid, spec, src))
    return len(HOSPITALS)

def get_specialties(hospital_id, db_path=None):
    with connect(db_path) as con:
        return [r["specialty"] for r in con.execute(
            "SELECT specialty FROM hospital_specialties WHERE hospital_id=? ORDER BY specialty", (hospital_id,))]

def search_hospitals(governorate=None, hospital_type=None, specialty=None,
                     include_unverified_specialty=False, db_path=None):
    """Real SQL filtering. None/'' = no filter. A hospital matches a specialty ONLY if a record
    supports it; with include_unverified_specialty=True, hospitals with NO specialty data are also
    returned (clearly flagged by specialty_status)."""
    sql, args = "SELECT h.* FROM hospitals h WHERE 1=1", []
    if governorate:
        sql += " AND h.governorate=?"; args.append(governorate)
    if hospital_type:
        sql += " AND h.type=?"; args.append(hospital_type)
    if specialty:
        cond = "EXISTS(SELECT 1 FROM hospital_specialties s WHERE s.hospital_id=h.id AND s.specialty=?)"
        if include_unverified_specialty:
            cond = "(" + cond + " OR NOT EXISTS(SELECT 1 FROM hospital_specialties s2 WHERE s2.hospital_id=h.id))"
        sql += " AND " + cond; args.append(specialty)
    sql += " ORDER BY h.governorate, h.name_en"
    with connect(db_path) as con:
        rows = [dict(r) for r in con.execute(sql, args)]
    for r in rows:
        r["specialties"] = get_specialties(r["id"], db_path)
        r["specialty_status"] = "verified" if r["specialties"] else "not_verified"
    return rows

def recommend_hospitals(governorate, specialty, limit=5, db_path=None):
    """Automatic recommendation (no manual choice). Returns (hospitals, level) where level says how
    the match was made: exact | unverified_specialty | other_governorates | same_governorate_any | none."""
    tiers = []
    if governorate:
        tiers += [("exact", dict(governorate=governorate, specialty=specialty)),
                  ("unverified_specialty", dict(governorate=governorate, specialty=specialty,
                                                include_unverified_specialty=True))]
    tiers.append(("other_governorates", dict(specialty=specialty)))
    if governorate:
        tiers.append(("same_governorate_any", dict(governorate=governorate)))
    for level, kw in tiers:
        rows = search_hospitals(db_path=db_path, **kw)
        if rows:
            return rows[:limit], level
    return [], "none"

def display(value):
    return value if value else NOT_VERIFIED

# ---- cases (no name/phone/ID stored) ----
def save_case(age, sex, symptoms, duration, severity, report, top_specialty, db_path=None,
              name="", address="", phone="", governorate="", owner=""):
    """owner = anonymous browser id (web version) so each visitor only sees their own cases; desktop leaves it empty."""
    with connect(db_path) as con:
        cur = con.execute("INSERT INTO cases(created,age,sex,symptoms,duration,severity,report,top_specialty,"
                          "name,address,phone,governorate,owner) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), age, sex, ",".join(symptoms),
                           duration, severity, report, top_specialty, name, address, phone, governorate, owner))
        return cur.lastrowid

def list_cases(db_path=None, owner=None):
    """owner=None -> all cases (desktop). owner='abc' -> only that visitor's cases (web)."""
    sql, args = "SELECT * FROM cases", []
    if owner is not None:
        sql += " WHERE owner=?"; args.append(owner)
    with connect(db_path) as con:
        return [dict(r) for r in con.execute(sql + " ORDER BY id DESC", args)]

def get_case(case_id, db_path=None, owner=None):
    sql, args = "SELECT * FROM cases WHERE id=?", [case_id]
    if owner is not None:
        sql += " AND owner=?"; args.append(owner)
    with connect(db_path) as con:
        r = con.execute(sql, args).fetchone()
        return dict(r) if r else None

def delete_case(case_id, db_path=None, owner=None):
    sql, args = "DELETE FROM cases WHERE id=?", [case_id]
    if owner is not None:
        sql += " AND owner=?"; args.append(owner)
    with connect(db_path) as con:
        return con.execute(sql, args).rowcount

def delete_all_cases(db_path=None, owner=None):
    sql, args = "DELETE FROM cases", []
    if owner is not None:
        sql += " WHERE owner=?"; args.append(owner)
    with connect(db_path) as con:
        return con.execute(sql, args).rowcount

if __name__ == "__main__":
    print("Seeded", seed_database(), "hospitals into", DB_PATH)
