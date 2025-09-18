# Mini Chat 0.2

**Mini Chat 0.2** is a modern chat application with AI integration, capable of generating text and images using OpenAI and Stability AI APIs. It features a responsive frontend with React and a FastAPI backend with SQLite support.

---

## Features

* Real-time chat interface
* AI-generated responses
* Image generation from prompts (`/image` command)
* Emoji and tag support
* User authentication
* Rate limiting for API requests
* Syntax-highlighted code snippets in messages

---

## Tech Stack

* **Frontend:** React, TailwindCSS, Framer Motion, React Icons
* **Backend:** FastAPI, SQLAlchemy, SQLite
* **AI APIs:** OpenAI GPT, Stability AI (Stable Diffusion)

---

## Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_key
STABILITY_API_KEY=your_stability_ai_key
SECRET_KEY=your_secret_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_password
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

Access at `http://localhost:3000`.

---

## Usage

* Type messages and send them using the arrow button.
* To generate an image, type `/image <your prompt>`.
* Use tags with the plus button.
* Scroll down automatically when new messages arrive.

---

## License

MIT License
