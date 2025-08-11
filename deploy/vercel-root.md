# Vercel Root Directory Configuration

The Next.js frontend for TitleTesterPro is located in the `/marketing` directory.

## Required Vercel Configuration

**Root Directory**: `/marketing`

This must be set in Vercel Dashboard under:
Project → Settings → Build & Development Settings → Root Directory

## Why This Is Important

- The `/marketing` folder contains the `package.json` with Next.js dependencies
- This is where the Next.js app structure (`app/`, `lib/`, `components/`) is located
- Vercel needs this to detect Next.js and run the correct build commands

## File Structure
```
TTPROv5/
├── marketing/           ← Set as Root Directory in Vercel
│   ├── package.json     (contains "next" dependency)
│   ├── app/            (Next.js app directory)
│   ├── lib/            (utilities and Firebase client)
│   └── components/     (React components)
├── app/                (FastAPI backend - deployed to Render)
└── ...
```