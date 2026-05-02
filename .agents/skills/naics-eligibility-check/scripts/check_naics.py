#!/usr/bin/env python3
"""
check_naics.py — NAICS Eligibility Checker for Government Contract Bids

Source: U.S. SBA Table of Small Business Size Standards
        Effective March 17, 2023

Usage:
    python check_naics.py <NAICS_CODE> [--revenue <MILLIONS>] [--employees <COUNT>] [--setaside <TYPE>]

Examples:
    python check_naics.py 622110 --revenue 36
    python check_naics.py 339112 --employees 160
    python check_naics.py 622110 --revenue 36 --setaside SDVOSB
"""

import argparse
import json

# ---------------------------------------------------------------------------
# NAICS Size Standards — pulled directly from SBA Table effective March 17, 2023
# Format: "NAICS": ("Description", "type", value)
#   type: "revenue_millions" or "employees"
# ---------------------------------------------------------------------------
NAICS_DATA = {

    # Sector 23 – Construction
    "236115": ("New Single-family Housing Construction", "revenue_millions", 45.0),
    "236116": ("New Multifamily Housing Construction", "revenue_millions", 45.0),
    "236117": ("New Housing For-Sale Builders", "revenue_millions", 45.0),
    "236118": ("Residential Remodelers", "revenue_millions", 45.0),
    "236210": ("Industrial Building Construction", "revenue_millions", 45.0),
    "236220": ("Commercial and Institutional Building Construction", "revenue_millions", 45.0),
    "237110": ("Water and Sewer Line Construction", "revenue_millions", 45.0),
    "237310": ("Highway, Street, and Bridge Construction", "revenue_millions", 45.0),
    "237990": ("Other Heavy and Civil Engineering Construction", "revenue_millions", 45.0),
    "238110": ("Poured Concrete Foundation Contractors", "revenue_millions", 19.0),
    "238210": ("Electrical Contractors", "revenue_millions", 19.0),
    "238220": ("Plumbing, Heating, and Air Conditioning Contractors", "revenue_millions", 19.0),
    "238290": ("Other Building Equipment Contractors", "revenue_millions", 22.0),
    "238910": ("Site Preparation Contractors", "revenue_millions", 19.0),
    "238990": ("All Other Specialty Trade Contractors", "revenue_millions", 19.0),

    # Sector 31-33 – Manufacturing (medical/defense focus)
    "325411": ("Medicinal and Botanical Manufacturing", "employees", 1000),
    "325412": ("Pharmaceutical Preparation Manufacturing", "employees", 1300),
    "325413": ("In Vitro Diagnostic Substance Manufacturing", "employees", 1250),
    "325414": ("Biological Product Manufacturing", "employees", 1250),
    "334510": ("Electromedical and Electrotherapeutic Apparatus Manufacturing", "employees", 1250),
    "334511": ("Search, Detection, Navigation, Guidance, Aeronautical, and Nautical System Manufacturing", "employees", 1350),
    "334516": ("Analytical Laboratory Instrument Manufacturing", "employees", 1000),
    "334517": ("Irradiation Apparatus Manufacturing", "employees", 1200),
    "336411": ("Aircraft Manufacturing", "employees", 1500),
    "336412": ("Aircraft Engine and Engine Parts Manufacturing", "employees", 1500),
    "336413": ("Other Aircraft Part and Auxiliary Equipment Manufacturing", "employees", 1250),
    "336414": ("Guided Missile and Space Vehicle Manufacturing", "employees", 1300),
    "339112": ("Surgical and Medical Instrument Manufacturing", "employees", 1000),
    "339113": ("Surgical Appliance and Supplies Manufacturing", "employees", 800),
    "339114": ("Dental Equipment and Supplies Manufacturing", "employees", 750),
    "339115": ("Ophthalmic Goods Manufacturing", "employees", 1000),
    "339116": ("Dental Laboratories", "employees", 500),

    # Sector 42 – Wholesale Trade
    "423450": ("Medical, Dental, and Hospital Equipment and Supplies Merchant Wholesalers", "employees", 200),
    "423460": ("Ophthalmic Goods Merchant Wholesalers", "employees", 175),

    # Sector 48-49 – Transportation and Warehousing
    "484110": ("General Freight Trucking, Local", "revenue_millions", 34.0),
    "484121": ("General Freight Trucking, Long Distance, Truckload", "revenue_millions", 34.0),
    "484122": ("General Freight Trucking, Long Distance, Less Than Truckload", "revenue_millions", 43.0),
    "484210": ("Used Household and Office Goods Moving", "revenue_millions", 34.0),
    "484220": ("Specialized Freight Trucking, Local", "revenue_millions", 34.0),
    "484230": ("Specialized Freight Trucking, Long Distance", "revenue_millions", 34.0),
    "488111": ("Air Traffic Control", "revenue_millions", 40.0),
    "488119": ("Other Airport Operations", "revenue_millions", 40.0),
    "488190": ("Other Support Activities for Air Transportation", "revenue_millions", 40.0),
    "488210": ("Support Activities for Rail Transportation", "revenue_millions", 34.0),
    "488310": ("Port and Harbor Operations", "revenue_millions", 47.0),
    "488320": ("Marine Cargo Handling", "revenue_millions", 47.0),
    "488510": ("Freight Transportation Arrangement", "revenue_millions", 20.0),
    "488991": ("Packing and Crating", "revenue_millions", 34.0),
    "492110": ("Couriers and Express Delivery Services", "employees", 1500),
    "492210": ("Local Messengers and Local Delivery", "revenue_millions", 34.0),
    "493110": ("General Warehousing and Storage", "revenue_millions", 34.0),
    "493120": ("Refrigerated Warehousing and Storage", "revenue_millions", 36.5),
    "493130": ("Farm Product Warehousing and Storage", "revenue_millions", 34.0),
    "493190": ("Other Warehousing and Storage", "revenue_millions", 36.5),

    # Sector 51 – Information
    "518210": ("Computing Infrastructure Providers, Data Processing, Web Hosting", "revenue_millions", 40.0),
    "513210": ("Software Publishers", "revenue_millions", 47.0),

    # Sector 54 – Professional, Scientific and Technical Services
    "541110": ("Offices of Lawyers", "revenue_millions", 15.5),
    "541211": ("Offices of Certified Public Accountants", "revenue_millions", 26.5),
    "541310": ("Architectural Services", "revenue_millions", 12.5),
    "541330": ("Engineering Services", "revenue_millions", 25.5),
    "541380": ("Testing Laboratories and Services", "revenue_millions", 19.0),
    "541511": ("Custom Computer Programming Services", "revenue_millions", 34.0),
    "541512": ("Computer Systems Design Services", "revenue_millions", 34.0),
    "541519": ("Other Computer Related Services", "revenue_millions", 34.0),
    "541611": ("Administrative Management and General Management Consulting Services", "revenue_millions", 24.5),
    "541612": ("Human Resources Consulting Services", "revenue_millions", 29.0),
    "541613": ("Marketing Consulting Services", "revenue_millions", 19.0),
    "541614": ("Process, Physical Distribution and Logistics Consulting Services", "revenue_millions", 20.0),
    "541618": ("Other Management Consulting Services", "revenue_millions", 19.0),
    "541620": ("Environmental Consulting Services", "revenue_millions", 19.0),
    "541690": ("Other Scientific and Technical Consulting Services", "revenue_millions", 19.0),
    "541713": ("Research and Development in Nanotechnology", "employees", 1000),
    "541714": ("Research and Development in Biotechnology", "employees", 1000),
    "541715": ("Research and Development in Physical, Engineering, and Life Sciences", "employees", 1000),
    "541720": ("Research and Development in the Social Sciences and Humanities", "revenue_millions", 28.0),
    "541810": ("Advertising Agencies", "revenue_millions", 25.5),
    "541910": ("Marketing Research and Public Opinion Polling", "revenue_millions", 22.5),
    "541990": ("All Other Professional, Scientific and Technical Services", "revenue_millions", 19.5),

    # Sector 56 – Administrative and Support Services
    "561110": ("Office Administrative Services", "revenue_millions", 12.5),
    "561210": ("Facilities Support Services", "revenue_millions", 47.0),
    "561311": ("Employment Placement Agencies", "revenue_millions", 34.0),
    "561320": ("Temporary Help Services", "revenue_millions", 34.0),
    "561330": ("Professional Employer Organizations", "revenue_millions", 41.5),
    "561612": ("Security Guards and Patrol Services", "revenue_millions", 29.0),
    "561720": ("Janitorial Services", "revenue_millions", 22.0),
    "561990": ("All Other Support Services", "revenue_millions", 16.5),

    # Sector 62 – Health Care and Social Assistance
    "621111": ("Offices of Physicians (except Mental Health Specialists)", "revenue_millions", 16.0),
    "621112": ("Offices of Physicians, Mental Health Specialists", "revenue_millions", 13.5),
    "621210": ("Offices of Dentists", "revenue_millions", 9.0),
    "621310": ("Offices of Chiropractors", "revenue_millions", 9.0),
    "621320": ("Offices of Optometrists", "revenue_millions", 9.0),
    "621330": ("Offices of Mental Health Practitioners (except Physicians)", "revenue_millions", 9.0),
    "621340": ("Offices of Physical, Occupational and Speech Therapists and Audiologists", "revenue_millions", 12.5),
    "621391": ("Offices of Podiatrists", "revenue_millions", 9.0),
    "621399": ("Offices of All Other Miscellaneous Health Practitioners", "revenue_millions", 10.0),
    "621410": ("Family Planning Centers", "revenue_millions", 19.0),
    "621420": ("Outpatient Mental Health and Substance Abuse Centers", "revenue_millions", 19.0),
    "621491": ("HMO Medical Centers", "revenue_millions", 44.5),
    "621492": ("Kidney Dialysis Centers", "revenue_millions", 47.0),
    "621493": ("Freestanding Ambulatory Surgical and Emergency Centers", "revenue_millions", 19.0),
    "621498": ("All Other Outpatient Care Centers", "revenue_millions", 25.5),
    "621511": ("Medical Laboratories", "revenue_millions", 41.5),
    "621512": ("Diagnostic Imaging Centers", "revenue_millions", 19.0),
    "621610": ("Home Health Care Services", "revenue_millions", 19.0),
    "621910": ("Ambulance Services", "revenue_millions", 22.5),
    "621991": ("Blood and Organ Banks", "revenue_millions", 40.0),
    "621999": ("All Other Miscellaneous Ambulatory Health Care Services", "revenue_millions", 20.5),
    "622110": ("General Medical and Surgical Hospitals", "revenue_millions", 47.0),
    "622210": ("Psychiatric and Substance Abuse Hospitals", "revenue_millions", 47.0),
    "622310": ("Specialty (except Psychiatric and Substance Abuse) Hospitals", "revenue_millions", 47.0),
    "623110": ("Nursing Care Facilities (Skilled Nursing Facilities)", "revenue_millions", 34.0),
    "623210": ("Residential Intellectual and Developmental Disability Facilities", "revenue_millions", 19.0),
    "623220": ("Residential Mental Health and Substance Abuse Facilities", "revenue_millions", 19.0),
    "623311": ("Continuing Care Retirement Communities", "revenue_millions", 34.0),
    "623312": ("Assisted Living Facilities for the Elderly", "revenue_millions", 23.5),
    "623990": ("Other Residential Care Facilities", "revenue_millions", 16.0),
    "624110": ("Child and Youth Services", "revenue_millions", 15.5),
    "624120": ("Services for the Elderly and Persons with Disabilities", "revenue_millions", 15.0),
    "624190": ("Other Individual and Family Services", "revenue_millions", 16.0),
    "624230": ("Emergency and Other Relief Services", "revenue_millions", 41.5),
    "624410": ("Child Care Services", "revenue_millions", 9.5),
}

