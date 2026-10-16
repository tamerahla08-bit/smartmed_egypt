"""Stage 4 - Inference Engine: forward chaining over the IF-THEN rules."""
from knowledge_base import RULES, SPECIALTIES, SYMPTOMS, URGENT_SYMPTOM_NOTES

DISCLAIMER_AR = ("هذا التطبيق لأغراض تعليمية فقط وليس أداة تشخيص. التخصص المقترح ليس تشخيصا مؤكدا. "
                 "لا يصف أدوية أو علاجا. استشر طبيبا مؤهلا.")
URGENT_AR = ("تحذير: الأعراض المختارة قد تحتاج تقييما طبيا عاجلا. لا تؤخر الرعاية الطارئة أثناء البحث "
             "عن مستشفى، واتصل بالإسعاف (123) أو اذهب لأقرب طوارئ.")

def derive_facts(patient):
    """Step 1: turn raw input into facts (selected symptoms + derived facts)."""
    facts = set(patient.get("symptoms", []))
    age = patient.get("age")
    if age is not None:
        if age < 12:
            facts.add("age_child")
        elif age >= 60:
            facts.add("age_senior")
    if patient.get("severity") == "severe":
        facts.add("severity_severe")
    if patient.get("duration") == "gt_4w":
        facts.add("duration_chronic")
    return facts

def rule_matches(rule, facts):
    if not all(f in facts for f in rule["all"]):
        return False
    if rule["any"]:
        return sum(1 for f in rule["any"] if f in facts) >= rule["min_any"]
    return True

def infer(patient, rules=None):
    """Step 2: match rules, Step 3: score specialties. Returns a result dict."""
    rules = RULES if rules is None else rules
    facts = derive_facts(patient)
    matched = [r for r in rules if rule_matches(r, facts)]
    scores = {}
    for r in matched:
        scores[r["specialty"]] = scores.get(r["specialty"], 0) + r["weight"]
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    fallback = False
    if not ranked:
        ranked = [("internal_medicine", 0)]
        fallback = True
    urgent = any(r["urgent"] for r in matched)
    notes = [URGENT_SYMPTOM_NOTES[s] for s in patient.get("symptoms", []) if s in URGENT_SYMPTOM_NOTES]
    return {
        "facts": sorted(facts), "matched_rules": matched, "scores": ranked,
        "top_specialty": ranked[0][0], "fallback": fallback, "urgent": urgent,
        "urgent_message": URGENT_AR if urgent else "", "extra_notes": notes,
        "disclaimer": DISCLAIMER_AR,
    }

def explain(patient, result):
    """Arabic plain-text report used by the results screen and saved cases."""
    lines = []
    if result["urgent"]:
        lines.append(result["urgent_message"]); lines.append("")
    for n in result["extra_notes"]:
        lines.append(n)
    lines.append("الأعراض المختارة: " + "، ".join(SYMPTOMS[s][0] for s in patient.get("symptoms", [])))
    lines.append("")
    lines.append("القواعد التي تحققت:")
    if result["matched_rules"]:
        for r in result["matched_rules"]:
            lines.append(f"  {r['id']}: {r['name_ar']} ← {SPECIALTIES[r['specialty']][0]} (الوزن {r['weight']})")
    else:
        lines.append("  لم تنطبق أي قاعدة؛ يُقترح الطبيب العام/الباطنة.")
    lines.append("")
    lines.append("التخصصات المقترحة (حسب مجموع الأوزان):")
    for key, score in result["scores"]:
        lines.append(f"  - {SPECIALTIES[key][0]} ({SPECIALTIES[key][1]}): {score}")
    lines.append(""); lines.append(result["disclaimer"])
    return "\n".join(lines)
