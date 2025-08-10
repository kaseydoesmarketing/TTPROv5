# 🔐 Firebase Secret File Setup for TTPROv5

## Required Firebase Service Account JSON

You need to add the complete Firebase service account JSON as a **Secret File** in Render.

### Step-by-Step Instructions:

1. **Go to Render Dashboard**
   - Navigate to your new TTPROv5 backend service
   - Go to Settings → Secret Files

2. **Add Secret File**
   - Click "Add Secret File"
   - **Filename:** `firebase-key.json`
   - **Content:** Paste the complete JSON from your Firebase service account

### Expected JSON Structure:
```json
{
  "type": "service_account",
  "project_id": "titletesterpro",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYour-private-key-content\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service@titletesterpro.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs/your-service%40titletesterpro.iam.gserviceaccount.com"
}
```

### Important Notes:
- The file will be available at `/etc/secrets/firebase-key.json` inside the container
- The environment variable `GOOGLE_APPLICATION_CREDENTIALS` points to this path
- Make sure the JSON is valid (no extra commas, proper quotes)
- The `project_id` should be `titletesterpro`

### Verification:
After adding the secret file and deploying, test:
```bash
curl https://your-backend-url.onrender.com/debug/firebase
```

Should return:
```json
{
  "configuration_method": "SECRET_FILE",
  "file_exists": true,
  "firebase_initialized": true,
  "google_application_credentials": "firebase-key.json",
  "allow_env_fallback": "0"
}
```

✅ **Ready to proceed with deployment once this secret file is configured!**