import { appState, createCaseId, resetVehicle } from "./state.js";
import { scenarios } from "./scenarios.js";
import { NODE_X } from "./config.js";
import { evaluateViolation, getWeatherProfile, calculateRiskScore, getRiskSeverity } from "./rules.js";
import {
  renderAll,
  renderCorridorSummary,
  renderWeatherBadges,
  renderTelemetry,
  renderGateState,
  updateNotificationUI,
  setOfficerButtons,
  renderLedger,
  renderTimeline,
  renderFleet,
  renderRiskChart
} from "./render.js";

const canvas = document.getElementById("corridorCanvas");
const ctx = canvas.getContext("2d");

let animationFrameId = null;

function speakAlert(text, lang = "en-IN") {
  if (!("speechSynthesis" in window)) {
    return;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.rate = 1.02;
  window.speechSynthesis.speak(utterance);
}

function addTimelineEvent(message) {
  appState.timeline.unshift({
    message,
    timestamp: new Date().toLocaleTimeString([], { hour12: false })
  });

  renderTimeline();
}

function addCurrentCaseToFleet() {
  const vehicle = appState.vehicle;

  if (!vehicle.caseId) return;

  appState.fleet.unshift({
    plate: vehicle.plate,
    state: vehicle.waitingOfficer ? "Awaiting Officer" : vehicle.stage,
    caseId: vehicle.caseId
  });

  if (appState.fleet.length > 5) {
    appState.fleet = appState.fleet.slice(0, 5);
  }

  renderFleet();
}

function saveNotification(payload) {
  appState.notification = payload;
  localStorage.setItem("rtvn_last_notification", JSON.stringify(payload));
}

function addLedgerEntry({ caseId, plate, speedsText, status, officerAction, hash, severityClass }) {
  appState.ledger.unshift({
    caseId,
    plate,
    speedsText,
    status,
    officerAction,
    hash,
    severityClass,
    timestamp: new Date().toISOString()
  });

  renderLedger();
}

function triggerNode1Alert() {
  const vehicle = appState.vehicle;
  const violation = evaluateViolation(vehicle, appState.weatherMode);
  const riskScore = calculateRiskScore(vehicle, appState.weatherMode);
  const severity = getRiskSeverity(riskScore);

  const voiceText = `Attention driver of vehicle ${vehicle.plate}. Violation detected at Camera Node 1 at ${vehicle.node1Speed.toFixed(1)} kilometers per hour. The enforced limit is ${violation.speedLimit} kilometers per hour. Reduce speed immediately.`;
  const detailedText = `[REAL-TIME VIOLATION ALERT — NODE 1]
Case ID: ${vehicle.caseId}
Plate: ${vehicle.plate}
Node 1 Speed: ${vehicle.node1Speed.toFixed(1)} km/h
Speed Limit: ${violation.speedLimit} km/h
Required SSD: ${violation.ssdRequired.toFixed(1)} m
Risk Score: ${riskScore}/100
Action: Reduce speed and stabilize lane discipline before Node 2.`;

  appState.lastVoiceText = voiceText;
  appState.currentCase = {
    ...appState.currentCase,
    riskScore,
    severity
  };

  speakAlert(voiceText, document.getElementById("voiceSelect").value);

  const payload = {
    caseId: vehicle.caseId,
    plate: vehicle.plate,
    headline: `Violation detected for ${vehicle.plate}`,
    stage: "NODE 1 ALERT",
    time: new Date().toLocaleTimeString([], { hour12: false }),
    message: voiceText,
    detailed: detailedText,
    severity
  };

  saveNotification(payload);

  updateNotificationUI({
    stageText: "NODE 1 ALERT",
    headline: `Violation detected for ${vehicle.plate} (${vehicle.node1Speed.toFixed(1)} km/h)`,
    bannerClass: severity === "danger" ? "danger" : severity === "amber" ? "warning" : "success",
    voiceText,
    detailedText
  });

  addTimelineEvent(`Node 1 alert sent for ${vehicle.plate}`);
}

function triggerNode2Event() {
  const vehicle = appState.vehicle;
  const profile = getWeatherProfile(appState.weatherMode);

  if (vehicle.node2Speed <= profile.speedLimit) {
    const voiceText = `Compliance confirmed for vehicle ${vehicle.plate}. Speed has reduced to ${vehicle.node2Speed.toFixed(1)} kilometers per hour. The violation is resolved.`;
    const detailedText = `[REAL-TIME RECTIFICATION — NODE 2]
Case ID: ${vehicle.caseId}
Plate: ${vehicle.plate}
Node 1 → Node 2: ${vehicle.node1Speed.toFixed(1)} → ${vehicle.node2Speed.toFixed(1)} km/h
Status: Self-rectified
Outcome: No penalty issued.`;

    appState.lastVoiceText = voiceText;
    speakAlert(voiceText, document.getElementById("voiceSelect").value);

    const payload = {
      caseId: vehicle.caseId,
      plate: vehicle.plate,
      headline: `Self-rectification confirmed`,
      stage: "NODE 2 COMPLIANCE",
      time: new Date().toLocaleTimeString([], { hour12: false }),
      message: voiceText,
      detailed: detailedText,
      severity: "success"
    };

    saveNotification(payload);

    updateNotificationUI({
      stageText: "NODE 2 COMPLIANCE",
      headline: `Self-rectification confirmed for ${vehicle.plate}`,
      bannerClass: "success",
      voiceText,
      detailedText
    });

    addLedgerEntry({
      caseId: vehicle.caseId,
      plate: vehicle.plate,
      speedsText: `${vehicle.node1Speed.toFixed(1)} → ${vehicle.node2Speed.toFixed(1)} km/h`,
      status: "L1: COMPLIED",
      officerAction: "Auto-closed at Node 2",
      hash: "SELF-RECTIFIED",
      severityClass: "severity-success"
    });

    addTimelineEvent(`Node 2 compliance check passed for ${vehicle.plate}`);

    vehicle.stage = "completed";
    vehicle.active = false;
    renderGateState();
    return;
  }

  const riskScore = calculateRiskScore(vehicle, appState.weatherMode);
  const severity = getRiskSeverity(riskScore);

  const voiceText = `Warning ignored at Camera Node 2. Case forwarded to Node 3 for human review.`;
  const detailedText = `[NODE 2 NON-COMPLIANCE — FORWARDED TO NODE 3]
Case ID: ${vehicle.caseId}
Plate: ${vehicle.plate}
Node 1 → Node 2: ${vehicle.node1Speed.toFixed(1)} → ${vehicle.node2Speed.toFixed(1)} km/h
Risk Score: ${riskScore}/100
Status: Awaiting officer confirmation
Outcome: Case moved to Node 3.`;

  appState.lastVoiceText = voiceText;
  appState.currentCase = {
    ...appState.currentCase,
    riskScore,
    severity
  };

  speakAlert(voiceText, document.getElementById("voiceSelect").value);

  const payload = {
    caseId: vehicle.caseId,
    plate: vehicle.plate,
    headline: `Unrectified violation for ${vehicle.plate}`,
    stage: "NODE 2 ESCALATION",
    time: new Date().toLocaleTimeString([], { hour12: false }),
    message: voiceText,
    detailed: detailedText,
    severity
  };

  saveNotification(payload);

  updateNotificationUI({
    stageText: "NODE 2 ESCALATION",
    headline: `Unrectified violation for ${vehicle.plate} — awaiting officer review`,
    bannerClass: severity === "danger" ? "danger" : "warning",
    voiceText,
    detailedText
  });

  vehicle.waitingOfficer = true;
  vehicle.stage = "waiting_officer";
  renderGateState();
  setOfficerButtons(true);

  addLedgerEntry({
    caseId: vehicle.caseId,
    plate: vehicle.plate,
    speedsText: `${vehicle.node1Speed.toFixed(1)} → ${vehicle.node2Speed.toFixed(1)} km/h`,
    status: "PENDING NODE 3",
    officerAction: "Awaiting Officer Decision",
    hash: "AWAIT_NODE3",
    severityClass: severity === "danger" ? "severity-danger" : "severity-amber"
  });

  addTimelineEvent(`Node 2 non-compliance escalated for ${vehicle.plate}`);
  renderRiskChart();
}

function handleOfficerDecision(decision) {
  const vehicle = appState.vehicle;

  vehicle.waitingOfficer = false;
  setOfficerButtons(false);
  renderGateState();

  const riskScore = calculateRiskScore(vehicle, appState.weatherMode);
  const severity = getRiskSeverity(riskScore);

  if (decision === "LEVEL_2") {
    const voiceText = `Node 3 officer confirmed Level 2 for vehicle ${vehicle.plate}. A challan of 2,000 rupees and 3 points has been issued.`;
    const detailedText = `[NODE 3 CONFIRMED — LEVEL 2]
Case ID: ${vehicle.caseId}
Plate: ${vehicle.plate}
Officer Decision: Level 2
Outcome: ₹2,000 challan + 3 demerit points.`;

    appState.lastVoiceText = voiceText;

    const payload = {
      caseId: vehicle.caseId,
      plate: vehicle.plate,
      headline: `Level 2 penalty confirmed`,
      stage: "NODE 3 CONFIRMED",
      time: new Date().toLocaleTimeString([], { hour12: false }),
      message: voiceText,
      detailed: detailedText,
      severity
    };

    saveNotification(payload);
    speakAlert(voiceText, document.getElementById("voiceSelect").value);

    updateNotificationUI({
      stageText: "NODE 3 CONFIRMED",
      headline: `Level 2 penalty confirmed for ${vehicle.plate}`,
      bannerClass: "warning",
      voiceText,
      detailedText
    });

    addLedgerEntry({
      caseId: vehicle.caseId,
      plate: vehicle.plate,
      speedsText: `${vehicle.node1Speed.toFixed(1)} → ${vehicle.node2Speed.toFixed(1)} km/h`,
      status: "L2: CHALLAN",
      officerAction: "confirmed level 2",
      hash: "LEVEL2",
      severityClass: "severity-warning"
    });

    addTimelineEvent(`Officer confirmed Level 2 for ${vehicle.plate}`);
  } else if (decision === "LEVEL_3") {
    vehicle.node3Signal = "RED";
    const voiceText = `Emergency Level 3 High-Speed Interception confirmed for vehicle ${vehicle.plate}. Node 3 signal is locked to red and police interception is in progress.`;
    const detailedText = `[NODE 3 CONFIRMED — LEVEL 3 HSIP]
Case ID: ${vehicle.caseId}
Plate: ${vehicle.plate}
Officer Decision: Level 3 HSIP
Outcome: RED signal locked, patrol dispatched, ₹10,000 fine + 6 points.`;

    appState.lastVoiceText = voiceText;

    const payload = {
      caseId: vehicle.caseId,
      plate: vehicle.plate,
      headline: `HSIP activated`,
      stage: "LEVEL 3 HSIP",
      time: new Date().toLocaleTimeString([], { hour12: false }),
      message: voiceText,
      detailed: detailedText,
      severity: "danger"
    };

    saveNotification(payload);
    speakAlert(voiceText, document.getElementById("voiceSelect").value);

    updateNotificationUI({
      stageText: "LEVEL 3 HSIP",
      headline: `HSIP activated for ${vehicle.plate}`,
      bannerClass: "danger",
      voiceText,
      detailedText
    });

    addLedgerEntry({
      caseId: vehicle.caseId,
      plate: vehicle.plate,
      speedsText: `${vehicle.node1Speed.toFixed(1)} → ${vehicle.node2Speed.toFixed(1)} km/h`,
      status: "L3: HSIP",
      officerAction: "confirmed level 3",
      hash: "LEVEL3",
      severityClass: "severity-danger"
    });

    addTimelineEvent(`Officer confirmed Level 3 HSIP for ${vehicle.plate}`);
  } else {
    const voiceText = `Case ${vehicle.caseId} has been dismissed by the reviewing officer.`;
    const detailedText = `[NODE 3 DISMISSED]
Case ID: ${vehicle.caseId}
Plate: ${vehicle.plate}
Officer Decision: Dismissed
Outcome: No penalty issued.`;

    appState.lastVoiceText = voiceText;

    const payload = {
      caseId: vehicle.caseId,
      plate: vehicle.plate,
      headline: `Case dismissed`,
      stage: "CASE DISMISSED",
      time: new Date().toLocaleTimeString([], { hour12: false }),
      message: voiceText,
      detailed: detailedText,
      severity: "success"
    };

    saveNotification(payload);
    speakAlert(voiceText, document.getElementById("voiceSelect").value);

    updateNotificationUI({
      stageText: "CASE DISMISSED",
      headline: `Case dismissed for ${vehicle.plate}`,
      bannerClass: "neutral",
      voiceText,
      detailedText
    });

    addLedgerEntry({
      caseId: vehicle.caseId,
      plate: vehicle.plate,
      speedsText: `${vehicle.node1Speed.toFixed(1)} → ${vehicle.node2Speed.toFixed(1)} km/h`,
      status: "DISMISSED",
      officerAction: "dismissed by officer",
      hash: "DISMISSED",
      severityClass: "severity-success"
    });

    addTimelineEvent(`Officer dismissed case for ${vehicle.plate}`);
  }

  vehicle.stage = "completed";
  renderRiskChart();
  renderTelemetry();
  drawCorridor();
}

function updateWeatherConfig() {
  appState.weatherMode = document.getElementById("weatherSelect").value;
  renderWeatherBadges();
  renderRiskChart();
  drawCorridor();
}

function updateCorridorConfig() {
  appState.corridorMeters = Number(document.getElementById("corridorSelect").value);
  renderCorridorSummary();
  drawCorridor();
}

function addFleetEntry() {
  const plate = appState.vehicle.plate;
  if (!plate) return;

  const exists = appState.fleet.some((v) => v.plate === plate);
  if (!exists) {
    appState.fleet.unshift({
      plate,
      state: "ready",
      caseId: appState.vehicle.caseId
    });
  }

  renderFleet();
}

function exportProof() {
  const exportData = {
    generatedAt: new Date().toISOString(),
    corridorMeters: appState.corridorMeters,
    weatherMode: appState.weatherMode,
    currentCase: appState.currentCase,
    ledger: appState.ledger,
    timeline: appState.timeline,
    officerNotes: document.getElementById("officerNotesInput").value,
    notification: appState.notification
  };

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = `${appState.currentCase?.caseId || "rtvn-case"}-proof.json`;
  link.click();

  URL.revokeObjectURL(url);
}

function drawNode(x, label, sublabel, color) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.setLineDash([5, 5]);
  ctx.beginPath();
  ctx.moveTo(x, 35);
  ctx.lineTo(x, 180);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = "#0f172a";
  ctx.fillRect(x - 62, 184, 124, 26);
  ctx.strokeStyle = color;
  ctx.strokeRect(x - 62, 184, 124, 26);

  ctx.fillStyle = color;
  ctx.font = "bold 10px sans-serif";
  ctx.fillText(label, x - 54, 196);

  ctx.fillStyle = "#cbd5e1";
  ctx.font = "9px monospace";
  ctx.fillText(sublabel, x - 54, 206);
}

