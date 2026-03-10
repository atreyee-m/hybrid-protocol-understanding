"""
Protocol extraction prompts for all 6 PC types.

PROMPT_VERSION tracks the prompt logic version independently of code version.
Bump PROMPT_VERSION when prompt text changes, not on code-only changes.
"""

PROMPT_VERSION = "v2.1"

PROMPT_CHANGELOG = {
    "v1.0": "Initial prompts based on real Alexion protocol structure. "
            "Objectives use two-column table extraction. "
            "Eligibility captures numbered criteria with category subheadings. "
            "All schemas validated against ALXN1840-WD-204.",
    "v2.0": "PC-EVENT schema expanded: nested Adverse_Events, Serious_Adverse_Events, "
            "Relationship_to_Study_Drug, Severity_Assessment (CTCAE grades), "
            "Study_Drug_Action_Taken, Adverse_Event_Outcome. "
            "PC-ASSESSMENT schema expanded: added Informed_Consent and "
            "Screening_Baseline_Assessments blocks.",
    "v2.1": "STUDY_METADATA_PROMPT: clarified acronym field — must be an explicit short acronym, "
            "not the study title or subtitle; null if not present.",
}

# ---------------------------------------------------------------------------
# Shared system prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert clinical trial protocol analyst with deep knowledge of \
ICH E6 GCP guidelines, CDISC standards, and pharmaceutical regulatory requirements.

Your task is to extract structured information from clinical trial protocol text with \
absolute precision.

Rules you must follow without exception:
1. Extract ONLY information explicitly stated in the provided text. Never infer, assume, \
or hallucinate content not present in the source text.
2. Use the exact wording from the protocol whenever possible. Do not paraphrase clinical \
criteria, dosing instructions, or eligibility text.
3. If a field is not present in the provided text, use null for that field. Never invent \
placeholder values.
4. Respond with valid JSON only. No preamble, no explanation, no markdown code fences, \
no trailing commas.
5. Preserve all numerical values, units, timepoints, and thresholds exactly as written."""

# ---------------------------------------------------------------------------
# Study-level metadata (extracted from title page / synopsis)
# ---------------------------------------------------------------------------

STUDY_METADATA_PROMPT = """Extract study-level metadata from the following protocol text \
(typically from the title page, synopsis, or protocol header).

Return a JSON object with this exact schema:
{{
  "study_id": "<protocol number or study ID, e.g., DCC-3014-02-001 or null>",
  "acronym": "<a short uppercase abbreviation (typically 2–10 characters, e.g., ATLAS, CLARITY, CHAMPION) that is explicitly labeled as the study acronym or short name in the protocol — if no such short abbreviation exists, use null. NEVER use a sentence, phrase, or the study title as the acronym>",
  "protocol_version": "<protocol version or amendment, e.g., Amendment 4 (06 Nov 2025) or null>",
  "phase": "<clinical trial phase, e.g., Phase 2 or null>",
  "sponsor_name": "<name of the sponsor company or null>",
  "study_title": "<full official study title or null>",
  "study_drug": [
    "<drug and dose level 1, e.g., Drug X 10 mg once daily>",
    "<drug and dose level 2>"
  ],
  "therapeutic_area": "<therapeutic area, e.g., Hematology / Transplant / Immunology or null>",
  "indication": "<disease or condition being studied, concise description or null>",
  "trial_design": "<brief description of the overall study design, including phase, blinding, \
number of arms, dose levels, treatment duration, follow-up or null>",
  "trial_population": "<brief description of the target patient population or null>"
}}

Notes:
- study_drug: if multiple dose levels are tested, list each as a separate string.
- trial_design and trial_population: extract from the synopsis or study overview if present; \
otherwise synthesize from the title page and section headers.
- Use null for any field not found in the provided text.

Protocol text (first pages):
{section_text}"""

# ---------------------------------------------------------------------------
# PC-OBJ: Study Objectives and Endpoints
# ---------------------------------------------------------------------------

PC_OBJ_PROMPT = """Extract all study objectives and their corresponding endpoints from the \
following protocol section.

IMPORTANT STRUCTURAL NOTE: In clinical protocols, objectives and endpoints are typically \
presented as a two-column table with rows grouped under category headers: Primary, Secondary, \
Safety, and Exploratory. A category label (e.g., "Primary") may appear only once above \
multiple rows — apply that category to all objective-endpoint pairs until the next category \
label appears.

