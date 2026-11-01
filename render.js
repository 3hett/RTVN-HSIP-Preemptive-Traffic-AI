import { appState } from "./state.js";
import { getWeatherProfile } from "./rules.js";

export function renderCorridorSummary() {
  const corridorSummary = document.getElementById("corridorSummary");
  const spacingLabel = appState.corridorMeters === 1000 ? "1000 m / 1 km" : "500 m";
  corridorSummary.textContent = `Node 1 → Node 2 (${spacingLabel}) → Node 3`;
}

export function renderWeatherBadges() {
  const profile = getWeatherProfile(appState.weatherMode);
  const limitBadge = document.getElementById("limitBadge");
  const ssdBadge = document.getElementById("ssdBadge");

  limitBadge.textContent = `Limit: ${profile.speedLimit} km/h`;
  const ssdValue = (0.278 * profile.speedLimit * 2.5) + ((profile.speedLimit ** 2) / (254 * profile.friction));
  ssdBadge.textContent = `SSD: ${ssdValue.toFixed(1)} m`;
}

export function renderTelemetry() {
  const vehicle = appState.vehicle;

  document.getElementById("telemetryPlate").textContent = vehicle.plate || "--";
  document.getElementById("telemetrySpeed").textContent = `${vehicle.speedKmh.toFixed(1)} km/h`;
  document.getElementById("telemetrySdlp").textContent = `${vehicle.sdlp.toFixed(2)} m`;
  document.getElementById("telemetrySafety").textContent = `${vehicle.ttc.toFixed(1)}s / ${vehicle.drac.toFixed(1)}`;
  document.getElementById("telemetrySignal").textContent = vehicle.node3Signal;
}

export function renderGateState() {
  const officerCard = document.getElementById("officerCard");
  const gateDot = document.getElementById("gateDot");
  const gateBadge = document.getElementById("gateBadge");
  const officerSummary = document.getElementById("officerSummary");

  if (appState.vehicle.waitingOfficer) {
    officerCard.classList.add("active");
    gateDot.classList.remove("idle");
    gateDot.classList.add("active");
    gateBadge.textContent = "AWAITING OFFICER";
    gateBadge.className = "badge warning";
    officerSummary.textContent = `${appState.vehicle.plate} reached Node 3 without rectification. Officer action is required.`;
  } else {
    officerCard.classList.remove("active");
    gateDot.classList.remove("active");
    gateDot.classList.add("idle");
    gateBadge.textContent = "STANDBY";
    gateBadge.className = "badge neutral";
    officerSummary.textContent = "Alerts are generated at Node 1 and verified at Node 2. If the driver fails to rectify, the case reaches the officer gate.";
  }
}

export function setOfficerButtons(active) {
  document.getElementById("btnLevel2").disabled = !active;
  document.getElementById("btnLevel3").disabled = !active;
  document.getElementById("btnDismiss").disabled = !active;
}

export function renderLedger() {
  const ledgerBody = document.getElementById("ledgerBody");
  ledgerBody.innerHTML = "";

  appState.ledger.forEach((entry) => {
    const row = document.createElement("tr");
    row.className = entry.severityClass || "";

    row.innerHTML = `
      <td>${entry.caseId}</td>
      <td>${entry.plate}</td>
      <td>${entry.speedsText}</td>
      <td>${entry.status}</td>
      <td>${entry.officerAction}</td>
      <td>${entry.hash}</td>
    `;

    ledgerBody.appendChild(row);
  });
}

export function renderTimeline() {
  const timelineList = document.getElementById("timelineList");
  timelineList.innerHTML = "";

  if (appState.timeline.length === 0) {
    timelineList.innerHTML = "<li>Waiting for scenario...</li>";
    return;
  }

  appState.timeline.slice(0, 6).forEach((event) => {
    const li = document.createElement("li");
    li.textContent = `${event.timestamp} — ${event.message}`;
    timelineList.appendChild(li);
  });
}

export function renderFleet() {
  const fleetList = document.getElementById("fleetList");
  fleetList.innerHTML = "";

  if (appState.fleet.length === 0) {
    fleetList.innerHTML = "<div class='fleet-item empty'>No active vehicles</div>";
    return;
  }

  appState.fleet.forEach((vehicle) => {
    const item = document.createElement("div");
    item.className = "fleet-item";
    item.innerHTML = `
      <span class="plate">${vehicle.plate}</span>
      <span class="state">${vehicle.state}</span>
    `;
    fleetList.appendChild(item);
  });
}

export function renderRiskChart() {
  const riskChart = document.getElementById("riskChart");
  riskChart.innerHTML = "";

  const score = appState.currentCase?.riskScore ?? 26;

  const bars = [
    { height: 18, cls: "low" },
    { height: 38, cls: "mid" },
    { height: Math.max(24, Math.min(100, score)) * 0.9, cls: score >= 75 ? "high" : score >= 45 ? "mid" : "low" }
  ];

  bars.forEach((bar) => {
    const div = document.createElement("div");
    div.className = `risk-bar ${bar.cls}`;
    div.style.height = `${bar.height}%`;
    riskChart.appendChild(div);
  });
}

export function updateNotificationUI({ stageText, headline, bannerClass, voiceText, detailedText }) {
  const banner = document.getElementById("violatorBanner");
  banner.className = `banner ${bannerClass}`;

  document.getElementById("bannerTag").textContent = stageText;
  document.getElementById("bannerTime").textContent = new Date().toLocaleTimeString([], { hour12: false }) + " IST";
  document.getElementById("bannerHeadline").textContent = headline;
  document.getElementById("voiceTranscript").textContent = `"${voiceText}"`;
  document.getElementById("detailedNoticeBox").textContent = detailedText;
}

export function renderAll() {
  renderCorridorSummary();
  renderWeatherBadges();
  renderTelemetry();
  renderGateState();
  renderLedger();
  renderTimeline();
  renderFleet();
  renderRiskChart();
}