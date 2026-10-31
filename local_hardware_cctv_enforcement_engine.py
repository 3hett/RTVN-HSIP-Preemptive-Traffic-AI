"""
===============================================================================
PROJECT: Preemptive AI-Based Urban Traffic Policy Enforcement (RTVN & HSIP)
COMPETITION: Viksit Bharat Young Leaders Dialogue (VBYLD) 2027
COPYRIGHT: (c) 2026 Het Prajapati. All Rights Reserved. 
           System Architecture, Civil Engineering Modeling & Engineering by Het Prajapati.
           Research assistance by Dhruv Thumar.
LICENSE: MIT License
===============================================================================
"""

import argparse
import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
    DEVICE_NAME = torch.cuda.get_device_name(0) if CUDA_AVAILABLE else "CPU Ready"
except ImportError:
    CUDA_AVAILABLE = False
    DEVICE_NAME = "CPU (OpenCV Accelerated)"

@dataclass
class CorridorConfig:
    corridor_type: str = "URBAN_500M"
    node1_to_node2_m: float = 500.0
    node2_to_node3_m: float = 500.0

    def set_corridor_type(self, c_type: str):
        if c_type == "HIGHWAY_1KM":
            self.corridor_type = "HIGHWAY_1KM"
            self.node1_to_node2_m = 1000.0
            self.node2_to_node3_m = 1000.0
        else:
            self.corridor_type = "URBAN_500M"
            self.node1_to_node2_m = 500.0
            self.node2_to_node3_m = 500.0

@dataclass
class WeatherPhysicsConfig:
    condition_name: str = "DRY_ASPHALT"
    friction_coeff_f: float = 0.35
    reaction_time_tr: float = 2.5
    base_speed_limit_kmh: float = 60.0

    @property
    def dynamic_speed_limit_kmh(self) -> float:
        if self.friction_coeff_f <= 0.20:
            return 42.0
        return self.base_speed_limit_kmh

@dataclass
class ThreeNodeCaseRecord:
    case_id: str
    track_id: int
    plate_number: str
    vehicle_type: str
    node_01_speed_kmh: float = 0.0
    node_02_speed_kmh: Optional[float] = None
    sdlp_weave_m: float = 0.0
    escalation_level: int = 0
    violation_category: str = "NONE"
    violator_voice_script: str = ""
    violator_detailed_sms: str = ""
    admin_enforcement_action: str = "MONITORING"
    bsa_section63_sha256: str = ""
    timestamp_ist: str = ""
    requires_human_confirmation: bool = False
    human_officer_decision: str = "PENDING"
    fine_inr: int = 0
    demerit_points: int = 0

