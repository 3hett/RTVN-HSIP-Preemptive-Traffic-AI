"""
===============================================================================
PROJECT: RTVN & HSIP — Real-Time Violation Notification & High-Speed Interception
ARCHITECTURE: 3-Node Preemptive Enforcement & Virtual Corridor Simulation Engine
COPYRIGHT: (c) 2026 Het Prajapati. All Rights Reserved.
AUTHOR: Het Prajapati — System Architecture, Civil Engineering Modeling & AI Engine
LICENSE: MIT License
===============================================================================
"""

import argparse
import hashlib
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np

# Optional OpenCV import so the simulation runs even on minimal environments
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


@dataclass
class CorridorGeometryConfig:
    """
    Defines the 3-Node spacing geometry:
      - URBAN_500M: Node 1 -> Node 2 = 500 m | Node 2 -> Node 3 = 500 m (Total: 1,000 m)
      - HIGHWAY_1KM: Node 1 -> Node 2 = 1,000 m | Node 2 -> Node 3 = 1,000 m (Total: 2,000 m)
    """
    corridor_mode: str = "URBAN_500M"
    node1_to_node2_m: float = 500.0
    node2_to_node3_m: float = 500.0
    irc35_dash_length_m: float = 3.0
    irc35_gap_length_m: float = 4.5

    def set_mode(self, mode: str) -> None:
        if mode == "HIGHWAY_1KM":
            self.corridor_mode = "HIGHWAY_1KM"
            self.node1_to_node2_m = 1000.0
            self.node2_to_node3_m = 1000.0
        else:
            self.corridor_mode = "URBAN_500M"
            self.node1_to_node2_m = 500.0
            self.node2_to_node3_m = 500.0


@dataclass
class WeatherPhysicsConfig:
    """
    Implements Indian Roads Congress (IRC:73) Stopping Sight Distance (SSD)
    equation: SSD = 0.278 * v * t_r + (v^2) / (254 * f)
    """
    surface_condition: str = "DRY_ASPHALT"
    friction_coeff_f: float = 0.35
    reaction_time_tr: float = 2.5
    base_speed_limit_kmh: float = 60.0

    def calculate_ssd_meters(self, speed_kmh: float) -> float:
        lag_dist = 0.278 * speed_kmh * self.reaction_time_tr
        braking_dist = (speed_kmh ** 2) / (254.0 * self.friction_coeff_f)
        return round(lag_dist + braking_dist, 2)

    @property
    def enforced_speed_limit_kmh(self) -> float:
        if self.friction_coeff_f <= 0.20:
            return 42.0
        return self.base_speed_limit_kmh


@dataclass
class ThreeNodeViolationRecord:
    """
    Stores the complete 3-Node trajectory, real-time notifications,
    Node 3 Human Officer Confirmation decision, and BSA 2023 Section 63 SHA-256 hash.
    """
    case_id: str
    track_id: int
    plate_number: str
    vehicle_class: str
    corridor_mode: str
    node_spacing_m: float
    weather_surface: str
    irc73_friction_f: float
    enforced_limit_kmh: float
    node_01_speed_kmh: float
    node_02_speed_kmh: float
    sdlp_lateral_weave_m: float
    ttc_seconds: float
    drac_ms2: float
    irc73_ssd_required_m: float
    escalation_level: int
    node_01_realtime_voice_alert: str
    node_01_detailed_notice: str
    node_02_rectification_status: str
    node_02_realtime_voice_alert: str
    node_02_detailed_notice: str
    requires_node_03_human_confirmation: bool
    node_03_officer_decision: str
    node_03_signal_state: str
    patrol_dispatch_status: str
    fine_amount_inr: int
    demerit_points: int
    bsa_2023_sec63_sha256: str
    timestamp_ist: str


