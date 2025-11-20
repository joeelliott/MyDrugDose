#!/usr/bin/env python3
"""
Neonatal & Pediatric Dosing + Infusion Rate Calculator (CLI)

- Based on your neonatal/peds protocol flow charts
- Lets you enter a weight (kg), pick a drug, and:
  * Get a single calculated dose
  * For infusion-type drugs (e.g. mcg/kg/min, unit/kg/hr), calculate mL/hr

*** EDUCATIONAL / REFERENCE ONLY ***
Always verify with current institutional protocols, order sets, MD/pharmacy.
"""

from typing import List, Dict, Optional

# ---------------------------------------------------------------------
# DRUG TABLE (truncated to the most common examples – you can expand)
# ---------------------------------------------------------------------
DRUGS: List[Dict] = [
    # --- Pediatric bolus / fluids ---
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

    # --- Pediatric anaphylaxis / airway ---
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

    # --- Pediatric asthma ---
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
        "notes": "Standard neb dose 2.5 mg in 3 mL NS"
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

    # --- Pediatric pressor / infusion examples ---
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

    # --- Neonatal fluids ---
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
        "notes": "2 mL/kg over 5 min; thresholds depend on age"
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

    # --- Neonatal pressor infusion examples ---
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

    # --- Pediatric fever / pain (examples) ---
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
]

# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------


def filter_by_population(pop: str) -> List[Dict]:
    """Return drugs filtered by population string ('peds', 'neo', 'all')."""
    pop = pop.strip().lower()
    if pop in ("all", ""):
        return DRUGS

    if pop.startswith("p"):
        target = "pediatric"
    elif pop.startswith("n"):
        target = "neonatal"
    else:
        print("Unknown population; showing all.")
        return DRUGS

    return [d for d in DRUGS if d["population"].lower() == target]


def search_drugs(query: str, population: str) -> List[Dict]:
    """Search for drugs by name substring within a population filter."""
    candidates = filter_by_population(population)
    q = query.lower().strip()
    return [d for d in candidates if q in d["name"].lower()]


def calculate_dose(weight_kg: float, drug: Dict) -> Optional[float]:
    """
    Calculate a single dose for the given weight and drug.

    - If dose_per_kg is None, returns None (fixed dose; see typical_low/high or notes)
    - If max_dose is provided, caps at that value
    """
    per_kg = drug.get("dose_per_kg", None)
    if per_kg is None:
        return None

    raw = per_kg * weight_kg
    max_dose = drug.get("max_dose", None)

    if max_dose is not None:
        return min(raw, max_dose)
    return raw


def format_float(x: Optional[float]) -> str:
    if x is None:
        return "-"
    if float(x).is_integer():
        return str(int(x))
    return f"{x:.3g}"  # 3 sig figs


def parse_infusion_unit(dose_unit: str):
    """
    Parse units like 'mcg/kg/min' or 'unit/kg/hr'.

    Returns (numerator_unit, time_unit, time_factor_hours):

      - numerator_unit: 'mcg', 'unit', 'mg', etc
      - time_unit: 'min' or 'hr'
      - time_factor: 60 if per min (to convert to per hour), else 1
    """
    du_compact = dose_unit.replace(" ", "").lower()

    if "/kg/min" in du_compact:
        time_unit = "min"
        time_factor = 60.0
    elif "/kg/hr" in du_compact:
        time_unit = "hr"
        time_factor = 1.0
    else:
        return None

    # numerator unit is the part before first '/'
    numerator_unit = dose_unit.split("/")[0].strip()
    return numerator_unit, time_unit, time_factor


def infusion_rate_calc(weight_kg: float, drug: Dict):
    """
    Interactive infusion rate calculation:
    - Asks for desired dose (numerator_unit/kg/time)
    - Asks for bag/syringe concentration (amount and volume)
    - Outputs mL/hr
    """
    info = parse_infusion_unit(drug.get("dose_unit", ""))
    if not info:
        return

    numerator_unit, time_unit, time_factor = info

    print("\nINFUSION CALCULATOR FOR THIS DRUG")
    print("---------------------------------")
    print(f"Dose units: {drug['dose_unit']}")
    print(f"Numerator unit: {numerator_unit}")
    print(f"Time basis   : per {time_unit}")

    default_dose = drug.get("dose_per_kg") or 0.0

    while True:
        dose_str = input(
            f"Desired infusion dose in {numerator_unit}/kg/{time_unit} "
            f"(Enter for default {default_dose}): "
        ).strip()
        if dose_str == "":
            dose_value = default_dose
            break
        try:
            dose_value = float(dose_str)
            if dose_value <= 0:
                print("Dose must be > 0.")
                continue
            break
        except ValueError:
            print("Could not parse that as a number. Try again.")

    # Bag/syringe concentration
    while True:
        amt_str = input(f"Total amount in bag/syringe (in {numerator_unit}): ").strip()
        vol_str = input("Total volume of bag/syringe (in mL): ").strip()
        try:
            total_amt = float(amt_str)
            total_vol = float(vol_str)
            if total_amt <= 0 or total_vol <= 0:
                print("Both amount and volume must be > 0. Try again.")
                continue
            break
        except ValueError:
            print("Couldn't parse amount/volume. Try again.")

    conc = total_amt / total_vol  # numerator_unit per mL

    # convert dose to per hour (e.g. mcg/kg/min -> mcg/kg/hr)
    dose_per_kg_per_hr = dose_value * time_factor
    total_per_hr = dose_per_kg_per_hr * weight_kg

    rate_mL_hr = total_per_hr / conc

    print("\nINFUSION RATE RESULT")
    print("--------------------")
    print(
        f"Concentration: {total_amt:g} {numerator_unit} / {total_vol:g} mL "
        f"= {conc:.4g} {numerator_unit}/mL"
    )
    if time_unit == "min":
        print(
            f"Dose: {dose_value:g} {numerator_unit}/kg/min × {weight_kg:g} kg "
            f"= {dose_value * weight_kg:.4g} {numerator_unit}/min "
            f"= {total_per_hr:.4g} {numerator_unit}/hr"
        )
    else:
        print(
            f"Dose: {dose_value:g} {numerator_unit}/kg/hr × {weight_kg:g} kg "
            f"= {total_per_hr:.4g} {numerator_unit}/hr"
        )
    print(f"Pump rate: ~ {rate_mL_hr:.2f} mL/hr")
    print("Round to the nearest practical rate per your pump + protocol.\n")


