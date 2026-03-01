# My Cooking Guide

A smart, AI-powered weekly meal planner that generates nutritionally balanced menus based on your ingredients, energy levels, and dietary needs. Built with Next.js, FastAPI, PostgreSQL, and Google Gemini.

## Prerequisites

- Node.js (v18+)
- Python (v3.11+)
- Docker and Docker Compose (for database and managed deployment)
- A Google Gemini API Key
- Google OAuth Credentials

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the root directory based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and configure your keys:
- Add your `GEMINI_API_KEY`
- Add your Google OAuth credentials (`GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`)
- Change the `JWT_SECRET` for production

### 2. Local Development (Docker Compose)

The easiest way to run the full stack locally is using Docker Compose. Make sure Docker is running on your machine.

```bash
docker-compose up --build
```

This starts:
1. **Frontend:** Next.js UI running on `http://localhost:3000`
2. **Backend:** FastAPI server running on `http://localhost:8000`
3. **Database:** PostgreSQL instance running on port `5432`

### 3. Usage

1. Open your browser and navigate to `http://localhost:3000`.
2. Click **"Get Started"** to enter the 3-step onboarding wizard.
3. Select your household size, diet, and meal types.
4. Add 3–5 items currently in your pantry.
5. Hit **Generate**! If the backend API isn't fully configured with keys, the app gracefully falls back to a robust mock UI to explore the calendar interface.
6. Check out the **Saturday Prep Plan**, use the **Swap** button on individual meals (which calls the AI to replace a single item), and browse past menus in the **History** tab.

## Deployment (DigitalOcean App Platform)

1. Connect your GitHub repository to DigitalOcean.
2. Create an App.
3. Configure **two Web Services** from the mono-repo:
   - Frontend path: `/frontend` (Build Command: `npm run build`)
   - Backend path: `/backend` (Uses Dockerfile)
4. Add a Managed PostgreSQL Database and map the connection URL to the backend's environment variables.
5. Set all secrets from your `.env` directly in the DigitalOcean App Platform dashboard.
