import AsyncStorage from "@react-native-async-storage/async-storage";

const BASE_URL = "http://192.168.18.31:8000";

const STORAGE_KEYS = {
  LAST_ANALYSIS: "aegis_last_analysis",
  HISTORY: "aegis_history",
  ALERTS: "aegis_alerts",
  FARMS: "aegis_farms",
  DEFAULT_FARM: "aegis_default_farm",
};

export type Cell = {
  id: string;
  row: number;
  col: number;
  status: string;
  severity: string;
  confidence: number;
  exg_value: number;
  issue: string;
  recommended_action: string;
};

export type Alert = {
  id?: number;
  analysis_id?: number;
  cell: string;
  severity: string;
  message: string;
  action: string;
};

export type Detection = {
  class_id: number;
  class: string;
  confidence: number;
  bbox: number[];
};

export type AnalysisData = {
  analysis_id?: number;
  farm_id?: string;
  timestamp?: string;

  overall_health_pct: number;

  overall_status?: string;
  overall_severity?: string;
  overall_issue?: string;
  overall_recommended_action?: string;

  grid?: {
    rows: number;
    cols: number;
    cell_size_m: number;
  };

  cells: Cell[];
  alerts: Alert[];
  detections: Detection[];

  offline?: boolean;
  cached_at?: string;
};

export type HistoryItem = {
  id: number;
  date: string | null;
  health: number | null;
  plots: number;
  issues: number;
};

export type Farm = {
  id: number;
  farm_id: string;
  name: string;
  latitude: number | null;
  longitude: number | null;
  crop: string;
  language: string;
  created_at: string;
};

export type ProductizationInsights = {
  confidence: number;
  confidence_pct: number;

  comparison: {
    available: boolean;
    health_change: number;
    previous_health?: number;
    current_health?: number;
    deteriorated: boolean;
    message: string;
  };

  deterioration_alert: boolean;

  expert_escalation: boolean;
  expert_reason: string;

  rescan: {
    recommended: boolean;
    hours: number;
    recommended_at: string;
    message: string;
  };
};

async function saveLocal<T>(
  key: string,
  value: T,
): Promise<void> {
  try {
    await AsyncStorage.setItem(
      key,
      JSON.stringify(value),
    );
  } catch (error) {
    console.warn(
      "Aegis-Terra local save failed:",
      error,
    );
  }
}

async function getLocal<T>(
  key: string,
): Promise<T | null> {
  try {
    const value =
      await AsyncStorage.getItem(key);

    if (!value) {
      return null;
    }

    return JSON.parse(value) as T;
  } catch (error) {
    console.warn(
      "Aegis-Terra local read failed:",
      error,
    );

    return null;
  }
}

export function buildOfflineRecommendation(
  analysis: AnalysisData,
): {
  overall_issue: string;
  overall_recommended_action: string;
  overall_severity: string;
} {
  const health = Math.max(
    0,
    Math.min(
      100,
      analysis.overall_health_pct ?? 0,
    ),
  );

  const dryCells =
    analysis.cells.filter(
      (cell) =>
        cell.status?.toLowerCase() ===
        "dry",
    ).length;

  const diseaseCells =
    analysis.cells.filter(
      (cell) =>
        cell.status?.toLowerCase() ===
        "disease",
    ).length;

  const pestCells =
    analysis.cells.filter(
      (cell) =>
        cell.status?.toLowerCase() ===
        "pest",
    ).length;

  if (diseaseCells > 0) {
    return {
      overall_issue:
        "Possible disease stress detected.",
      overall_recommended_action:
        "Inspect the affected zones closely and seek expert advice before treatment.",
      overall_severity:
        health < 45
          ? "urgent"
          : "high",
    };
  }

  if (pestCells > 0) {
    return {
      overall_issue:
        "Possible pest pressure detected.",
      overall_recommended_action:
        "Inspect affected plants for visible pest damage.",
      overall_severity:
        health < 45
          ? "urgent"
          : "high",
    };
  }

  if (dryCells > 0) {
    return {
      overall_issue:
        "Possible water stress detected.",
      overall_recommended_action:
        "Check irrigation and water distribution in the affected zones.",
      overall_severity:
        health < 70
          ? "high"
          : "medium",
    };
  }

  if (health < 45) {
    return {
      overall_issue:
        "The crop shows significant stress.",
      overall_recommended_action:
        "Inspect the affected field zones as soon as possible.",
      overall_severity:
        "urgent",
    };
  }

  if (health < 70) {
    return {
      overall_issue:
        "The crop shows moderate stress.",
      overall_recommended_action:
        "Monitor affected zones and inspect them during the next field visit.",
      overall_severity:
        "high",
    };
  }

  if (health < 85) {
    return {
      overall_issue:
        "Some crop stress may be present.",
      overall_recommended_action:
        "Continue monitoring and rescan the affected area.",
      overall_severity:
        "medium",
    };
  }

  return {
    overall_issue:
      "Crop appears mostly healthy.",
    overall_recommended_action:
      "Continue normal monitoring and rescan if conditions change.",
    overall_severity:
      "low",
  };
}

