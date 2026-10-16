# Presentation guide
**Idea:** help a person move from symptoms to a *suggested specialty* and nearby hospitals; an expert system copies how a human expert reasons using explicit rules.
**Knowledge Base:** `knowledge_base.py` - facts (symptoms) and IF-THEN rules, e.g. IF cough AND shortness_breath THEN pulmonology (weight 3). Separate from the GUI so it can be edited.
**Inference Engine:** forward chaining: (1) collect facts (symptoms + age group, severity, duration), (2) fire every rule whose IF part is true, (3) add up weights per specialty, (4) show matched rules (explanation) and urgent warnings.
**Hospital DB:** SQLite tables hospitals, hospital_specialties, cases. Search = SQL WHERE on governorate/type/specialty. Missing data stays blank = "Not verified".
**Flow:** Patient form -> Symptoms -> Inference -> one Results screen (hospital auto-recommended) -> save -> History. Advanced hospital search is optional.
**Tech:** Python, Tkinter, SQLite, unittest.
**Demo:** age 55, symptoms chest pain + shortness of breath, severe -> red urgent warning, cardiology, rules R01/R02/R07 -> the SAME results screen already shows Dar Al Fouad (Giza) with address/phone, tests to discuss and guidance -> save case -> History -> delete.
**Likely questions**
- *Is it a diagnosis?* No: it suggests a specialty with transparent rules.
- *Why not machine learning?* Rules are explainable and need no patient data.
- *How do you know why it answered?* The matched rules are listed.
- *Where is hospital data from?* Cited source per record; unknown fields are "Not verified".
- *Why few hospitals?* Only verifiable records were added; more can be added in seed_data.py.
- *How would you improve it?* More rules reviewed by doctors, official MoHP data, Arabic names, maps.
