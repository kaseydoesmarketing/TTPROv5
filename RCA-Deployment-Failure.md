# Root Cause Analysis: Vercel Deployment Failures

## Executive Summary
Multiple deployment failures occurred on Vercel for the TTPROv5 marketing frontend between August 10-11, 2025, with the primary issue being an environment variable misconfiguration referencing a non-existent secret.

## Timeline of Events

### August 10, 2025
- **~20:00 UTC**: Initial deployment attempts begin failing
- **Multiple attempts**: 15+ failed deployments over several hours
- **Error message**: "Environment Variable 'NEXT_PUBLIC_API_BASE_URL' references Secret 'next_public_api_base_url', which does not exist"

### August 11, 2025  
- **03:00 UTC**: Issue identified in vercel.json configuration
- **03:07 UTC**: Fix applied, successful deployment achieved
- **03:13 UTC**: Branch configuration updated for bootstrap/v5

## Root Causes Identified

### 1. PRIMARY CAUSE: Secret Reference in vercel.json
**Location**: `/marketing/vercel.json` line 24
```json
"env": {
  "NEXT_PUBLIC_API_BASE_URL": "@next_public_api_base_url"
}
```

**Issue**: The `@` prefix indicates a Vercel Secret reference, but no secret with name `next_public_api_base_url` existed in the Vercel project.

**Impact**: 100% deployment failure rate - this was a blocking issue

### 2. SECONDARY CAUSE: Branch Configuration Mismatch
**Location**: `/marketing/vercel.json` lines 3-7
```json
"deploymentEnabled": {
  "TTPROv5": true,
  "bootstrap/v5": false
}
```

**Issue**: Auto-deployment was enabled for wrong branch (TTPROv5) instead of the active development branch (bootstrap/v5)

**Impact**: GitHub pushes to bootstrap/v5 didn't trigger automatic deployments

### 3. CONTRIBUTING FACTOR: Environment Variable Management
- Environment variables were being set via CLI but the vercel.json override took precedence
- CLI attempts to remove/re-add the variable didn't resolve the issue because vercel.json configuration persisted
- Mix of configuration methods (Dashboard, CLI, vercel.json) created confusion

## Technical Analysis

### Why the Issue Persisted Despite CLI Changes
1. **Configuration Hierarchy**: vercel.json > Dashboard > CLI runtime values
2. **Secret vs Plain Text**: Vercel treats `@variable_name` as a secret reference, requiring the secret to exist
3. **Cache/State**: Even after removing env vars via CLI, the vercel.json configuration remained

### Deployment Flow Breakdown
```
Push to GitHub → Vercel receives webhook → Reads vercel.json → 
Attempts to resolve @next_public_api_base_url → Secret not found → 
Deployment fails before build starts
```

## Resolution Steps Taken

1. **Fixed vercel.json** (Commit: 162a58b2)
   - Changed `"@next_public_api_base_url"` to `"https://ttprov5.onrender.com"`
   
2. **Updated branch configuration** (Commit: f2d828a8)
   - Set `"bootstrap/v5": true` and `"TTPROv5": false`

3. **Pushed fixes to repository**
   - Ensured GitHub integration would use correct configuration

## Lessons Learned

### 1. Configuration Management
- **Problem**: Multiple configuration sources created confusion
- **Solution**: Establish single source of truth (prefer vercel.json for version control)

### 2. Secret Management
- **Problem**: Hardcoded secret references without validation
- **Solution**: Use plain text for non-sensitive values like API URLs

### 3. Branch Strategy
- **Problem**: Deployment configuration didn't match active development branch
- **Solution**: Align deployment settings with git workflow

### 4. Error Messages
- **Problem**: Error message was clear but fix location wasn't obvious
- **Solution**: Check vercel.json first for configuration issues

## Preventive Measures

### Immediate Actions
1. ✅ Fixed vercel.json to use plain text URL instead of secret reference
2. ✅ Enabled auto-deployment for correct branch (bootstrap/v5)
3. ✅ Verified successful deployment

### Recommended Long-term Actions
1. **Standardize Configuration Approach**
   - Use vercel.json as primary configuration source
   - Document all environment variables and their types (secret vs plain)

2. **Add Pre-deployment Validation**
   - Create a script to validate vercel.json before commits
   - Check for non-existent secret references

3. **Documentation**
   - Document the deployment configuration in README
   - Include troubleshooting guide for common deployment issues

4. **Monitoring**
   - Set up deployment failure alerts
   - Monitor deployment success rate

## Configuration Best Practices

### DO:
- Use plain text for non-sensitive configuration (URLs, feature flags)
- Keep vercel.json in version control
- Align branch configuration with git workflow
- Test deployments after configuration changes

### DON'T:
- Use secret references (@) for non-sensitive values
- Mix configuration methods without clear hierarchy understanding
- Assume CLI changes override vercel.json
- Deploy from multiple branches without clear strategy

## Impact Assessment

- **Downtime**: ~7 hours of deployment blockage
- **Failed Deployments**: 15+ attempts
- **Development Impact**: Delayed frontend updates to use TTPROv5 backend
- **Resolution Time**: ~15 minutes once root cause identified

## Conclusion

The deployment failures were caused by a misconfigured environment variable reference in vercel.json pointing to a non-existent secret. The issue was compounded by branch configuration misalignment. The resolution was straightforward once the root cause was identified, highlighting the importance of understanding Vercel's configuration hierarchy and proper secret management practices.

**Status**: RESOLVED ✅
**Risk of Recurrence**: LOW (with current fixes in place)

---
*Generated: August 11, 2025*
*Author: System Analysis*
*Review Status: Pending*
