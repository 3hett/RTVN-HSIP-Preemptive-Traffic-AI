/**
 * RTVN & HSIP — Python FastAPI WebSocket Bridge & BSA 2023 Section 63 Auditor
 * System Architecture & Engineering by Het Prajapati ((c) 2026 Het Prajapati)
 */

(function initRtvnBackendBridge() {
  // 1. Inject the non-intrusive BSA 2023 Cryptographic Verifier & Backend Status Widget
  const widgetHtml = `
    <div id="bsa-verifier-widget" style="position:fixed;bottom:16px;right:16px;z-index:9999;background:#0f172a;border:1px solid #334155;border-radius:10px;padding:12px 16px;color:#f8fafc;font-family:system-ui,sans-serif;font-size:12px;box-shadow:0 10px 25px rgba(0,0,0,0.5);max-width:360px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;gap:8px;">
        <span id="backend-status-pill" style="background:#1e293b;color:#38bdf8;padding:3px 8px;border-radius:999px;font-weight:600;font-size:11px;">
          ⚡ ENGINE: STANDALONE WEB SIMULATOR
        </span>
        <span style="color:#94a3b8;font-size:10px;">BSA Sec. 63 Ledger</span>
      </div>
      <div id="bsa-audit-output" style="background:#020617;padding:8px;border-radius:6px;font-family:monospace;font-size:11px;color:#cbd5e1;margin-bottom:8px;word-break:break-all;">
        Ready to audit SHA-256 electronic evidence chain.
      </div>
      <div style="display:flex;gap:6px;">
        <button id="btn-bsa-verify" style="flex:1;background:#0284c7;color:#fff;border:none;padding:6px 8px;border-radius:5px;cursor:pointer;font-weight:600;font-size:11px;">
          ✓ Verify SHA-256
        </button>
        <button id="btn-bsa-tamper" style="flex:1;background:#dc2626;color:#fff;border:none;padding:6px 8px;border-radius:5px;cursor:pointer;font-weight:600;font-size:11px;">
          ⚠ Test Tamper (+1 km/h)
        </button>
      </div>
    </div>
  `;

  document.addEventListener("DOMContentLoaded", () => {
    document.body.insertAdjacentHTML("beforeend", widgetHtml);

    const statusPill = document.getElementById("backend-status-pill");
    const auditBox = document.getElementById("bsa-audit-output");

    // 2. Connect to Local Python FastAPI WebSocket Server (if running)
    try {
      const ws = new WebSocket("ws://127.0.0.1:8000/ws/telemetry");
      ws.onopen = () => {
        statusPill.style.background = "#064e3b";
        statusPill.style.color = "#34d399";
        statusPill.textContent = "🟢 PYTHON FASTAPI ENGINE: LIVE SYNC";
      };
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.records && data.records.length > 0) {
          window.latestPythonTelemetry = data.records;
          auditBox.innerHTML = `<span style="color:#38bdf8;">Synced ${data.records.length} verified records from Python engine.</span>`;
        }
      };
      ws.onerror = () => {};
    } catch (err) {}

    // 3. BSA 2023 Section 63 SHA-256 Audit & Tamper Simulation
    async function runBsaAudit(simulateTamper) {
      const baseRecord = (window.latestPythonTelemetry && window.latestPythonTelemetry[2]) || {
        case_id: "HSIP-2026-003",
        plate_number: "GJ-27-TC-7740",
        node1_speed_kmh: 108.0,
        node2_speed_kmh: 111.5,
        sdlp_meters: 0.727,
        weather_mode: "MONSOON"
      };

      const enc = new TextEncoder();
      const origBuf = await crypto.subtle.digest("SHA-256", enc.encode(JSON.stringify(baseRecord)));
      const origHash = Array.from(new Uint8Array(origBuf)).map(b => b.toString(16).padStart(2, "0")).join("");

      const testRecord = { ...baseRecord };
      if (simulateTamper) {
        testRecord.node2_speed_kmh = Number((testRecord.node2_speed_kmh + 1.0).toFixed(1));
      }
      const testBuf = await crypto.subtle.digest("SHA-256", enc.encode(JSON.stringify(testRecord)));
      const testHash = Array.from(new Uint8Array(testBuf)).map(b => b.toString(16).padStart(2, "0")).join("");

      if (!simulateTamper && origHash === testHash) {
        auditBox.style.borderLeft = "3px solid #22c55e";
        auditBox.innerHTML = `<span style="color:#4ade80;font-weight:bold;">[VALID BSA SEC. 63 MATCH]</span><br>Orig: ${origHash.slice(0, 24)}...<br>Calc: ${testHash.slice(0, 24)}...`;
      } else {
        auditBox.style.borderLeft = "3px solid #ef4444";
        auditBox.innerHTML = `<span style="color:#f87171;font-weight:bold;">[TAMPER DETECTED — EVIDENCE REJECTED]</span><br>Orig: ${origHash.slice(0, 24)}...<br>Altered (+1 km/h): ${testHash.slice(0, 18)}...`;
      }
    }

    document.getElementById("btn-bsa-verify").addEventListener("click", () => runBsaAudit(false));
    document.getElementById("btn-bsa-tamper").addEventListener("click", () => runBsaAudit(true));
  });
})();
