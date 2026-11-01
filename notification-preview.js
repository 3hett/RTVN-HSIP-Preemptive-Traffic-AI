const saved = JSON.parse(localStorage.getItem("rtvn_last_notification") || "{}");

const severityBadge = document.getElementById("severityBadge");
const headline = document.getElementById("headline");
const timestamp = document.getElementById("timestamp");
const noticeText = document.getElementById("noticeText");

const severityMap = {
  success: { label: "Resolved", className: "success" },
  warning: { label: "Warning", className: "warn" },
  amber: { label: "Review", className: "warn" },
  danger: { label: "Critical", className: "danger" }
};

const item = saved || {
  headline: "Violation Alert",
  stage: "NODE 1 ALERT",
  time: new Date().toLocaleTimeString([], { hour12: false }),
  message: "No recent violation recorded.",
  detailed: "No notification available.",
  severity: "warning"
};

const state = severityMap[item.severity] || severityMap.warning;

severityBadge.textContent = state.label;
severityBadge.className = `badge ${state.className}`;

headline.textContent = item.headline || "Violation Alert";
timestamp.textContent = item.time || new Date().toLocaleTimeString([], { hour12: false });

noticeText.textContent = item.message || item.detailed || "No notification available.";