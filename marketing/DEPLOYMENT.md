# TTPROv5 Marketing Frontend Deployment

## Deployment Configuration

### Active Branch
- **Production Branch**: `bootstrap/v5`
- **Auto-deploy Enabled**: Yes

### Backend API
- **Production API**: https://ttprov5.onrender.com

### Environment Variables
All environment variables are configured in:
1. `vercel.json` - API base URL
2. Vercel Dashboard - Sensitive keys and secrets

### Deployment Status
- ✅ Automatic deployments from `bootstrap/v5` branch
- ✅ Backend pointing to TTPROv5
- ✅ All environment variables configured

### Last Verified
- Date: August 11, 2025
- Status: Working
- Deployment URL: https://marketing-pevsial99-ttpro-live.vercel.app

## Troubleshooting

If deployments fail:
1. Check `vercel.json` for any `@secret_name` references
2. Verify branch configuration in vercel.json
3. Ensure Vercel Dashboard Production Branch matches `bootstrap/v5`