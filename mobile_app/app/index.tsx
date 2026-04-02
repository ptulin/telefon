import { SafeAreaView } from "react-native-safe-area-context";
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { useState } from "react";

import { CapabilityChips } from "@/components/CapabilityChips";
import { SummaryCard } from "@/components/SummaryCard";
import { useAssistant } from "@/hooks/useAssistant";

const MODES = ["talk", "call", "calendar", "camera", "documents", "memory"] as const;

export default function HomeScreen() {
  const [prompt, setPrompt] = useState("");
  const [mode, setMode] = useState<(typeof MODES)[number]>("talk");
  const { reply, sendPrompt, status } = useAssistant();

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.hero}>
          <Text style={styles.title}>Personal AI</Text>
          <Text style={styles.subtitle}>
            One place to talk, call, plan, remember, and get help.
          </Text>
          <Text style={styles.status}>{status}</Text>
        </View>

        <CapabilityChips
          items={MODES}
          selected={mode}
          onSelect={(next) => setMode(next as (typeof MODES)[number])}
        />

        <SummaryCard
          title="Try saying"
          body="Call my daughter. What is on my calendar tomorrow? Read this letter. Remind me to take my medicine at 8."
        />

        <View style={styles.inputCard}>
          <Text style={styles.label}>Ask naturally</Text>
          <TextInput
            multiline
            value={prompt}
            onChangeText={setPrompt}
            placeholder="How can I help you today?"
            placeholderTextColor="#7b8790"
            style={styles.input}
          />
          <Pressable
            style={styles.primaryButton}
            onPress={() => sendPrompt({ prompt, preferredMode: mode })}
          >
            <Text style={styles.primaryButtonText}>Ask AI</Text>
          </Pressable>
        </View>

        <SummaryCard title="AI Reply" body={reply || "Nothing yet."} />

        <View style={styles.grid}>
          <SummaryCard title="Today" body="Calendar, reminders, and follow-ups will surface here." compact />
          <SummaryCard title="People" body="Favorites, family, doctors, and helpers." compact />
          <SummaryCard title="Agent Tasks" body="Future delegated tasks and assistant-to-assistant workflows." compact />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#0c1216" },
  container: { padding: 20, gap: 16 },
  hero: { gap: 6, paddingTop: 8 },
  title: { color: "#f4fafc", fontSize: 34, fontWeight: "700" },
  subtitle: { color: "#a2b2ba", fontSize: 16, lineHeight: 23 },
  status: { color: "#6dd0a0", fontSize: 14 },
  inputCard: {
    backgroundColor: "#172128",
    borderRadius: 22,
    padding: 16,
    gap: 12
  },
  label: { color: "#dbe7ec", fontSize: 16, fontWeight: "600" },
  input: {
    minHeight: 120,
    backgroundColor: "#0b1013",
    color: "#f4fafc",
    borderRadius: 16,
    padding: 14,
    textAlignVertical: "top"
  },
  primaryButton: {
    backgroundColor: "#68d4a9",
    borderRadius: 16,
    paddingVertical: 16,
    alignItems: "center"
  },
  primaryButtonText: { color: "#081316", fontSize: 17, fontWeight: "700" },
  grid: { gap: 12 }
});