class RTVNHSIPThreeNodeEngine:
    """
    Core 3-Node Preemptive Enforcement Engine architected by Het Prajapati:
      - Node 1: Automated violation detection + immediate real-time notification to violator.
      - Node 2: Automated rectification check (Rs. 0 fine notification sent immediately if rectified).
      - Node 3: Human Officer Confirmation Gate for unrectified violations before Level 2 / Level 3 execution.
    """

    def __init__(self) -> None:
        self.corridor = CorridorGeometryConfig()
        self.weather = WeatherPhysicsConfig()
        self.records: Dict[int, ThreeNodeViolationRecord] = {}

    @staticmethod
    def compute_sdlp(lateral_offsets_m: List[float]) -> float:
        if len(lateral_offsets_m) < 2:
            return 0.0
        return round(float(np.std(lateral_offsets_m)), 3)

    @staticmethod
    def compute_ssm(v_follower_kmh: float, v_leader_kmh: float, gap_m: float) -> Tuple[float, float]:
        vf = v_follower_kmh / 3.6
        vl = v_leader_kmh / 3.6
        rel_v = vf - vl
        if rel_v <= 0.1 or gap_m <= 0.5:
            return 9.9, 0.2
        ttc = round(gap_m / rel_v, 2)
        drac = round((rel_v ** 2) / (2.0 * gap_m), 2)
        return min(ttc, 9.9), min(drac, 15.0)

    @staticmethod
    def generate_bsa_hash(payload: dict) -> str:
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def simulate_three_node_case(
        self,
        track_id: int,
        plate: str,
        vehicle_class: str,
        node1_speed_kmh: float,
        node2_speed_kmh: float,
        lateral_offsets_m: List[float],
        officer_decision_at_node3: str = "AUTO_CLOSED_AT_NODE_2"
    ) -> ThreeNodeViolationRecord:
        limit = self.weather.enforced_speed_limit_kmh
        sdlp = self.compute_sdlp(lateral_offsets_m)
        ttc, drac = self.compute_ssm(node1_speed_kmh, 50.0, 22.0)
        ssd = self.weather.calculate_ssd_meters(node1_speed_kmh)
        spacing_m = self.corridor.node1_to_node2_m
        now_ist = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        case_id = f"HET-2027-{track_id:04d}"

        # Node 1 Real-Time Notification to Violator
        n1_voice = (
            f"Attention driver of vehicle {plate}. Violation detected at Camera Node 1 at "
            f"{node1_speed_kmh:.0f} kilometers per hour. Enforced limit is {limit:.0f}. "
            f"Decelerate before Camera Node 2, {spacing_m:.0f} meters ahead, to qualify for zero fine."
        )
        n1_notice = (
            f"[NODE 1 REAL-TIME VIOLATION ALERT] Case: {case_id} | Vehicle: {plate} | "
            f"Speed: {node1_speed_kmh:.1f} km/h (Limit: {limit:.0f} km/h) | SDLP: {sdlp:.2f} m | "
            f"Action: Rectify speed before Node 2 ({spacing_m:.0f} m ahead) for Rs. 0 fine."
        )

        # Evaluate Node 2 Rectification vs Escalation to Node 3 Human Officer Gate
        if node2_speed_kmh <= limit and sdlp < 0.28:
            # Self-Rectified at Node 2 -> Immediate Rectification Notification Sent!
            level = 1
            n2_status = "SELF_RECTIFIED_AT_NODE_2"
            n2_voice = (
                f"Compliance confirmed for vehicle {plate} at Camera Node 2. Speed reduced to "
                f"{node2_speed_kmh:.0f} kilometers per hour. Violation rectified with zero rupee fine."
            )
            n2_notice = (
                f"[NODE 2 REAL-TIME RECTIFICATION CONFIRMATION] Case: {case_id} | Vehicle: {plate} | "
                f"Node 1: {node1_speed_kmh:.1f} km/h -> Node 2: {node2_speed_kmh:.1f} km/h | "
                f"Status: Complied within {spacing_m:.0f} m corridor. Fine: Rs. 0 (Closed Automatically)."
            )
            req_human = False
            n3_decision = "NOT_REQUIRED (RECTIFIED_AT_NODE_2)"
            n3_signal = "GREEN (NORMAL)"
            patrol_status = "STANDBY"
            fine_inr = 0
            points = 0
        else:
            # Unrectified at Node 2 -> Forwarded to Node 3 for Mandatory Human Officer Confirmation
            n2_status = "UNRECTIFIED_AT_NODE_2_ESCALATED_TO_NODE_3"
            n2_voice = (
                f"Warning ignored by vehicle {plate} at Camera Node 2, recorded at "
                f"{node2_speed_kmh:.0f} kilometers per hour. Case forwarded to Camera Node 3 "
                "for human officer enforcement confirmation."
            )
            n2_notice = (
                f"[NODE 2 NON-COMPLIANCE ESCALATION] Case: {case_id} | Vehicle: {plate} | "
                f"Node 1: {node1_speed_kmh:.1f} km/h -> Node 2: {node2_speed_kmh:.1f} km/h | "
                f"Status: Paused at Node 3 ({spacing_m:.0f} m ahead) awaiting Human Officer Confirmation."
            )
            req_human = True

            if officer_decision_at_node3 == "CONFIRM_LEVEL_3_HSIP":
                level = 3
                n3_decision = "OFFICER_CONFIRMED_LEVEL_3_HSIP"
                n3_signal = "PREEMPTED_TO_RED (TRAFFIC_BUFFER_ACTIVE)"
                patrol_status = "DISPATCHED_INTERCEPTOR_UNIT_TO_NODE_3"
                fine_inr = 10000
                points = 6
            elif officer_decision_at_node3 == "DISMISS":
                level = 0
                n3_decision = "OFFICER_DISMISSED_AT_NODE_3"
                n3_signal = "GREEN (NORMAL)"
                patrol_status = "STANDBY"
                fine_inr = 0
                points = 0
            else:
                level = 2
                n3_decision = "OFFICER_CONFIRMED_LEVEL_2_CHALLAN"
                n3_signal = "GREEN (NORMAL)"
                patrol_status = "CHALLAN_AND_POINTS_LOCKED"
                fine_inr = 2000
                points = 3

        hash_payload = {
            "case_id": case_id,
            "plate": plate,
            "v1": node1_speed_kmh,
            "v2": node2_speed_kmh,
            "sdlp": sdlp,
            "level": level,
            "node3_decision": n3_decision,
            "timestamp": now_ist
        }
        bsa_hash = self.generate_bsa_hash(hash_payload)

        rec = ThreeNodeViolationRecord(
            case_id=case_id,
            track_id=track_id,
            plate_number=plate,
            vehicle_class=vehicle_class,
            corridor_mode=self.corridor.corridor_mode,
            node_spacing_m=spacing_m,
            weather_surface=self.weather.surface_condition,
            irc73_friction_f=self.weather.friction_coeff_f,
            enforced_limit_kmh=limit,
            node_01_speed_kmh=node1_speed_kmh,
            node_02_speed_kmh=node2_speed_kmh,
            sdlp_lateral_weave_m=sdlp,
            ttc_seconds=ttc,
            drac_ms2=drac,
            irc73_ssd_required_m=ssd,
            escalation_level=level,
            node_01_realtime_voice_alert=n1_voice,
            node_01_detailed_notice=n1_notice,
            node_02_rectification_status=n2_status,
            node_02_realtime_voice_alert=n2_voice,
            node_02_detailed_notice=n2_notice,
            requires_node_03_human_confirmation=req_human,
            node_03_officer_decision=n3_decision,
            node_03_signal_state=n3_signal,
            patrol_dispatch_status=patrol_status,
            fine_amount_inr=fine_inr,
            demerit_points=points,
            bsa_2023_sec63_sha256=bsa_hash,
            timestamp_ist=now_ist
        )
        self.records[track_id] = rec
        return rec


