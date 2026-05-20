"""Quick test to verify DB works end-to-end."""
from database import (
    init_db,
    save_message,
    get_chat_history,
    save_journal,
    get_journal_entries,
    save_mood,
    get_mood_logs,
    clear_chat_history,
)


def test():
    print("=" * 50)
    print("MindSphere DB Test")
    print("=" * 50)

    # 1. Init
    print("\n[1] Initializing DB...")
    init_db()

    # 2. Chat
    print("\n[2] Testing chat messages...")
    clear_chat_history()
    save_message("user", "Hey, I'm feeling stressed about exams")
    save_message("assistant", "I hear you. Want to talk about what's making it heavy?")
    save_message("user", "Too much syllabus, too little time")
    history = get_chat_history()
    print(f"   Saved {len(history)} chat messages:")
    for m in history:
        print(f"   - [{m['role']}] {m['content'][:60]}")

    # 3. Journal
    print("\n[3] Testing journal entries...")
    jid = save_journal(
        content="Had a long day. Lab submission tomorrow and I haven't started.",
        sentiment="anxious",
        themes="academic stress, procrastination",
        ai_reflection="It sounds like you're feeling overwhelmed. Breaking the lab into 3 small chunks might help.",
    )
    print(f"   Saved journal entry id={jid}")
    entries = get_journal_entries()
    print(f"   Total journal entries: {len(entries)}")
    print(f"   Latest sentiment: {entries[0]['sentiment']}")
    print(f"   Latest themes: {entries[0]['themes']}")

    # 4. Mood
    print("\n[4] Testing mood logs...")
    save_mood(3, "okay-ish day")
    save_mood(4, "felt better after a walk")
    save_mood(2, "rough morning")
    moods = get_mood_logs()
    print(f"   Total mood logs: {len(moods)}")
    for m in moods:
        print(f"   - score={m['mood_score']} note='{m['note']}' at {m['created_at']}")

    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED — DB is working")
    print("=" * 50)


if __name__ == "__main__":
    test()