# naics-eligibility-check

A reusable AI skill for SDVOSBs bidding on government contracts. Validates NAICS codes
against SBA size standards, determines small business eligibility, and flags SDVOSB
set-aside signals — producing a structured go/no-go report in seconds.

\---

## Why I Built This

JANZ Corporation is a Service-Disabled Veteran-Owned Small Business (SDVOSB), dual-certified
through both the SBA and the VA, that bids primarily on federal medical contracts. JANZ has
a 3-year average annual revenue of $36M and 160 employees.

One of the most time-consuming and error-prone steps in the BD workflow is manually looking
up SBA size standards for each NAICS code on a solicitation and determining whether the
company qualifies as a small business — and therefore whether SDVOSB set-aside rules apply.

This task is a perfect fit for a skill with a deterministic script because:

* Size standards are **exact numeric thresholds** — a model cannot reliably recall or
compute these without hallucinating outdated or wrong values
* The go/no-go determination is **rule-based**, not interpretive
* The lookup needs to be **fast and repeatable** across many solicitations per week

\---

## Skill Structure

```
.agents/
└── skills/
    └── naics-eligibility-check/
        ├── SKILL.md                        # Skill instructions + activation logic
        ├── scripts/
        │   └── check\_naics.py             # Deterministic size standard lookup
        └── references/
            └── sba-size-standards.md      # Reference doc for SBA rules \& set-aside types
README.md
```

\---

## How to Use

### In Claude Code

1. Open the project in Claude Code (this repo is the project root).
2. Ask Claude something like:

   * *"Can JANZ bid on NAICS 622110? We have a 3-year average revenue of $36M as an SDVOSB."*
   * *"Check NAICS 339113 — JANZ has 160 employees."*
   * *"Is 621610 a good fit for a home health services bid?"*
3. Claude will read the SKILL.md, run the Python script, and produce a formatted report.

### Running the script directly

```bash
# Basic lookup (no size determination)
python .agents/skills/naics-eligibility-check/scripts/check\_naics.py 622110

# With 3-year average revenue (most medical codes use revenue-based standards)
python .agents/skills/naics-eligibility-check/scripts/check\_naics.py 622110 --revenue 36

# With employee count (manufacturing codes use employee-based standards)
python .agents/skills/naics-eligibility-check/scripts/check\_naics.py 339113 --employees 160

# With set-aside type
python .agents/skills/naics-eligibility-check/scripts/check\_naics.py 622110 --revenue 36 --setaside SDVOSB
```

\---

## What the Script Does

`check\_naics.py` is a self-contained Python script that:

1. Looks up the provided 6-digit NAICS code against an embedded SBA size standards table
(focused on medical, professional services, defense, and staffing sectors)
2. Determines whether the company qualifies as a **small business** based on the
applicable threshold type (3-year average revenue or employee count)
3. Flags whether the NAICS code falls in a **medical/healthcare sector** (621–624, 339)
4. Notes **SDVOSB eligibility** based on size qualification
5. Returns a structured **JSON object** for the agent to interpret and format

The model cannot do this reliably on its own — SBA size standards change periodically
and the model's training data may be outdated. The script is the single source of truth.

\---

## Test Cases (used in demo)

|Prompt|Type|
|-|-|
|"Can JANZ bid on NAICS 622110? 3-year avg revenue is $36M, 160 employees, SDVOSB."|Normal case — GO ($36M < $47M standard)|
|"Check NAICS 622110 — we haven't finalized our 3-year average yet."|Edge case — CONDITIONAL (missing data)|
|"JANZ has $36M in revenue. Can we bid on NAICS 621999?"|Decline — NO-GO ($36M exceeds $19.5M standard)|

\---

## What Worked Well

* The script's JSON output makes it easy for the model to interpret results consistently
* The skill description is specific enough that Claude Code reliably activates it
* The reference doc prevents the model from needing to recall SBA rules from memory
* The go/no-go framing gives BD staff a clear, actionable answer
* Using JANZ's real profile ($36M 3-year avg, 160 employees, dual SBA/VA certification)
makes the demo grounded and immediately useful

## Limitations

* The embedded NAICS table covers \~70 codes (medical/services/defense focus); codes
outside this set return a "not found" error with a link to the full SBA table
* Size standards are current as of March 2024 — the SBA updates these periodically
* The script does not query SAM.gov live; certification status must be verified separately
* Revenue input should always be the SBA-defined 3-year average, not a single year

\---

## Video Walkthrough

🎥 \[https://youtu.be/e\_MWratvBOM]

\---

*Built for JHU Week 5: Build a Reusable AI Skill
JANZ Corporation — SDVOSB, Dual SBA/VA Certified, Federal Medical Contracting*



*https://youtu.be/e\_MWratvBOM*