MEDICAL_SECTORS = {"621", "622", "623", "624", "334", "339"}

SETASIDE_NOTES = {
    "SDVOSB": "SBA-certified or VA-verified Service-Disabled Veteran-Owned Small Business required.",
    "VOSB": "Veteran-Owned Small Business; primarily used for VA contracts.",
    "WOSB": "Women-Owned Small Business; must be at least 51% woman-owned and controlled.",
    "8A": "SBA 8(a) Business Development program participant required.",
    "HUBZONE": "Business must be in a HUBZone with 35% employees in zone.",
    "SB": "Any concern qualifying as small under the applicable size standard.",
}


def check_size(standard_type, standard_value, revenue=None, employees=None):
    if standard_type == "revenue_millions":
        if revenue is None:
            return None, "Revenue not provided; cannot determine size qualification."
        if revenue <= standard_value:
            return True, f"${revenue}M avg annual revenue <= ${standard_value}M size standard limit."
        else:
            return False, f"${revenue}M avg annual revenue exceeds ${standard_value}M size standard limit."
    elif standard_type == "employees":
        if employees is None:
            return None, "Employee count not provided; cannot determine size qualification."
        if employees <= standard_value:
            return True, f"{employees} employees <= {standard_value} employee size standard limit."
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
                f"NAICS code {code} not in skill data table. "
                "Verify at: https://www.sba.gov/document/support-table-size-standards"
            ),
        }

    description, standard_type, standard_value = NAICS_DATA[code]
    sector = code[:3]
    medical = sector in MEDICAL_SECTORS

    qualified, size_detail = check_size(standard_type, standard_value, revenue, employees)

    if standard_type == "revenue_millions":
        size_standard_display = f"${standard_value}M average annual receipts"
    else:
        size_standard_display = f"{standard_value} employees"

    if qualified is True:
        recommendation = "GO"
    elif qualified is False:
        recommendation = "NO-GO"
    else:
        recommendation = "CONDITIONAL"

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
        "sdvosb_eligible": qualified,
        "recommendation": recommendation,
        "source": "SBA Table of Small Business Size Standards, effective March 17, 2023",
    }

    if setaside:
        key = setaside.upper().replace("-", "").replace("_", "")
        note = SETASIDE_NOTES.get(key, f"Set-aside type '{setaside}' not recognized.")
        result["setaside_requested"] = setaside
        result["setaside_note"] = note

    return result


def main():
    parser = argparse.ArgumentParser(description="Check NAICS eligibility using official SBA size standards.")
    parser.add_argument("naics_code", help="6-digit NAICS code")
    parser.add_argument("--revenue", type=float, default=None, metavar="MILLIONS",
                        help="3-year average annual revenue in millions (e.g. 36 for $36M)")
    parser.add_argument("--employees", type=int, default=None, metavar="COUNT",
                        help="Employee count (e.g. 160)")
    parser.add_argument("--setaside", type=str, default=None,
                        help="Set-aside type: SDVOSB, VOSB, WOSB, 8A, HUBZONE, SB")

    args = parser.parse_args()
    result = build_result(args.naics_code, args.revenue, args.employees, args.setaside)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
