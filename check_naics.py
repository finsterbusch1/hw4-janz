#!/usr/bin/env python3
"""
check_naics.py — NAICS Eligibility Checker for Government Contract Bids

Usage:
    python check_naics.py <NAICS_CODE> [--revenue <MILLIONS>] [--employees <COUNT>] [--setaside <TYPE>]

Examples:
    python check_naics.py 621111 --revenue 12.5
    python check_naics.py 336413 --employees 1250
    python check_naics.py 561320 --revenue 28 --setaside SDVOSB

Outputs a JSON object with size standard info, sector classification,
small business qualification status, and SDVOSB eligibility signals.
"""

import argparse
import json
import sys

# ---------------------------------------------------------------------------
# SBA Size Standards Table (excerpt — medical/defense/services focus)
# Source: SBA Table of Small Business Size Standards, effective March 2024
# Full table: https://www.sba.gov/document/support-table-size-standards
#
# Format: NAICS_CODE: (description, standard_type, standard_value)
#   standard_type: "revenue_millions" | "employees"
#   standard_value: numeric threshold
# ---------------------------------------------------------------------------
NAICS_DATA = {
    # --- Healthcare & Medical (621–622) ---
    "621111": ("Offices of Physicians (except Mental Health)", "revenue_millions", 20.5),
    "621112": ("Offices of Physicians - Mental Health Specialists", "revenue_millions", 20.5),
    "621210": ("Offices of Dentists", "revenue_millions", 9.5),
    "621310": ("Offices of Chiropractors", "revenue_millions", 9.5),
    "621320": ("Offices of Optometrists", "revenue_millions", 9.5),
    "621330": ("Offices of Mental Health Practitioners", "revenue_millions", 9.5),
    "621340": ("Offices of Physical, Occupational, Speech Therapists", "revenue_millions", 9.5),
    "621391": ("Offices of Podiatrists", "revenue_millions", 9.5),
    "621399": ("Offices of All Other Health Practitioners", "revenue_millions", 9.5),
    "621410": ("Family Planning Centers", "revenue_millions", 19.5),
    "621420": ("Outpatient Mental Health / Substance Abuse Centers", "revenue_millions", 19.5),
    "621491": ("HMO Medical Centers", "revenue_millions", 35.0),
    "621492": ("Kidney Dialysis Centers", "revenue_millions", 35.0),
    "621493": ("Freestanding Ambulatory Surgical & Emergency Centers", "revenue_millions", 35.0),
    "621498": ("All Other Outpatient Care Centers", "revenue_millions", 19.5),
    "621511": ("Medical Laboratories", "revenue_millions", 35.0),
    "621512": ("Diagnostic Imaging Centers", "revenue_millions", 35.0),
    "621610": ("Home Health Care Services", "revenue_millions", 19.5),
    "621910": ("Ambulance Services", "revenue_millions", 19.5),
    "621991": ("Blood & Organ Banks", "revenue_millions", 19.5),
    "621999": ("All Other Ambulatory Health Care Services", "revenue_millions", 19.5),
    "622110": ("General Medical & Surgical Hospitals", "revenue_millions", 47.0),
    "622210": ("Psychiatric & Substance Abuse Hospitals", "revenue_millions", 47.0),
    "622310": ("Specialty Hospitals (except Psychiatric)", "revenue_millions", 47.0),
    "623110": ("Nursing Care Facilities", "revenue_millions", 35.0),
    "623210": ("Residential Intellectual / Developmental Disability Facilities", "revenue_millions", 19.5),
    "623220": ("Residential Mental Health Facilities", "revenue_millions", 19.5),
    "623311": ("Continuing Care Retirement Communities", "revenue_millions", 35.0),
    "623312": ("Assisted Living Facilities (except CCRCs)", "revenue_millions", 19.5),
    # --- Medical Devices & Supplies (339) ---
    "339112": ("Surgical & Medical Instrument Manufacturing", "employees", 1000),
    "339113": ("Surgical Appliance & Supplies Manufacturing", "employees", 750),
    "339114": ("Dental Equipment & Supplies Manufacturing", "employees", 500),
    "339115": ("Ophthalmic Goods Manufacturing", "employees", 500),
    "339116": ("Dental Laboratories", "revenue_millions", 22.0),
    # --- Professional Scientific & Technical Services (541) ---
    "541110": ("Offices of Lawyers", "revenue_millions", 12.5),
    "541211": ("Offices of Certified Public Accountants", "revenue_millions", 22.0),
    "541330": ("Engineering Services", "revenue_millions", 22.0),
    "541511": ("Custom Computer Programming Services", "revenue_millions", 34.0),
    "541512": ("Computer Systems Design Services", "revenue_millions", 34.0),
    "541519": ("Other Computer Related Services", "revenue_millions", 34.0),
    "541611": ("Administrative Management & General Management Consulting", "revenue_millions", 22.0),
    "541612": ("Human Resources Consulting Services", "revenue_millions", 16.5),
    "541613": ("Marketing Consulting Services", "revenue_millions", 22.0),
    "541614": ("Process, Physical Distribution, & Logistics Consulting", "revenue_millions", 22.0),
    "541618": ("Other Management Consulting Services", "revenue_millions", 22.0),
    "541690": ("Other Scientific & Technical Consulting Services", "revenue_millions", 19.0),
    "541711": ("Research & Development in Biotechnology", "employees", 1000),
    "541712": ("Research & Development in Physical, Engineering & Life Sciences", "employees", 1000),
    "541720": ("Research & Development in Social Sciences & Humanities", "revenue_millions", 22.0),
    "541990": ("All Other Professional, Scientific & Technical Services", "revenue_millions", 19.0),
    # --- Defense / Aerospace (336) ---
    "336411": ("Aircraft Manufacturing", "employees", 1500),
    "336412": ("Aircraft Engine & Engine Parts Manufacturing", "employees", 1500),
    "336413": ("Other Aircraft Parts & Auxiliary Equipment Manufacturing", "employees", 1500),
    "336414": ("Guided Missile & Space Vehicle Manufacturing", "employees", 1250),
    # --- Staffing / Support Services (561) ---
    "561320": ("Temporary Help Services", "revenue_millions", 34.0),
    "561330": ("Professional Employer Organizations", "revenue_millions", 34.0),
    "561110": ("Office Administrative Services", "revenue_millions", 22.0),
    "561210": ("Facilities Support Services", "revenue_millions", 47.0),
    "561990": ("All Other Support Services", "revenue_millions", 19.5),
    # --- IT / Cybersecurity (518, 519) ---
    "518210": ("Data Processing, Hosting & Related Services", "revenue_millions", 34.0),
    "519130": ("Internet Publishing & Broadcasting & Web Search Portals", "revenue_millions", 34.0),
    # --- Logistics / Transportation (488, 484) ---
    "484110": ("General Freight Trucking, Local", "revenue_millions", 34.0),
    "484121": ("General Freight Trucking, Long-Distance TL", "revenue_millions", 34.0),
    "488190": ("Other Support Activities for Air Transportation", "revenue_millions", 34.0),
}