function drawCorridor() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const weatherColor = appState.weatherMode === "wet" ? "#0f172a" : "#1e293b";
  const vehicle = appState.vehicle;

  ctx.fillStyle = weatherColor;
  ctx.fillRect(0, 35, canvas.width, 145);

  ctx.strokeStyle = "#64748b";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, 35);
  ctx.lineTo(canvas.width, 35);
  ctx.moveTo(0, 180);
  ctx.lineTo(canvas.width, 180);
  ctx.stroke();

  ctx.strokeStyle = "#cbd5e1";
  ctx.lineWidth = 2;
  ctx.setLineDash([18, 24]);
  ctx.beginPath();
  ctx.moveTo(0, 108);
  ctx.lineTo(canvas.width, 108);
  ctx.stroke();
  ctx.setLineDash([]);

  drawNode(NODE_X.NODE1, "NODE 1", "Detection", "#38bdf8");
  drawNode(NODE_X.NODE2, "NODE 2", "Verify", "#fbbf24");

  const n3Color = vehicle.node3Signal === "RED" ? "#ef4444" : "#10b981";
  drawNode(NODE_X.NODE3, "NODE 3", "Officer", n3Color);

  ctx.fillStyle = vehicle.node3Signal === "RED" ? "#ef4444" : "#10b981";
  ctx.beginPath();
  ctx.arc(NODE_X.NODE3, 24, 7, 0, Math.PI * 2);
  ctx.fill();

  if (vehicle.active || vehicle.waitingOfficer) {
    const isViolating = vehicle.speedKmh > getWeatherProfile(appState.weatherMode).speedLimit || vehicle.sdlp >= 0.45;
    const boxColor = isViolating ? "#ef4444" : "#22c55e";

    ctx.fillStyle = "#f8fafc";
    ctx.fillRect(vehicle.x - 22, vehicle.y - 12, 44, 24);

    ctx.strokeStyle = boxColor;
    ctx.lineWidth = 2;
    ctx.strokeRect(vehicle.x - 26, vehicle.y - 16, 52, 32);

    ctx.fillStyle = "#0f172a";
    ctx.fillRect(vehicle.x - 48, vehicle.y - 36, 100, 18);
    ctx.strokeStyle = boxColor;
    ctx.lineWidth = 1;
    ctx.strokeRect(vehicle.x - 48, vehicle.y - 36, 100, 18);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 10px monospace";
    ctx.fillText(`${vehicle.speedKmh.toFixed(0)} km/h | ${vehicle.plate.slice(-4)}`, vehicle.x - 43, vehicle.y - 24);
  }
}

