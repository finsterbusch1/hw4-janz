# \# naics-eligibility-check

# 

# A reusable AI skill for SDVOSBs bidding on government contracts. Validates NAICS codes

# against SBA size standards, determines small business eligibility, and flags SDVOSB

# set-aside signals — producing a structured go/no-go report in seconds.

# 

# \## Why I Built This

# 

# JANZ Corporation is a Service-Disabled Veteran-Owned Small Business (SDVOSB), dual-certified

# through both the SBA and the VA, that bids primarily on federal medical contracts. JANZ has

# a 3-year average annual revenue of $36M and 160 employees.

# 

# One of the most time-consuming steps in BD is manually looking up SBA size standards for

# each NAICS code on a solicitation and determining whether the company qualifies as a small

# business — and therefore whether SDVOSB set-aside rules apply.

# 

# This task is a perfect fit for a skill with a deterministic script because:

# \- Size standards are exact numeric thresholds — a model cannot reliably recall these without hallucinating wrong values

# \- The go/no-go determination is rule-based, not interpretive

# \- The lookup needs to be fast and repeatable across many solicitations per week

# 

# \## Skill Structure

# 

# .agents/skills/naics-eligibility-check/

# &#x20;   SKILL.md

# &#x20;   scripts/check\_naics.py

# &#x20;   references/sba-size-standards.md

# 

# \## How to Use

# 

# Open the project in Claude Code and ask:

# \- "Can JANZ bid on NAICS 622110? We have a 3-year average revenue of $36M as an SDVOSB."

# \- "Check NAICS 339113 — JANZ has 160 employees."

# \- "JANZ has $36M in revenue. Can we bid on NAICS 621999?"

# 

# \## What the Script Does

# 

# check\_naics.py is a self-contained Python script that looks up any 6-digit NAICS code

# against the complete SBA size standards table (444 codes, effective March 17, 2023),

# determines whether the company qualifies as a small business, flags medical/healthcare

# sectors, and returns a structured JSON object for the agent to interpret.

# 

# The model cannot do this reliably on its own — SBA size standards change periodically.

# The script is the single source of truth.

# 

# \## Test Cases

# 

# \- "Can JANZ bid on NAICS 622110? 3-year avg revenue $36M, 160 employees, SDVOSB." — GO

# \- "Check NAICS 622110 — we haven't finalized our 3-year average yet." — CONDITIONAL

# \- "JANZ has $36M in revenue. Can we bid on NAICS 621999?" — NO-GO

# 

# \## What Worked Well

# 

# \- Script JSON output makes results easy to interpret consistently

# \- Skill description is specific enough that Claude Code reliably activates it

# \- go/no-go framing gives BD staff a clear, actionable answer

# \- Built on JANZ's real profile making the demo immediately useful

# 

# \## Limitations

# 

# \- Size standards are from official SBA table effective March 17, 2023

# \- Script does not query SAM.gov live; certification status must be verified separately

# \- Revenue input should always be the SBA-defined 3-year average, not a single year

# 

# \## Video Walkthrough

# 

# 🎥 \[Walkthrough Video](https://youtu.be/e\_MWratvBOM)

# 

# Built for JHU Week 5: Build a Reusable AI Skill

# JANZ Corporation — SDVOSB, Dual SBA/VA Certified, Federal Medical Contracting