# NAICS sectors that are medical/health-related
MEDICAL_SECTORS = {"621", "622", "623", "624", "339"}

# Known common set-aside types and basic notes
SETASIDE_NOTES = {
    "SDVOSB": "VA-verified or SBA-certified Service-Disabled Veteran-Owned Small Business required.",
    "VOSB": "Veteran-Owned Small Business; verify through VA's VetBiz portal.",
    "WOSB": "Women-Owned Small Business; must be at least 51% woman-owned and controlled.",
    "8A": "SBA 8(a) Business Development program participant required.",
    "HUBZONE": "Business must be located in a HUBZone and meet employment requirements.",
    "SB": "Any concern that qualifies as a small business under the applicable size standard.",
}


def get_sector(naics_code: str) -> str:
    """Return the 3-digit NAICS sector prefix."""
    return naics_code[:3]


def is_medical(naics_code: str) -> bool:
    return get_sector(naics_code) in MEDICAL_SECTORS


def check_size(standard_type, standard_value, revenue=None, employees=None):
    """
    Returns (qualified: bool|None, detail: str)
    None means insufficient data to determine.
    """
    if standard_type == "revenue_millions":
        if revenue is None:
            return None, "Revenue not provided; cannot determine size qualification."
        if revenue <= standard_value:
            return True, f"${revenue}M annual revenue ≤ ${standard_value}M size standard limit."
        else:
            return False, f"${revenue}M annual revenue exceeds ${standard_value}M size standard limit."
    elif standard_type == "employees":
        if employees is None:
            return None, "Employee count not provided; cannot determine size qualification."
        if employees <= standard_value:
            return True, f"{employees} employees ≤ {standard_value} employee size standard limit."
        else:
            return False, f"{employees} employees exceeds {standard_value} employee size standard limit."
    return None, "Unknown standard type."


