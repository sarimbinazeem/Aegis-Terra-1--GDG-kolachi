// theme.ts — single source of truth for colors, status, and nav config.
// Change a color once here, it updates everywhere.
import { Home, UploadCloud, History, Bell, Settings, Droplets, Leaf, AlertTriangle, CheckCircle2 } from "lucide-react-native";

export const COLORS = {
  paper: "#E8F5E9",
  line: "#A5D6A7",
  fieldGreen: "#66BB6A",
  fieldGreenDeep: "#1B5E20",
  card: "#FFFFFF",
  ink: "#1B5E20",
  inkSoft: "#4F8D53",
  navInactive: "#8FBF92",
};

export const STATUS: Record<string, { hex: string; label: string; Icon: any }> = {
  healthy: {
    hex: "#66BB6A",
    label: "Healthy",
    Icon: CheckCircle2,
  },

  dry: {
    hex: "#E8B93A",
    label: "Dry",
    Icon: Droplets,
  },

  disease: {
    hex: "#E07B29",
    label: "Disease",
    Icon: Leaf,
  },

  pest: {
    hex: "#D63B3B",
    label: "Pest Attack",
    Icon: AlertTriangle,
  },

  critical: {
    hex: "#D63B3B",
    label: "Critical",
    Icon: AlertTriangle,
  },
};
export const COLS = ["A", "B", "C", "D"];
export const ROWS = [1, 2, 3, 4];

export type NavKey = "dashboard" | "upload" | "history" | "alerts" | "settings";

export const NAV_ITEMS: { key: NavKey; label: string; Icon: any }[] = [
  { key: "dashboard", label: "Home", Icon: Home },
  { key: "upload", label: "Upload", Icon: UploadCloud },
  { key: "history", label: "History", Icon: History },
  { key: "alerts", label: "Alerts", Icon: Bell },
  { key: "settings", label: "Settings", Icon: Settings },
];
