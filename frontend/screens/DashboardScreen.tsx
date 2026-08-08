
import React, {
  useState,
} from "react";

import {
  View,
  Text,
  ScrollView,
  Pressable,
  StyleSheet,
} from "react-native";

import Svg, {
  Circle,
} from "react-native-svg";

import {
  CheckCircle2,
  AlertTriangle,
  Droplets,
} from "lucide-react-native";

import {
  COLORS,
  STATUS,
  COLS,
  ROWS,
} from "../theme";

import {
  SectionCard,
} from "../components/Shared";

import type {
  AnalysisData,
  Alert,
  Cell,
} from "../services/api";

import {
  useLanguage,
} from "../translations";

type Props = {
  setSelected: (
    cell: Cell | null,
  ) => void;

  analysisData:
    AnalysisData | null;

  language: string;
};

export default function DashboardScreen({
  setSelected,
  analysisData,
  language,
}: Props) {
  const {
    t,
  } = useLanguage();

  /*
   * IMPORTANT:
   *
   * We intentionally DO NOT restore an old cached analysis here.
   *
   * A new app session should start with:
   *
   *     analysisData = null
   *
   * and therefore show "No analysis yet".
   *
   * A dashboard result will only appear after a
   * new analysis is loaded into analysisData.
   */

  const data =
    analysisData;

  if (!data) {
    return (
      <View
        style={
          styles.emptyContainer
        }
      >
        <Text
          style={
            styles.emptyTitle
          }
        >
          {t.noAnalysis}
        </Text>

        <Text
          style={
            styles.emptyText
          }
        >
          {t.uploadCropImage}
        </Text>
      </View>
    );
  }

  const ringCircumference =
    2 *
    Math.PI *
    42;

  const health =
    Math.max(
      0,
      Math.min(
        100,
        data.overall_health_pct ??
          0,
      ),
    );

  const ringProgress =
    (health / 100) *
    ringCircumference;

  return (
    <ScrollView
      contentContainerStyle={
        styles.container
      }
    >
      {data.offline && (
        <View
          style={
            styles.offlineBanner
          }
        >
          <Text
            style={
              styles.offlineText
            }
          >
            {t.offlineMode}
          </Text>
        </View>
      )}

      <View
        style={
          styles.heroCard
        }
      >
        <View>
          <Text
            style={
              styles.heroLabel
            }
          >
            {t.farmHealth}
          </Text>

          <Text
            style={
              styles.heroNumber
            }
          >
            {health.toFixed(0)}%
          </Text>

          {data.overall_status && (
            <Text
              style={
                styles.overallStatus
              }
            >
              {
                data.overall_status
              }
            </Text>
          )}
        </View>

        <View
          style={{
            width: 100,
            height: 100,
          }}
        >
          <Svg
            width={100}
            height={100}
            viewBox="0 0 100 100"
          >
            <Circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke={
                COLORS.line
              }
              strokeWidth={10}
            />

            <Circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke={
                COLORS.fieldGreen
              }
              strokeWidth={10}
              strokeDasharray={`${ringProgress} ${ringCircumference}`}
              strokeLinecap="round"
              rotation="-90"
              origin="50, 50"
            />
          </Svg>

          <View
            style={
              StyleSheet.absoluteFillObject
            }
          >
            <View
              style={{
                flex: 1,
                alignItems:
                  "center",
                justifyContent:
                  "center",
              }}
            >
              <CheckCircle2
                size={30}
                color={
                  COLORS.fieldGreenDeep
                }
              />
            </View>
          </View>
        </View>
      </View>

      {(data.overall_recommended_action ||
        data.overall_issue) && (
        <SectionCard
          style={{
            marginBottom: 18,
          }}
        >
          <Text
            style={
              styles.sectionTitle
            }
          >
            {t.recommendation}
          </Text>

          {data.overall_issue && (
            <Text
              style={
                styles.issueText
              }
            >
              {
                data.overall_issue
              }
            </Text>
          )}

          {data.overall_recommended_action && (
            <Text
              style={
                styles.recommendationText
              }
            >
              {
                data.overall_recommended_action
              }
            </Text>
          )}
        </SectionCard>
      )}

      <View
        style={
          styles.alertRow
        }
      >
        {data.alerts.length ===
        0 ? (
          <View
            style={
              styles.alertCard
            }
          >
            <CheckCircle2
              size={26}
              color={
                STATUS.healthy.hex
              }
            />

            <Text
              style={
                styles.alertPlot
              }
            >
              {t.noAlerts}
            </Text>

            <Text
              style={
                styles.alertMsg
              }
            >
              {t.cropHealthy}
            </Text>
          </View>
        ) : (
          data.alerts.map(
            (
              alert: Alert,
              index: number,
            ) => {
              const urgent =
                alert.severity ===
                "urgent";

              const Icon =
                urgent
                  ? AlertTriangle
                  : Droplets;

              const accent =
                urgent
                  ? STATUS.pest.hex
                  : STATUS.dry.hex;

              return (
                <Pressable
                  key={`${alert.cell}-${index}`}
                  onPress={() => {
                    const selectedCell =
                      data.cells.find(
                        (
                          cell: Cell,
                        ) =>
                          cell.id ===
                          alert.cell,
                      );

                    if (
                      selectedCell
                    ) {
                      setSelected(
                        selectedCell,
                      );
                    }
                  }}
                  style={[
                    styles.alertCard,
                    {
                      backgroundColor:
                        urgent
                          ? "#FCEAEA"
                          : "#FEF6E4",
                      borderColor:
                        accent +
                        "44",
                    },
                  ]}
                >
                  <Icon
                    size={26}
                    color={
                      accent
                    }
                  />

                  <Text
                    style={
                      styles.alertPlot
                    }
                  >
                    {
                      alert.cell
                    }
                  </Text>

                  <Text
                    style={[
                      styles.alertMsg,
                      {
                        color:
                          accent,
                      },
                    ]}
                  >
                    {
                      alert.message
                    }
                  </Text>

                  <Text
                    style={[
                      styles.alertAction,
                      {
                        color:
                          accent,
                      },
                    ]}
                  >
                    {
                      alert.action
                    }
                  </Text>
                </Pressable>
              );
            },
          )
        )}
      </View>

      <SectionCard>
        <View
          style={
            styles.mapHeaderRow
          }
        >
          <Text
            style={
              styles.mapTitle
            }
          >
            {t.fieldMap}
          </Text>

          <Text
            style={
              styles.mapHint
            }
          >
            {t.tapPlot}
          </Text>
        </View>

        <View
          style={{
            flexDirection:
              "row",
          }}
        >
          <View
            style={
              styles.rowLabelsCol
            }
          >
            {ROWS.map(
              (row) => (
                <Text
                  key={row}
                  style={
                    styles.rowLabel
                  }
                >
                  {row}
                </Text>
              ),
            )}
          </View>

          <View
            style={{
              flex: 1,
            }}
          >
            <View
              style={
                styles.gridRow
              }
            >
              {COLS.map(
                (column) => (
                  <Text
                    key={column}
                    style={
                      styles.colLabel
                    }
                  >
                    {column}
                  </Text>
                ),
              )}
            </View>

            {ROWS.map(
              (row) => (
                <View
                  key={row}
                  style={
                    styles.gridRow
                  }
                >
                  {COLS.map(
                    (
                      column,
                    ) => {
                      const id =
                        `${column}${row}`;

                      const cell =
                        data.cells.find(
                          (
                            current: Cell,
                          ) =>
                            current.id ===
                            id,
                        );

                      if (!cell) {
                        return (
                          <View
                            key={id}
                            style={
                              styles.gridCell
                            }
                          />
                        );
                      }

                      const status =
                        STATUS[
                          cell.status
                        ] ??
                        STATUS.healthy;

                      return (
                        <Pressable
                          key={id}
                          onPress={() =>
                            setSelected(
                              cell,
                            )
                          }
                          style={[
                            styles.gridCell,
                            {
                              backgroundColor:
                                status.hex,

                              borderColor:
                                cell.severity ===
                                "urgent"
                                  ? status.hex
                                  : "transparent",

                              borderWidth:
                                cell.severity ===
                                "urgent"
                                  ? 3
                                  : 0,
                            },
                          ]}
                        >
                          <Text
                            style={
                              styles.cellText
                            }
                          >
                            {id}
                          </Text>
                        </Pressable>
                      );
                    },
                  )}
                </View>
              ),
            )}
          </View>
        </View>

        <View
          style={
            styles.legendRow
          }
        >
          {Object.entries(
            STATUS,
          ).map(
            ([key, status]) => (
              <View
                key={key}
                style={
                  styles.legendItem
                }
              >
                <View
                  style={[
                    styles.legendSwatch,
                    {
                      backgroundColor:
                        status.hex,
                    },
                  ]}
                />

                <Text
                  style={
                    styles.legendLabel
                  }
                >
                  {
                    status.label
                  }
                </Text>
              </View>
            ),
          )}
        </View>
      </SectionCard>

      {data.detections &&
        data.detections.length >
          0 && (
          <SectionCard
            style={{
              marginTop: 18,
            }}
          >
            <Text
              style={
                styles.sectionTitle
              }
            >
              {t.detectedIssues}
            </Text>

            {data.detections.map(
              (
                detection,
                index: number,
              ) => (
                <View
                  key={index}
                  style={
                    styles.detectionRow
                  }
                >
                  <Text
                    style={
                      styles.detectionName
                    }
                  >
                    {
                      detection.class
                    }
                  </Text>

                  <Text
                    style={
                      styles.detectionConfidence
                    }
                  >
                    {(
                      detection.confidence *
                      100
                    ).toFixed(0)}
                    %
                  </Text>
                </View>
              ),
            )}
          </SectionCard>
        )}
    </ScrollView>
  );
}

