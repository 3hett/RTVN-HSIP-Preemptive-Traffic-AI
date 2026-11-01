import { WEATHER_PROFILES } from "./config.js";

export function computeSSD(speedKmh, friction) {
  const reactionTime = 2.5;
  return 0.278 * speedKmh * reactionTime + (speedKmh * speedKmh) / (254 * friction);
}

export function getWeatherProfile(weatherMode) {
  return WEATHER_PROFILES[weatherMode] || WEATHER_PROFILES.dry;
}

export function evaluateViolation(vehicle, weatherMode) {
  const profile = getWeatherProfile(weatherMode);
  const ssdRequired = computeSSD(vehicle.node1Speed, profile.friction);

  return {
    speedLimit: profile.speedLimit,
    friction: profile.friction,
    ssdRequired,
    overLimit: vehicle.node1Speed > profile.speedLimit,
    risk: vehicle.sdlp >= 0.45 ? "high" : "normal"
  };
}

export function calculateRiskScore(vehicle, weatherMode) {
  const profile = getWeatherProfile(weatherMode);
  const speedFactor = (vehicle.node1Speed / profile.speedLimit) * 100;
  const weaveFactor = (vehicle.sdlp / 0.6) * 100;
  const timeFactor = (1 / Math.max(vehicle.ttc, 0.5)) * 30;

  const score = Math.min(100, Math.round(speedFactor * 0.55 + weaveFactor * 0.3 + timeFactor * 0.15));
  return score;
}

export function getRiskSeverity(score) {
  if (score >= 75) return "danger";
  if (score >= 45) return "amber";
  return "warning";
}