Return a JSON object with this exact schema:
{{
  "primary": [
    {{
      "objective": "<exact objective text>",
      "endpoint": "<exact endpoint text>"
    }}
  ],
  "secondary": [
    {{
      "objective": "<exact objective text>",
      "endpoint": "<exact endpoint text>"
    }}
  ],
  "safety": [
    {{
      "objective": "<exact objective text>",
      "endpoint": "<exact endpoint text>"
    }}
  ],
  "exploratory": [
    {{
      "objective": "<exact objective text>",
      "endpoint": "<exact endpoint text>"
    }}
  ]
}}

Notes:
- If a category (e.g., "exploratory") is not present in the protocol, return an empty list [].
- If an objective has multiple endpoints listed as bullet points, concatenate them as a \
single string with "; " as separator.
- Safety endpoints are often a list of safety parameters — capture all of them.

Protocol section text:
{section_text}"""

# ---------------------------------------------------------------------------
# PC-ELG-CRIT: Eligibility Criteria
# ---------------------------------------------------------------------------

PC_ELG_CRIT_PROMPT = """Extract all eligibility criteria from the following protocol section.

IMPORTANT STRUCTURAL NOTE: Inclusion and exclusion criteria are typically numbered lists. \
Inclusion criteria may have category subheadings (e.g., "Age", "Medical Conditions", \
"Prior/Concomitant Therapy") — capture the category for each criterion. \
Exclusion criteria follow the same pattern. Screen failures and lifestyle considerations \
may appear as separate subsections within the same section — extract those too if present.

Return a JSON object with this exact schema:
{{
  "inclusion_criteria": [
    {{
      "criterion_number": <integer>,
      "category": "<subheading category or null if none>",
      "text": "<exact criterion text>"
    }}
  ],
  "exclusion_criteria": [
    {{
      "criterion_number": <integer>,
      "category": "<subheading category or null if none>",
      "text": "<exact criterion text>"
    }}
  ],
  "screen_failures": {{
    "definition": "<definition of screen failure or null>",
    "rescreening_allowed": <true | false | null>,
    "rescreening_conditions": "<conditions under which rescreening is allowed or null>"
  }},
  "lifestyle_considerations": [
    {{
      "restriction_type": "<e.g., Food, Fluids, Alcohol, Physical activity, Contraception>",
      "details": "<exact restriction text>",
      "timeframe": "<when restriction applies or null>"
    }}
  ]
}}

Notes:
- criterion_number must match the numbering in the protocol exactly.
- If lifestyle_considerations or screen_failures subsections are not present, return [] or \
null for those fields respectively.
- Do not merge or combine criteria. Each numbered item is one entry.

Protocol section text:
{section_text}"""

# ---------------------------------------------------------------------------
# PC-EVENT: Adverse Events and Serious Adverse Events
# ---------------------------------------------------------------------------

PC_EVENT_PROMPT = """Extract adverse event and safety reporting information from the \
following protocol section.

