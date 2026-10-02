import streamlit as st
import time
import json
import os
import random
from datetime import datetime

# ============================================================
# API CONFIGURATION
# ============================================================

# General AI API
AI_PROVIDER = "Gemini"
AI_API_KEY = st.secrets["GEMINI_API_KEY"]

# AI model
AI_MODEL = "gemini-3.5-flash"

# AI library
AI_LIBRARY = "google-genai"

# API_KEY = st.secrets["GEMINI_API_KEY"]
# Gemini API
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
# Gemini model
GEMINI_MODEL = "gemini-3.5-flash"

# Gemini library
GEMINI_LIBRARY = "google-genai"


# ============================================================
# APP CONFIGURATION
# ============================================================

HISTORY_FILE = "typing_history.json"


# ============================================================
# IMPORT GEMINI
# ============================================================

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Typing Speed Tester",
    page_icon="⌨️",
    layout="wide"
)


# ============================================================
# LEVELS
# ============================================================

LEVELS = {
    "Easy": {
        "time": 60,
        "icon": "🟢",
        "description": "Simple words and normal sentences."
    },
    "Hard": {
        "time": 45,
        "icon": "🟠",
        "description": "Longer sentences and more punctuation."
    },
    "Difficult": {
        "time": 30,
        "icon": "🔴",
        "description": "Advanced vocabulary and challenging sentences."
    }
}


# ============================================================
# PARAGRAPHS
# ============================================================

PARAGRAPHS = {

    "Easy": [
        "The sun rises in the morning and gives us a beautiful new day. Every day is a chance to learn something new and improve our skills.",

        "Learning to type quickly can save time and make computer work much easier. Practice every day and focus on accuracy before speed.",

        "Technology is an important part of modern life. We use computers and phones to learn, communicate, create projects, and discover new ideas."
    ],

    "Hard": [
        "Modern technology has changed the way people communicate, learn, and work. Students can access thousands of educational resources within seconds, but using technology effectively requires concentration and discipline.",

        "Successful people understand that improvement does not happen overnight. They practice regularly, learn from their mistakes, and continue working even when the results are not immediately visible.",

        "Typing quickly is useful, but typing accurately is even more important. A fast typist who makes many mistakes may spend more time correcting errors than a slower typist who carefully enters the correct information."
    ],

    "Difficult": [
        "Artificial intelligence is transforming numerous industries by analyzing enormous amounts of information, identifying complex patterns, and assisting people with tasks that once required considerable time and effort.",

        "Although technological progress provides remarkable opportunities, responsible innovation requires thoughtful consideration of privacy, security, accessibility, reliability, and the potential consequences of automated systems.",

        "Developing exceptional typing proficiency requires patience, consistency, coordination, and attention to detail. Professional performance is not determined exclusively by raw speed; accuracy, rhythm, endurance, and concentration are equally significant."
    ]
}


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_level" not in st.session_state:
    st.session_state.selected_level = None

if "paragraph" not in st.session_state:
    st.session_state.paragraph = ""

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "test_started" not in st.session_state:
    st.session_state.test_started = False

if "user_text" not in st.session_state:
    st.session_state.user_text = ""

if "result" not in st.session_state:
    st.session_state.result = None

if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = ""

if "last_level" not in st.session_state:
    st.session_state.last_level = None

if "unlocked_levels" not in st.session_state:
    st.session_state.unlocked_levels = ["Easy"]


# ============================================================
# HISTORY FUNCTIONS
# ============================================================

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


def save_history(history):

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(
                history,
                file,
                indent=4,
                ensure_ascii=False
            )
    except:
        pass


if "history" not in st.session_state:
    st.session_state.history = load_history()


# ============================================================
# GEMINI API KEY
# ============================================================

def get_gemini_key():

    # Streamlit Secrets
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")

        if key:
            return key
    except:
        pass

    # Dedicated Gemini key
    if GEMINI_API_KEY:
        return GEMINI_API_KEY

    # General AI key
    if AI_API_KEY:
        return AI_API_KEY

    return ""


# ============================================================
# CALCULATE RESULT
# ============================================================

