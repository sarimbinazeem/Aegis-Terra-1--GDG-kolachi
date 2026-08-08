
import React, {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  View,
  Text,
  Pressable,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
} from "react-native";

import {
  AlertTriangle,
  ChevronRight,
  Sprout,
} from "lucide-react-native";

import {
  COLORS,
} from "../theme";

import {
  getAlerts,
  type Alert,
  type Cell,
  type AnalysisData,
} from "../services/api";

import {
  useLanguage,
} from "../translations";

type Props = {
  setSelected: React.Dispatch<
    React.SetStateAction<Cell | null>
  >;
  analysisData: AnalysisData | null;
  language: string;
};

export default function AlertsScreen({
  setSelected,
  analysisData,
  language,
}: Props) {
  const {
    t,
  } = useLanguage();

  const [
    alerts,
    setAlerts,
  ] = useState<Alert[]>([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );

  const loadAlerts =
    useCallback(
      async () => {
        try {
          setLoading(true);
          setError(null);

          const data =
            await getAlerts();

          setAlerts(data);
        } catch (error) {
          console.error(
            "Alerts loading error:",
            error,
          );

          setError(
            error instanceof Error
              ? error.message
              : "Failed to load alerts.",
          );
        } finally {
          setLoading(false);
        }
      },
      [],
    );

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  function getSeverityStyle(
    severity: string,
  ) {
    const value =
      severity?.toLowerCase();

    if (value === "urgent") {
      return styles.urgent;
    }

    if (value === "high") {
      return styles.high;
    }

    if (value === "medium") {
      return styles.medium;
    }

    return styles.low;
  }

  if (loading) {
    return (
      <View
        style={
          styles.loading
        }
      >
        <ActivityIndicator
          size="large"
          color={
            COLORS.fieldGreenDeep
          }
        />

        <Text
          style={
            styles.loadingText
          }
        >
          {t.loadingAlerts ??
            "Loading alerts..."}
        </Text>
      </View>
    );
  }

  return (
    <ScrollView
      contentContainerStyle={
        styles.container
      }
      showsVerticalScrollIndicator={
        false
      }
    >
      {error && (
        <View
          style={
            styles.errorCard
          }
        >
          <Text
            style={
              styles.errorText
            }
          >
            {error}
          </Text>

          <Pressable
            onPress={
              loadAlerts
            }
          >
            <Text
              style={
                styles.retryText
              }
            >
              Retry
            </Text>
          </Pressable>
        </View>
      )}

      {alerts.length === 0 ? (
        <View
          style={
            styles.empty
          }
        >
          <Sprout
            size={32}
            color={
              COLORS.fieldGreenDeep
            }
          />

          <Text
            style={
              styles.emptyTitle
            }
          >
            {t.noAlerts ??
              "No alerts"}
          </Text>

          <Text
            style={
              styles.emptyText
            }
          >
            {t.noAlerts ??
              "No crop health alerts have been detected."}
          </Text>
        </View>
      ) : (
        <View
          style={
            styles.list
          }
        >
          {alerts.map(
            (alert, index) => (
              <View
                key={
                  alert.id ??
                  `${alert.cell}-${index}`
                }
                style={
                  styles.alertCard
                }
              >
                <View
                  style={
                    styles.alertHeader
                  }
                >
                  <View
                    style={
                      styles.iconWrap
                    }
                  >
                    <AlertTriangle
                      size={21}
                      color={
                        COLORS.fieldGreenDeep
                      }
                    />
                  </View>

                  <View
                    style={
                      styles.headerText
                    }
                  >
                    <Text
                      style={
                        styles.cell
                      }
                    >
                      {alert.cell}
                    </Text>

                    <Text
                      style={[
                        styles.severity,
                        getSeverityStyle(
                          alert.severity,
                        ),
                      ]}
                    >
                      {alert.severity}
                    </Text>
                  </View>
                </View>

                <Text
                  style={
                    styles.message
                  }
                >
                  {alert.message}
                </Text>

                <Text
                  style={
                    styles.action
                  }
                >
                  {alert.action}
                </Text>

                <View
                  style={
                    styles.divider
                  }
                />

                <View
                  style={
                    styles.footer
                  }
                >
                  <Text
                    style={
                      styles.footerText
                    }
                  >
                    {t.recommendation ??
                      "Recommended action"}
                  </Text>

                  <ChevronRight
                    size={17}
                    color={
                      COLORS.inkSoft
                    }
                  />
                </View>
              </View>
            ),
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles =
  StyleSheet.create({
    container: {
      paddingBottom: 24,
    },

    list: {
      gap: 12,
    },

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

    empty: {
      backgroundColor:
        COLORS.card,
      borderColor:
        COLORS.line,
      borderWidth: 1,
      borderRadius: 20,
      padding: 28,
      alignItems:
        "center",
    },

    emptyTitle: {
      marginTop: 12,
      fontSize: 18,
      fontWeight: "800",
      color:
        COLORS.fieldGreenDeep,
    },

    emptyText: {
      marginTop: 6,
      textAlign: "center",
      color:
        COLORS.inkSoft,
      fontWeight: "600",
      lineHeight: 19,
    },

    errorCard: {
      backgroundColor:
        COLORS.card,
      borderColor:
        "#F0B4B4",
      borderWidth: 1,
      borderRadius: 18,
      padding: 16,
      marginBottom: 12,
    },

    errorText: {
      color: "#B42318",
      fontWeight: "700",
    },

    retryText: {
      marginTop: 10,
      color:
        COLORS.fieldGreenDeep,
      fontWeight: "800",
    },

    alertCard: {
      backgroundColor:
        COLORS.card,
      borderColor:
        COLORS.line,
      borderWidth: 1,
      borderRadius: 20,
      padding: 16,
    },

    alertHeader: {
      flexDirection:
        "row",
      alignItems:
        "center",
    },

    iconWrap: {
      width: 46,
      height: 46,
      borderRadius: 15,
      backgroundColor:
        COLORS.paper,
      alignItems:
        "center",
      justifyContent:
        "center",
    },

    headerText: {
      marginLeft: 12,
      flex: 1,
    },

    cell: {
      fontSize: 16,
      fontWeight: "800",
      color:
        COLORS.fieldGreenDeep,
    },

    severity: {
      marginTop: 3,
      fontSize: 11,
      fontWeight: "900",
      textTransform:
        "uppercase",
    },

    urgent: {
      color: "#B42318",
    },

    high: {
      color: "#D63B3B",
    },

    medium: {
      color: "#C47A00",
    },

    low: {
      color:
        COLORS.fieldGreenDeep,
    },

    message: {
      marginTop: 14,
      fontSize: 14,
      lineHeight: 20,
      fontWeight: "700",
      color:
        COLORS.ink,
    },

    action: {
      marginTop: 8,
      fontSize: 13,
      lineHeight: 19,
      fontWeight: "600",
      color:
        COLORS.inkSoft,
    },

    divider: {
      height: 1,
      backgroundColor:
        COLORS.line,
      marginTop: 14,
      marginBottom: 10,
    },

    footer: {
      flexDirection:
        "row",
      alignItems:
        "center",
      justifyContent:
        "space-between",
    },

    footerText: {
      fontSize: 12,
      fontWeight: "800",
      color:
        COLORS.fieldGreenDeep,
    },
  });

