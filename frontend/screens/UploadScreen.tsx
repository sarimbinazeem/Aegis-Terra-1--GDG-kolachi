import React, {
  useState,
} from "react";

import {
  View,
  Text,
  Pressable,
  ScrollView,
  StyleSheet,
} from "react-native";

import * as ImagePicker from "expo-image-picker";

import {
  ImagePlus,
  Plane,
  Trash2,
} from "lucide-react-native";

import {
  COLORS,
  STATUS,
  NavKey,
} from "../theme";

import {
  SectionCard,
} from "../components/Shared";

import {
  uploadImage,
} from "../services/api";

import {
  useLanguage,
} from "../translations";

type QueuedFile = {
  id: string;
  name: string;
  uri: string;
  mimeType?: string;
  fileName?: string;
};

type Props = {
  setAnalysisData: (
    data: any,
  ) => void;

  setActive: (
    tab: NavKey,
  ) => void;
  language: string;
};

export default function UploadScreen({
  setAnalysisData,
  setActive,
  
}: Props) {
  const {
    t,
  } = useLanguage();

  const [
    files,
    setFiles,
  ] = useState<QueuedFile[]>([]);

  const pickImages = async () => {
    const permission =
      await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permission.granted) {
      return;
    }

    const result =
      await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ["images"],
        allowsMultipleSelection: true,
        quality: 0.8,
      });

    if (result.canceled) {
      return;
    }

    const picked: QueuedFile[] =
      result.assets.map(
        (a, i) => ({
          id: `${Date.now()}-${i}`,
          name:
            a.fileName ??
            a.uri
              .split("/")
              .pop() ??
            `image_${i}.jpg`,
          uri: a.uri,
          mimeType:
            a.mimeType ??
            undefined,
          fileName:
            a.fileName ??
            undefined,
        }),
      );

    setFiles((prev) => [
      ...prev,
      ...picked,
    ]);
  };

  const handleAnalyze =
    async () => {
      if (files.length === 0) {
        return;
      }

      try {
        const result =
          await uploadImage(
            files[0],
          );

        console.log(
          "Analysis result:",
          result,
        );

        setAnalysisData(
          result,
        );

        setFiles([]);

        setActive(
          "dashboard",
        );

        alert(
          t.uploadSuccessful,
        );
      } catch (err) {
        console.error(
          "Upload error:",
          err,
        );

        alert(
          t.uploadFailed,
        );
      }
    };

  const removeFile = (
    id: string,
  ) =>
    setFiles((prev) =>
      prev.filter(
        (f) => f.id !== id,
      ),
    );

  return (
    <ScrollView
      contentContainerStyle={{
        paddingBottom: 24,
      }}
    >
      <SectionCard
        style={{
          marginBottom: 18,
        }}
      >
        <Pressable
          onPress={
            pickImages
          }
          style={
            styles.dropZone
          }
        >
          <ImagePlus
            size={40}
            color={
              COLORS.fieldGreen
            }
          />

          <Text
            style={
              styles.dropTitle
            }
          >
            {
              t.selectDroneImages
            }
          </Text>

          <Text
            style={
              styles.dropHint
            }
          >
            {
              t.browsePhotoLibrary
            }
          </Text>
        </Pressable>

        <View
          style={
            styles.noteBox
          }
        >
          <Plane
            size={18}
            color={
              STATUS.dry.hex
            }
          />

          <Text
            style={
              styles.noteText
            }
          >
            {
              t.batchUploadNote
            }
          </Text>
        </View>
      </SectionCard>

      {files.length > 0 && (
        <SectionCard>
          <Text
            style={
              styles.queueTitle
            }
          >
            {files.length} image
            {files.length > 1
              ? "s"
              : ""}{" "}
            {t.queued}
          </Text>

          <View
            style={{
              gap: 10,
            }}
          >
            {files.map(
              (f) => (
                <View
                  key={f.id}
                  style={
                    styles.fileRow
                  }
                >
                  <View
                    style={{
                      flexDirection:
                        "row",
                      alignItems:
                        "center",
                      gap: 10,
                      flex: 1,
                    }}
                  >
                    <ImagePlus
                      size={16}
                      color={
                        COLORS.fieldGreen
                      }
                    />

                    <Text
                      style={
                        styles.fileName
                      }
                      numberOfLines={
                        1
                      }
                    >
                      {f.name}
                    </Text>
                  </View>

                  <View
                    style={{
                      flexDirection:
                        "row",
                      alignItems:
                        "center",
                      gap: 10,
                    }}
                  >
                    <View
                      style={
                        styles.queuedChip
                      }
                    >
                      <Text
                        style={
                          styles.queuedChipText
                        }
                      >
                        {
                          t.queued
                        }
                      </Text>
                    </View>

                    <Pressable
                      onPress={() =>
                        removeFile(
                          f.id,
                        )
                      }
                    >
                      <Trash2
                        size={16}
                        color={
                          COLORS.inkSoft
                        }
                      />
                    </Pressable>
                  </View>
                </View>
              ),
            )}
          </View>

          <Pressable
            style={
              styles.analyzeButton
            }
            onPress={
              handleAnalyze
            }
          >
            <Text
              style={
                styles.analyzeButtonText
              }
            >
              {
                t.analyzeImage
              }
            </Text>
          </Pressable>
        </SectionCard>
      )}
    </ScrollView>
  );
}

const styles =
  StyleSheet.create({
    dropZone: {
      borderWidth: 2,
      borderStyle: "dashed",
      borderColor: COLORS.line,
      borderRadius: 18,
      paddingVertical: 40,
      alignItems: "center",
      backgroundColor: COLORS.paper,
    },

    dropTitle: {
      fontSize: 17,
      fontWeight: "800",
      color: COLORS.fieldGreenDeep,
      marginTop: 10,
    },

    dropHint: {
      fontSize: 13,
      fontWeight: "500",
      color: COLORS.inkSoft,
      marginTop: 3,
    },

    noteBox: {
      flexDirection: "row",
      alignItems: "flex-start",
      gap: 10,
      marginTop: 18,
      padding: 14,
      borderRadius: 16,
      backgroundColor: "#FEF6E4",
      borderWidth: 1,
      borderColor: "#EBD9A6",
    },

    noteText: {
      flex: 1,
      fontSize: 13,
      fontWeight: "600",
      color: COLORS.fieldGreenDeep,
    },

    queueTitle: {
      fontSize: 17,
      fontWeight: "800",
      color: COLORS.fieldGreenDeep,
      textAlign: "center",
      marginBottom: 14,
    },

    fileRow: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      padding: 14,
      borderRadius: 16,
      backgroundColor: COLORS.paper,
    },

    fileName: {
      fontSize: 13,
      fontWeight: "600",
      color: COLORS.ink,
    },

    queuedChip: {
      paddingHorizontal: 10,
      paddingVertical: 4,
      borderRadius: 999,
      backgroundColor: COLORS.line,
    },

    queuedChipText: {
      fontSize: 11,
      fontWeight: "800",
      color: COLORS.fieldGreenDeep,
    },

    analyzeButton: {
      marginTop: 18,
      backgroundColor: COLORS.fieldGreen,
      borderRadius: 16,
      paddingVertical: 15,
      alignItems: "center",
    },

    analyzeButtonText: {
      color: "#fff",
      fontSize: 15,
      fontWeight: "800",
    },
  });