export const appState = {
  corridorMeters: 500,
  weatherMode: "dry",
  currentScenarioId: null,
  caseCounter: 100,
  fleet: [],
  ledger: [],
  timeline: [],
  notification: null,
  currentCase: null,
  lastVoiceText: "",
  vehicle: {
    active: false,
    plate: "",
    caseId: "",
    x: 35,
    y: 108,
    baseY: 108,
    speedKmh: 0,
    node1Speed: 0,
    node2Speed: 0,
    sdlp: 0.08,
    ttc: 4.8,
    drac: 0.9,
    stage: "idle",
    node3Signal: "GREEN",
    waitingOfficer: false,
    scenarioId: null
  }
};

export function createCaseId() {
  appState.caseCounter += 1;
  return `HET-${appState.caseCounter}`;
}

export function resetVehicle() {
  appState.vehicle = {
    active: false,
    plate: "",
    caseId: "",
    x: 35,
    y: 108,
    baseY: 108,
    speedKmh: 0,
    node1Speed: 0,
    node2Speed: 0,
    sdlp: 0.08,
    ttc: 4.8,
    drac: 0.9,
    stage: "idle",
    node3Signal: "GREEN",
    waitingOfficer: false,
    scenarioId: null
  };
}