const styles =
  StyleSheet.create({
    container: {
      paddingBottom: 24,
    },

    emptyContainer: {
      flex: 1,
      alignItems:
        "center",
      justifyContent:
        "center",
      padding: 30,
    },

    emptyTitle: {
      marginTop: 12,
      fontSize: 20,
      fontWeight: "800",
      color:
        COLORS.fieldGreenDeep,
    },

    emptyText: {
      marginTop: 6,
      textAlign:
        "center",
      color:
        COLORS.inkSoft,
      fontWeight:
        "600",
    },

    offlineBanner: {
      flexDirection:
        "row",
      alignItems:
        "center",
      backgroundColor:
        COLORS.paper,
      borderColor:
        COLORS.line,
      borderWidth: 1,
      borderRadius: 12,
      paddingHorizontal: 14,
      paddingVertical: 10,
      marginBottom: 12,
    },

    offlineText: {
      flex: 1,
      fontSize: 12,
      fontWeight: "700",
      color:
        COLORS.fieldGreenDeep,
    },

    heroCard: {
      flexDirection:
        "row",
      alignItems:
        "center",
      justifyContent:
        "space-between",
      backgroundColor:
        COLORS.card,
      borderColor:
        COLORS.line,
      borderWidth: 1,
      borderRadius: 24,
      padding: 22,
      marginBottom: 16,
    },

    heroLabel: {
      fontSize: 12,
      fontWeight: "700",
      color:
        COLORS.inkSoft,
      letterSpacing: 0.5,
      marginBottom: 4,
    },

    heroNumber: {
      fontSize: 56,
      fontWeight: "900",
      color:
        COLORS.fieldGreenDeep,
    },

    overallStatus: {
      marginTop: 4,
      fontSize: 13,
      fontWeight: "800",
      color:
        COLORS.inkSoft,
      textTransform:
        "capitalize",
    },

    sectionTitle: {
      fontSize: 18,
      fontWeight: "800",
      color:
        COLORS.fieldGreenDeep,
      marginBottom: 8,
    },

    issueText: {
      fontSize: 14,
      fontWeight: "700",
      color:
        COLORS.ink,
      marginBottom: 4,
    },

    recommendationText: {
      fontSize: 14,
      fontWeight: "600",
      color:
        COLORS.inkSoft,
    },

    alertRow: {
      flexDirection:
        "column",
      gap: 12,
      marginBottom: 18,
    },

    alertCard: {
      width: "100%",
      borderRadius: 18,
      borderWidth: 2,
      padding: 16,
      gap: 8,
    },

    alertPlot: {
      fontSize: 18,
      fontWeight: "800",
      color:
        COLORS.fieldGreenDeep,
    },

    alertMsg: {
      fontSize: 13,
      fontWeight: "700",
    },

    alertAction: {
      fontSize: 12,
      fontWeight: "600",
    },

    mapHeaderRow: {
      alignItems:
        "center",
      marginBottom: 16,
      position:
        "relative",
    },

    mapTitle: {
      fontSize: 18,
      fontWeight: "800",
      color:
        COLORS.fieldGreenDeep,
    },

    mapHint: {
      position:
        "absolute",
      right: 0,
      top: 2,
      fontSize: 12,
      fontWeight: "700",
      color:
        COLORS.inkSoft,
    },

    rowLabelsCol: {
      justifyContent:
        "space-around",
      paddingVertical: 4,
      width: 18,
    },

    rowLabel: {
      fontSize: 12,
      fontWeight: "700",
      color:
        COLORS.inkSoft,
      textAlign:
        "center",
    },

    gridRow: {
      flexDirection:
        "row",
      marginBottom: 6,
    },

    colLabel: {
      flex: 1,
      fontSize: 12,
      fontWeight: "700",
      color:
        COLORS.inkSoft,
      textAlign:
        "center",
    },

    gridCell: {
      flex: 1,
      aspectRatio: 1,
      margin: 3,
      borderRadius: 10,
      alignItems:
        "center",
      justifyContent:
        "center",
    },

    cellText: {
      color: "white",
      fontWeight:
        "bold",
    },

    legendRow: {
      flexDirection:
        "row",
      flexWrap:
        "wrap",
      justifyContent:
        "center",
      gap: 16,
      marginTop: 16,
      paddingTop: 16,
      borderTopWidth: 1,
      borderTopColor:
        COLORS.line,
    },

    legendItem: {
      flexDirection:
        "row",
      alignItems:
        "center",
      gap: 6,
    },

    legendSwatch: {
      width: 12,
      height: 12,
      borderRadius: 3,
    },

    legendLabel: {
      fontSize: 12,
      fontWeight: "700",
      color:
        COLORS.ink,
    },

    detectionRow: {
      flexDirection:
        "row",
      justifyContent:
        "space-between",
      paddingVertical: 10,
      borderBottomWidth: 1,
      borderBottomColor:
        COLORS.line,
    },

    detectionName: {
      fontSize: 14,
      fontWeight: "700",
      color:
        COLORS.ink,
      textTransform:
        "capitalize",
    },

    detectionConfidence: {
      fontSize: 14,
      fontWeight: "800",
      color:
        COLORS.fieldGreenDeep,
    },
  });

