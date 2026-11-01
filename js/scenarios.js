export const scenarios = {
  1: {
    id: 1,
    name: "Scenario 1: Self Rectification",
    plate: "GJ-01-HX-4821",
    node1Speed: 76.4,
    node2Speed: 52.0,
    sdlp: 0.11,
    ttc: 3.9,
    drac: 1.1,
    expectedOutcome: "rectified",
    severity: "warning"
  },
  2: {
    id: 2,
    name: "Scenario 2: Persistent Violator",
    plate: "GJ-01-KP-9012",
    node1Speed: 78.5,
    node2Speed: 84.2,
    sdlp: 0.24,
    ttc: 2.3,
    drac: 2.6,
    expectedOutcome: "officer_review",
    severity: "amber"
  },
  3: {
    id: 3,
    name: "Scenario 3: Extreme Speed / DUI",
    plate: "GJ-27-TC-7740",
    node1Speed: 108.0,
    node2Speed: 111.5,
    sdlp: 0.61,
    ttc: 1.1,
    drac: 5.4,
    expectedOutcome: "level_3",
    severity: "danger"
  }
};