import React, {
  useEffect,
  useState,
} from "react";

import {
  setLanguage as saveAppLanguage,
  type Language,
} from "../translations";

import {
  View,
  Text,
  Pressable,
  TextInput,
  Switch,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";

import {
  Bell,
  Globe,
  Users,
  Info,
  LogOut,
  ChevronRight,
  Save,
  MapPin,
  Sprout,
} from "lucide-react-native";

import { COLORS } from "../theme";

import {
  SectionCard,
} from "../components/Shared";

import {
  getFarm,
  updateFarm,
  Farm,
} from "../services/api";


const FARM_ID = "AT1-DEMO";


type RowProps = {
  Icon: any;
  label: string;
  control: React.ReactNode;
  onPress?: () => void;
};


function Row({
  Icon,
  label,
  control,
  onPress,
}: RowProps) {

  return (
    <Pressable
      style={styles.row}
      onPress={onPress}
      disabled={!onPress}
    >

      <View style={styles.rowLeft}>

        <Icon
          size={19}
          color={COLORS.fieldGreenDeep}
        />

        <Text style={styles.rowLabel}>
          {label}
        </Text>

      </View>

      {control}

    </Pressable>
  );
}


export default function SettingsScreen({
  language,
  setLanguage,
}: {
  language: string;
  setLanguage: (language: string) => void;
}) {

  

  const [
    notifications,
    setNotifications,
  ] = useState(true);


  const [
    units,
    setUnits,
  ] = useState<
    "metric" | "imperial"
  >("metric");


  const [farmName, setFarmName] =
    useState("");

  const [loadingFarm, setLoadingFarm] =
    useState(true);

  const [savingFarm, setSavingFarm] =
    useState(false);


  const [
    crop,
    setCrop,
  ] = useState("");




  const [
    latitude,
    setLatitude,
  ] = useState("");


  const [
    longitude,
    setLongitude,
  ] = useState("");


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    saving,
    setSaving,
  ] = useState(false);


  /* =====================================================
     Load farm
     ===================================================== */

  useEffect(() => {

    loadFarm();

  }, []);


  async function loadFarm() {

    try {

      setLoading(true);

      const farm =
        await getFarm(
          FARM_ID,
        );

      populateFarm(
        farm,
      );

    } catch (error) {

      console.error(
        "Farm loading error:",
        error,
      );

      Alert.alert(
        "Farm Profile",
        "Could not load the farm profile.",
      );

    } finally {

      setLoading(false);

    }
  }


  function populateFarm(
    farm: Farm,
  ) {

    setFarmName(
      farm.name ?? "",
    );

    setCrop(
      farm.crop ?? "",
    );

    setLatitude(
      farm.latitude !== null
        ? String(farm.latitude)
        : "",
    );

    setLongitude(
      farm.longitude !== null
        ? String(farm.longitude)
        : "",
    );
  }


  /* =====================================================
     Save farm
     ===================================================== */

  async function handleSave() {

    if (!farmName.trim()) {

      Alert.alert(
        "Farm Name Required",
        "Please enter a farm name.",
      );

      return;
    }


    try {

      setSaving(true);


      const lat =
        latitude.trim()
          ? Number(latitude)
          : null;


      const lon =
        longitude.trim()
          ? Number(longitude)
          : null;


      if (
        lat !== null &&
        Number.isNaN(lat)
      ) {

        Alert.alert(
          "Invalid Latitude",
          "Please enter a valid latitude.",
        );

        return;
      }


      if (
        lon !== null &&
        Number.isNaN(lon)
      ) {

        Alert.alert(
          "Invalid Longitude",
          "Please enter a valid longitude.",
        );

        return;
      }


      await updateFarm(
        FARM_ID,
        {
          name:
            farmName.trim(),

          crop:
            crop.trim() ||
            "Unknown",

          language:
            language.trim() ||
            "English",

          latitude: lat,

          longitude: lon,
        },
      );
      const selectedLanguage =
        language.trim() === "Urdu"
          ? "Urdu"
          : "English";

      await saveAppLanguage(
        selectedLanguage as Language,
      );

      Alert.alert(
        "Saved",
        "Farm profile updated successfully.",
      );

    } catch (error) {

      console.error(
        "Farm saving error:",
        error,
      );

      Alert.alert(
        "Save Failed",
        "Could not save the farm profile.",
      );

    } finally {

      setSaving(false);

    }
  }


  const showTeamAccess =
    () => {

      Alert.alert(
        "Team Access",
        "Team management will be available in a future version of Aegis-Terra.",
      );

    };


  const showAbout =
    () => {

      Alert.alert(
        "Aegis-Terra",
        "Aegis-Terra is a low-cost aerial crop inspection system designed to help smallholder farmers identify crop health issues using image analysis, vegetation indices, grid-based analysis and AI detection.",
      );

    };


  const handleSignOut =
    () => {

      Alert.alert(
        "Sign Out",
        "There is no account session to sign out of in the current demo.",
        [
          {
            text: "Cancel",
            style: "cancel",
          },
          {
            text: "OK",
          },
        ],
      );

    };


  if (loading) {

    return (
      <View style={styles.loading}>

        <ActivityIndicator
          size="large"
          color={
            COLORS.fieldGreen
          }
        />

        <Text
          style={
            styles.loadingText
          }
        >
          Loading farm profile...
        </Text>

      </View>
    );
  }


  return (

    <ScrollView
      contentContainerStyle={{
        paddingBottom: 24,
      }}
      showsVerticalScrollIndicator={
        false
      }
    >

      {/* =================================================
          FARM PROFILE
          ================================================= */}

      <SectionCard
        style={{
          marginBottom: 18,
        }}
      >

        <View
          style={
            styles.sectionTitle
          }
        >

          <Sprout
            size={20}
            color={
              COLORS.fieldGreenDeep
            }
          />

          <Text
            style={
              styles.sectionTitleText
            }
          >
            Farm Profile
          </Text>

        </View>


        <Text
          style={
            styles.fieldLabel
          }
        >
          FARM ID
        </Text>

        <View
          style={
            styles.readOnlyBox
          }
        >

          <Text
            style={
              styles.readOnlyText
            }
          >
            {FARM_ID}
          </Text>

        </View>


        <Text
          style={
            styles.fieldLabel
          }
        >
          FARM NAME
        </Text>

        <View style={styles.languageToggle}>
          {["English", "Urdu"].map((item) => {
            const selected = language === item;

            return (
              <Pressable
                key={item}
                onPress={() => setLanguage(item)}
                style={[
                  styles.languageButton,
                  selected && {
                    backgroundColor: COLORS.fieldGreen,
                  },
                ]}
              >
                <Text
                  style={[
                    styles.languageButtonText,
                    selected && {
                      color: "#fff",
                    },
                  ]}
                >
                  {item}
                </Text>
              </Pressable>
            );
          })}
        </View>


        <Text
          style={
            styles.fieldLabel
          }
        >
          CROP
        </Text>

        <TextInput
          value={crop}
          onChangeText={
            setCrop
          }
          placeholder="e.g. Wheat"
          placeholderTextColor={
            COLORS.inkSoft
          }
          style={
            styles.input
          }
        />


        <Text
          style={
            styles.fieldLabel
          }
        >
          PREFERRED LANGUAGE
        </Text>

        <TextInput
          value={language}
          onChangeText={
            setLanguage
          }
          placeholder="e.g. Urdu"
          placeholderTextColor={
            COLORS.inkSoft
          }
          style={
            styles.input
          }
        />

      </SectionCard>


      {/* =================================================
          LOCATION
          ================================================= */}

      <SectionCard
        style={{
          marginBottom: 18,
        }}
      >

        <View
          style={
            styles.sectionTitle
          }
        >

          <MapPin
            size={20}
            color={
              COLORS.fieldGreenDeep
            }
          />

          <Text
            style={
              styles.sectionTitleText
            }
          >
            Farm Location
          </Text>

        </View>


        <Text
          style={
            styles.helperText
          }
        >
          GPS coordinates allow Aegis-Terra
          to retrieve local environmental
          information later.
        </Text>


        <Text
          style={
            styles.fieldLabel
          }
        >
          LATITUDE
        </Text>

        <TextInput
          value={latitude}
          onChangeText={
            setLatitude
          }
          placeholder="e.g. 24.8607"
          placeholderTextColor={
            COLORS.inkSoft
          }
          keyboardType="numeric"
          style={
            styles.input
          }
        />


        <Text
          style={
            styles.fieldLabel
          }
        >
          LONGITUDE
        </Text>

        <TextInput
          value={longitude}
          onChangeText={
            setLongitude
          }
          placeholder="e.g. 67.0011"
          placeholderTextColor={
            COLORS.inkSoft
          }
          keyboardType="numeric"
          style={
            styles.input
          }
        />


        <Pressable
          style={
            styles.saveButton
          }
          onPress={
            handleSave
          }
          disabled={saving}
        >

          {saving ? (

            <ActivityIndicator
              color="#fff"
            />

          ) : (

            <>
              <Save
                size={18}
                color="#fff"
              />

              <Text
                style={
                  styles.saveText
                }
              >
                Save Farm Profile
              </Text>
            </>

          )}

        </Pressable>

      </SectionCard>


      {/* =================================================
          OTHER SETTINGS
          ================================================= */}

      <SectionCard>

        <Row
          Icon={Bell}
          label="Push Notifications"
          control={
            <Switch
              value={
                notifications
              }
              onValueChange={
                setNotifications
              }
              trackColor={{
                true:
                  COLORS.fieldGreen,
                false:
                  COLORS.line,
              }}
              thumbColor="#fff"
            />
          }
        />


        <Row
          Icon={Globe}
          label="Units"
          control={

            <View
              style={
                styles.unitToggle
              }
            >

              {(
                [
                  "metric",
                  "imperial",
                ] as const
              ).map(
                (unit) => {

                  const selected =
                    units === unit;

                  return (

                    <Pressable
                      key={unit}
                      onPress={() =>
                        setUnits(
                          unit,
                        )
                      }
                      style={[
                        styles.unitButton,
                        selected && {
                          backgroundColor:
                            COLORS.fieldGreen,
                        },
                      ]}
                    >

                      <Text
                        style={[
                          styles.unitButtonText,
                          selected && {
                            color:
                              "#fff",
                          },
                        ]}
                      >
                        {unit}
                      </Text>

                    </Pressable>

                  );
                },
              )}

            </View>

          }
        />


        <Row
          Icon={Users}
          label="Team Access"
          control={
            <ChevronRight
              size={17}
              color={
                COLORS.inkSoft
              }
            />
          }
          onPress={
            showTeamAccess
          }
        />


        <Row
          Icon={Info}
          label="About Aegis-Terra"
          control={
            <ChevronRight
              size={17}
              color={
                COLORS.inkSoft
              }
            />
          }
          onPress={
            showAbout
          }
        />


        <Pressable
          style={
            styles.signOutRow
          }
          onPress={
            handleSignOut
          }
        >

          <View
            style={
              styles.rowLeft
            }
          >

            <LogOut
              size={19}
              color="#D63B3B"
            />

            <Text
              style={[
                styles.rowLabel,
                {
                  color:
                    "#D63B3B",
                },
              ]}
            >
              Sign Out
            </Text>

          </View>

        </Pressable>

      </SectionCard>


      <Text
        style={
          styles.version
        }
      >
        Aegis-Terra · Demo Build
      </Text>

    </ScrollView>
  );
}