function animateCorridor() {
  const vehicle = appState.vehicle;

  if (!vehicle.active) return;

  if (vehicle.waitingOfficer) {
    drawCorridor();
    return;
  }

  const pxStep = vehicle.node1Speed > 100 ? 2.2 : 1.8;
  vehicle.x += pxStep;

  if (vehicle.x >= NODE_X.NODE1 && vehicle.x <= NODE_X.NODE2) {
    const ratio = (vehicle.x - NODE_X.NODE1) / (NODE_X.NODE2 - NODE_X.NODE1);
    vehicle.speedKmh = vehicle.node1Speed + (vehicle.node2Speed - vehicle.node1Speed) * ratio;
  }

  if (vehicle.scenarioId === 3 && vehicle.x < NODE_X.NODE3 - 35) {
    vehicle.y = vehicle.baseY + Math.sin(vehicle.x * 0.08) * 18;
  } else {
    vehicle.y = vehicle.baseY;
  }

  if (vehicle.stage === "approaching_node_1" && vehicle.x >= NODE_X.NODE1) {
    vehicle.stage = "node1_passed";
    triggerNode1Alert();
  }

  if (vehicle.stage === "node1_passed" && vehicle.x >= NODE_X.NODE2) {
    vehicle.stage = "node2_passed";
    triggerNode2Event();
  }

  if (vehicle.stage === "waiting_officer") {
    drawCorridor();
    return;
  }

  if (vehicle.stage === "completed") {
    vehicle.active = false;
    renderTelemetry();
    drawCorridor();
    return;
  }

  renderTelemetry();
  renderRiskChart();
  drawCorridor();

  if (vehicle.x < canvas.width + 50) {
    animationFrameId = requestAnimationFrame(animateCorridor);
  } else {
    vehicle.active = false;
    vehicle.stage = "completed";
  }
}

