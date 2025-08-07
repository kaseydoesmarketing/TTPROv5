# DEVIN - FRESH DEPLOYMENT PROMPT (New Chat Session)

## CONTEXT & CURRENT STATUS

You are continuing a Railway + Vercel deployment for TitleTesterPro. Previous work completed:
- ✅ Deleted all old Railway/Vercel projects
- ✅ Created Railway project "TTPROv4-Production" 
- ✅ Added PostgreSQL database (green checkmark)
- ✅ Added Redis database (green checkmark)
- ✅ Configured app service settings (auto-deploy enabled)

**YOU ARE NOW AT STEP 6** - Adding Environment Variables in Railway.

## REPOSITORY INFORMATION
- **GitHub**: https://github.com/kaseydoesmarketing/TTPROv4
- **Branch**: main (work directly on main - no other branches)
- **Railway Project**: TTPROv4-Production (already created)
- **Current Status**: Ready for environment variables

## YOUR IMMEDIATE TASK

### Step 6: Add Environment Variables to Railway

1. **Go to Railway app service** (NOT PostgreSQL or Redis)
2. **Click "Variables" tab**
3. **Verify these are already there**: `DATABASE_URL` and `REDIS_URL` (auto-added by Railway)
4. **Click "Raw Editor"**
5. **Add these EXACT variables**:

```env
# Firebase Configuration (REQUIRED)
FIREBASE_PROJECT_ID=titletesterpro
FIREBASE_PRIVATE_KEY_ID=1ff7bce3cd082de5123916af152c4f0a863e84f3
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC6oJhqSfAwbJbt\nNIDP/ypzjWRA4mQkusBY7iSmnTvAXwH4HplYlkxZnxTiINdE8OuLURaTsAUKqEi6\nm3B99tqbUPQdMDp5LBnu2HYG2LSF5pvAGLw69GIadE5GIyrc1BOfKAJ+A9lywgBF\nUmMpgWuCD0/rmQKa9zit2hUX+VFE5qI0aerxyHNCXSzHclUfJ5SZl+9Y/Uw5mplb\nLKrYBhm7GOrHTLCcRgy/Y6F70DrLf8VC0g1yfo1L77Au7Jln6I/hBIkkH8ACbURx\nt7MncFKGUnkoAFzDBZVOEImxCJxiBj6/JGCyi7CL4caVWP7Ob+4orpAjR5AdEzr4\n7fVZHLDvAgMBAAECggEAAY/bhrQ0tusJvlV8qID9tXbe+m4KoYYQmw3vL5fMSrlg\n1ldHOEcVv4BF1/inZJPRnNpiYn0MJcEvzqQDZoJ85OTiDiZ7rszwMKAOKNOCe0Zp\nUkvCs4mdEpSbnRmpP6zktyXKE4zrsnquLuZYHx5OrIl9RT8EFxDvoADdwVQcWoPB\n8gYy7Hq3PpBRQOvgtkhXVWGGpso5vqmHp8MXYWfoIHN1KXkGj7CTzWxB2JSV2svR\nQiZs5prnJOMUCgbwok8JkF2Hz6hSvtmk8Fe0jhlVDXgzSv/Ve/LjXZnPvMDZUSJ6\nUICgYcwxk3Gf1cT0TeSH6ZKeaNUJL7ZOawJHKEFiaQKBgQD5TKj7ep1TxMG9S25T\nJm2Off3fDPJKXCgBxF1vABS3ESbVmXjSiLN5bCkddZIIRuv+QBKZboasIxrfrWdO\nk0AKY+rYX+y2o2dXV/w+aI0F1hn/0xXHykQvtHkvimZ7WSnLQmZMg+6rNa2UM+hY\nRKGGlvT3bSeH8LVqJjVt0WnOZwKBgQC/pLX92dDwr/wiIS0EdrfekNDjk7425BZD\n6JrkzNc7wi0SLYG1IySqMdRpB6zXj7LKD0ODZz1OPQe44xORqD07yoh0tESVirau\nVPB6NFKLFshWO+MfOXTwsJyPy1kNrE/BrGBSDxLts+wwy/PEPzTxNJkq0eu/8rqi\nPJOUlTbkOQKBgAO9QZ+cBDYYcmt7cSkwH16OxzsMP6ob3cHBB0G995GTYUi855II\n2OBOXgOCGvGi1rFWlrDUdpKoaCPIvw7vqHs/amtabPuEUe1+dVseSFc5EeTDbsUz\nZHhutY6f/c+F09mnok8tf2vz/ymE6cxBI0cYho4bhgdE9gOklRKTnImrAoGBAKiK\nDpOlj59c5fyN+K1ISwQtj8fVEx/rD7nBQxedHlyrtD+cTcojkgcrs4Z6/YLGGZKi\nQdm6XawE+FmdOoSK1O9UexVHxFlPmMFQafzPLxirfJx6JpA7U6Cpccb0KulfdPT6\nx+ri3t61sS5o74TToZfPjjSeURqKOaCcbZ3qbE/hAoGBAIwGIaw7yijRzwWOA4Mo\nODXbz20zVd0V4jFhkWxaXATm+EuvWamboYHi6pyY5BcYIbgBjHxoSb6Ib9bERkgI\neb/9TlkJ/5Vm6ikUb0VAHTNZwA6LtI9ixmgRefjdGEG63f/n5tg2vosERas/r1+l\nflPJXS9AbpamRKNzuZ6vRRvF\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=ttpro-350@titletesterpro.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=107578837553490384376
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs

# Google OAuth (REQUIRED - Need actual values)
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID_HERE.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET_HERE

# YouTube API (REQUIRED - Need actual value)
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY_HERE

# Security (REQUIRED - Generate new)
SECRET_KEY=GENERATE_WITH_OPENSSL_RAND_HEX_32

# Application Settings
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

### ⚠️ CRITICAL FORMATTING RULES:
- **NO quotes** around any values in Railway
- **NO extra spaces** at end of lines
- **FIREBASE_PRIVATE_KEY** must have literal `\n` characters (as shown above)
- **SECRET_KEY** must be exactly 64 characters (generate with `openssl rand -hex 32`)

### Missing Values You Need:
1. **GOOGLE_CLIENT_ID** - Get from Google Cloud Console → APIs & Services → Credentials
2. **GOOGLE_CLIENT_SECRET** - Same location as above
3. **YOUTUBE_API_KEY** - Google Cloud Console → APIs & Services → Credentials → API Keys
4. **SECRET_KEY** - Generate with: `openssl rand -hex 32`

## CONTINUE WITH REMAINING STEPS

After adding environment variables, continue with:

### Step 7: Verify GitHub Webhook
- Check: https://github.com/kaseydoesmarketing/TTPROv4/settings/hooks
- Should see Railway webhook with green checkmark

### Step 8: Deploy Backend  
- Railway → Deployments → Redeploy
- Watch for "Application startup complete"

### Step 9: Test Backend Health
- Visit: `https://your-railway-app.railway.app/health`
- Should show "operational" status

