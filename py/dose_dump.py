#!/usr/bin/env python3
"""
Neonatal & Pediatric Raw Dose Calculator for All Drugs

- Enter a weight in kg
- Optionally filter by population (Pediatric / Neonatal / All)
- Prints raw weight-based calculations for every drug:
      raw_dose = weight_kg * dose_per_kg
- Does NOT apply max-dose caps (this is pure/raw math)
- For drugs without a per-kg value, prints N/A and any typical range.

*** EDUCATIONAL / REFERENCE ONLY ***
Always verify against institutional protocols, MD, and pharmacy.
"""

from typing import List, Dict, Optional

# ---------------------------------------------------------------------
# DRUG TABLE
#   This is the same structure as before; add/remove drugs as you like.
# ---------------------------------------------------------------------

DRUGS: List[Dict] = [
    # --- Pediatric: General / Glucose / Hypertonic / Fluids ---
    {
        "name": "D10W bolus (peds)",
        "population": "Pediatric",
        "protocol": "Altered Mental Status / Hypoglycemia / Seizure",
        "route": "IV",
        "dose_per_kg": 5.0,
        "dose_unit": "mL/kg",
        "max_dose": 100.0,
        "max_unit": "mL",
        "typical_low": None,
        "typical_high": None,
        "notes": "Use for blood glucose < 60 mg/dL"
    },
    {
        "name": "Hypertonic Saline 3% (seizure, peds)",
        "population": "Pediatric",
        "protocol": "Altered Mental Status / Seizure",
        "route": "IV",
        "dose_per_kg": 3.0,
        "dose_unit": "mL/kg",
        "max_dose": 250.0,
        "max_unit": "mL",
        "typical_low": None,
        "typical_high": None,
        "notes": "Na < 130 and actively seizing; max 250 mL"
    },
    {
        "name": "Hypertonic Saline 3% (ICP, peds)",
        "population": "Pediatric",
        "protocol": "Head Trauma / ICP concern",
        "route": "IV push",
        "dose_per_kg": 5.0,
        "dose_unit": "mL/kg",
        "max_dose": None,
        "max_unit": "mL",
        "typical_low": None,
        "typical_high": None,
        "notes": "Consider for increased ICP"
    },
    {
        "name": "Normal Saline bolus (peds)",
        "population": "Pediatric",
        "protocol": "Shock / Bronchiolitis / Overdose / DKA",
        "route": "IV",
        "dose_per_kg": 20.0,
        "dose_unit": "mL/kg",
        "max_dose": None,
        "max_unit": "mL",
        "typical_low": None,
        "typical_high": 60.0,
        "notes": "May repeat; up to 60 mL/kg total in shock"
    },

    # --- Pediatric Anaphylaxis / Upper airway ---
    {
        "name": "Epinephrine 1:1000 IM (anaphylaxis, peds)",
        "population": "Pediatric",
        "protocol": "Anaphylaxis",
        "route": "IM",
        "dose_per_kg": 0.01,
        "dose_unit": "mg/kg",
        "max_dose": 0.3,
        "max_unit": "mg",
        "typical_low": None,
        "typical_high": None,
        "notes": "May repeat once for persistent symptoms"
    },
    {
        "name": "Diphenhydramine (peds)",
        "population": "Pediatric",
        "protocol": "Anaphylaxis / Allergic reaction",
        "route": "IV/IM",
        "dose_per_kg": 1.0,
        "dose_unit": "mg/kg",
        "max_dose": 50.0,
        "max_unit": "mg",
        "typical_low": None,
        "typical_high": None,
        "notes": ""
    },
    {
        "name": "Dexamethasone (Decadron, peds)",
        "population": "Pediatric",
        "protocol": "Anaphylaxis / Asthma / Upper airway",
        "route": "IV/PO",
        "dose_per_kg": 0.6,
        "dose_unit": "mg/kg",
        "max_dose": 16.0,
        "max_unit": "mg",
        "typical_low": None,
        "typical_high": None,
        "notes": ""
    },
    {
        "name": "Racemic Epinephrine neb (peds)",
        "population": "Pediatric",
        "protocol": "Upper Airway Respiratory Distress",
        "route": "Inhalation",
        "dose_per_kg": None,
        "dose_unit": "mg",
        "max_dose": None,
        "max_unit": "mg",
        "typical_low": 11.25,
        "typical_high": 11.25,
        "notes": "Standard neb 11.25 mg; may repeat"
    },

    # --- Pediatric Asthma ---
    {
        "name": "Albuterol neb (peds)",
        "population": "Pediatric",
        "protocol": "Asthma / Lower Airway",
        "route": "Nebulized",
        "dose_per_kg": None,
        "dose_unit": "mg",
        "max_dose": None,
        "max_unit": "mg",
        "typical_low": 2.5,
        "typical_high": 2.5,
        "notes": "Standard 2.5 mg neb in 3 mL NS"
    },
    {
        "name": "Magnesium sulfate (asthma, peds)",
        "population": "Pediatric",
        "protocol": "Asthma",
        "route": "IV",
        "dose_per_kg": 75.0,
        "dose_unit": "mg/kg",
        "max_dose": 2000.0,
        "max_unit": "mg",
        "typical_low": None,
        "typical_high": None,
        "notes": "Max 2 g"
    },
    {
        "name": "Terbutaline bolus (peds)",
        "population": "Pediatric",
        "protocol": "Asthma (MC direction)",
        "route": "IV",
        "dose_per_kg": 0.01,
        "dose_unit": "mg/kg",
        "max_dose": 0.4,
        "max_unit": "mg",
        "typical_low": None,
        "typical_high": None,
        "notes": "Bolus prior to infusion"
    },

    # --- Pediatric Pressors / Overdose / DKA (examples) ---
    {
        "name": "Epinephrine infusion (peds)",
        "population": "Pediatric",
        "protocol": "Shock / Beta-blocker OD / Clonidine OD",
        "route": "IV infusion",
        "dose_per_kg": 0.05,
        "dose_unit": "mcg/kg/min",
        "max_dose": 0.5,
        "max_unit": "mcg/kg/min",
        "typical_low": 0.05,
        "typical_high": 0.5,
        "notes": "Titrate to effect"
    },
    {
        "name": "Glucagon bolus (peds OD)",
        "population": "Pediatric",
        "protocol": "Beta/Calcium channel blocker OD",
        "route": "IV",
        "dose_per_kg": 0.15,
        "dose_unit": "mg/kg",
        "max_dose": 5.0,
        "max_unit": "mg",
        "typical_low": None,
        "typical_high": None,
        "notes": "Give over 10 min"
    },
    {
        "name": "Insulin regular bolus (peds OD)",
        "population": "Pediatric",
        "protocol": "Beta/Calcium channel blocker OD",
        "route": "IV",
        "dose_per_kg": 0.1,
        "dose_unit": "unit/kg",
        "max_dose": 10.0,
        "max_unit": "units",
        "typical_low": None,
        "typical_high": None,
        "notes": ""
    },
    {
        "name": "Calcium gluconate (peds OD)",
        "population": "Pediatric",
        "protocol": "Beta/Calcium channel blocker OD",
        "route": "IV",
        "dose_per_kg": 60.0,
        "dose_unit": "mg/kg",
        "max_dose": 3000.0,
        "max_unit": "mg",
        "typical_low": None,
        "typical_high": None,
        "notes": ""
    },
    {
        "name": "Insulin infusion (DKA, peds)",
        "population": "Pediatric",
        "protocol": "Diabetic Ketoacidosis",
        "route": "IV infusion",
        "dose_per_kg": 0.1,
        "dose_unit": "unit/kg/hr",
        "max_dose": None,
        "max_unit": "unit/kg/hr",
        "typical_low": None,
        "typical_high": None,
        "notes": ""
    },

    # --- Pediatric Fever / Pain / Nausea ---
    {
        "name": "Ibuprofen (peds)",
        "population": "Pediatric",
        "protocol": "Fever Management",
        "route": "PO",
        "dose_per_kg": 10.0,
        "dose_unit": "mg/kg",
        "max_dose": 600.0,
        "max_unit": "mg",
        "typical_low": None,
        "typical_high": None,
        "notes": "Age ≥ 6 months"
    },
    {
        "name": "Acetaminophen (peds)",
        "population": "Pediatric",
        "protocol": "Fever Management",
        "route": "PO/PR",
        "dose_per_kg": 15.0,
        "dose_unit": "mg/kg",
        "max_dose": 650.0,
        "max_unit": "mg",
        "typical_low": None,
        "typical_high": None,
        "notes": ""
    },
    {
        "name": "Morphine (peds)",
        "population": "Pediatric",
        "protocol": "Pain Management",
        "route": "IV/IM",
        "dose_per_kg": 0.05,
        "dose_unit": "mg/kg",
        "max_dose": 4.0,
        "max_unit": "mg",
        "typical_low": 0.05,
        "typical_high": 0.1,
        "notes": "Range 0.05–0.1 mg/kg"
    },
    {
        "name": "Fentanyl bolus (peds)",
        "population": "Pediatric",
        "protocol": "Pain / RSI / Sedation",
        "route": "IV/IN",
        "dose_per_kg": 1.0,
        "dose_unit": "mcg/kg",
        "max_dose": 100.0,
        "max_unit": "mcg",
        "typical_low": 1.0,
        "typical_high": 2.0,
        "notes": "Range 1–2 mcg/kg"
    },

    # --- Neonatal Glucose / Fluids ---
    {
        "name": "D10W bolus (neonatal)",
        "population": "Neonatal",
        "protocol": "Hypoglycemia / Seizure / Bradycardia",
        "route": "IV",
        "dose_per_kg": 2.0,
        "dose_unit": "mL/kg",
        "max_dose": None,
        "max_unit": "mL",
        "typical_low": None,
        "typical_high": None,
        "notes": "2 mL/kg over 5 min"
    },
    {
        "name": "Normal Saline bolus (neonatal)",
        "population": "Neonatal",
        "protocol": "Hypotension / Shock / Bradycardia",
        "route": "IV",
        "dose_per_kg": 10.0,
        "dose_unit": "mL/kg",
        "max_dose": None,
        "max_unit": "mL",
        "typical_low": None,
        "typical_high": 20.0,
        "notes": "May give x2 for shock"
    },

    # --- Neonatal Pressors (examples) ---
    {
        "name": "Dopamine infusion (neonatal)",
        "population": "Neonatal",
        "protocol": "Hypotension / Shock",
        "route": "IV infusion",
        "dose_per_kg": 5.0,
        "dose_unit": "mcg/kg/min",
        "max_dose": 20.0,
        "max_unit": "mcg/kg/min",
        "typical_low": 5.0,
        "typical_high": 20.0,
        "notes": ""
    },
    {
        "name": "Epinephrine infusion (neonatal)",
        "population": "Neonatal",
        "protocol": "Hypotension / Shock",
        "route": "IV infusion",
        "dose_per_kg": 0.02,
        "dose_unit": "mcg/kg/min",
        "max_dose": 1.0,
        "max_unit": "mcg/kg/min",
        "typical_low": 0.02,
        "typical_high": 1.0,
        "notes": ""
    },

    # --- Neonatal Antibiotics (examples) ---
    {
        "name": "Ampicillin (neonatal)",
        "population": "Neonatal",
        "protocol": "Sepsis / Abdominal wall / Bowel obstruction / HSV risk",
        "route": "IV",
        "dose_per_kg": 100.0,
        "dose_unit": "mg/kg",
        "max_dose": None,
        "max_unit": "mg",
        "typical_low": 50.0,
        "typical_high": 100.0,
        "notes": "Frequency age/weight dependent"
    },
    {
        "name": "Gentamicin (neonatal)",
        "population": "Neonatal",
        "protocol": "Sepsis / Abdominal wall / Bowel obstruction",
        "route": "IV",
        "dose_per_kg": 5.0,
        "dose_unit": "mg/kg",
        "max_dose": None,
        "max_unit": "mg",
        "typical_low": 4.0,
        "typical_high": 5.0,
        "notes": "Frequency age/weight dependent"
    },
]

# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------


def format_float(x: Optional[float]) -> str:
    if x is None:
        return "-"
    if float(x).is_integer():
        return str(int(x))
    return f"{x:.3g}"  # 3 significant figures


def filter_by_population(pop: str) -> List[Dict]:
    """Return drugs filtered by population string ('p', 'n', 'all')."""
    pop = pop.strip().lower()
    if pop in ("", "all"):
        return DRUGS

    if pop.startswith("p"):
        target = "pediatric"
    elif pop.startswith("n"):
        target = "neonatal"
    else:
        print("Unknown population filter; showing all populations.")
        return DRUGS

    return [d for d in DRUGS if d["population"].lower() == target]


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------


def main():
    print("=" * 72)
    print(" Neonatal & Pediatric RAW Dose Table")
    print(" raw_dose = weight_kg × dose_per_kg (no max-dose capping)")
    print(" *** EDUCATION / REFERENCE ONLY – VERIFY WITH PROTOCOL ***")
    print("=" * 72)
    print()

    # Get weight
    while True:
        w_str = input("Enter patient weight in kg (or 'q' to quit): ").strip()
        if w_str.lower() in ("q", "quit", "exit"):
            print("Bye.")
            return
        try:
            weight_kg = float(w_str)
            if weight_kg <= 0:
                print("Weight must be > 0.")
                continue
            break
        except ValueError:
            print("Couldn't parse that as a number. Try again.")

    # Population filter
    pop = input(
        "Population filter [Pediatric / Neonatal / All] "
        "(e.g. 'p', 'n', or Enter for all): "
    ).strip()

    drugs = filter_by_population(pop)

    print("\nRAW DOSE CALCULATIONS")
    print("-" * 72)
    header = (
        f"{'Drug':40} {'Pop':8} {'Route':10} "
        f"{'Per kg':12} {'Unit':14} {'RAW dose':15}"
    )
    print(header)
    print("-" * 72)

    for d in drugs:
        per_kg = d.get("dose_per_kg", None)
        if per_kg is None:
            raw = None
        else:
            raw = per_kg * weight_kg

        name = (d["name"][:37] + "...") if len(d["name"]) > 40 else d["name"]
        line = (
            f"{name:40} "
            f"{d['population'][:8]:8} "
            f"{d['route'][:10]:10} "
            f"{format_float(per_kg):12} "
            f"{d['dose_unit'][:14]:14} "
            f"{(format_float(raw) + ' ' + (d['dose_unit'].replace('/kg', ''))) if raw is not None else 'N/A':15}"
        )
        print(line)

    print("-" * 72)
    print(f"Weight used for calcs: {format_float(weight_kg)} kg")
    print("Reminder: RAW numbers only – no max-dose caps applied.")
    print("Always verify against institutional protocol / MD / pharmacy.\n")


if __name__ == "__main__":
    main()
