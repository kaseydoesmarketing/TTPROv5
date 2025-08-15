# Firebase Service Account Setup for Render

## IMPORTANT: This file contains sensitive credentials. DO NOT commit to Git\!

## Setup Instructions for Render:

1. **Go to Render Dashboard**
   - Navigate to your service: https://dashboard.render.com/
   - Select your TTPROv5 service (srv-d29srkqdbo4c73antk40)

2. **Add Secret File**
   - Go to "Environment" tab
   - Scroll to "Secret Files" section
   - Click "Add Secret File"
   - Filename: `service-account.json`
   - Content: Copy the entire contents of the service-account.json file

3. **Add Environment Variable**
   - In "Environment Variables" section
   - Add: `GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/service-account.json`
   - This tells Firebase where to find the credentials

4. **Deploy**
   - Save changes
   - Render will automatically redeploy with the new configuration

## Security Notes:
- The service account file is stored securely by Render
- It's mounted at `/etc/secrets/` at runtime
- Never commit the actual service-account.json to Git
- Always use Secret Files for sensitive credentials

## Verification:
After deployment, your logs should show:
```
🔐 Firebase: Using SECURE service account file: /etc/secrets/service-account.json
✅ Firebase Admin SDK initialized successfully using SECURE service account file
```
