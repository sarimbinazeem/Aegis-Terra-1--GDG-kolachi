import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { COLORS } from "../theme";

export function SectionCard({ children, style }: { children: React.ReactNode; style?: any }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function CenteredHeading({ title, right }: { title: string; right?: string }) {
  return (
    <View style={styles.headingRow}>
      <Text style={styles.headingText}>{title}</Text>
      {right ? <Text style={styles.headingRight}>{right}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.card,
    borderColor: COLORS.line,
    borderWidth: 1,
    borderRadius: 22,
    padding: 18,
    shadowColor: COLORS.fieldGreenDeep,
    shadowOpacity: 0.08,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
    elevation: 2,
  },
  headingRow: { alignItems: "center", marginBottom: 18, position: "relative" },
  headingText: { fontWeight: "800", fontSize: 24, color: COLORS.fieldGreenDeep, textAlign: "center" },
  headingRight: { position: "absolute", right: 0, top: 4, fontSize: 12, fontWeight: "700", color: COLORS.inkSoft },
});
