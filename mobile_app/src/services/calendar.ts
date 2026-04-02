type CalendarPermissionState = "granted" | "denied" | "unknown";

export async function requestCalendarAccess(): Promise<CalendarPermissionState> {
  // Placeholder service layer for future Expo/native calendar integration.
  // This keeps the app architecture ready for calendar support even before the
  // package choice is finalized.
  return "unknown";
}

export async function createCalendarEvent(input: {
  title: string;
  startAt: string;
  endAt?: string;
  notes?: string;
}) {
  return {
    status: "not_implemented",
    ...input
  };
}
