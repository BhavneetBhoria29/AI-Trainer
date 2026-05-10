# Real-time AI Gym Coach

An AI-powered fitness trainer that watches your workout through your webcam, analyzes your form in real-time, counts your reps, and delivers personalized voice coaching — powered by MediaPipe, Claude AI, and Streamlit.

---

## What It Does

- **Live pose detection** — MediaPipe tracks 33 body landmarks on every frame from your camera
- **Form analysis** — exercise-specific detectors check angles, depth, balance, and alignment
- **Rep & set counting** — automatic counting via pose state machines (no manual input)
- **AI voice coaching** — Claude Sonnet generates natural coaching cues, spoken aloud via text-to-speech
- **Workout history** — sessions saved to a local database with daily aggregated stats

---

## Supported Exercises

| Exercise | Metrics Tracked |
|---|---|
| Squats | Knee angle, depth, back lean, balance |
| Push-ups | Elbow angle, back arch, body alignment |
| Biceps Curls | Elbow angle, swing detection, elbow drift |
| Shoulder Press | Elbow angle, overhead extension, back arch |
| Lunges | Knee angles, torso upright, balance, hip level |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Streamlit 1.54 |
| Video streaming | streamlit-webrtc 0.64.5 |
| Pose detection | MediaPipe 0.10.35 (PoseLandmarker full model) |
| Image processing | OpenCV |
| AI coaching | Anthropic Claude Sonnet (`claude-sonnet-4-6`) |
| Text-to-speech | gTTS (Google TTS) |
| Database | SQLite3 |

---

## Project Structure

```
AI TRAINER/
├── main.py                              # Streamlit app entry point
├── core/
│   └── base_exercise.py                 # Abstract base class for detectors
├── detectors/
│   ├── squats.py
│   ├── bench_press.py                   # Used for push-ups
│   ├── biceps_curl.py
│   ├── shoulder_press.py
│   └── lunges.py
├── services/
│   ├── auth/login_wall.py               # Username-based login
│   ├── coaching/
│   │   ├── llm.py                       # Claude API integration
│   │   ├── tts.py                       # gTTS wrapper
│   │   └── voice_pipeline.py            # Event-driven coaching orchestration
│   ├── config/workout_config.py         # Exercise list, metrics schema, AI prompt
│   ├── persistence/exercise_repository.py  # SQLite CRUD
│   ├── state/session_default.py         # Streamlit session state defaults
│   ├── tracking/metrics.py              # Real-time metrics sync & set logic
│   ├── ui/style_loader.py               # CSS/font injection
│   └── vision/exercise_video_processor.py  # MediaPipe + detector orchestration
├── ml_models/
│   └── pose_landmarker_full.task        # MediaPipe pose model
├── static/
│   └── style.css
├── requirements.txt
└── packages.txt                         # System dependencies for Streamlit Cloud
```

---

## Getting Started

### Prerequisites

- Python 3.10–3.12
- A webcam
- An [Anthropic API key](https://console.anthropic.com/)

### Installation

```bash
git clone https://github.com/BhavneetBhoria29/AI-Trainer.git
cd AI-Trainer
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your-api-key-here
```

### Run

```bash
streamlit run main.py
```

Open `http://localhost:8501` in your browser, allow camera access, and start training.

---

## How It Works

```
Login → Select Exercise & Plan (sets/reps) → Start Workout
    ↓
Camera → WebRTC stream → VideoProcessorClass
    ↓
MediaPipe detects 33 body landmarks per frame
    ↓
Exercise detector analyzes angles & form → metrics
    ↓
VoicePipeline detects events (rep done, bad form, set complete)
    ↓
Claude generates coaching cue → gTTS speaks it aloud
    ↓
Reps & sets saved to SQLite → history displayed
```

### Coaching Events

| Event | Trigger | Response |
|---|---|---|
| `workout_started` | User clicks Start | Motivational cue |
| `ongoing_form_check` | Every frame | Form correction or encouragement |
| `set_completed` | Reps hit target | Praise + save to DB |
| `no_pose_detected` | No body in frame | Repositioning instruction |
| `workout_completed` | All sets done | Closing message |

Form corrections are rate-limited to one every 5 seconds to avoid overwhelming the user.

---

## Deployment

### Streamlit Community Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select this repo, `main.py`
3. Add your API key under **Settings → Secrets**:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
4. Deploy

### Landing Page (Netlify)

The `landingpage/` folder contains a static HTML/CSS landing page deployed separately on Netlify. The `netlify.toml` configures Netlify to publish only that folder.

---

## Notes

- Workout history is stored in `data.db` (SQLite). On Streamlit Cloud, this resets on each restart — use a hosted database for persistent storage.
- The full MediaPipe pose model (`pose_landmarker_full.task`) provides the most accurate landmark detection but requires more compute than the lite model.
- All voice coaching happens client-side via auto-playing audio injected into the Streamlit page.

---

## Author

**Bhavneet Bhoria**

- [LinkedIn](https://www.linkedin.com/in/bhavneet-bhoria-3b7021319/)
- [GitHub](https://github.com/BhavneetBhoria29)
- [Email](mailto:bhavrajput97@gmail.com)