export async function uploadImage(
  image: any,
): Promise<AnalysisData> {
  const formData = new FormData();

  formData.append(
    "image",
    {
      uri: image.uri,
      name: image.fileName ?? "image.jpg",
      type: image.mimeType ?? "image/jpeg",
    } as any,
  );

  console.log("=================================");
  console.log("UPLOAD IMAGE");
  console.log("URI:", image.uri);
  console.log("NAME:", image.fileName);
  console.log("TYPE:", image.mimeType);
  console.log("POST:", `${BASE_URL}/upload`);
  console.log("=================================");

  try {
    const response = await fetch(
      `${BASE_URL}/upload`,
      {
        method: "POST",
        body: formData,
      },
    );

    console.log(
      "UPLOAD STATUS:",
      response.status,
    );

    const responseText =
      await response.text();

    console.log(
      "UPLOAD RESPONSE:",
      responseText,
    );

    if (!response.ok) {
      throw new Error(
        `Upload failed: ${response.status} - ${responseText}`,
      );
    }

    let result: AnalysisData;

    try {
      result =
        JSON.parse(responseText) as AnalysisData;
    } catch {
      throw new Error(
        "Backend returned invalid JSON.",
      );
    }

    console.log(
      "UPLOAD ANALYSIS RESULT:",
      result,
    );

    const cachedResult: AnalysisData = {
      ...result,
      offline: false,
      cached_at:
        new Date().toISOString(),
    };

    await saveLocal(
      STORAGE_KEYS.LAST_ANALYSIS,
      cachedResult,
    );

    return cachedResult;
  } catch (error) {
    console.error(
      "UPLOAD REQUEST FAILED:",
      error,
    );

    /*
     * IMPORTANT:
     *
     * Do NOT silently return the previous analysis here.
     *
     * If the upload fails, showing the previous cached
     * analysis makes a completely different image appear
     * to have the previous image's health score.
     */

    throw error instanceof Error
      ? error
      : new Error(
          "Unable to upload image.",
        );
  }
}
export async function getCachedAnalysis(): Promise<
  AnalysisData | null
> {
  const cached =
    await getLocal<AnalysisData>(
      STORAGE_KEYS.LAST_ANALYSIS,
    );

  if (!cached) {
    return null;
  }

  return {
    ...cached,
    ...buildOfflineRecommendation(
      cached,
    ),
    offline: true,
  };
}

export async function getHistory(): Promise<
  HistoryItem[]
> {
  try {
    const response =
      await fetch(
        `${BASE_URL}/history`,
      );

    if (!response.ok) {
      throw new Error(
        "Failed to fetch history.",
      );
    }

    const result =
      (await response.json()) as HistoryItem[];

    await saveLocal(
      STORAGE_KEYS.HISTORY,
      result,
    );

    return result;
  } catch {
    return (
      (await getLocal<
        HistoryItem[]
      >(
        STORAGE_KEYS.HISTORY,
      )) ?? []
    );
  }
}

export async function getHistoryDetail(
  id: number,
): Promise<AnalysisData> {
  try {
    const response =
      await fetch(
        `${BASE_URL}/history/${id}`,
      );

    if (!response.ok) {
      throw new Error(
        "Failed to fetch analysis history.",
      );
    }

    const result =
      (await response.json()) as AnalysisData;

    await saveLocal(
      STORAGE_KEYS.LAST_ANALYSIS,
      result,
    );

    return result;
  } catch (error) {
    const cached =
      await getLocal<AnalysisData>(
        STORAGE_KEYS.LAST_ANALYSIS,
      );

    if (cached) {
      return {
        ...cached,
        offline: true,
      };
    }

    throw error;
  }
}

export async function getAlerts(): Promise<
  Alert[]