const styles =
  StyleSheet.create({

    loading: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
    },

    loadingText: {
      marginTop: 10,
      color:
        COLORS.inkSoft,
      fontWeight: "600",
    },

    sectionTitle: {
      flexDirection:
        "row",
      alignItems:
        "center",
      justifyContent:
        "center",
      gap: 8,
      marginBottom: 18,
    },

    sectionTitleText: {
      fontSize: 17,
      fontWeight: "800",
      color:
        COLORS.fieldGreenDeep,
    },

    fieldLabel: {
      fontSize: 11,
      fontWeight: "700",
      color:
        COLORS.inkSoft,
      textAlign: "center",
      marginTop: 10,
      marginBottom: 8,
      letterSpacing: 0.5,
    },

    input: {
      backgroundColor:
        COLORS.paper,
      borderColor:
        COLORS.line,
      borderWidth: 1,
      borderRadius: 16,
      paddingVertical: 12,
      paddingHorizontal: 14,
      textAlign: "center",
      fontSize: 16,
      fontWeight: "800",
      color:
        COLORS.fieldGreenDeep,
    },

    readOnlyBox: {
      backgroundColor:
        COLORS.paper,
      borderColor:
        COLORS.line,
      borderWidth: 1,
      borderRadius: 16,
      paddingVertical: 12,
      alignItems: "center",
    },

    readOnlyText: {
      fontSize: 16,
      fontWeight: "800",
      color:
        COLORS.inkSoft,
    },

    helperText: {
      marginBottom: 10,
      textAlign: "center",
      fontSize: 11,
      fontWeight: "600",
      color:
        COLORS.inkSoft,
      lineHeight: 17,
    },

    saveButton: {
      marginTop: 18,
      flexDirection:
        "row",
      alignItems:
        "center",
      justifyContent:
        "center",
      gap: 8,
      backgroundColor:
        COLORS.fieldGreenDeep,
      borderRadius: 16,
      paddingVertical: 14,
    },

    saveText: {
      color: "#fff",
      fontSize: 14,
      fontWeight: "800",
    },

    row: {
      flexDirection:
        "row",
      alignItems:
        "center",
      justifyContent:
        "space-between",
      paddingVertical: 14,
      borderBottomWidth: 1,
      borderBottomColor:
        COLORS.line,
    },

    rowLeft: {
      flexDirection:
        "row",
      alignItems:
        "center",
      gap: 10,
      flex: 1,
    },

    rowLabel: {
      fontSize: 15,
      fontWeight: "600",
      color:
        COLORS.ink,
    },

    unitToggle: {
      flexDirection:
        "row",
      borderRadius: 999,
      borderWidth: 1,
      borderColor:
        COLORS.line,
      overflow:
        "hidden",
    },

    unitButton: {
      paddingHorizontal: 14,
      paddingVertical: 6,
    },

    unitButtonText: {
      fontSize: 11,
      fontWeight: "800",
      color:
        COLORS.inkSoft,
      textTransform:
        "capitalize",
    },

    signOutRow: {
      flexDirection:
        "row",
      alignItems:
        "center",
      justifyContent:
        "space-between",
      paddingVertical: 14,
    },

    version: {
      textAlign: "center",
      marginTop: 18,
      fontSize: 11,
      fontWeight: "600",
      color:
        COLORS.inkSoft,
    },

    languageToggle: {
      flexDirection: "row",
      borderWidth: 1,
      borderColor: COLORS.line,
      borderRadius: 16,
      overflow: "hidden",
    },

    languageButton: {
      flex: 1,
      paddingVertical: 12,
      alignItems: "center",
    },

    languageButtonText: {
      fontSize: 14,
      fontWeight: "800",
      color: COLORS.inkSoft,
    },

  });