# ---------------------------------------------------------------------
# MAIN CLI LOOP
# ---------------------------------------------------------------------


def main():
    print("=" * 72)
    print(" Neonatal & Pediatric Dosing + Infusion Calculator (CLI)")
    print(" *** FOR EDUCATION/REFERENCE ONLY ***")
    print("=" * 72)
    print()

    while True:
        try:
            weight_str = input("Enter patient weight in kg (or 'q' to quit): ").strip()
            if weight_str.lower() in ("q", "quit", "exit"):
                print("Bye.")
                return

            weight_kg = float(weight_str)
            if weight_kg <= 0:
                print("Weight must be > 0.")
                continue
        except ValueError:
            print("Couldn't parse that as a number. Try again.")
            continue

        pop = input(
            "Population [Pediatric / Neonatal / All] "
            "(e.g. 'p', 'n', or Enter for all): "
        ).strip()

        query = input(
            "Search drug name (substring, e.g. 'epi', 'd10', 'dopamine'): "
        ).strip()
        matches = search_drugs(query, pop)

        if not matches:
            print("No drugs found for that search. Try again.\n")
            continue

        print("\nMatched drugs:")
        for idx, d in enumerate(matches, start=1):
            print(f"  {idx:2d}. {d['name']}  [{d['population']}]  ({d['route']})")

        try:
            sel_str = input("Select a drug by number (or 'c' to cancel): ").strip()
            if sel_str.lower() in ("c", "cancel"):
                print("Canceled. Start over.\n")
                continue

            sel = int(sel_str)
            if not (1 <= sel <= len(matches)):
                print("Out of range. Start over.\n")
                continue
        except ValueError:
            print("Not a valid number. Start over.\n")
            continue

        drug = matches[sel - 1]
        print("\nSelected:")
        print(f"  Name      : {drug['name']}")
        print(f"  Population: {drug['population']}")
        print(f"  Protocol  : {drug['protocol']}")
        print(f"  Route     : {drug['route']}")
        print(f"  Per-kg    : {format_float(drug['dose_per_kg'])} {drug['dose_unit']}")
        print(f"  Max dose  : {format_float(drug['max_dose'])} {drug['max_unit']}")
        if drug.get("typical_low") is not None or drug.get("typical_high") is not None:
            print(
                f"  Typical   : {format_float(drug['typical_low'])}"
                f"–{format_float(drug['typical_high'])}"
            )
        if drug.get("notes"):
            print(f"  Notes     : {drug['notes']}")

        dose = calculate_dose(weight_kg, drug)

        print("\nCALCULATED SINGLE DOSE:")
        if dose is None:
            print("  This entry doesn’t use a simple per-kg calc here.")
            print("  Check 'typical' range and notes; verify with protocol.")
        else:
            per_kg = drug["dose_per_kg"] or 0
            raw = per_kg * weight_kg
            print(
                f"  Raw calc  : {format_float(weight_kg)} kg × "
                f"{format_float(per_kg)} {drug['dose_unit']} "
                f"= {format_float(raw)}"
            )
            if drug.get("max_dose") is not None and dose < raw:
                print(
                    f"  Capped at : {format_float(drug['max_dose'])} "
                    f"{drug['max_unit']}"
                )
            final_unit = drug["max_unit"] or drug["dose_unit"].replace("/kg", "")
            print(f"  Final     : {format_float(dose)} {final_unit}")

        # Infusion rate option if applicable
        inf_info = parse_infusion_unit(drug.get("dose_unit", ""))
        if inf_info:
            yn = input(
                "\nCalculate infusion pump rate (mL/hr) for this drug? [y/N]: "
            ).strip().lower()
            if yn in ("y", "yes"):
                infusion_rate_calc(weight_kg, drug)

        print("\nRemember: verify against your institutional protocol.")
        print("-" * 72)
        again = input(
            "Calculate another drug for this or another patient? [y/N]: "
        ).strip().lower()
        if again not in ("y", "yes"):
            print("Bye.")
            break
        print()


if __name__ == "__main__":
    main()
