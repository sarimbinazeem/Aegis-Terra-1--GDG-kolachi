import AsyncStorage from "@react-native-async-storage/async-storage";
import { useEffect, useState } from "react";

export type Language = "English" | "Urdu";

const LANGUAGE_KEY = "@aegis_terra_language";

type TranslationKeys = {
  home: string;
  upload: string;
  history: string;
  alerts: string;
  settings: string;

  farmHealth: string;
  noAnalysis: string;
  uploadCropImage: string;
  recommendation: string;
  fieldMap: string;
  tapPlot: string;
  noAlerts: string;
  cropHealthy: string;
  detectedIssues: string;

  selectDroneImages: string;
  browsePhotoLibrary: string;
  queued: string;
  analyzeImage: string;
  uploadSuccessful: string;
  uploadFailed: string;
  batchUploadNote: string;

  loadingHistory: string;
  noFlightHistory: string;
  completedAnalyses: string;
  issuesFlagged: string;

  loadingAlerts: string;
  noActiveAlerts: string;
  fieldFullyHealthy: string;

  plot: string;
  confidence: string;
  exg: string;
  close: string;

  offlineMode: string;
};

export const translations: Record<Language, TranslationKeys> = {
  English: {
    home: "Home",
    upload: "Upload",
    history: "History",
    alerts: "Alerts",
    settings: "Settings",

    farmHealth: "FARM HEALTH",
    noAnalysis: "No analysis yet",
    uploadCropImage: "Upload a crop image to begin the analysis.",
    recommendation: "Recommendation",
    fieldMap: "Field Map",
    tapPlot: "Tap a plot",
    noAlerts: "No Alerts",
    cropHealthy: "Crop looks healthy.",
    detectedIssues: "Detected Issues",

    selectDroneImages: "Select drone images",
    browsePhotoLibrary: "Tap to browse your photo library",
    queued: "Queued",
    analyzeImage: "Analyze Image",
    uploadSuccessful: "Upload Successful!",
    uploadFailed: "Upload Failed. Make sure the backend is running.",
    batchUploadNote:
      "Batch upload for full drone flights is coming soon. This screen currently prepares images for the single-image dev endpoint.",

    loadingHistory: "Loading flight history...",
    noFlightHistory: "No flight history yet",
    completedAnalyses: "Completed crop analyses will appear here.",
    issuesFlagged: "issue(s) flagged",

    loadingAlerts: "Loading alerts...",
    noActiveAlerts: "No active alerts.",
    fieldFullyHealthy: "Field is fully healthy.",

    plot: "Plot",
    confidence: "Confidence",
    exg: "ExG",
    close: "Close",

    offlineMode: "Offline mode — showing saved farm data",
  },

  Urdu: {
    home: "ہوم",
    upload: "اپ لوڈ",
    history: "تاریخ",
    alerts: "الرٹس",
    settings: "سیٹنگز",

    farmHealth: "فصل کی صحت",
    noAnalysis: "ابھی کوئی تجزیہ نہیں",
    uploadCropImage: "تجزیہ شروع کرنے کے لیے فصل کی تصویر اپ لوڈ کریں۔",
    recommendation: "تجویز",
    fieldMap: "کھیت کا نقشہ",
    tapPlot: "پلاٹ منتخب کریں",
    noAlerts: "کوئی الرٹ نہیں",
    cropHealthy: "فصل صحت مند نظر آ رہی ہے۔",
    detectedIssues: "شناخت شدہ مسائل",

    selectDroneImages: "ڈرون کی تصاویر منتخب کریں",
    browsePhotoLibrary: "تصاویر دیکھنے کے لیے ٹیپ کریں",
    queued: "قطار میں شامل",
    analyzeImage: "تصویر کا تجزیہ کریں",
    uploadSuccessful: "اپ لوڈ کامیاب!",
    uploadFailed: "اپ لوڈ ناکام۔ یقینی بنائیں کہ بیک اینڈ چل رہا ہے۔",
    batchUploadNote:
      "مکمل ڈرون فلائٹ کے لیے بیچ اپ لوڈ جلد دستیاب ہوگا۔ فی الحال یہ اسکرین ایک تصویر کے ڈیولپمنٹ اینڈ پوائنٹ کے لیے تیار کرتی ہے۔",

    loadingHistory: "فلائٹ کی تاریخ لوڈ ہو رہی ہے...",
    noFlightHistory: "ابھی کوئی فلائٹ ہسٹری نہیں",
    completedAnalyses: "مکمل فصل کے تجزیے یہاں ظاہر ہوں گے۔",
    issuesFlagged: "مسئلہ/مسائل کی نشاندہی ہوئی",

    loadingAlerts: "الرٹس لوڈ ہو رہے ہیں...",
    noActiveAlerts: "کوئی فعال الرٹ نہیں۔",
    fieldFullyHealthy: "کھیت مکمل طور پر صحت مند ہے۔",

    plot: "پلاٹ",
    confidence: "اعتماد",
    exg: "ExG",
    close: "بند کریں",

    offlineMode: "آف لائن موڈ — محفوظ شدہ کھیت کا ڈیٹا دکھایا جا رہا ہے",
  },
};

let currentLanguage: Language = "English";

const listeners = new Set<(language: Language) => void>();

export async function getLanguage(): Promise<Language> {
  try {
    const stored = await AsyncStorage.getItem(LANGUAGE_KEY);

    if (stored === "Urdu" || stored === "English") {
      currentLanguage = stored;
    }
  } catch (error) {
    console.error("Language loading error:", error);
  }

  return currentLanguage;
}

export async function setLanguage(language: Language) {
  currentLanguage = language;

  await AsyncStorage.setItem(
    LANGUAGE_KEY,
    language,
  );

  listeners.forEach((listener) => {
    listener(language);
  });
}

export function subscribeLanguage(
  listener: (language: Language) => void,
) {
  listeners.add(listener);

  return () => {
    listeners.delete(listener);
  };
}

export function useLanguage() {
  const [language, setLanguageState] =
    useState<Language>(currentLanguage);

  useEffect(() => {
    let mounted = true;

    getLanguage().then((lang) => {
      if (mounted) {
        setLanguageState(lang);
      }
    });

    const unsubscribe =
      subscribeLanguage((lang) => {
        setLanguageState(lang);
      });

    return () => {
      mounted = false;
      unsubscribe();
    };
  }, []);

  return {
    language,
    t: translations[language],
  };
}