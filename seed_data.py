"""Hospital records. EVERY field comes from the cited source; blank = 'Not verified'.
Sources: G = UK FCDO list 'Egypt: doctors and medical facilities' (gov.uk).
Governorate is assigned by the project author from the stated city/area."""
G = "https://www.gov.uk/government/publications/egypt-list-of-medical-facilities-practitioners/egypt-doctors-and-medical-facilities"
WIKI_KA = "https://en.wikipedia.org/wiki/Kasr_Al_Aini_Hospital"
KA_CONTACT = "https://medicine.cu.edu.eg/contact-2/"
BSU_CONTACT = "https://www.bsu.edu.eg/Content.aspx?side_id=70&cat_id=1&lang=en"
MINIA_TEL = "https://www.minia.edu.eg/Minia/Etelephone.aspx"
DAF = "https://www.myhospitalnow.com/hospitals/dar-al-fouad-hospital"
BSU = "https://www.bsu.edu.eg/Backend/Uploads/PDF/SDG/2022 - 2023/Report on SDG3 .pdf"
BSU2 = "https://www.bsu.edu.eg/Backend/Uploads/PDF/مركز تطوير الاداء/مكتب التصنيف الدولي/Society/S-H1- Physical.pdf"
MINIA = "https://mohesr.gov.eg/en/all-news/minia-university-hospitals-achievements-during-year-2025-2026"

def H(name_en, gov, city, typ, address="", phone="", website="", source=G, specs=(), notes="", name_ar=""):
    return dict(name_en=name_en, name_ar=name_ar, governorate=gov, city=city, type=typ, address=address,
                phone=phone, website=website, source_url=source, specialties=list(specs), notes=notes)

