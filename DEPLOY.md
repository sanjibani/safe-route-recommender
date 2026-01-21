# Deploying to Vercel (Free Tier)

Your application is now fully configured for a **Zero-Cost** Serverless deployment.

## Prerequisites
- A GitHub account.
- A Vercel account (linked to GitHub).

## Steps

### 1. Push to GitHub
If you haven't already, push this repository to GitHub:
```bash
git init
git add .
git commit -m "Ready for Vercel deployment"
git branch -M main
git remote add origin https://github.com/<your-username>/safe-route-recommender.git
git push -u origin main
```

### 2. Deploy on Vercel
1.  Go to [Vercel Dashboard](https://vercel.com/dashboard).
2.  Click **"Add New..."** -> **"Project"**.
3.  Import your `safe-route-recommender` repository.
4.  **Configuration**:
    - **Framework Preset**: select `Other` (or efficient defaults).
    - **Root Directory**: `./` (default).
    - **Build Command**: Leave empty (Python builds automatically).
    - **Output Directory**: Leave empty.
5.  Click **Deploy**.

### 3. Verify
Once deployed, Vercel will give you a URL (e.g., `https://safe-route.vercel.app`).
- Open `https://safe-route.vercel.app/static/index.html` to see your map!

## What Changed?
- **Database**: Removed. We now load `data/processed_crime.csv` into memory (RAM) at startup.
- **Routing**: Removed local Docker OSRM. We now use the free `router.project-osrm.org` API.
- **Cost**: **$0/month**.
