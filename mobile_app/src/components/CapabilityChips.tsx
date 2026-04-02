import { Pressable, StyleSheet, Text, View } from "react-native";

type Props = {
  items: readonly string[];
  selected: string;
  onSelect: (item: string) => void;
};

export function CapabilityChips({ items, selected, onSelect }: Props) {
  return (
    <View style={styles.wrap}>
      {items.map((item) => (
        <Pressable
          key={item}
          onPress={() => onSelect(item)}
          style={[styles.chip, selected === item && styles.selected]}
        >
          <Text style={[styles.text, selected === item && styles.selectedText]}>{item}</Text>
        </Pressable>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  chip: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 999,
    backgroundColor: "#1a252c"
  },
  selected: { backgroundColor: "#68d4a9" },
  text: { color: "#d4e0e6", fontWeight: "600", textTransform: "capitalize" },
  selectedText: { color: "#081316" }
});
