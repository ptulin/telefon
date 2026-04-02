export const capabilityTiers = {
  now: [
    "contacts_lookup",
    "call_initiation",
    "calendar_read",
    "calendar_create",
    "camera_capture",
    "document_upload",
    "memory_recall"
  ],
  next: [
    "message_drafting",
    "routine_tracking",
    "offline_queue",
    "caregiver_shortcuts",
    "navigation_assist"
  ],
  future: [
    "agent_to_agent_scheduling",
    "commerce_agent",
    "booking_agent",
    "delegated_task_loops",
    "cross_service_negotiation"
  ]
} as const;