def build_result(naics_code, revenue=None, employees=None, setaside=None):
    code = naics_code.strip()

    if code not in NAICS_DATA:
        return {
            "naics_code": code,
            "found": False,
            "error": (
                f"NAICS code {code} is not in the skill's embedded data table. "
                "This may be a valid code not yet included. Check SBA's full size standards table: "
                "https://www.sba.gov/document/support-table-size-standards"
            ),
        }

    description, standard_type, standard_value = NAICS_DATA[code]
    sector = get_sector(code)
    medical = is_medical(code)

    qualified, size_detail = check_size(standard_type, standard_value, revenue, employees)

    # Build size standard display string
    if standard_type == "revenue_millions":
        size_standard_display = f"${standard_value}M average annual receipts"
    else:
        size_standard_display = f"{standard_value} employees"

    # SDVOSB eligibility: qualifies if small business qualified (or unknown)
    sdvosb_eligible = None
    if qualified is True:
        sdvosb_eligible = True
    elif qualified is False:
        sdvosb_eligible = False
    # else: unknown (no size data)

    # Recommendation
    if qualified is True:
        recommendation = "GO"
        rec_color = "green"
    elif qualified is False:
        recommendation = "NO-GO"
        rec_color = "red"
    else:
        recommendation = "CONDITIONAL"
        rec_color = "yellow"

    result = {
        "naics_code": code,
        "found": True,
        "description": description,
        "sector": sector,
        "is_medical": medical,
        "size_standard_type": standard_type,
        "size_standard_value": standard_value,
        "size_standard_display": size_standard_display,
        "company_revenue_millions": revenue,
        "company_employees": employees,
        "small_business_qualified": qualified,
        "size_determination_detail": size_detail,
        "sdvosb_eligible": sdvosb_eligible,
        "recommendation": recommendation,
        "recommendation_color": rec_color,
    }

    if setaside:
        key = setaside.upper().replace("-", "").replace("_", "")
        note = SETASIDE_NOTES.get(key, f"Set-aside type '{setaside}' not recognized in skill data.")
        result["setaside_requested"] = setaside
        result["setaside_note"] = note

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Check NAICS code eligibility for government contract bids."
    )
    parser.add_argument("naics_code", help="6-digit NAICS code (e.g. 621111)")
    parser.add_argument(
        "--revenue",
        type=float,
        default=None,
        metavar="MILLIONS",
        help="Company average annual revenue in millions (e.g. 12.5 for $12.5M)",
    )
    parser.add_argument(
        "--employees",
        type=int,
        default=None,
        metavar="COUNT",
        help="Company employee count (e.g. 450)",
    )
    parser.add_argument(
        "--setaside",
        type=str,
        default=None,
        help="Set-aside type of interest: SDVOSB, VOSB, WOSB, 8A, HUBZONE, SB",
    )

    args = parser.parse_args()

    result = build_result(
        naics_code=args.naics_code,
        revenue=args.revenue,
        employees=args.employees,
        setaside=args.setaside,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
