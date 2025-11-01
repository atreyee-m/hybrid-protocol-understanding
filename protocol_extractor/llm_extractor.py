import os
import re
import json
import anthropic


class ExtractorAgent:
    """
    Neural agent using Sonnet to extract objectives and endpoints from a clinical trial protocol.
    """

    def __init__(self, model_id: str ='claude-sonnet-4-5-202509299'):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY in environment variables.")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_id = 'claude-sonnet-4-5-20250929'

    def extract_objectives_json(self, symbolic_data: dict) -> dict:

        prompt = f"""
        You are an expert in clinical trial protocols and endpoint analysis.

        Your task is to extract study objectives and endpoints from the following text.
        The text may be formatted as paragraphs or as a **table** with columns such as:
        "Objective Type", "Objective", "Endpoint", "Measure", "Timepoint".

        If presented in tabular form, interpret each row as one objective-endpoint pair.
        If sections are fragmented or headers are missing, infer them logically from context.

        <protocol_sections>
        Protocol ID: {symbolic_data.get('protocol_id')}
        Title: {symbolic_data.get('protocol_title')}
        Phase: {symbolic_data.get('study_phase')}
        Extracted Text:
        {symbolic_data.get('objectives_section_raw', '')}
        </protocol_sections>

        Return structured JSON with the following schema:

        - objectives: list of objects, each containing:
        - objective_type: "Primary" | "Secondary" | "Tertiary" | "Exploratory" (guess if unclear)
        - objective_text: full statement of the objective
        - endpoints: list of endpoint objects, each containing:
            - endpoint_name: name of endpoint (if not labeled, infer concise name)
            - endpoint_definition: full description of endpoint
            - measurement_method: how it is measured (e.g., "EDSS score", "MRI lesion count")
            - timepoint: time of assessment (e.g., "Week 24", "Baseline to Week 52")
            - endpoint_type: "Primary" | "Secondary" | "Tertiary" | "Exploratory"

        Always output **only valid JSON** in this exact format:
        {{
        "objectives": [
            {{
            "objective_type": "Primary",
            "objective_text": "...",
            "endpoints": [
                {{
                "endpoint_name": "...",
                "endpoint_definition": "...",
                "measurement_method": "...",
                "timepoint": "...",
                "endpoint_type": "Primary"
                }}
            ]
            }}
        ]
        }}
If you cannot find clear objectives, return an empty list: {{"objectives": []}}.
"""


        response = self.client.messages.create(
            model=self.model_id,
            max_tokens=4000,
            temperature=0,
            system="You are a clinical research data extraction expert. Return only valid JSON.",
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text if response.content else ""

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        return {"objectives": []}