HOSPITALS = [
    # ---- Cairo ----
    H("Kasr Al Ainy Hospital (Cairo University)", "Cairo", "Kasr Al Ainy", "Government",
      address="Kasr Al Ainy Faculty of Medicine, Al-Manial, Cairo 11956", phone="02 23647545",
      website="http://hospitals.kasralainy.edu.eg", source=KA_CONTACT,
      notes="Address and phone are those published on the Cairo University Faculty of Medicine contact page (the hospital's parent faculty), not a dedicated hospital switchboard. Affiliation: Wikipedia. Specialties not verified."),
    H("Abu El Reesh Japanese Children University Hospital (Cairo University)", "Cairo", "Cairo", "Government",
      source=WIKI_KA, specs=[("pediatrics", WIKI_KA)], notes="Specialty inferred from the hospital's stated children's role in the source."),
    H("National Cancer Institute (Cairo University)", "Cairo", "Cairo", "Government",
      source=WIKI_KA, specs=[("oncology", WIKI_KA)], notes="Specialty from the institute's name in the source."),
    H("Anglo-American Hospital", "Cairo", "Zamalek", "Private", "3 Hadiqet El Zohreya St, Zamalek", "02 7356162/3/4/5"),
    H("El Nada Hospital", "Cairo", "El Manial", "Private", "54 Manial Street (near McDonalds)", "02 25311616"),
    H("As-Salam International Hospital", "Cairo", "Maadi", "Private", "Nile Corniche, Maadi", "02 25240232; 02 25240250"),
    # ---- Giza ----
    H("Al-Shorouk Hospital", "Giza", "Mohandessin", "Private", "5 Bahr El-Ghazal Street, Mohandesseen", "02 33044891; 02 33044901"),
    H("Dar Al Fouad Hospital", "Giza", "6th of October City", "Private", "26th July Street, The Touristic Zone, 6th October City, Giza",
      "02 38356030; 02 38356040",
      specs=[(s, DAF) for s in ["cardiology", "oncology", "neurology", "nephrology", "urology", "orthopedics"]],
      notes="Specialties come from a secondary directory (myhospitalnow), not the hospital's own site."),
    # ---- Alexandria ----
    H("Alexandria International Hospital", "Alexandria", "Smouha", "Private", "20 Mohamed Bahaa El Din El Ghatwary St, Smouha", "03 4207243; 03 4207244"),
    H("Al Salama Specialised Hospital", "Alexandria", "Azarita", "Private", "7 Mohamed Motawa Street, off Sultan Hussein, Azarita", "03 4879999"),
    H("Armed Forces Hospital", "Alexandria", "Sidi Gaber", "Government", "Intersection of El Guish Avenue and Port Said Street, Sidi Gaber", "03 5452013-18"),
    H("El Ahly Specialised Hospital", "Alexandria", "Boulkley", "Private", "3 Dr Borgy Street, Boulkley", "03 5227208; 03 5227209"),
    H("El Madina El Tebia Hospital", "Alexandria", "Moustafa Kamel", "Private", "Ahmed Shawky Street, Moustafa Kamel", "03 5432150; 03 5437402"),
    H("El Sherouk Hospital (Alexandria)", "Alexandria", "Glym", "Private", "9 Moustafa Fahmy Street, Glym", "03 5856549"),
    H("German Hospital (Alexandria)", "Alexandria", "Saba Pacha", "Private", "56 Abdel Salam Aref Street, Saba Pacha", "03 5841806; 03 5857682"),
    H("International Cardiac Centre (ICC)", "Alexandria", "Smouha", "Private", "24 Mohamed Bahaa El Din El Ghatwary St, Smouha", "03 4207320; 03 4207321",
      specs=[("cardiology", G)], notes="Specialty taken from the centre's name in the source."),
    H("Ibrahim Obeid Hospital", "Alexandria", "Glym", "Private", "76 Abdel Salam Aref Street, Glym", "03 5833232; 03 5828653"),
    H("Louran Hospital", "Alexandria", "Louran", "Private", "13 Sharawy Street, Louran", "03 5834221; 03 5434241"),
    H("Victoria Hospital", "Alexandria", "Victoria", "Private", "18 Phillip Galad Street, Victoria", "03 5776770-5"),
    H("Zizinia Hospital", "Alexandria", "Zizinia", "Private", "Behind No 7 Amin Yehia Street, Zizinia", "03 5826420; 03 5838802"),
    H("Alexandria University Hospital (Miri Hospital)", "Alexandria", "Azarita", "Government", "Koliet El Teb Street, Azarita", "03 4862920"),
    H("Sidi Krier Military Hospital", "Alexandria", "Sidi Krier", "Government", "Alexandria Matrouh Road", "03 3402090"),
    # ---- Beni Suef ----
    H("Beni-Suef University Hospital", "Beni Suef", "Beni Suef", "Government", address="Salah Salem Street, Beni Suef", phone="082 2356845; 082 2356846; 082 2324879",
      website="http://www.bsu.edu.eg/", source=BSU_CONTACT,
      specs=[("oncology", BSU2), ("burns", BSU2)],
      notes="Public university hospital complex; its Oncology and Burn Hospital is described in the BSU report. Address and phone are from the university's official contact page; some online directories list Mohamed Hassan Street instead."),
    # ---- Minya ----
    H("Minia University Hospitals", "Minya", "Minya", "Government",
      address="Corniche El Nil Street, Minya", phone="086 2342505; 086 2366743; 086 2369076",
      website="http://mn.minia.edu.eg/arabic/hospitals/hos/pages/default.aspx.htm", source=MINIA_TEL,
      specs=[(s, MINIA) for s in ["gastroenterology", "ophthalmology", "urology", "nephrology", "internal_medicine", "surgery"]],
      notes="GAHAR-accredited units listed in the source: Liver & Gastroenterology, Ophthalmology, Kidney & Urology, Internal Medicine & Surgery. "
            "Oncology/neurology/psychiatry hospitals are described as new/expected, so NOT recorded. Phones: Minia University official telephone page. Address (Corniche El Nil): taken from several public directories, not from an official page."),
    # ---- Upper Egypt ----
    H("Luxor International Hospital", "Luxor", "Luxor", "Government", phone="095 2279629; 095 2280192"),
    H("Aswan General Hospital", "Aswan", "Aswan", "Government", phone="097 2302855"),
    # ---- South Sinai ----
    H("Sharm International Hospital", "South Sinai", "Sharm El Sheikh", "Government", phone="069 3660894"),
    H("Misr Medical Center Hospital", "South Sinai", "Sharm El Sheikh", "Private", phone="069 3666765"),
    H("Dahab Hospital", "South Sinai", "Dahab", "Government", phone="069 3640208"),
    H("Newiba Hospital", "South Sinai", "Nuweiba", "Government", phone="069 3500302; 069 3501001"),
    H("St Catherine Hospital", "South Sinai", "Saint Catherine", "Government", phone="069 3470205"),
    # ---- Red Sea ----
    H("Egyptian Hospital (Hurghada)", "Red Sea", "Hurghada", "Private", phone="065 3450318"),
    H("El Gouna Hospital", "Red Sea", "El Gouna", "Private", phone="065 3580012-19"),
    H("El Hakma Hospital", "Red Sea", "Hurghada", "Private", phone="065 3553999"),
    H("El Salam Hospital (Hurghada)", "Red Sea", "Hurghada", "Private", phone="065 3548785-7"),
    H("Nile Hospital (Hurghada)", "Red Sea", "Hurghada", "Private", phone="065 3550974-8"),
    H("Red Sea Hospital", "Red Sea", "Hurghada", "Government", phone="065 3544850"),
    H("General Hospital Hurghada", "Red Sea", "Hurghada", "Government", phone="065 3546740"),
    H("General Hospital Safaga", "Red Sea", "Safaga", "Government", phone="065 3251549"),
    H("General Hospital El Quseir", "Red Sea", "El Quseir", "Government", phone="065 3330070"),
]
