import React from "react";
import {
  View,
  Text,
  Pressable,
  StyleSheet,
} from "react-native";

import {
  COLORS,
  NAV_ITEMS,
  NavKey,
} from "../theme";

import { useLanguage } from "../translations";

export default function BottomNav({
  active,
  onChange,
}: {
  active: NavKey;
  onChange: (k: NavKey) => void;
}) {
  const { t } = useLanguage();

  const labels: Record<NavKey, string> = {
    dashboard: t.home,
    upload: t.upload,
    history: t.history,
    alerts: t.alerts,
    settings: t.settings,
  };

  return (
    <View style={styles.bar}>
      {NAV_ITEMS.map((item) => {
        const isActive = active === item.key;
        const Icon = item.Icon;

        return (
          <Pressable
            key={item.key}
            onPress={() => onChange(item.key)}
            style={styles.item}
          >
            <View
              style={[
                styles.iconWrap,
                isActive && styles.iconWrapActive,
              ]}
            >
              <Icon
                size={20}
                color={
                  isActive
                    ? "#fff"
                    : COLORS.navInactive
                }
              />
            </View>

            <Text
              style={[
                styles.label,
                isActive && styles.labelActive,
              ]}
            >
              {labels[item.key]}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    flexDirection: "row",
    backgroundColor:
      COLORS.fieldGreenDeep,
    paddingTop: 10,
    paddingBottom: 22,
    paddingHorizontal: 8,
    justifyContent: "space-around",
  },

  item: {
    alignItems: "center",
    gap: 3,
  },

  iconWrap: {
    width: 40,
    height: 32,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },

  iconWrapActive: {
    backgroundColor: COLORS.fieldGreen,
  },

  label: {
    fontSize: 10,
    fontWeight: "600",
    color: COLORS.navInactive,
  },

  labelActive: {
    color: "#fff",
  },
});