> {
  try {
    const response =
      await fetch(
        `${BASE_URL}/alerts`,
      );

    if (!response.ok) {
      throw new Error(
        "Failed to fetch alerts.",
      );
    }

    const result =
      (await response.json()) as Alert[];

    await saveLocal(
      STORAGE_KEYS.ALERTS,
      result,
    );

    return result;
  } catch {
    return (
      (await getLocal<Alert[]>(
        STORAGE_KEYS.ALERTS,
      )) ?? []
    );
  }
}

export async function getHealth() {
  try {
    const response =
      await fetch(
        `${BASE_URL}/health`,
      );

    if (!response.ok) {
      throw new Error();
    }

    return response.json();
  } catch {
    return {
      status: "offline",
      offline: true,
    };
  }
}

export async function getFarms(): Promise<
  Farm[]
> {
  try {
    const response =
      await fetch(
        `${BASE_URL}/farms`,
      );

    if (!response.ok) {
      throw new Error();
    }

    const result =
      (await response.json()) as Farm[];

    await saveLocal(
      STORAGE_KEYS.FARMS,
      result,
    );

    return result;
  } catch {
    return (
      (await getLocal<Farm[]>(
        STORAGE_KEYS.FARMS,
      )) ?? []
    );
  }
}

export async function getFarm(
  farmId: string,
): Promise<Farm> {
  try {
    console.log(
      "GET FARM:",
      `${BASE_URL}/farms/${farmId}`,
    );

    const response = await fetch(
      `${BASE_URL}/farms/${farmId}`,
    );

    console.log(
      "GET FARM STATUS:",
      response.status,
    );

    if (!response.ok) {
      throw new Error(
        `Farm not found: ${response.status}`,
      );
    }

    const result =
      (await response.json()) as Farm;

    console.log(
      "GET FARM RESULT:",
      result,
    );

    await saveLocal(
      STORAGE_KEYS.DEFAULT_FARM,
      result,
    );

    return result;

  } catch (error) {
    console.error(
      "GET FARM FAILED:",
      error,
    );

    throw error;
  }
}

export async function createFarm(
  farm: {
    farm_id: string;
    name: string;
    latitude?: number | null;
    longitude?: number | null;
    crop: string;
    language: string;
  },
): Promise<Farm> {
  const response =
    await fetch(
      `${BASE_URL}/farms`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body:
          JSON.stringify(farm),
      },
    );

  if (!response.ok) {
    throw new Error(
      "Failed to create farm.",
    );
  }

  const result =
    (await response.json()) as Farm;

  await saveLocal(
    STORAGE_KEYS.DEFAULT_FARM,
    result,
  );

  return result;
}

export async function updateFarm(
  farmId: string,
  farm: {
    name?: string;
    latitude?: number | null;
    longitude?: number | null;
    crop?: string;
    language?: string;
  },
): Promise<Farm> {
  const response =
    await fetch(
      `${BASE_URL}/farms/${farmId}`,
      {
        method: "PUT",

        headers: {
          "Content-Type":
            "application/json",
        },

        body:
          JSON.stringify(farm),
      },
    );

  if (!response.ok) {
    throw new Error(
      "Failed to update farm.",
    );
  }

  const result =
    (await response.json()) as Farm;

  await saveLocal(
    STORAGE_KEYS.DEFAULT_FARM,
    result,
  );

  return result;
}

export async function getDefaultFarm(): Promise<Farm> {
  return getFarm("AT1-DEMO");
}

/* =========================================================
   Phase 10
   ========================================================= */

export async function getAnalysisInsights(
  analysisId: number,
): Promise<ProductizationInsights> {
  const response =
    await fetch(
      `${BASE_URL}/analysis/${analysisId}/insights`,
    );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch analysis insights.",
    );
  }

  return response.json();
}

export async function submitAnalysisFeedback(
  analysisId: number,
  rating: number,
  comment: string = "",
) {
  const response =
    await fetch(
      `${BASE_URL}/analysis/${analysisId}/feedback`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body: JSON.stringify({
          rating,
          comment,
        }),
      },
    );

  if (!response.ok) {
    throw new Error(
      "Failed to submit feedback.",
    );
  }

  return response.json();
}

export async function hasOfflineData(): Promise<boolean> {
  const analysis =
    await getLocal<AnalysisData>(
      STORAGE_KEYS.LAST_ANALYSIS,
    );

  return analysis !== null;
}