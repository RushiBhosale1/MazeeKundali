# Marathi Kundali & Biodata Platform — Project Overview

## Vision
A web app for Marathi marriage-seeking families to:
1. Generate an accurate, detailed Vedic kundali (birth chart) for one person.
2. Match two kundalis (patrikas) using the Ashtakoot Guna Milan system for marriage compatibility.
3. Auto-generate a shareable Marathi biodata using data from the kundali.

## Core Principles (non-negotiable)
- **Accuracy first**: astrology output must match what a competent astrologer / established reference tool (DrikPanchang, AstroSage, ProKerala) would produce for the same birth data. See `03-ASTROLOGY-ENGINE-SPEC.md` for the validation strategy — this is treated as a hard QA gate before launch, not a nice-to-have.
- **Simplicity for Marathi users**: minimum fields to get a result, Marathi + English dual labeling, mobile-first, WhatsApp-shareable output.
- **Free-to-paid funnel**: user sees enough value for free (basic chart, basic Gana/Nadi/Manglik status) before being asked to pay for the detailed report / matching / biodata.

## Three Product Surfaces
| Surface | What it does | Price |
|---|---|---|
| Kundali Generator | Full birth chart + detailed analysis + PDF | ₹100 (free preview) |
| Patrika Matching | Ashtakoot Guna Milan between two people | ₹50 (free preview) |
| Biodata Builder | Marathi biodata using bio + auto-filled kundali data | included with kundali, or standalone |

## Who This Document Set Is For
This is the full planning doc-set for building the product from scratch. Read in this order:
1. `00-PROJECT-OVERVIEW.md` (this file)
2. `01-FEATURES-SCOPE.md`
3. `02-ARCHITECTURE.md`
4. `03-ASTROLOGY-ENGINE-SPEC.md` — **most important file, read fully before writing any calculation code**
5. `04-DATABASE-SCHEMA.md`
6. `05-USER-FLOW-UX.md`
7. `06-API-DESIGN.md`
8. `07-PAYMENT-INTEGRATION.md`
9. `08-TECH-STACK.md`
10. `09-MVP-ROADMAP.md`

## Success Criteria for MVP
- A user with no astrology knowledge can generate their kundali in under 2 minutes on mobile.
- Two kundalis can be matched and produce a Marathi-language plain-sentence verdict, not just a number.
- Engine output for 10 known reference birth-data test cases matches DrikPanchang/AstroSage within acceptable tolerance (see engine spec §Validation).
- Payment completes and unlocks content within the same session, no manual intervention.
