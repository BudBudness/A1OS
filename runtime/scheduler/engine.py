class Scheduler:
    async def schedule(self,event):
        return event

# A1OS_KAMPALA_FEEDBACK_SCHEDULE
# Read/analysis-only scheduled JARVIS feedback.
# Africa/Kampala is UTC+03:00.
A1OS_KAMPALA_FEEDBACK_SCHEDULE = (
    {"time": "00:00", "timezone": "Africa/Kampala", "intent": "scheduled_feedback", "execution": "read_only"},
    {"time": "06:00", "timezone": "Africa/Kampala", "intent": "scheduled_feedback", "execution": "read_only"},
    {"time": "12:00", "timezone": "Africa/Kampala", "intent": "scheduled_feedback", "execution": "read_only"},
    {"time": "18:00", "timezone": "Africa/Kampala", "intent": "scheduled_feedback", "execution": "read_only"},
)
