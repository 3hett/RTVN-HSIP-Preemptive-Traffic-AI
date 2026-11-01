"""
===============================================================================
PROJECT: RTVN & HSIP — Preemptive AI Traffic Policy Enforcement & Telemetry Engine
ARCHITECTURE: 3-Node Preemptive Corridor, IRC:35 Homography & IRC:73 Physics
COPYRIGHT: (c) 2026 Het Prajapati. All Rights Reserved.
AUTHOR: Het Prajapati — System Architecture, Civil Engineering Modeling & AI Engine
LICENSE: MIT License
===============================================================================
"""

import argparse
import hashlib
import json
import logging
import math
import os
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

import cv2
import numpy as np

# Optional Deep Learning (YOLOv8) & FastAPI WebSocket dependencies with safe fallback
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("RTVN_HSIP_Engine")


# =====================================================================
# 1. CIVIL ENGINEERING & PHYSICS CALIBRATION (IRC:35 & IRC:73)
# =====================================================================

class IRCPhysicsEngine:
    """
    Implements IRC:35 Perspective Homography (3.0m dash + 4.5m gap)
    and IRC:73 Stopping Sight Distance (SSD) weather-adaptive braking physics.
    """
    def __init__(self, weather_mode: str = "DRY"):
        self.reaction_time_s = 2.5  # IRC:73 standard reaction time (t_r = 2.5s)
        self.homography_matrix = self._calibrate_irc35_homography()
        self.set_weather_mode(weather_mode)

    def _calibrate_irc35_homography(self) -> np.ndarray:
        """
        Maps 4 perspective CCTV pixel coordinates to a flat top-down metric plane:
        - Standard 2-lane urban carriageway width: 7.0 meters
        - 4 consecutive IRC:35 cycles (3.0m dash + 4.5m gap = 7.5m): 30.0 meters
        """
        src_pixels = np.float32([
            [420, 220],   # Top-Left (Far left lane edge)
            [860, 220],   # Top-Right (Far right lane edge)
            [1180, 680],  # Bottom-Right (Near right lane edge)
            [100, 680]    # Bottom-Left (Near left lane edge)
        ])
        dst_meters = np.float32([
            [0.0, 0.0],
            [7.0, 0.0],
            [7.0, 30.0],
            [0.0, 30.0]
        ])
        return cv2.getPerspectiveTransform(src_pixels, dst_meters)

    def pixel_to_ground_meters(self, px_x: float, px_y: float) -> Tuple[float, float]:
        """
        Transforms the tire-asphalt contact point (bottom-center of bounding box)
        into real-world ground-plane coordinates (X_meters, Y_meters).
        """
        pt = np.array([[[px_x, px_y]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(pt, self.homography_matrix)
        return float(transformed[0][0][0]), float(transformed[0][0][1])

    def set_weather_mode(self, mode: str) -> None:
        self.weather_mode = mode.upper()
        if self.weather_mode == "MONSOON":
            self.friction_f = 0.18
            self.enforced_speed_limit_kmh = 42.0
        else:
            self.friction_f = 0.35
            self.enforced_speed_limit_kmh = 60.0

    def compute_irc73_ssd(self, velocity_kmh: float, gradient_pct: float = 0.0) -> float:
        """SSD = 0.278 * v * t_r + (v^2) / (254 * (f +/- 0.01 * S))"""
        v = max(0.0, velocity_kmh)
        lag_distance = 0.278 * v * self.reaction_time_s
        effective_f = max(0.05, self.friction_f + (0.01 * gradient_pct))
        braking_distance = (v ** 2) / (254.0 * effective_f)
        return round(lag_distance + braking_distance, 2)

    @staticmethod
    def compute_sdlp(lateral_x_history_m: List[float]) -> float:
        """Standard Deviation of Lateral Position (SDLP) in meters for DUI weave detection."""
        if len(lateral_x_history_m) < 2:
            return 0.0
        return round(float(np.std(lateral_x_history_m, ddof=1)), 3)

    @staticmethod
    def compute_surrogate_safety(
        v_following_kmh: float,
        v_lead_kmh: float,
        gap_meters: float
    ) -> Tuple[float, float]:
        """Computes Time-to-Collision (TTC) and Deceleration Rate to Avoid a Crash (DRAC)."""
        v_fol_ms = v_following_kmh / 3.6
        v_lead_ms = v_lead_kmh / 3.6
        effective_gap = max(0.5, gap_meters)

        if v_fol_ms <= v_lead_ms:
            return 99.9, 0.0

        rel_v = v_fol_ms - v_lead_ms
        ttc = round(effective_gap / rel_v, 2)
        drac = round((rel_v ** 2) / (2.0 * effective_gap), 2)
        return ttc, drac


# =====================================================================
# 2. BSA 2023 SECTION 63 CRYPTOGRAPHIC EVIDENCE LEDGER
# =====================================================================

def generate_bsa_section63_hash(payload: Dict) -> str:
    """Generates an immutable SHA-256 hash under Section 63 of the Bharatiya Sakshya Adhiniyam 2023."""
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


# =====================================================================
# 3. 3-NODE PREEMPTIVE ESCALATION STATE MACHINE
# =====================================================================

@dataclass
class CorridorCaseRecord:
    case_id: str
    plate_number: str
    corridor_type: str
    node_spacing_m: int
    weather_mode: str
    speed_limit_kmh: float
    node1_speed_kmh: float
    node2_speed_kmh: float
    sdlp_meters: float
    ttc_seconds: float
    drac_ms2: float
    irc73_ssd_meters: float
    node1_action: str
    node2_status: str
    node3_officer_decision: str
    fine_inr: int
    morth_demerit_points: int
    signal_preemption_state: str
    timestamp_utc: str
    bsa_sec63_sha256: str = ""


class ThreeNodeEnforcementEngine:
    def __init__(self, physics: IRCPhysicsEngine):
        self.physics = physics
        self.ledger: List[CorridorCaseRecord] = []

    def evaluate_corridor_traversal(
        self,
        case_id: str,
        plate: str,
        corridor_type: str,
        node1_speed: float,
        node2_speed: float,
        lateral_positions_m: List[float],
        lead_vehicle_speed_kmh: float = 50.0,
        lead_vehicle_gap_m: float = 18.0,
        officer_action_at_node3: str = "AUTO"
    ) -> CorridorCaseRecord:
        spacing = 1000 if corridor_type == "HIGHWAY_1KM" else 500
        limit = self.physics.enforced_speed_limit_kmh
        sdlp = self.physics.compute_sdlp(lateral_positions_m)
        ttc, drac = self.physics.compute_surrogate_safety(
            node2_speed, lead_vehicle_speed_kmh, lead_vehicle_gap_m
        )
        ssd = self.physics.compute_irc73_ssd(node2_speed)

        if node1_speed > limit or sdlp >= 0.45:
            node1_action = "RTVN_VOICE_TTS_AND_WRITTEN_NOTICE_DISPATCHED"
        else:
            node1_action = "COMPLIANT_AT_NODE_1"

        is_extreme_hazard = (node2_speed >= 90.0) or (sdlp >= 0.45) or (ttc < 1.5)

        if node2_speed <= limit and sdlp < 0.45:
            node2_status = "SELF_RECTIFIED_AT_NODE_2"
            node3_decision = "AUTO_CLOSED_LEVEL_1_COMPLIED"
            fine = 0
            points = 0
            signal_state = "NORMAL_GREEN_WAVE"
        else:
            node2_status = "WARNING_IGNORED_ESCALATED_TO_NODE_3"
            if officer_action_at_node3 == "DISMISS":
                node3_decision = "OFFICER_DISMISSED_EXEMPT_VEHICLE"
                fine = 0
                points = 0
                signal_state = "NORMAL_GREEN_WAVE"
            elif is_extreme_hazard or officer_action_at_node3 == "CONFIRM_LEVEL_3":
                node3_decision = "OFFICER_CONFIRMED_LEVEL_3_HSIP"
                fine = 5000
                points = 6
                signal_state = "PREEMPTED_TO_RED (TRAFFIC_BUFFER_ACTIVE)"
            else:
                node3_decision = "OFFICER_CONFIRMED_LEVEL_2_CHALLAN"
                fine = 2000
                points = 3
                signal_state = "NORMAL_GREEN_WAVE"

        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        record = CorridorCaseRecord(
            case_id=case_id,
            plate_number=plate,
            corridor_type=corridor_type,
            node_spacing_m=spacing,
            weather_mode=self.physics.weather_mode,
            speed_limit_kmh=limit,
            node1_speed_kmh=round(node1_speed, 1),
            node2_speed_kmh=round(node2_speed, 1),
            sdlp_meters=sdlp,
            ttc_seconds=ttc,
            drac_ms2=drac,
            irc73_ssd_meters=ssd,
            node1_action=node1_action,
            node2_status=node2_status,
            node3_officer_decision=node3_decision,
            fine_inr=fine,
            morth_demerit_points=points,
            signal_preemption_state=signal_state,
            timestamp_utc=ts
        )

        hash_dict = asdict(record)
        hash_dict.pop("bsa_sec63_sha256", None)
        record.bsa_sec63_sha256 = generate_bsa_section63_hash(hash_dict)

        self.ledger.append(record)
        return record


# =====================================================================
# 4. LIVE YOLOv8 + BYTETRACK + IRC:35 HOMOGRAPHY CAMERA TRACKER
# =====================================================================

def run_live_cv_tracker(video_source: str = "0", weather: str = "DRY") -> None:
    physics = IRCPhysicsEngine(weather_mode=weather)
    src = 0 if video_source == "0" else video_source
    cap = cv2.VideoCapture(src)

    if not cap.isOpened():
        logger.error(f"Could not open video source '{video_source}'.")
        return

    model = None
    if YOLO_AVAILABLE:
        logger.info("Loading YOLOv8n + ByteTrack for vehicle detection...")
        model = YOLO("yolov8n.pt")
    else:
        logger.warning("Ultralytics YOLOv8 not found; using OpenCV motion contours with IRC:35 homography.")
        bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=40)

    track_history: Dict[int, List[Tuple[float, float, float]]] = {}
    logger.info("Live CV Stream started. Press [W] for Monsoon, [D] for Dry, [Q] to Quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (1280, 720))
        now = time.time()
        detections: List[Tuple[int, int, int, int, int]] = []

        if YOLO_AVAILABLE and model is not None:
            results = model.track(frame, persist=True, classes=[2, 3, 5, 7], verbose=False)
            if results and results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                ids = results[0].boxes.id.cpu().numpy().astype(int)
                for box, track_id in zip(boxes, ids):
                    detections.append((int(track_id), box[0], box[1], box[2], box[3]))
        else:
            fg_mask = bg_subtractor.apply(frame)
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for idx, cnt in enumerate(contours):
                if cv2.contourArea(cnt) > 1800:
                    x, y, w, h = cv2.boundingRect(cnt)
                    detections.append((idx + 1, x, y, x + w, y + h))

        for track_id, x1, y1, x2, y2 in detections:
            # Tire-road contact point (bottom-center pixel) eliminates 3D parallax error
            tire_px_x = (x1 + x2) / 2.0
            tire_px_y = float(y2)
            xm, ym = physics.pixel_to_ground_meters(tire_px_x, tire_px_y)

            if track_id not in track_history:
                track_history[track_id] = []
            track_history[track_id].append((now, xm, ym))
            if len(track_history[track_id]) > 15:
                track_history[track_id].pop(0)

            speed_kmh = 0.0
            sdlp_m = 0.0
            hist = track_history[track_id]
            if len(hist) >= 3:
                dt = hist[-1][0] - hist[0][0]
                if dt > 0.05:
                    dist_m = math.hypot(hist[-1][1] - hist[0][1], hist[-1][2] - hist[0][2])
                    speed_kmh = round(min(max((dist_m / dt) * 3.6, 0.0), 160.0), 1)
                    sdlp_m = physics.compute_sdlp([pt[1] for pt in hist])

            limit = physics.enforced_speed_limit_kmh
            if speed_kmh >= 90.0 or sdlp_m >= 0.45:
                color, status = (0, 0, 255), "L3 HSIP INTERCEPT"
            elif speed_kmh > limit:
                color, status = (0, 165, 255), "RTVN SPEED ALERT"
            else:
                color, status = (0, 220, 0), "COMPLIANT"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"ID:{track_id} | {speed_kmh} km/h | SDLP:{sdlp_m:.2f}m | {status}"
            cv2.putText(frame, label, (x1, max(25, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        hud = f"IRC:73 Mode: {physics.weather_mode} (f={physics.friction_f}) | Enforced Limit: {physics.enforced_speed_limit_kmh} km/h"
        cv2.putText(frame, hud, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        cv2.imshow("RTVN & HSIP Live Homography CV Engine — Het Prajapati", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("w"):
            physics.set_weather_mode("MONSOON")
        elif key == ord("d"):
            physics.set_weather_mode("DRY")

    cap.release()
    cv2.destroyAllWindows()


# =====================================================================
# 5. DIAGNOSTIC SUITE & FASTAPI WEBSOCKET SERVER
# =====================================================================

def run_diagnostic_suite() -> List[Dict]:
    physics = IRCPhysicsEngine("DRY")
    engine = ThreeNodeEnforcementEngine(physics)

    s1 = engine.evaluate_corridor_traversal(
        case_id="RTVN-2026-001", plate="GJ-01-HX-4821", corridor_type="URBAN_500M",
        node1_speed=76.4, node2_speed=52.0, lateral_positions_m=[1.75, 1.78, 1.74, 1.76, 1.75]
    )
    s2 = engine.evaluate_corridor_traversal(
        case_id="RTVN-2026-002", plate="GJ-01-KP-9012", corridor_type="URBAN_500M",
        node1_speed=78.5, node2_speed=84.2, lateral_positions_m=[1.80, 1.88, 1.75, 1.83, 1.79],
        officer_action_at_node3="CONFIRM_LEVEL_2"
    )
    physics.set_weather_mode("MONSOON")
    s3 = engine.evaluate_corridor_traversal(
        case_id="HSIP-2026-003", plate="GJ-27-TC-7740", corridor_type="HIGHWAY_1KM",
        node1_speed=108.0, node2_speed=111.5, lateral_positions_m=[1.10, 2.35, 0.95, 2.55, 1.20],
        lead_vehicle_speed_kmh=45.0, lead_vehicle_gap_m=19.0, officer_action_at_node3="CONFIRM_LEVEL_3"
    )

    records = [asdict(s1), asdict(s2), asdict(s3)]
    os.makedirs("sample_data", exist_ok=True)
    out_path = os.path.join("sample_data", "corridor_telemetry_logs.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print("=" * 84)
    print("RTVN & HSIP — 3-NODE VIRTUAL CORRIDOR SIMULATION SUITE")
    print("System Architecture & Engineering by Het Prajapati ((c) 2026 Het Prajapati)")
    print("=" * 84)
    for idx, r in enumerate([s1, s2, s3], 1):
        print(f"[SCENARIO {idx} | {r.corridor_type} ({r.node_spacing_m}m) | Limit {r.speed_limit_kmh} km/h] {r.plate_number}:")
        print(f"  -> Node 1: {r.node1_speed_kmh} km/h | Node 2: {r.node2_speed_kmh} km/h (SDLP: {r.sdlp_meters}m, TTC: {r.ttc_seconds}s)")
        print(f"  -> Outcome: {r.node3_officer_decision} | Fine: Rs. {r.fine_inr} | Signal: {r.signal_preemption_state}")
        print(f"  -> BSA Sec. 63 SHA-256: {r.bsa_sec63_sha256[:36]}...")
    print("=" * 84)
    logger.info(f"Exported verified telemetry dataset to: {out_path}")
    return records


def start_websocket_bridge(port: int = 8000) -> None:
    if not FASTAPI_AVAILABLE:
        logger.error("FastAPI/Uvicorn not installed. Run: pip install fastapi uvicorn websockets")
        return

    app = FastAPI(title="RTVN & HSIP Real-Time Telemetry API")
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )

    @app.get("/api/telemetry")
    def get_verified_telemetry():
        return run_diagnostic_suite()

    @app.websocket("/ws/telemetry")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        logger.info("Frontend Web Dashboard connected via WebSocket!")
        records = run_diagnostic_suite()
        try:
            await websocket.send_json({"type": "INITIAL_SYNC", "records": records})
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if msg.get("action") == "VERIFY_SCENARIO":
                    await websocket.send_json({"type": "VERIFIED_ACK", "records": records})
        except WebSocketDisconnect:
            logger.info("Frontend Web Dashboard disconnected.")

    logger.info(f"Starting FastAPI WebSocket Bridge on ws://127.0.0.1:{port}/ws/telemetry")
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RTVN & HSIP Computer Vision & Telemetry Engine")
    parser.add_argument("--mode", choices=["diagnostic", "live", "server"], default="diagnostic",
                        help="diagnostic (default), live (webcam/video CV), or server (FastAPI bridge)")
    parser.add_argument("--source", default="0", help="Webcam index (0) or path to .mp4 traffic video")
    parser.add_argument("--weather", choices=["DRY", "MONSOON"], default="DRY", help="IRC:73 pavement condition")
    args = parser.parse_args()

    if args.mode == "live":
        run_live_cv_tracker(video_source=args.source, weather=args.weather)
    elif args.mode == "server":
        start_websocket_bridge()
    else:
        run_diagnostic_suite()
