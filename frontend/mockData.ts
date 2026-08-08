// mockData.ts — matches the JSON contract the Python backend will eventually send.
// Swap for a real fetch() in a hook once /results/{job_id} is live; nothing
// else in the app needs to change since screens only read from these shapes.
import { STATUS } from "./theme";

export const MOCK = {
  farm_id: "AT1-DEMO",
  overall_health_pct: 92,
  cells: [
    { id: "A1", status: "healthy", exg_value: 0.41, confidence: 0.97 },
    { id: "B1", status: "healthy", exg_value: 0.39, confidence: 0.95 },
    { id: "C1", status: "healthy", exg_value: 0.44, confidence: 0.96 },
    { id: "D1", status: "healthy", exg_value: 0.4, confidence: 0.94 },
    { id: "A2", status: "healthy", exg_value: 0.38, confidence: 0.93 },
    { id: "B2", status: "dry", exg_value: 0.21, confidence: 0.89, issue: "Water stress", recommended_action: "Irrigate tomorrow" },
    { id: "C2", status: "healthy", exg_value: 0.37, confidence: 0.92 },
    { id: "D2", status: "healthy", exg_value: 0.42, confidence: 0.95 },
    { id: "A3", status: "healthy", exg_value: 0.4, confidence: 0.94 },
    { id: "B3", status: "dry", exg_value: 0.23, confidence: 0.87, issue: "Water stress", recommended_action: "Irrigate tomorrow" },
    { id: "C3", status: "healthy", exg_value: 0.39, confidence: 0.93 },
    { id: "D3", status: "healthy", exg_value: 0.41, confidence: 0.96 },
    { id: "A4", status: "healthy", exg_value: 0.4, confidence: 0.95 },
    { id: "B4", status: "healthy", exg_value: 0.36, confidence: 0.91 },
    { id: "C4", status: "pest", exg_value: 0.18, confidence: 0.88, issue: "Leaf miner", recommended_action: "Spray today", severity: "urgent" },
    { id: "D4", status: "healthy", exg_value: 0.4, confidence: 0.94 },
  ],
  alerts: [
    { type: "urgent", areas: ["C4"], message: "Pest detected", action: "Today" },
    { type: "irrigate", areas: ["B2", "B3"], message: "Irrigate", action: "Tomorrow" },
  ],
};

export function cellById(id: string) {
  return MOCK.cells.find((c) => c.id === id)!;
}

export const ALL_ISSUES = MOCK.cells
  .filter((c) => c.status !== "healthy")
  .map((c) => ({ ...c, s: STATUS[c.status] }));

export const HISTORY = [
  { id: "f1", date: "Today, 9:15 AM", health: 92, plots: 16, issues: 3 },
  { id: "f2", date: "Yesterday, 8:40 AM", health: 89, plots: 16, issues: 4 },
  { id: "f3", date: "Aug 1, 8:50 AM", health: 94, plots: 16, issues: 1 },
  { id: "f4", date: "Jul 30, 9:05 AM", health: 85, plots: 16, issues: 5 },
];
