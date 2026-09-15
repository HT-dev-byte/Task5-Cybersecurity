# PhishAware — Security Awareness & Incident Response Simulator

**PhishAware** is a self-contained, non-deployable security awareness phishing simulation and incident response web application. It demonstrates the complete lifecycle of a phishing incident within a fictional corporate environment, emphasizing security awareness education, defensive telemetry analysis, security event logging, and SOC incident containment.

> ⚠️ **EDUCATIONAL AND SIMULATION USE ONLY**
> This application is strictly an educational tool designed for security awareness training, capstone demonstrations, and SOC workflow simulation.
> - **NO REAL EMAILS ARE SENT.**
> - **NO REAL PASSWORDS ARE COLLECTED OR STORED.**
> - **NO REAL ORGANIZATIONS ARE IMPERSONATED** (Uses fictional entity `Northstar Financial Services` and reserved domain `northstar.example`).
> - **NO EXTERNAL SYSTEMS ARE CONTACTED.**

---

## 📋 Table of Contents

- [1. Executive Summary & Objectives](#1-executive-summary--objectives)
- [2. Technology Stack](#2-technology-stack)
- [3. Safety & Boundary Controls](#3-safety--boundary-controls)
- [4. Project Architecture](#4-project-architecture)
- [5. Installation & Local Run Guide](#5-installation--local-run-guide)
- [6. Application Workflow & Demonstration Guide](#6-application-workflow--demonstration-guide)
- [7. Incident Response & SIEM Integration](#7-incident-response--siem-integration)
- [8. Limitations & Ethical Considerations](#8-limitations-&-ethical-considerations)

---

## 1. Executive Summary & Objectives

### Objectives
1. Demonstrate user interaction analysis and defensive educational feedback for phishing campaigns.
2. Provide interactive SOC incident response workflows: Detection, Analysis, Containment, Eradication, Recovery, and Lessons Learned.
3. Expose structured SIEM telemetry logs with JSON and CSV export capabilities.
4. Maintain a 100% safe, non-deployable local footprint.

---

## 2. Technology Stack

- **Backend:** Python 3.12+, Flask 3.1+
- **Database:** SQLite 3 (local relational database)
- **Frontend:** Responsive HTML5, CSS3, Vanilla JavaScript, Chart.js (CDNs)
- **Data Formats:** JSON, CSV (SIEM telemetry exports)

---

## 3. Safety & Boundary Controls

PhishAware enforces safety constraints by design:
- All domain references point exclusively to reserved example domain `northstar.example`.
- Fictional target users: `Alex Morgan`, `Jordan Lee`, `Taylor Smith`, `Casey Vance`, `Riley Davis`.
- Any password input field shown on the simulated phishing landing page is explicitly labeled as a dummy field. Submissions discard inputs immediately without recording or transmitting values.
- Event logs record safe event strings such as `FORM_INTERACTION` and `LINK_INTERACTION`.

---

## 4. Project Architecture

```text
                        ┌─────────────────────────────────────────┐
                        │             Simulated User              │
                        │ (Alex Morgan, Jordan Lee, Taylor Smith) │
                        └────────────────────┬────────────────────┘
                                             │
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │           Mock Email Inbox              │
                        │      (Northstar IT / HR / Payroll)      │
                        └────────────────────┬────────────────────┘
                                             │
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │        Phishing Scenario Engine         │
                        │    (Decision: Report / Open / Ignore)   │
                        └────────────────────┬────────────────────┘
                                             │
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │          Security Event Logger          │
                        │   (Telemetry: LINK_CLICK, REPORT, etc.) │
                        └────────────────────┬────────────────────┘
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
          ┌──────────────────────────┐               ┌──────────────────────────┐
          │ Security Awareness Engine│               │ Incident Response Module │
          │  - Score Calculation     │               │  - Phase 1: Detection    │
          │  - Indicator Analysis    │               │  - Phase 2: Containment  │
          │  - Defensive Guidance    │               │  - Phase 3: Eradication  │
          └────────────┬─────────────┘               │  - Phase 4: Recovery     │
                       │                             └────────────┬─────────────┘
                       │                                          │
                       └─────────────────────┬────────────────────┘
                                             │
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │          SIEM Export & Reports          │
                        │        (JSON / CSV / Findings)          │
                        └─────────────────────────────────────────┘
```

---

## 5. Installation & Local Run Guide

### Prerequisites
- Python 3.10+ installed.

### Setup Steps
1. Clone the repository and navigate to the project root:
   ```bash
   cd PhishAware
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize and seed the SQLite database:
   ```bash
   python seed.py
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Access the application in your browser at `http://localhost:5000`.

---

## 6. Application Workflow & Demonstration Guide

1. **Dashboard (`/`)**: View campaign status, user count, link interactions, active incident phase, and real-time security logs.
2. **Simulated Inbox (`/inbox`)**: Switch personas (e.g. `Alex Morgan`) and review incoming messages (legitimate vs. simulated phishing).
3. **Email View (`/email/<id>`)**: Inspect email body, headers, and select decision (`Report as Phishing`, `Open Link`, `Ignore Message`).
4. **Safe Landing Page (`/landing-page`)**: Observe corporate verification prompt with non-storing dummy password input.
5. **Awareness Analysis (`/awareness-analysis`)**: Review indicator feedback, awareness score adjustments, and defensive guidance.
6. **Event Logs (`/events`)**: Audit security event logs with filters (User, Event Type, Severity) and export SIEM JSON/CSV.
7. **Incident Response (`/incident-response`)**: Walk through SOC phases (Detection, Containment, Eradication, Recovery).
8. **Incident Timeline (`/incident-timeline`)**: Review chronological event progression.
9. **Metrics (`/metrics`)**: Inspect interaction rates, reporting rates, and departmental awareness scores via Chart.js visuals.

---

## 7. Incident Response & SIEM Integration

### SIEM Log Telemetry
Telemetry logs are recorded for all actions in `security_events`:
```json
{
  "id": 3,
  "timestamp": "2025-05-10 08:31:45",
  "username": "alex.morgan@northstar.example",
  "event_type": "LINK_INTERACTION",
  "severity": "HIGH",
  "details": "Clicked link in simulated phishing message (Email ID 1)"
}
```

Exports can be ingested into external SIEM tools (ELK Stack, Splunk, QRadar) for simulated security monitoring analysis.

---
## 8. Limitations & Ethical Considerations

- **Educational Boundaries:** The tool strictly avoids real credential transmission or email relay capabilities.
- **Fictional Data:** All domains (`northstar.example`) and personas are mock entities.
- **Local Application:** Designed specifically to run on local developer instances (`localhost:5000`) without external cloud infrastructure.