def run_virtual_simulation_suite() -> dict:
    print("=" * 84)
    print("RTVN & HSIP — 3-NODE VIRTUAL CORRIDOR SIMULATION SUITE")
    print("System Architecture & Engineering by Het Prajapati ((c) 2026 Het Prajapati)")
    print("=" * 84)

    engine = RTVNHSIPThreeNodeEngine()

    # Scenario 1: Urban Corridor (500m spacing), Level 1 Self-Rectification at Node 2
    engine.corridor.set_mode("URBAN_500M")
    engine.weather.surface_condition = "DRY_ASPHALT"
    engine.weather.friction_coeff_f = 0.35
    c1 = engine.simulate_three_node_case(
        101, "GJ-01-HX-4821", "Sedan", 76.4, 52.0, [1.80, 1.85, 1.82],
        officer_decision_at_node3="AUTO_CLOSED_AT_NODE_2"
    )
    print(f"[SCENARIO 1 | {c1.corridor_mode} ({c1.node_spacing_m:.0f}m)] {c1.plate_number}:")
    print(f"  -> Node 1: {c1.node_01_speed_kmh} km/h (Real-Time Alert Dispatched)")
    print(f"  -> Node 2: {c1.node_02_speed_kmh} km/h ({c1.node_02_rectification_status} -> Rs. {c1.fine_amount_inr} Fine)")
    print(f"  -> BSA Sec. 63 SHA-256: {c1.bsa_2023_sec63_sha256[:32]}...\n")

    # Scenario 2: Urban Corridor (500m spacing), Persistent Violator -> Node 3 Officer Confirms Level 2
    c2 = engine.simulate_three_node_case(
        102, "GJ-01-KP-9012", "SUV", 78.5, 84.2, [2.10, 2.28, 2.02],
        officer_decision_at_node3="CONFIRM_LEVEL_2_CHALLAN"
    )
    print(f"[SCENARIO 2 | {c2.corridor_mode} ({c2.node_spacing_m:.0f}m)] {c2.plate_number}:")
    print(f"  -> Node 1: {c2.node_01_speed_kmh} km/h -> Node 2: {c2.node_02_speed_kmh} km/h (Ignored Warning)")
    print(f"  -> Node 3 Human Gate: {c2.node_03_officer_decision} -> Rs. {c2.fine_amount_inr} Fine + {c2.demerit_points} Pts")
    print(f"  -> BSA Sec. 63 SHA-256: {c2.bsa_2023_sec63_sha256[:32]}...\n")

    # Scenario 3: High-Speed Highway (1,000m / 1km spacing) + Monsoon Wet Physics + Level 3 HSIP at Node 3
    engine.corridor.set_mode("HIGHWAY_1KM")
    engine.weather.surface_condition = "MONSOON_WET_PAVEMENT"
    engine.weather.friction_coeff_f = 0.18
    c3 = engine.simulate_three_node_case(
        103, "GJ-27-TC-7740", "Hatchback", 108.0, 111.5, [1.10, 2.35, 0.85, 2.48],
        officer_decision_at_node3="CONFIRM_LEVEL_3_HSIP"
    )
    print(f"[SCENARIO 3 | {c3.corridor_mode} ({c3.node_spacing_m:.0f}m) | Monsoon Limit {c3.enforced_limit_kmh:.0f} km/h] {c3.plate_number}:")
    print(f"  -> Node 1: {c3.node_01_speed_kmh} km/h -> Node 2: {c3.node_02_speed_kmh} km/h (SDLP Weave: {c3.sdlp_lateral_weave_m}m)")
    print(f"  -> Node 3 Human Gate: {c3.node_03_officer_decision} | Signal: {c3.node_03_signal_state}")
    print(f"  -> BSA Sec. 63 SHA-256: {c3.bsa_2023_sec63_sha256[:32]}...")
    print("=" * 84)

    dataset = {
        "project_metadata": {
            "system_name": "RTVN & HSIP — Real-Time Violation Notification & High-Speed Interception System",
            "architect_and_copyright": "(c) 2026 Het Prajapati. All Rights Reserved. System Architecture & Engineering by Het Prajapati.",
            "architecture_topology": "3-Node Preemptive Corridor (Node 1 Auto Alert -> Node 2 Auto Rectification Check -> Node 3 Human Officer Confirmation Gate)",
            "supported_corridor_geometries": {
                "urban_road_spacing_m": 500.0,
                "high_speed_highway_spacing_m": 1000.0
            },
            "civil_engineering_standards": [
                "IRC:35 Road Marking Perspective Homography (3.0m dash + 4.5m gap)",
                "IRC:73 Stopping Sight Distance (SSD) Weather-Adaptive Physics",
                "Surrogate Safety Measures (TTC, DRAC, SDLP Lateral Weave)",
                "Bharatiya Sakshya Adhiniyam (BSA) 2023 Section 63 SHA-256 Evidence Hashing"
            ]
        },
        "verified_simulation_telemetry_logs": [asdict(c1), asdict(c2), asdict(c3)]
    }

    os.makedirs("sample_data", exist_ok=True)
    out_path = os.path.join("sample_data", "corridor_telemetry_logs.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    print(f"Exported verified sample telemetry dataset to: {out_path}")
    return dataset


if __name__ == "__main__":
    run_virtual_simulation_suite()