Return a JSON object with this exact schema:
{{
  "Adverse_Events": {{
    "definition": "<exact definition of an Adverse Event or null>",
    "preexisting_conditions": "<how preexisting conditions are handled, exact text or null>",
    "pregnancy": "<how pregnancy is handled as an AE, exact text or null>",
    "disease_progression": "<whether disease progression meets AE definition, exact text or null>"
  }},
  "Serious_Adverse_Events": {{
    "definition": "<exact definition of a Serious Adverse Event or null>",
    "criteria": [
      "<SAE criterion 1, e.g., Death>",
      "<SAE criterion 2, e.g., Life-threatening event>"
    ],
    "clarifications": [
      "<clarification 1, e.g., Nonmedical/social admissions are not SAEs>"
    ]
  }},
  "ae_collection_period": "<when AE collection starts and ends>",
  "sae_reporting_timeframe": "<timeframe for reporting SAEs to sponsor, e.g., within 24 hours>",
  "Relationship_to_Study_Drug": {{
    "assessment": "<how causality is assessed, exact text or null>",
    "categories": {{
      "Related": "<definition of Related or null>",
      "Not_Related": "<definition of Not Related or null>"
    }}
  }},
  "Severity_Assessment": {{
    "grading_scale": "<grading scale used, e.g., NCI-CTCAE v5.0 or null>",
    "non_CTCAE_events": {{
      "Grade_1": "<description or null>",
      "Grade_2": "<description or null>",
      "Grade_3": "<description or null>",
      "Grade_4": "<description or null>",
      "Grade_5": "<description or null>"
    }},
    "note": "<any additional note about severity recording or null>"
  }},
  "Study_Drug_Action_Taken": {{
    "description": "<how study drug action is documented or null>",
    "categories": {{
      "Dose_Not_Changed": "<description or null>",
      "Drug_Interrupted": "<description or null>",
      "Dose_Reduced": "<description or null>",
      "Drug_Withdrawn": "<description or null>",
      "Not_Applicable": "<description or null>"
    }}
  }},
  "Adverse_Event_Outcome": {{
    "follow_up": "<how AEs are followed up, exact text or null>",
    "categories": {{
      "Recovered_Resolved": "<description or null>",
      "Recovered_with_Sequelae": "<description or null>",
      "Recovering": "<description or null>",
      "Ongoing": "<description or null>",
      "Fatal": "<description or null>",
      "Unknown": "<description or null>"
    }}
  }},
  "adverse_events_of_special_interest": [
    "<AESI description or statement that none exist>"
  ],
  "susar_definition": "<definition of SUSAR or null>",
  "events_meeting_ae_definition": [
    "<event type that meets AE definition>"
  ],
  "events_not_meeting_ae_definition": [
    "<event type that does NOT meet AE definition>"
  ]
}}

Notes:
- Many of these fields (definitions, CTCAE grades, causality) are often in a general \
definitions section (e.g., Section 10.3) cross-referenced from the main AE section. \
Extract whatever is present in the provided text; use null for anything not found.
- If adverse_events_of_special_interest explicitly states "none", capture that statement.
- SAE criteria are typically a bulleted list (Death, Life-threatening, hospitalization, etc.) \
— extract each as a separate string in the "criteria" array.

Protocol section text:
{section_text}"""

# ---------------------------------------------------------------------------
# PC-ASSESSMENT: Study Assessments and Procedures
# ---------------------------------------------------------------------------

PC_ASSESSMENT_PROMPT = """Extract study assessment and procedure information from the \
following protocol section.

IMPORTANT STRUCTURAL NOTE: Assessments are organized by subsection. Capture each subsection \
faithfully. The Schedule of Activities (SoA) table may be referenced — extract assessment \
descriptions from prose text, not from the SoA table itself.

Return a JSON object with this exact schema:
{{
  "Informed_Consent": {{
    "requirements": "<informed consent requirements, exact text or null>",
    "documentation": "<what must be documented, exact text or null>"
  }},
  "Screening_Baseline_Assessments": {{
    "demographics_and_history": "<what demographic/history data is collected or null>",
    "date_and_eligibility": "<eligibility confirmation process or null>",
    "prior_medications_procedures": "<prior medications/procedures collected or null>",
    "pulmonary_function_tests": "<PFT requirements or null>",
    "pregnancy_testing": "<pregnancy testing requirements or null>",
    "echocardiogram": "<echo requirements or null>",
    "walk_test": "<walk test requirements or null>"
  }},
  "efficacy_assessments": [
    {{
      "name": "<assessment name>",
      "description": "<what is being measured and how>",
      "collection_method": "<e.g., ICP-MS, blood draw, questionnaire or null>",
      "collection_timepoints": "<description of when collected or null>"
    }}
  ],
  "safety_assessments": [
    {{
      "name": "<assessment name, e.g., Physical Examination, ECG, Vital Signs>",
      "description": "<what is assessed>",
      "collection_method": "<method or null>",
      "collection_timepoints": "<description of when collected or null>"
    }}
  ],
  "pharmacokinetic_assessments": [
    {{
      "name": "<assessment name>",
      "analyte": "<what is being measured, e.g., total molybdenum>",
      "matrix": "<biological matrix, e.g., plasma, urine>",
      "collection_timepoints": "<description or null>"
    }}
  ],
  "pharmacodynamic_assessments": [
    {{
      "name": "<assessment name>",
      "analyte": "<what is being measured>",
      "matrix": "<biological matrix>",
      "collection_timepoints": "<description or null>"
    }}
  ],
  "biomarker_assessments": [
    {{
      "name": "<assessment name>",
      "description": "<description or null>"
    }}
  ],
  "other_assessments": [
    {{
      "name": "<assessment name>",
      "description": "<description or null>"
    }}
  ]
}}