function startScenario(scenarioId) {
  const scenario = scenarios[scenarioId];
  if (!scenario) return;

  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }

  resetVehicle();

  appState.currentScenarioId = scenarioId;
  appState.vehicle = {
    active: true,
    plate: scenario.plate,
    caseId: createCaseId(),
    x: 35,
    y: 108,
    baseY: 108,
    speedKmh: scenario.node1Speed,
    node1Speed: scenario.node1Speed,
    node2Speed: scenario.node2Speed,
    sdlp: scenario.sdlp,
    ttc: scenario.ttc,
    drac: scenario.drac,
    stage: "approaching_node_1",
    node3Signal: "GREEN",
    waitingOfficer: false,
    scenarioId
  };

  appState.currentCase = {
    caseId: appState.vehicle.caseId,
    plate: appState.vehicle.plate,
    riskScore: calculateRiskScore(appState.vehicle, appState.weatherMode),
    severity: getRiskSeverity(calculateRiskScore(appState.vehicle, appState.weatherMode))
  };

  addFleetEntry();

  setOfficerButtons(false);
  renderGateState();
  renderTelemetry();
  renderCorridorSummary();
  renderWeatherBadges();
  renderRiskChart();
  drawCorridor();

  animationFrameId = requestAnimationFrame(animateCorridor);
}

