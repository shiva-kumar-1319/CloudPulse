# CloudPulse Firebase Hosting & Deployment Guide

This guide outlines how to deploy and operate the **CloudPulse Autonomous Command Center** on **Firebase Hosting**.

---

## 1. Architecture Overview

The web dashboard is packaged as a high-performance static SPA located in the `public/` directory:
- `public/index.html`: Main HTML5 application container with SEO & OpenGraph meta tags.
- `public/style.css`: Glassmorphism design system, responsive layouts, and animations.
- `public/app.js`: Reactive telemetry engine, Chart.js multi-metric streams, chaos fault injection simulator, and interactive API sandbox.

---

## 2. Automated Deployment via GitHub Actions (CI/CD)

The repository includes a pre-configured CI/CD workflow at `.github/workflows/firebase-deploy.yml`.

### Step 1: Generate Firebase Service Account Key
1. Open the [Firebase Console](https://console.firebase.google.com/).
2. Select or create your project: `cloudpulse-platform`.
3. Navigate to **Project Settings** > **Service Accounts**.
4. Click **Generate New Private Key** and download the JSON credentials file.

### Step 2: Configure GitHub Repository Secret
1. In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret**.
3. Name: `FIREBASE_SERVICE_ACCOUNT_CLOUDPULSE_PLATFORM`
4. Value: Paste the full contents of the generated JSON service account key.
5. Save secret.

### Step 3: Trigger Deployment
- Every push to the `main` branch will automatically validate static assets and deploy directly to Firebase Hosting live channel!

---

## 3. Manual Deployment via Firebase CLI

If you prefer deploying directly from your terminal:

```bash
# 1. Install Firebase Tools globally (or use npx)
npm install -g firebase-tools

# 2. Authenticate with Google
firebase login

# 3. Verify active project
firebase use cloudpulse-platform

# 4. Preview locally before deploying
firebase emulators:start --only hosting

# 5. Deploy to Production
firebase deploy --only hosting
```

---

## 4. Security & Caching Headers

The production configuration in `firebase.json` automatically enforces:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- Long-term immutable caching for CSS & JS bundles (`max-age=604800`)