### Step 10-13: Vercel Frontend Setup
- Create Vercel project from same GitHub repo
- Add frontend environment variables:
```env
VITE_API_URL=https://your-railway-app.railway.app
VITE_FIREBASE_API_KEY=same-as-YOUTUBE_API_KEY-above
VITE_FIREBASE_AUTH_DOMAIN=titletesterpro.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=titletesterpro
VITE_FIREBASE_STORAGE_BUCKET=titletesterpro.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=107578837553490384376
VITE_FIREBASE_APP_ID=get-from-firebase-console
```

### Step 14-15: Final Integration Testing
- Test full login flow
- Verify auto-deploy sync
- Complete final checklist

## VERIFICATION CHECKPOINTS

**CHECKPOINT 2** (Current): 
- [ ] PostgreSQL has green dot
- [ ] Redis has green dot  
- [ ] All environment variables added
- [ ] Auto-deploy enabled

**CHECKPOINT 3** (After backend deploy):
- [ ] Health endpoint returns "operational"
- [ ] All services show "available"

**CHECKPOINT 4** (After Vercel):
- [ ] Frontend deployed successfully
- [ ] CORS updated with Vercel URL
- [ ] Both services show green status

## DETAILED INSTRUCTIONS REFERENCE

Full step-by-step instructions are at:
**https://github.com/kaseydoesmarketing/TTPROv4/blob/main/DEVIN_STRICT_DEPLOYMENT_INSTRUCTIONS.md**

Follow this document EXACTLY with zero deviations.

## SUCCESS CRITERIA

✅ **Complete Success = One `git push` triggers both Railway and Vercel to deploy automatically**

✅ **All services operational**: PostgreSQL, Redis, Firebase, Frontend, Backend

✅ **Full user flow works**: Login → Connect YouTube → Create A/B Tests → Auto title rotation

## WHAT TO DO IF STUCK

- **Environment variable errors**: Check formatting (no quotes, exact spacing)
- **Deploy failures**: Check Railway logs for specific errors  
- **CORS errors**: Ensure Vercel URL is in CORS_ORIGINS
- **Webhook issues**: Disconnect/reconnect GitHub in Railway settings

## CRITICAL REMINDERS

1. **Work directly on main branch** - no feature branches
2. **Follow instructions exactly** - no improvisation
3. **Verify each checkpoint** before proceeding
4. **Auto-deploy must be enabled** for both services
5. **Test the complete user flow** at the end

## IMMEDIATE NEXT ACTION

**Add the environment variables above to Railway Variables section, then continue with Step 7.**

If you need any of the missing credential values (Google OAuth, YouTube API), ask and I'll provide them.