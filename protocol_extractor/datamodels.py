from dataclasses import dataclass
from typing import List


@dataclass
class Endpoint:
    endpoint_name: str
    endpoint_definition: str
    measurement_method: str
    timepoint: str
    endpoint_type: str 


@dataclass
class Objective:
    objective_type: str 
    objective_text: str
    endpoints: List[Endpoint]


@dataclass
class ProtocolData:
    protocol_id: str
    protocol_title: str
    short_title: str
    study_phase: str
    protocol_version: str
    protocol_date: str
    study_type: str
    population: str
    intervention: str
    comparator: str
    objectives: List[Objective]