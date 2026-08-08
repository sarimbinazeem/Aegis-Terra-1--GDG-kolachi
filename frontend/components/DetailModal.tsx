import React from "react";
import { View, Text, Pressable, Modal, StyleSheet } from "react-native";
import { AlertTriangle, Gauge, X } from "lucide-react-native";
import { COLORS, STATUS } from "../theme";

export default function DetailModal({ selected, onClose }: { selected: any; onClose: () => void }) {
  const s = selected ? STATUS[selected.status] : null;
  console.log("Modal selected:", selected);
  return (
    <Modal visible={!!selected} transparent animationType="slide" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose}>
        <Pressable style={styles.sheet} onPress={(e) => e.stopPropagation()}>
          {selected && s && (
            <>
              <View style={styles.headerRow}>
                <View>
                  <Text style={styles.eyebrow}>PLOT {selected.id}</Text>
                  <Text style={styles.title}>{s.label}</Text>
                </View>
                <Pressable onPress={onClose}><X size={22} color={COLORS.inkSoft} /></Pressable>
              </View>

              <View style={styles.statRow}>
                <View style={styles.statBox}>
                  <View style={{ flexDirection: "row", alignItems: "center", gap: 4, marginBottom: 4 }}>
                    <Gauge size={13} color={COLORS.inkSoft} />
                    <Text style={styles.statLabel}>ExG</Text>
                  </View>
                  <Text style={styles.statValue}>{selected.exg_value}</Text>
                </View>
                <View style={[styles.statBox, { marginLeft: 10 }]}>
                  <Text style={styles.statLabel}>Confidence</Text>
                  <Text style={styles.statValue}>{Math.round(selected.confidence * 100)}%</Text>
                </View>
              </View>

              {selected.issue && (
                <View style={[styles.issueBox, { backgroundColor: s.hex + "1A", borderColor: s.hex + "55" }]}>
                  <AlertTriangle size={18} color={s.hex} />
                  <View style={{ marginLeft: 8, flex: 1 }}>
                    <Text style={styles.issueTitle}>{selected.issue}</Text>
                    {selected.recommended_action && <Text style={styles.issueBody}>{selected.recommended_action}</Text>}
                  </View>
                </View>
              )}

              <Pressable style={styles.closeButton} onPress={onClose}>
                <Text style={styles.closeButtonText}>Close</Text>
              </Pressable>
            </>
          )}
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: "rgba(27,94,32,0.45)", justifyContent: "flex-end" },
  sheet: { backgroundColor: COLORS.card, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 22, paddingBottom: 34 },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 18 },
  eyebrow: { fontSize: 11, fontWeight: "700", color: COLORS.inkSoft, letterSpacing: 0.5 },
  title: { fontSize: 24, fontWeight: "800", color: COLORS.fieldGreenDeep, marginTop: 2 },
  statRow: { flexDirection: "row", marginBottom: 16 },
  statBox: { flex: 1, backgroundColor: COLORS.paper, borderRadius: 14, padding: 14 },
  statLabel: { fontSize: 11, fontWeight: "700", color: COLORS.inkSoft },
  statValue: { fontSize: 20, fontWeight: "800", color: COLORS.fieldGreenDeep, marginTop: 4 },
  issueBox: { flexDirection: "row", alignItems: "flex-start", borderWidth: 1, borderRadius: 14, padding: 14, marginBottom: 18 },
  issueTitle: { fontSize: 14, fontWeight: "700", color: COLORS.fieldGreenDeep },
  issueBody: { fontSize: 12, color: COLORS.inkSoft, marginTop: 2, fontWeight: "500" },
  closeButton: { backgroundColor: COLORS.fieldGreen, borderRadius: 16, paddingVertical: 15, alignItems: "center" },
  closeButtonText: { color: "#fff", fontSize: 15, fontWeight: "800" },
});
