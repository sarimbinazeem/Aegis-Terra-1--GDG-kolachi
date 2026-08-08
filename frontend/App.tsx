import React, { useEffect, useState } from "react";
import {
View,
StyleSheet,
ActivityIndicator,
} from "react-native";

import AsyncStorage from "@react-native-async-storage/async-storage";

import {
SafeAreaProvider,
SafeAreaView,
} from "react-native-safe-area-context";

import { COLORS, NavKey } from "./theme";

import BottomNav from "./components/BottomNav";
import DetailModal from "./components/DetailModal";

import DashboardScreen from "./screens/DashboardScreen";
import UploadScreen from "./screens/UploadScreen";
import HistoryScreen from "./screens/HistoryScreen";
import AlertsScreen from "./screens/AlertsScreen";
import SettingsScreen from "./screens/SettingsScreen";
import FarmSetupScreen from "./screens/FarmSetupScreen";

import {
getFarm,
type AnalysisData,
type Cell,
} from "./services/api";

const SETUP_KEY = "farm_setup_complete";
const LANGUAGE_KEY = "app_language";

export default function App() {
const [setupComplete, setSetupComplete] =
useState<boolean | null>(null);

const [active, setActive] =
useState<NavKey>("dashboard");

const [selected, setSelected] =
useState<Cell | null>(null);

const [analysisData, setAnalysisData] =
useState<AnalysisData | null>(null);

const [language, setLanguage] =
useState("English");

// =========================================================
// LOAD APP SETTINGS + CHECK FARM
// =========================================================

useEffect(() => {
const initializeApp = async () => {
try {
const savedLanguage =
await AsyncStorage.getItem(
LANGUAGE_KEY
);

    setLanguage(
      savedLanguage ?? "English"
    );

    /*
     * IMPORTANT:
     * The backend is now the source of truth
     * for whether a farm exists.
     */

    try {
      const farm =
        await getFarm("AT1-DEMO");

      console.log(
        "APP STARTUP FARM:",
        farm
      );

      /*
       * Farm exists.
       * Make sure local setup flag is also synced.
       */

      await AsyncStorage.setItem(
        SETUP_KEY,
        "true"
      );

      setSetupComplete(true);

    } catch (farmError: any) {
      console.error(
        "APP STARTUP FARM CHECK FAILED:",
        farmError
      );

      /*
       * If backend specifically says farm
       * does not exist, show setup screen.
       */

      const message =
        farmError?.message ?? "";

      if (
        message.includes("404") ||
        message
          .toLowerCase()
          .includes("farm not found")
      ) {
        await AsyncStorage.removeItem(
          SETUP_KEY
        );

        setSetupComplete(false);

        return;
      }

      /*
       * Backend/network unavailable.
       * Fall back to local setup state.
       */

      const setup =
        await AsyncStorage.getItem(
          SETUP_KEY
        );

      setSetupComplete(
        setup === "true"
      );
    }

  } catch (error) {
    console.error(
      "Settings loading error:",
      error
    );

    /*
     * Final fallback.
     */

    try {
      const setup =
        await AsyncStorage.getItem(
          SETUP_KEY
        );

      setSetupComplete(
        setup === "true"
      );
    } catch {
      setSetupComplete(false);
    }
  }
};

initializeApp();

}, []);

// =========================================================
// LANGUAGE
// =========================================================

const handleLanguageChange = async (
newLanguage: string
) => {
setLanguage(newLanguage);

try {
  await AsyncStorage.setItem(
    LANGUAGE_KEY,
    newLanguage
  );
} catch (error) {
  console.error(
    "Language save error:",
    error
  );
}

};

// =========================================================
// FARM SETUP COMPLETE
// =========================================================

const handleSetupComplete = async () => {
try {
await AsyncStorage.setItem(
SETUP_KEY,
"true"
);
} catch (error) {
console.error(
"Setup state save error:",
error
);
}

setSetupComplete(true);
setActive("dashboard");

};

// =========================================================
// LOADING
// =========================================================

if (setupComplete === null) {
return (
<SafeAreaProvider>
<SafeAreaView
style={styles.root}
edges={["top"]}
>
<View
style={
styles.loadingContainer
}
>
<ActivityIndicator
size="large"
color={
COLORS.fieldGreenDeep
}
/>
</View>
</SafeAreaView>
</SafeAreaProvider>
);
}

// =========================================================
// FARM SETUP
// =========================================================

if (!setupComplete) {
return (
<SafeAreaProvider>
<SafeAreaView
style={styles.root}
edges={["top"]}
>
<FarmSetupScreen
onComplete={
handleSetupComplete
}
/>
</SafeAreaView>
</SafeAreaProvider>
);
}

// =========================================================
// MAIN SCREENS
// =========================================================

const screens: Record<
NavKey,
React.ReactNode

>= {
dashboard: (
<DashboardScreen setSelected={setSelected} analysisData={analysisData} language={language} />
),

upload: (
  <UploadScreen
    setAnalysisData={
      setAnalysisData
    }
    setActive={setActive}
    language={language}
  />
),

history: (
  <HistoryScreen
    setAnalysisData={
      setAnalysisData
    }
    setActive={setActive}
    language={language}
  />
),

alerts: (
  <AlertsScreen
    setSelected={setSelected}
    analysisData={analysisData}
    language={language}
  />
),

settings: (
  <SettingsScreen
    language={language}
    setLanguage={
      handleLanguageChange
    }
  />
),

};

return (
<SafeAreaProvider>
<SafeAreaView
style={styles.root}
edges={["top"]}
>
<View style={styles.content}>
{screens[active]}
</View>

    <BottomNav
      active={active}
      onChange={setActive}
    />

    <DetailModal
      selected={selected}
      onClose={() =>
        setSelected(null)
      }
    />
  </SafeAreaView>
</SafeAreaProvider>

);
}

const styles = StyleSheet.create({
root: {
flex: 1,
backgroundColor:
COLORS.paper,
},

content: {
flex: 1,
paddingHorizontal: 18,
paddingTop: 16,
},

loadingContainer: {
flex: 1,
alignItems: "center",
justifyContent: "center",
},
});
