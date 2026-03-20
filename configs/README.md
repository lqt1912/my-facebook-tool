# 📁 Configs Directory

**⚠️ WARNING: This directory contains sensitive information!**

## 🚫 What NOT to do:
- ❌ **DO NOT commit** this directory to Git
- ❌ **DO NOT share** files in this directory
- ❌ **DO NOT upload** to public repositories

## ✅ What to do:
- ✅ Add `configs/` to `.gitignore`
- ✅ Keep config files local only
- ✅ Use environment variables for production
- ✅ Encrypt sensitive data if needed

## 📋 Files in this directory:

### `facebook_config.json`
Contains:
- Facebook App ID
- Facebook App Secret  
- Access Tokens (short-lived, long-lived)
- Page Access Tokens
- User information

## 🔐 Security Best Practices:

### 1. Local Development:
```bash
# Create config file from template
cp configs/facebook_config.example.json configs/facebook_config.json
# Edit with your credentials
```

### 2. Production:
```bash
# Use environment variables
export FB_APP_ID="your_app_id"
export FB_APP_SECRET="your_app_secret"
export FB_ACCESS_TOKEN="your_token"
```

### 3. Team Collaboration:
```bash
# Share template only
git add configs/facebook_config.example.json
# Keep real config local
echo "configs/facebook_config.json" >> .gitignore
```

## 🎯 Template File:
Create `facebook_config.example.json` as a template:

```json
{
  "app_id": "YOUR_APP_ID_HERE",
  "app_secret": "YOUR_APP_SECRET_HERE",
  "short_lived_token": "SHORT_LIVED_TOKEN_HERE",
  "long_lived_token": "LONG_LIVED_TOKEN_HERE",
  "user_id": "USER_ID_HERE",
  "user_name": "USER_NAME_HERE",
  "pages": {}
}
```

## 🛡️ Backup Strategy:
1. **Local backup**: Keep in password manager
2. **Encrypted backup**: Use GPG or similar
3. **Access control**: Limit who can read these files

---

**Remember**: Tokens and secrets are like passwords. Protect them accordingly!