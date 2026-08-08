import React, { useState } from "react";
import {
  View,
  Text,
  Pressable,
  TextInput,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";
import * as Location from "expo-location";

import { MapPin, Check, ChevronDown } from "lucide-react-native";

import { COLORS } from "../theme";
import { createFarm } from "../services/api";

type Props = {
  onComplete: () => void;
};

const CROPS = [
  "Wheat",
  "Rice",
  "Maize",
  "Cotton",
  "Sugarcane",
  "Tomato",
  "Potato",
  "Other",
];

const LANGUAGES = [
  "English",
  "Urdu",
  "Sindhi",
  "Punjabi",
  "Pashto",
];

export default function FarmSetupScreen({
  onComplete,
}: Props) {
  const [farmName, setFarmName] =
    useState("AT1-DEMO Farm");

  const [crop, setCrop] =
    useState("Wheat");

  const [language, setLanguage] =
    useState("English");

  const [latitude, setLatitude] =
    useState<number | null>(null);

  const [longitude, setLongitude] =
    useState<number | null>(null);

  const [locationLoading, setLocationLoading] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [showCrops, setShowCrops] =
    useState(false);

  const [showLanguages, setShowLanguages] =
    useState(false);


  const getLocation = async () => {
    try {
      setLocationLoading(true);

      const { status } =
        await Location.requestForegroundPermissionsAsync();

      if (status !== "granted") {
        Alert.alert(
          "Location Permission",
          "Location permission is needed to automatically associate your farm with its location."
        );

        return;
      }

      const location =
        await Location.getCurrentPositionAsync({
          accuracy:
            Location.Accuracy.Balanced,
        });

      setLatitude(
        location.coords.latitude
      );

      setLongitude(
        location.coords.longitude
      );

    } catch (error) {
      Alert.alert(
        "Location Error",
        "Unable to get your current location. You can try again."
      );
    } finally {
      setLocationLoading(false);
    }
  };


  const handleCreateFarm = async () => {
    if (!farmName.trim()) {
      Alert.alert(
        "Farm Name Required",
        "Please enter a name for your farm."
      );

      return;
    }

    if (latitude === null || longitude === null) {
      Alert.alert(
        "Location Required",
        "Please use your current location before continuing."
      );

      return;
    }

    try {
      setSaving(true);

      await createFarm({
        farm_id: "AT1-DEMO",
        name: farmName.trim(),
        latitude,
        longitude,
        crop,
        language,
      });

      onComplete();

    } catch (error: any) {
      Alert.alert(
        "Unable to Save Farm",
        error?.message ??
          "Something went wrong while creating your farm."
      );
    } finally {
      setSaving(false);
    }
  };


  return (
    <ScrollView
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >

      <View style={styles.header}>
        <Text style={styles.eyebrow}>
          WELCOME TO AEGIS-TERRA
        </Text>

        <Text style={styles.title}>
          Create your farm
        </Text>

        <Text style={styles.subtitle}>
          Tell us a few basic things about your farm.
          Aegis-Terra will use this information to
          provide more relevant crop insights.
        </Text>
      </View>


      {/* FARM NAME */}

      <View style={styles.card}>

        <Text style={styles.label}>
          Farm Name
        </Text>

        <TextInput
          value={farmName}
          onChangeText={setFarmName}
          placeholder="Enter farm name"
          placeholderTextColor={
            COLORS.inkSoft
          }
          style={styles.input}
        />

      </View>


      {/* CROP */}

      <View style={styles.card}>

        <Text style={styles.label}>
          Crop
        </Text>

        <Pressable
          style={styles.selector}
          onPress={() =>
            setShowCrops(!showCrops)
          }
        >
          <Text style={styles.selectorText}>
            {crop}
          </Text>

          <ChevronDown
            size={19}
            color={COLORS.inkSoft}
          />
        </Pressable>


        {showCrops && (
          <View style={styles.optionsBox}>

            {CROPS.map((item) => (

              <Pressable
                key={item}
                style={styles.option}
                onPress={() => {
                  setCrop(item);
                  setShowCrops(false);
                }}
              >

                <Text
                  style={[
                    styles.optionText,
                    item === crop && {
                      color:
                        COLORS.fieldGreenDeep,
                      fontWeight: "800",
                    },
                  ]}
                >
                  {item}
                </Text>

                {item === crop && (
                  <Check
                    size={17}
                    color={
                      COLORS.fieldGreenDeep
                    }
                  />
                )}

              </Pressable>

            ))}

          </View>
        )}

      </View>


      {/* LANGUAGE */}

      <View style={styles.card}>

        <Text style={styles.label}>
          Preferred Language
        </Text>

        <Pressable
          style={styles.selector}
          onPress={() =>
            setShowLanguages(
              !showLanguages
            )
          }
        >

          <Text style={styles.selectorText}>
            {language}
          </Text>

          <ChevronDown
            size={19}
            color={COLORS.inkSoft}
          />

        </Pressable>


        {showLanguages && (
          <View style={styles.optionsBox}>

            {LANGUAGES.map((item) => (

              <Pressable
                key={item}
                style={styles.option}
                onPress={() => {
                  setLanguage(item);
                  setShowLanguages(false);
                }}
              >

                <Text
                  style={[
                    styles.optionText,
                    item === language && {
                      color:
                        COLORS.fieldGreenDeep,
                      fontWeight: "800",
                    },
                  ]}
                >
                  {item}
                </Text>

                {item === language && (
                  <Check
                    size={17}
                    color={
                      COLORS.fieldGreenDeep
                    }
                  />
                )}

              </Pressable>

            ))}

          </View>
        )}

      </View>


      {/* LOCATION */}

      <View style={styles.card}>

        <Text style={styles.label}>
          Farm Location
        </Text>

        <Pressable
          style={[
            styles.locationButton,
            latitude !== null &&
              styles.locationButtonSuccess,
          ]}
          onPress={getLocation}
          disabled={locationLoading}
        >

          {locationLoading ? (
            <ActivityIndicator
              color={
                COLORS.fieldGreenDeep
              }
            />
          ) : (
            <MapPin
              size={20}
              color={
                COLORS.fieldGreenDeep
              }
            />
          )}

          <Text
            style={
              styles.locationButtonText
            }
          >
            {locationLoading
              ? "Getting location..."
              : latitude !== null
              ? "Location captured"
              : "Use my current location"}
          </Text>

        </Pressable>


        {latitude !== null &&
          longitude !== null && (
            <View style={styles.locationInfo}>

              <Text style={styles.locationText}>
                Latitude:{" "}
                {latitude.toFixed(6)}
              </Text>

              <Text style={styles.locationText}>
                Longitude:{" "}
                {longitude.toFixed(6)}
              </Text>

            </View>
          )}

      </View>


      {/* SAVE */}

      <Pressable
        style={[
          styles.saveButton,
          saving &&
            styles.saveButtonDisabled,
        ]}
        onPress={handleCreateFarm}
        disabled={saving}
      >

        {saving ? (
          <ActivityIndicator
            color="#fff"
          />
        ) : (
          <>
            <Check
              size={20}
              color="#fff"
            />

            <Text style={styles.saveText}>
              Create Farm
            </Text>
          </>
        )}

      </Pressable>


      <Text style={styles.footer}>
        You can change your farm information
        later from Settings.
      </Text>

    </ScrollView>
  );
}


const styles = StyleSheet.create({

  container: {
    padding: 20,
    paddingBottom: 40,
  },

  header: {
    marginBottom: 22,
  },

  eyebrow: {
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 1,
    color: COLORS.inkSoft,
    marginBottom: 6,
  },

  title: {
    fontSize: 30,
    fontWeight: "900",
    color: COLORS.fieldGreenDeep,
  },

  subtitle: {
    marginTop: 8,
    fontSize: 14,
    lineHeight: 21,
    fontWeight: "600",
    color: COLORS.inkSoft,
  },

  card: {
    backgroundColor: COLORS.card,
    borderWidth: 1,
    borderColor: COLORS.line,
    borderRadius: 20,
    padding: 16,
    marginBottom: 14,
  },

  label: {
    fontSize: 12,
    fontWeight: "800",
    color: COLORS.inkSoft,
    marginBottom: 8,
    letterSpacing: 0.4,
  },

  input: {
    backgroundColor: COLORS.paper,
    borderWidth: 1,
    borderColor: COLORS.line,
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    fontWeight: "700",
    color: COLORS.fieldGreenDeep,
  },

  selector: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: COLORS.paper,
    borderWidth: 1,
    borderColor: COLORS.line,
    borderRadius: 14,
    paddingHorizontal: 14,
    paddingVertical: 13,
  },

  selectorText: {
    fontSize: 15,
    fontWeight: "700",
    color: COLORS.fieldGreenDeep,
  },

  optionsBox: {
    marginTop: 8,
    borderWidth: 1,
    borderColor: COLORS.line,
    borderRadius: 14,
    overflow: "hidden",
  },

  option: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.line,
  },

  optionText: {
    fontSize: 14,
    fontWeight: "600",
    color: COLORS.ink,
  },

  locationButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    backgroundColor: COLORS.paper,
    borderWidth: 1,
    borderColor: COLORS.line,
    borderRadius: 14,
    paddingVertical: 13,
  },

  locationButtonSuccess: {
    backgroundColor: "#E8F5E9",
  },

  locationButtonText: {
    fontSize: 14,
    fontWeight: "800",
    color: COLORS.fieldGreenDeep,
  },

  locationInfo: {
    marginTop: 10,
    padding: 10,
    backgroundColor: COLORS.paper,
    borderRadius: 10,
  },

  locationText: {
    fontSize: 11,
    fontWeight: "600",
    color: COLORS.inkSoft,
    marginBottom: 2,
  },

  saveButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    backgroundColor: COLORS.fieldGreenDeep,
    borderRadius: 16,
    paddingVertical: 15,
    marginTop: 4,
  },

  saveButtonDisabled: {
    opacity: 0.6,
  },

  saveText: {
    color: "#fff",
    fontSize: 15,
    fontWeight: "800",
  },

  footer: {
    textAlign: "center",
    marginTop: 14,
    fontSize: 11,
    fontWeight: "600",
    color: COLORS.inkSoft,
  },

});