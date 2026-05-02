---
name: naics-eligibility-check
description: >
  Validates NAICS codes for government contract bids, checks SBA size standards,
  flags SDVOSB set-aside eligibility, and produces a structured go/no-go report.
  Use this skill whenever the user mentions a NAICS code, asks about size standards,
  wants to know if a solicitation is a good fit, or asks about set-aside eligibility
  for a government contract — even if they don't use those exact terms. Also trigger
  for questions like "can we bid on this?", "are we eligible?", or "what's our size
  standard for this code?"
---

# NAICS Eligibility Check

A reusable skill for SDVOSBs (and other small businesses) to quickly validate whether
a NAICS code is a good fit for a bid, check SBA size standards, and surface any
set-aside eligibility signals before investing time in a proposal.

---

## When to use this skill

- User provides a NAICS code (6-digit) and wants to know if they qualify
- User pastes a solicitation title or description and wants eligibility analysis
- User asks "are we a small business under this code?"
- User asks about set-aside types (SDVOSB, WOSB, 8(a), HUBZone, SB-only)
- User wants a quick go/no-go signal before pulling a full solicitation

## When NOT to use this skill

- User is asking about SAM.gov registration steps (out of scope)
- User needs legal advice about eligibility disputes
- User is asking about past performance narrative writing
- NAICS code is not yet known — prompt the user to find it in the solicitation first

---

## Expected Inputs

The user should provide at least one of:
- A 6-digit NAICS code (e.g., `621111`)
- A company annual revenue or employee count (for size standard comparison)
- Optional: set-aside type of interest (SDVOSB, 8(a), WOSB, HUBZone, etc.)

If the user does not provide revenue/employee count, note it in the output and
flag that the size determination cannot be completed without it.

---

## Step-by-Step Instructions

### Step 1 — Extract the NAICS code
Pull the 6-digit NAICS code from the user's message. If it's embedded in a solicitation
snippet, extract it. If missing, ask the user: "What is the NAICS code listed on the
solicitation?"

### Step 2 — Run the script
Run the deterministic lookup script:

```bash
python .agents/skills/naics-eligibility-check/scripts/check_naics.py <NAICS_CODE> [--revenue <MILLIONS>] [--employees <COUNT>]
```

Examples:
```bash
python .agents/skills/naics-eligibility-check/scripts/check_naics.py 621111 --revenue 12.5
python .agents/skills/naics-eligibility-check/scripts/check_naics.py 336413 --employees 1250
```

The script outputs a JSON object. Parse it and use it as the factual basis for your response.

### Step 3 — Interpret and respond
Using the script's JSON output, produce a clear eligibility report (see Output Format below).

- If `small_business_qualified` is `true` and set-aside type is SDVOSB, give a **GO** signal
- If size standard is exceeded, give a **NO-GO** with explanation
- If company size was not provided, give a **CONDITIONAL** signal
- Always note if the code falls in a medical/healthcare sector

### Step 4 — Surface risks and next steps
Always end with 2–3 concrete next steps the BD team should take.

---

## Output Format

```
## NAICS Eligibility Report

**Code:** 621111 — Offices of Physicians (except Mental Health Specialists)
**Sector:** Healthcare / Medical (621)
**SBA Size Standard:** $20.5M average annual receipts

**Size Determination:** ✅ QUALIFIES as Small Business (your revenue: $12.5M < $20.5M limit)
**SDVOSB Set-Aside Eligible:** ✅ Yes — if VA-verified or SBA-certified SDVOSB

**Recommendation:** 🟢 GO — pursue this solicitation

**Next Steps:**
1. Confirm SDVOSB certification is active in SAM.gov
2. Check if the solicitation is a VA or non-VA federal agency (VA uses VOSB portal)
3. Pull the full RFP to verify any additional qualifications (licenses, bonding, etc.)
```

---

## Important Limitations

- Size standards are embedded in the script's data table (sourced from SBA, current as of 2024).
  Re-verify against [SBA's size standards table](https://www.sba.gov/document/support-table-size-standards)
  if the bid is high-stakes — standards are updated periodically.
- The script does not connect to SAM.gov or beta.SAM.gov live data.
- SDVOSB eligibility requires active certification; this skill checks code-level eligibility only.
- For 8(a) and HUBZone, additional program-specific requirements apply beyond size.
