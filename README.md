# 🧠 CursorEye — Empowering Accessibility Through Eye Control

> A Hackathon project built to make technology accessible to everyone — especially individuals with physical disabilities — by enabling full computer control using **eye and facial movements**.

---

## 📖 Description

**CursorEye** is an assistive technology web app that uses **real-time eye tracking and facial recognition** to replace traditional mouse input.  
Users can perform core mouse functionalities — **click, double-click, drag, drop, and scroll** — entirely through eye blinks and facial gestures.

As part of our Hackathon demo, we’ve included a **Tic-Tac-Toe game** that’s fully controllable using CursorEye, showcasing the potential of accessible gaming and real-time interactivity.

### 💡 Vision

Empower individuals with limited mobility to **participate, create, and work** in the digital world independently.

---

## ✨ Key Features

- 👁️ **Eye-Based Mouse Control** — Perform clicks and drags using facial gestures
- 🔄 **Real-Time Updates** — Built using WebSockets for smooth, responsive control
- 🔒 **User Authentication** — Secure login and personalized settings
- ⚙️ **Customizable Sensitivity** — Adjust blink thresholds and motion detection
- 🎮 **Interactive Demo Game** — Play Tic-Tac-Toe hands-free
- ☁️ **Cloud-Ready Deployment** — Easy to host on AWS, Render, or Railway
- 🧠 **Assistive Technology Focus** — Designed to improve independence and accessibility

---

## 🧰 Tech Stack

| Layer                       | Technology             |
| :-------------------------- | :--------------------- |
| **Frontend**                | Angular + Tailwind CSS |
| **Backend**                 | Flask (Python)         |
| **Real-Time Communication** | WebSockets             |
| **AI / Vision**             | OpenCV + Mediapipe     |
| **Database**                | SQLite / PostgreSQL    |
| **Deployment**              | AWS / Render / Railway |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

git clone https://github.com/The-Azure-Coder/cursor_eye.git
cd CursorEye

### 2️⃣ Create a Virtual Environment (Optional but Recommended)

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

### 3️⃣ Install Dependencies

pip install -r requirements.txt

### 4️⃣ Run the Application

python run.py

Once the app is running, open your browser and navigate to:
👉 http://127.0.0.1:5000/

### 🕹️ How to Use:

- Launch the backend server (python run.py)
- Open the Angular frontend in your browser
- Log in or register an account
- Calibrate your eye-tracking preferences
- Control the mouse and play Tic-Tac-Toe — hands-free!

### 🚀 Future Roadmap

Feature: ................................... Description:
🗣️ Speech AI Input | Add hybrid control via voice commands
🔤 Dyslexia-Friendly Text Converter | Adjust fonts and spacing for readability
⌨️ On-Screen Keyboard | Type using gaze-based key selection
☁️ Cloud User Profiles | Sync user settings across devices

## 🌍 Real-World Impact

CursorEye helps bridge the digital divide by enabling people with disabilities to:
💼 Work standard office jobs remotely
🧠 Exercise facial muscles naturally through interaction
🙌 Gain independence and confidence in daily tech use
💬 Engage socially and professionally online
🌐 Fully participate in the growing digital economy

“Technology becomes truly powerful when it empowers everyone.”

## 👥 Team:

Name: .......................... Role:
Anita Baker | FrontEnd, Authentication, Documentation
Akeem Henry | FrontEnd, UI/UX Designer
Aldaine Clarke | Backend, API, frontend integration, Database
Tyrese Morgan | Backend, AI integration,frontend integration
