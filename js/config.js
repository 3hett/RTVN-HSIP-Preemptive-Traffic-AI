export const WEATHER_PROFILES = {
  dry: {
    friction: 0.35,
    speedLimit: 60,
    label: "Dry Asphalt"
  },
  wet: {
    friction: 0.18,
    speedLimit: 42,
    label: "Wet Monsoon Surface"
  }
};

export const CORRIDOR_PROFILES = {
  500: {
    label: "500 m / 0.5 km",
    node1ToNode2: "500 m",
    node2ToNode3: "500 m"
  },
  1000: {
    label: "1000 m / 1 km",
    node1ToNode2: "1000 m",
    node2ToNode3: "1000 m"
  }
};

export const NODE_X = {
  NODE1: 150,
  NODE2: 430,
  NODE3: 700
};

export const CASE_PREFIX = "HET";