document.getElementById("weatherSelect").addEventListener("change", updateWeatherConfig);
document.getElementById("corridorSelect").addEventListener("change", updateCorridorConfig);

document.querySelectorAll(".scenario-btn").forEach((button) => {
  button.addEventListener("click", () => {
    const scenarioId = Number(button.dataset.scenario);
    startScenario(scenarioId);
  });
});

document.getElementById("btnLevel2").addEventListener("click", () => handleOfficerDecision("LEVEL_2"));
document.getElementById("btnLevel3").addEventListener("click", () => handleOfficerDecision("LEVEL_3"));
document.getElementById("btnDismiss").addEventListener("click", () => handleOfficerDecision("DISMISS"));

document.getElementById("replayVoiceBtn").addEventListener("click", () => {
  if (appState.lastVoiceText) {
    speakAlert(appState.lastVoiceText, document.getElementById("voiceSelect").value);
  }
});

document.getElementById("voiceSelect").addEventListener("change", () => {
  if (appState.lastVoiceText) {
    speakAlert(appState.lastVoiceText, document.getElementById("voiceSelect").value);
  }
});

document.getElementById("resetLedgerBtn").addEventListener("click", () => {
  appState.ledger = [];
  renderLedger();
});

document.getElementById("exportProofBtn").addEventListener("click", exportProof);

document.getElementById("openNotificationBtn").addEventListener("click", () => {
  window.open("./notification-preview.html", "_blank", "width=430,height=760");
});

document.getElementById("officerNotesInput").addEventListener("input", (event) => {
  appState.currentCase = {
    ...appState.currentCase,
    officerNotes: event.target.value
  };
});

renderAll();
renderFleet();
renderTimeline();
renderRiskChart();
setOfficerButtons(false);
startScenario(1);