def calculate_result(original, typed, elapsed):

    elapsed = max(elapsed, 0.1)

    typed_characters = len(typed)

    correct_characters = 0

    for i in range(
        min(len(original), len(typed))
    ):
        if original[i] == typed[i]:
            correct_characters += 1

    cpm = (typed_characters / elapsed) * 60

    wpm = cpm / 5

    if typed_characters > 0:
        accuracy = (
            correct_characters /
            typed_characters
        ) * 100
    else:
        accuracy = 0

    mistakes = max(
        typed_characters - correct_characters,
        0
    )

    speed_score = min(wpm / 100, 1) * 50

    accuracy_score = (
        accuracy / 100
    ) * 50

    score = round(
        speed_score + accuracy_score
    )

    return {
        "wpm": round(wpm, 1),
        "cpm": round(cpm, 1),
        "accuracy": round(accuracy, 1),
        "mistakes": mistakes,
        "correct": correct_characters,
        "typed": typed_characters,
        "time": round(elapsed, 1),
        "score": score
    }


# ============================================================
# AI FEEDBACK
# ============================================================

def generate_ai_feedback(result, level):

    api_key = get_gemini_key()

    if not api_key:

        return (
            "AI feedback is not connected yet. "
            "Your typing statistics have been calculated "
            "and saved successfully."
        )

    if not GEMINI_AVAILABLE:

        return (
            "The Gemini library is not installed. "
            "Run: pip install google-genai"
        )

    try:

        client = genai.Client(
            api_key=api_key
        )

        prompt = f"""
You are an AI typing coach.

Analyze this typing test:

Level: {level}
WPM: {result['wpm']}
CPM: {result['cpm']}
Accuracy: {result['accuracy']}%
Mistakes: {result['mistakes']}
Correct Characters: {result['correct']}
Typed Characters: {result['typed']}
Time: {result['time']} seconds
Score: {result['score']}/100

Give a concise and friendly typing analysis.

Include:
1. Overall performance
2. What the user did well
3. What they should improve
4. One practical typing tip
5. Encouragement for the next level

Do not invent or change any statistics.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        if response and response.text:
            return response.text

        return "AI could not generate feedback."

    except Exception as error:

        return (
            "AI analysis is temporarily unavailable. "
            "Your typing result was still saved successfully."
        )


# ============================================================
# START TEST
# ============================================================

def start_test(level):

    st.session_state.selected_level = level

    st.session_state.paragraph = random.choice(
        PARAGRAPHS[level]
    )

    st.session_state.start_time = time.time()

    st.session_state.test_started = True

    st.session_state.user_text = ""

    st.session_state.result = None

    st.session_state.ai_feedback = ""

    st.session_state.page = "test"


# ============================================================
# FINISH TEST
# ============================================================

def finish_test():

    level = st.session_state.selected_level

    original = st.session_state.paragraph

    typed = st.session_state.user_text

    elapsed = time.time() - st.session_state.start_time

    elapsed = min(
        elapsed,
        LEVELS[level]["time"]
    )

    result = calculate_result(
        original,
        typed,
        elapsed
    )

    st.session_state.result = result

    st.session_state.test_started = False

    st.session_state.last_level = level

    # Unlock next level
    if level == "Easy":

        if "Hard" not in st.session_state.unlocked_levels:
            st.session_state.unlocked_levels.append("Hard")

    elif level == "Hard":

        if "Difficult" not in st.session_state.unlocked_levels:
            st.session_state.unlocked_levels.append("Difficult")

    # Save history
    history_item = {
        "date": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "level": level,
        "wpm": result["wpm"],
        "cpm": result["cpm"],
        "accuracy": result["accuracy"],
        "mistakes": result["mistakes"],
        "correct": result["correct"],
        "typed": result["typed"],
        "time": result["time"],
        "score": result["score"]
    }

    st.session_state.history.insert(
        0,
        history_item
    )

    st.session_state.history = (
        st.session_state.history[:50]
    )

    save_history(
        st.session_state.history
    )

    # AI analysis
    st.session_state.ai_feedback = (
        generate_ai_feedback(
            result,
            level
        )
    )

    st.session_state.page = "result"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⌨️ Typing Tester")

    st.caption(
        "AI-powered typing practice"
    )

    st.divider()

    if st.button(
        "🏠 Home",
        use_container_width=True
    ):

        st.session_state.page = "home"

        st.session_state.test_started = False

        st.rerun()

    if st.button(
        "📊 History",
        use_container_width=True
    ):

        st.session_state.page = "history"

        st.session_state.test_started = False

        st.rerun()

    st.divider()

    st.subheader("🏆 Progress")

    for level in [
        "Easy",
        "Hard",
        "Difficult"
    ]:

        if level in st.session_state.unlocked_levels:
            st.success(f"✓ {level}")
        else:
            st.info(f"🔒 {level}")

    st.divider()

    st.caption(
        f"AI Provider: {AI_PROVIDER}"
    )

    st.caption(
        f"AI Model: {GEMINI_MODEL}"
    )


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    st.title("⌨️ AI Typing Speed Tester")

    st.subheader(
        "Test your typing speed, accuracy and improvement."
    )

    st.divider()

    st.header("Choose Your Level")

    columns = st.columns(3)

    for index, level in enumerate(
        ["Easy", "Hard", "Difficult"]
    ):

        with columns[index]:

            config = LEVELS[level]

            st.subheader(
                f"{config['icon']} {level}"
            )

            st.write(
                config["description"]
            )

            st.metric(
                "Time",
                f"{config['time']} sec"
            )

            if level in st.session_state.unlocked_levels:

                if st.button(
                    f"Start {level}",
                    key=f"start_{level}",
                    type="primary",
                    use_container_width=True
                ):

                    start_test(level)

                    st.rerun()

            else:

                st.button(
                    "🔒 Locked",
                    key=f"locked_{level}",
                    disabled=True,
                    use_container_width=True
                )

    st.divider()

    st.header("🚀 How It Works")

    info_columns = st.columns(4)

    with info_columns[0]:
        st.subheader("1️⃣ Select")
        st.write("Choose your difficulty level.")

    with info_columns[1]:
        st.subheader("2️⃣ Type")
        st.write("Type the paragraph before the timer ends.")

    with info_columns[2]:
        st.subheader("3️⃣ Analyze")
        st.write("See your WPM, accuracy and mistakes.")

    with info_columns[3]:
        st.subheader("4️⃣ Improve")
        st.write("Get AI feedback and unlock the next level.")


# ============================================================
# TEST PAGE
# ============================================================

elif st.session_state.page == "test":

    level = st.session_state.selected_level

    config = LEVELS[level]

    st.title(
        f"{config['icon']} {level} Typing Test"
    )

    st.caption(
        "Type the paragraph as accurately as possible."
    )

    elapsed = (
        time.time()
        -
        st.session_state.start_time
    )

    remaining = max(
        config["time"] - elapsed,
        0
    )

    if remaining <= 0:

        finish_test()

        st.rerun()

    minutes = int(
        remaining // 60
    )

    seconds = int(
        remaining % 60
    )

    timer_columns = st.columns(3)

    with timer_columns[0]:
        st.metric(
            "⏱️ Time Remaining",
            f"{minutes:02d}:{seconds:02d}"
        )

    with timer_columns[1]:
        st.metric(
            "🎯 Level",
            level
        )

    with timer_columns[2]:
        st.metric(
            "⏳ Total Time",
            f"{config['time']} sec"
        )

    st.progress(
        min(
            elapsed / config["time"],
            1.0
        )
    )

    st.divider()

    st.subheader("📖 Paragraph")

    st.info(
        st.session_state.paragraph
    )

    st.subheader("⌨️ Your Typing")

    typed_text = st.text_area(
        "Type here:",
        value=st.session_state.user_text,
        height=220,
        placeholder="Start typing the paragraph above...",
        label_visibility="collapsed"
    )

    st.session_state.user_text = typed_text

    live_result = calculate_result(
        st.session_state.paragraph,
        typed_text,
        max(elapsed, 0.1)
    )

    st.divider()

    st.subheader("📊 Live Statistics")

    stats = st.columns(4)

    with stats[0]:
        st.metric(
            "⚡ WPM",
            live_result["wpm"]
        )

    with stats[1]:
        st.metric(
            "🎯 Accuracy",
            f"{live_result['accuracy']}%"
        )

    with stats[2]:
        st.metric(
            "❌ Mistakes",
            live_result["mistakes"]
        )

    with stats[3]:
        st.metric(
            "🔤 Characters",
            live_result["typed"]
        )

    st.divider()

    if st.button(
        "✅ Finish Test",
        type="primary",
        use_container_width=True
    ):

        finish_test()

        st.rerun()

    time.sleep(1)

    st.rerun()


# ============================================================
# RESULT PAGE
# ============================================================

elif st.session_state.page == "result":

    result = st.session_state.result

    level = st.session_state.last_level

    st.title("🎉 Test Complete!")

    st.caption(
        f"{level} level result"
    )

    st.divider()

    stats = st.columns(5)

    with stats[0]:
        st.metric(
            "⚡ WPM",
            result["wpm"]
        )

    with stats[1]:
        st.metric(
            "🎯 Accuracy",
            f"{result['accuracy']}%"
        )

    with stats[2]:
        st.metric(
            "❌ Mistakes",
            result["mistakes"]
        )

    with stats[3]:
        st.metric(
            "⏱️ Time",
            f"{result['time']}s"
        )

    with stats[4]:
        st.metric(
            "🏆 Score",
            f"{result['score']}/100"
        )

    st.divider()

    st.header("📊 Detailed Result")

    detail_columns = st.columns(3)

    with detail_columns[0]:

        st.write(
            f"**Typing Speed:** {result['wpm']} WPM"
        )

        st.write(
            f"**Characters Per Minute:** {result['cpm']} CPM"
        )

    with detail_columns[1]:

        st.write(
            f"**Correct Characters:** {result['correct']}"
        )

        st.write(
            f"**Characters Typed:** {result['typed']}"
        )

    with detail_columns[2]:

        st.write(
            f"**Mistakes:** {result['mistakes']}"
        )

        st.write(
            f"**Time:** {result['time']} seconds"
        )

    st.divider()

    st.header("🤖 AI Typing Coach")

    st.info(
        st.session_state.ai_feedback
    )

    st.divider()

    next_level = None

    if level == "Easy":
        next_level = "Hard"

    elif level == "Hard":
        next_level = "Difficult"

    buttons = st.columns(3)

    with buttons[0]:

        if st.button(
            "🔄 Retry",
            use_container_width=True
        ):

            start_test(level)

            st.rerun()

    with buttons[1]:

        if next_level:

            if st.button(
                f"➡️ Next: {next_level}",
                type="primary",
                use_container_width=True
            ):

                start_test(next_level)

                st.rerun()

        else:

            st.success(
                "🏆 You completed all levels!"
            )

    with buttons[2]:

        if st.button(
            "📊 History",
            use_container_width=True
        ):

            st.session_state.page = "history"

            st.rerun()


# ============================================================
# HISTORY PAGE
# ============================================================

elif st.session_state.page == "history":

    st.title("📊 Typing History")

    st.caption(
        "Track your typing performance over time."
    )

    history = st.session_state.history

    if not history:

        st.info(
            "No tests completed yet."
        )

    else:

        total_tests = len(history)

        average_wpm = (
            sum(
                item["wpm"]
                for item in history
            )
            /
            total_tests
        )

        best_wpm = max(
            item["wpm"]
            for item in history
        )

        best_accuracy = max(
            item["accuracy"]
            for item in history
        )

        average_accuracy = (
            sum(
                item["accuracy"]
                for item in history
            )
            /
            total_tests
        )

        st.header("📈 Overall Statistics")

        overview = st.columns(4)

        with overview[0]:
            st.metric(
                "🧪 Tests",
                total_tests
            )

        with overview[1]:
            st.metric(
                "⚡ Average WPM",
                round(average_wpm, 1)
            )

        with overview[2]:
            st.metric(
                "🚀 Best WPM",
                best_wpm
            )

        with overview[3]:
            st.metric(
                "🎯 Best Accuracy",
                f"{best_accuracy}%"
            )

        st.caption(
            f"Average Accuracy: {round(average_accuracy, 1)}%"
        )

        st.divider()

        st.header("📜 Previous Tests")

        for index, item in enumerate(history):

            with st.expander(
                f"{item['level']} • "
                f"{item['wpm']} WPM • "
                f"{item['accuracy']}% • "
                f"{item['date']}"
            ):

                cols = st.columns(6)

                with cols[0]:
                    st.metric(
                        "Level",
                        item["level"]
                    )

                with cols[1]:
                    st.metric(
                        "WPM",
                        item["wpm"]
                    )

                with cols[2]:
                    st.metric(
                        "Accuracy",
                        f"{item['accuracy']}%"
                    )

                with cols[3]:
                    st.metric(
                        "Mistakes",
                        item["mistakes"]
                    )

                with cols[4]:
                    st.metric(
                        "Time",
                        f"{item['time']}s"
                    )

                with cols[5]:
                    st.metric(
                        "Score",
                        f"{item['score']}/100"
                    )

        st.divider()

        if st.button(
            "🗑️ Clear History",
            use_container_width=True
        ):

            st.session_state.history = []

            save_history([])

            st.success(
                "History cleared successfully."
            )

            st.rerun()
# ```

# ### `requirements.txt`

# streamlit
# google-genai

# Bas ab **purana `app.py` poora replace** karke ye wala code paste karo. Is version mein UI ke liye **koi custom HTML/CSS nahi hai**, sirf Streamlit ke native components use hue hain.
