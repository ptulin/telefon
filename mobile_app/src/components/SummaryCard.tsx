import { StyleSheet, Text, View } from "react-native";

type Props = {
  title: string;
  body: string;
  compact?: boolean;
};

export function SummaryCard({ title, body, compact = false }: Props) {
  return (
    <View style={[styles.card, compact && styles.compact]}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.body}>{body}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#172128",
    borderRadius: 22,
    padding: 16,
    gap: 8
  },
  compact: {
    minHeight: 110
  },
  title: { color: "#f4fafc", fontSize: 18, fontWeight: "700" },
  body: { color: "#a8b7be", fontSize: 15, lineHeight: 21 }
});