class RTVNHSIPEngine:
    def __init__(self):
        self.weather = WeatherPhysicsConfig()
        self.corridor = CorridorConfig()
        self.active_records: Dict[int, ThreeNodeCaseRecord] = {}

    @staticmethod
    def compute_sdlp(lateral_positions_m: List[float]) -> float:
        if len(lateral_positions_m) < 2: return 0.0
        return round(float(np.std(lateral_positions_m)), 3)

    @staticmethod
    def generate_bsa_hash(rec: ThreeNodeCaseRecord) -> str:
        payload = {
            "case_id": rec.case_id,
            "plate": rec.plate_number,
            "v1": rec.node_01_speed_kmh,
            "v2": rec.node_02_speed_kmh,
            "level": rec.escalation_level,
            "ts": rec.timestamp_ist
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def process_node_01(
        self, track_id: int, plate: str, v_type: str, speed_kmh: float, lat_x: List[float]
    ) -> ThreeNodeCaseRecord:
        limit = self.weather.dynamic_speed_limit_kmh
        sdlp = self.compute_sdlp(lat_x)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")

        rec = ThreeNodeCaseRecord(
            case_id=f"HET-2027-{track_id:04d}",
            track_id=track_id, plate_number=plate, vehicle_type=v_type,
            node_01_speed_kmh=round(speed_kmh, 1), sdlp_weave_m=sdlp, timestamp_ist=ts
        )

        if speed_kmh > limit or sdlp >= 0.28:
            rec.escalation_level = 1
            rec.violation_category = f"Over-Speeding ({speed_kmh:.1f} in {limit:.0f} zone)" if speed_kmh > limit else f"Lane Weaving (SDLP {sdlp:.2f}m)"
            rec.admin_enforcement_action = "NODE 1: Initial Violation Detected. RTVN Alert Sent."
            rec.violator_voice_script = f"Warning driver of {plate}. Speed {speed_kmh:.0f} km/h detected. Slow down before Node 2 to avoid challan."
            rec.violator_detailed_sms = f"[RTVN ALERT] {plate} | {rec.violation_category} | Rectify before Node 2 ({self.corridor.node1_to_node2_m}m ahead)."
        else:
            rec.escalation_level = 0
            rec.violation_category = "COMPLIANT"
            rec.admin_enforcement_action = "COMPLIANT @ NODE 1"

        self.active_records[track_id] = rec
        return rec

    def process_node_02(self, track_id: int, speed_kmh: float, sdlp: float = 0.1) -> ThreeNodeCaseRecord:
        rec = self.active_records[track_id]
        rec.node_02_speed_kmh = round(speed_kmh, 1)
        limit = self.weather.dynamic_speed_limit_kmh

        if speed_kmh <= limit and sdlp < 0.25:
            rec.escalation_level = 1
            rec.admin_enforcement_action = "NODE 2: Self-Rectified. Rs. 0 Fine."
            rec.violator_voice_script = f"Thank you driver of {rec.plate_number}. Speed reduced to {speed_kmh:.0f} km/h. Zero fine issued."
            rec.violator_detailed_sms = f"[RTVN COMPLIANCE] {rec.plate_number} | Rectified | Penalty Waived (Rs. 0)."
            rec.bsa_section63_sha256 = self.generate_bsa_hash(rec)
        else:
            rec.escalation_level = 2
            rec.requires_human_confirmation = True
            rec.admin_enforcement_action = f"NODE 2: Warning Ignored ({speed_kmh:.1f} km/h). Paused for Node 3 Human Confirmation."
            rec.violator_voice_script = f"Driver of {rec.plate_number}. Warning ignored. Escalating case to Node 3 Human Officer."
            rec.violator_detailed_sms = f"[RTVN ESCALATION] {rec.plate_number} | Ignored Warning | Pending Officer Review at Node 3 ({self.corridor.node2_to_node3_m}m ahead)."
            rec.bsa_section63_sha256 = self.generate_bsa_hash(rec)

        return rec

    def process_node_03_human_confirmation(self, track_id: int, decision: str) -> ThreeNodeCaseRecord:
        rec = self.active_records[track_id]
        rec.human_officer_decision = decision
        rec.requires_human_confirmation = False

        if decision == "LEVEL_2":
            rec.fine_inr = 2000
            rec.demerit_points = 3
            rec.admin_enforcement_action = "NODE 3 OFFICER CONFIRMED: Level 2 e-Challan + 3 Pts Issued."
        elif decision == "LEVEL_3_HSIP":
            rec.escalation_level = 3
            rec.admin_enforcement_action = "NODE 3 OFFICER CONFIRMED: Level 3 HSIP. Signal Preempted RED. Patrol Dispatched."
        elif decision == "DISMISS":
            rec.escalation_level = 0
            rec.admin_enforcement_action = "NODE 3 OFFICER DISMISSED: False Positive."

        rec.bsa_section63_sha256 = self.generate_bsa_hash(rec)
        return rec


def run_live_webcam():
    print("\nStarting live webcam view... Press 'q' in the video window to quit.")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open the webcam.")
        return

    # Basic setup to mimic what you built in the HTML for local python testing
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        h, w, _ = frame.shape
        node1_x = int(w * 0.3)
        node2_x = int(w * 0.7)
        
        cv2.line(frame, (node1_x, 0), (node1_x, h), (255, 255, 0), 2)
        cv2.putText(frame, "NODE 1", (node1_x - 70, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        cv2.line(frame, (node2_x, 0), (node2_x, h), (0, 165, 255), 2)
        cv2.putText(frame, "NODE 2", (node2_x + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        cv2.putText(frame, "Het Prajapati - CV Engine Ready", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow('RTVN Live Testing (Press Q to quit)', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RTVN & HSIP By Het Prajapati")
    parser.add_argument("--mode", choices=["test", "live"], default="test", help="'test' for logic, 'live' for webcam")
    args = parser.parse_args()
    
    if args.mode == 'live':
        run_live_webcam()
    else:
        print("================================================================================")
        print("RTVN & HSIP — 3-NODE AUTOMATED DIAGNOSTIC SUITE (© 2026 Het Prajapati)")
        print("================================================================================")
        engine = RTVNHSIPEngine()
        
        c1 = engine.process_node_01(1, "GJ-01-HX-4821", "Car", 74.0, [1.80, 1.84, 1.82])
        c1 = engine.process_node_02(1, 54.0)
        print(f"CASE 1 (Self-Correction): {c1.admin_enforcement_action}")

        c2 = engine.process_node_01(2, "GJ-04-BB-9999", "Car", 85.0, [1.80])
        c2 = engine.process_node_02(2, 80.0)
        print(f"CASE 2 (Ignored Warning): {c2.admin_enforcement_action}")
        c2 = engine.process_node_03_human_confirmation(2, "LEVEL_2")
        print(f"CASE 2 (Node 3 Officer Action): {c2.admin_enforcement_action}")