Notes:
- Informed_Consent and Screening_Baseline_Assessments: use null for any sub-field not \
present in the text.
- If a category list (efficacy, PK, etc.) has no assessments, return an empty list [].
- Immunogenicity, genetics, health economics: include under other_assessments.
- Focus on prose descriptions; do not reconstruct the SoA table.

Protocol section text:
{section_text}"""

# ---------------------------------------------------------------------------
# PC-EXPOSURE: Study Intervention / Dosing
# ---------------------------------------------------------------------------

PC_EXPOSURE_PROMPT = """Extract all study intervention (drug exposure) information from the \
following protocol section.

Return a JSON object with this exact schema:
{{
  "drug_name": "<INN or study drug name>",
  "former_names": ["<alias 1>", "<alias 2>"],
  "formulation": "<e.g., Tablet, Capsule, IV infusion>",
  "unit_dose_strength": "<e.g., 15 mg per tablet>",
  "dose_levels": ["<dose level 1>", "<dose level 2>"],
  "route_of_administration": "<e.g., Oral, IV>",
  "dosing_schedule": "<frequency and duration, e.g., once daily for 28 days>",
  "dose_escalation": "<escalation scheme if applicable or null>",
  "administration_instructions": [
    "<instruction 1>",
    "<instruction 2>"
  ],
  "storage_conditions": "<storage requirements or null>",
  "dose_modifications": [
    {{
      "parameter": "<lab or clinical parameter triggering modification>",
      "condition": "<threshold or condition, exact text>",
      "action": "<dose action: reduce, interrupt, discontinue>",
      "monitoring": "<follow-up monitoring required>",
      "rechallenge": "<rechallenge conditions or null>"
    }}
  ],
  "overdose_definition": "<what constitutes an overdose in this study or null>",
  "overdose_management": "<instructions for managing overdose or null>",
  "blinding": "<open-label | single-blind | double-blind>",
  "randomization": "<randomized | non-randomized>"
}}

Notes:
- dose_modifications: extract all rows from the dose modification table. \
Each parameter-condition combination is a separate entry.
- administration_instructions: capture fasting requirements, water volume, \
timing relative to meals.
- former_names: include all aliases mentioned (e.g., WTX101 for ALXN1840).

Protocol section text:
{section_text}"""

# ---------------------------------------------------------------------------
# PC-CONMED: Concomitant Medications
# ---------------------------------------------------------------------------

PC_CONMED_PROMPT = """Extract all concomitant medication information from the following \
protocol section.

Return a JSON object with this exact schema:
{{
  "recording_window": {{
    "start": "<when conmed recording begins, e.g., 14 days prior to enrollment>",
    "end": "<when recording ends, e.g., EOS Visit>"
  }},
  "fields_to_capture": [
    "<field 1, e.g., reason for use>",
    "<field 2, e.g., start and end dates>",
    "<field 3, e.g., dose and frequency>"
  ],
  "permitted_medications": [
    {{
      "medication": "<medication name or class>",
      "conditions": "<conditions of use, dose limits, approval requirements>",
      "notes": "<additional notes or null>"
    }}
  ],
  "medications_requiring_caution": [
    {{
      "medication": "<medication name or class>",
      "reason": "<reason for caution>",
      "instructions": "<what to do>"
    }}
  ],
  "prohibited_medications": [
    {{
      "medication_or_class": "<medication, drug class, or supplement type>",
      "washout_period": "<required washout before study start or null>",
      "restriction_end": "<when restriction ends or null>"
    }}
  ],
  "documentation_requirements": "<any specific documentation requirements for conmeds or null>"
}}

Notes:
- permitted_medications: include everything explicitly listed as allowed, with dose caps.
- medications_requiring_caution: typically CYP substrate interactions — capture these \
separately from permitted and prohibited.
- prohibited_medications: include prescription drugs, OTC, vitamins, herbal supplements \
with their respective washout periods.
- If the protocol references another section for details, extract what's available in \
this section and note the reference.

Protocol section text:
{section_text}"""
