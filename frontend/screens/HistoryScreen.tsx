
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
  ChevronRight,
  Sprout,
} from "lucide-react-native";

import {
  COLORS,
  NavKey,
} from "../theme";

import {
  getHistory,
  getHistoryDetail,
  type HistoryItem,
  type AnalysisData,
} from "../services/api";

import {
  useLanguage,
} from "../translations";

type Props = {
  setAnalysisData: (
    data: AnalysisData,
  ) => void;

  setActive: (
    screen: NavKey,
  ) => void;
  language: string;
};

export default function HistoryScreen({
  setAnalysisData,
  setActive,
  language,
}: Props) {
  const {
    t,
  } = useLanguage();

  const [
    history,
    setHistory,
  ] =
    useState<HistoryItem[]>(
      [],
    );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null,
    );

  const loadHistory =
    useCallback(
      async () => {
        try {
          setLoading(true);
          setError(null);

          const data =
            await getHistory();

          setHistory(data);
        } catch (error) {
          console.error(
            "History loading error:",
            error,
          );

          setError(
            error instanceof Error
              ? error.message
              : "Failed to load history.",
          );
        } finally {
          setLoading(false);
        }
      },
      [],
    );

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  async function openHistory(
    analysisId: number,
  ) {
    try {
      setError(null);

      const analysis =
        await getHistoryDetail(
          analysisId,
        );

      setAnalysisData(
        analysis,
      );

      setActive(
        "dashboard",
      );
    } catch (error) {
      console.error(
        "Historical analysis error:",
        error,
      );

      setError(
        error instanceof Error
          ? error.message
          : "Failed to load analysis.",
      );
    }
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
          {
            t.loadingHistory
          }
        </Text>
      </View>
    );
  }

  return (
    <ScrollView
      contentContainerStyle={
        styles.container
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
              loadHistory
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

      {history.length === 0 ? (
        <View
          style={
            styles.empty
          }
        >
          <Sprout
            size={30}
            color={
              COLORS.fieldGreenDeep
            }
          />

          <Text
            style={
              styles.emptyTitle
            }
          >
            {
              t.noFlightHistory
            }
          </Text>

          <Text
            style={
              styles.emptyText
            }
          >
            {
              t.completedAnalyses
            }
          </Text>
        </View>
      ) : (
        <View
          style={
            styles.list
          }
        >
          {history.map(
            (item) => (
              <Pressable
                key={item.id}
                style={
                  styles.row
                }
                onPress={() =>
                  openHistory(
                    item.id,
                  )
                }
              >
                <View
                  style={
                    styles.left
                  }
                >
                  <View
                    style={
                      styles.iconWrap
                    }
                  >
                    <Sprout
                      size={22}
                      color={
                        COLORS.fieldGreenDeep
                      }
                    />
                  </View>

                  <View
                    style={{
                      flex: 1,
                    }}
                  >
                    <Text
                      style={
                        styles.date
                      }
                    >
                      {item.date
                        ? new Date(
                            item.date,
                          ).toLocaleString()
                        : "Unknown date"}
                    </Text>

                    <Text
                      style={
                        styles.meta
                      }
                    >
                      {item.plots} plots ·{" "}
                      {item.issues}{" "}
                      {t.issuesFlagged}
                    </Text>
                  </View>
                </View>

                <View
                  style={
                    styles.right
                  }
                >
                  <Text
                    style={
                      styles.health
                    }
                  >
                    {item.health ??
                      0}
                    %
                  </Text>

                  <ChevronRight
                    size={18}
                    color={
                      COLORS.inkSoft
                    }
                  />
                </View>
              </Pressable>
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
      color: COLORS.inkSoft,
      fontWeight: "600",
    },

    empty: {
      backgroundColor: COLORS.card,
      borderColor: COLORS.line,
      borderWidth: 1,
      borderRadius: 20,
      padding: 24,
      alignItems: "center",
    },

    emptyTitle: {
      marginTop: 10,
      fontSize: 17,
      fontWeight: "800",
      color: COLORS.fieldGreenDeep,
    },

    emptyText: {
      marginTop: 4,
      textAlign: "center",
      color: COLORS.inkSoft,
      fontWeight: "600",
    },

    errorCard: {
      backgroundColor: COLORS.card,
      borderColor: "#F0B4B4",
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
      color: COLORS.fieldGreenDeep,
      fontWeight: "800",
    },

    row: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      backgroundColor: COLORS.card,
      borderColor: COLORS.line,
      borderWidth: 1,
      borderRadius: 20,
      padding: 16,
    },

    left: {
      flexDirection: "row",
      alignItems: "center",
      gap: 14,
      flex: 1,
    },

    right: {
      flexDirection: "row",
      alignItems: "center",
      gap: 8,
    },

    iconWrap: {
      width: 48,
      height: 48,
      borderRadius: 16,
      backgroundColor: COLORS.paper,
      alignItems: "center",
      justifyContent: "center",
    },

    date: {
      fontSize: 15,
      fontWeight: "800",
      color: COLORS.fieldGreenDeep,
    },

    meta: {
      fontSize: 12,
      fontWeight: "600",
      color: COLORS.inkSoft,
      marginTop: 2,
    },

    health: {
      fontSize: 20,
      fontWeight: "900",
      color: COLORS.fieldGreenDeep,
    },
  });

  