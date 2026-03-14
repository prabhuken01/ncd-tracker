# 🚀 Streamlit Cloud Deployment Guide

## Complete guide to deploy NCD Tracker on Streamlit Cloud

---

## 📋 Prerequisites

1. **GitHub Account** - Sign up at https://github.com
2. **Streamlit Cloud Account** - Sign up at https://share.streamlit.io
3. **Git installed** (optional, for command line) - Download from https://git-scm.com

---

## 🔧 Step 1: Prepare Your Repository

### Option A: Using GitHub Desktop (Recommended for Beginners)

1. **Download GitHub Desktop**: https://desktop.github.com
2. **Install and sign in** to your GitHub account
3. **Create new repository**:
   - Click "File" → "New Repository"
   - Repository name: `ncd-tracker`
   - Local path: `E:\Personal\Trading_Champion\Projects\Solutions_Execution\Code_Streamlit`
   - Click "Create Repository"
4. **Initial commit**:
   - All files will be shown in "Changes" tab
   - Summary: "Initial commit - NCD Tracker application"
   - Click "Commit to main"
5. **Publish to GitHub**:
   - Click "Publish repository"
   - Uncheck "Keep this code private" (or keep checked if you prefer)
   - Click "Publish repository"

### Option B: Using Command Line

```bash
# Navigate to project folder
cd E:\Personal\Trading_Champion\Projects\Solutions_Execution\Code_Streamlit

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - NCD Tracker application"

# Create GitHub repository (via GitHub website)
# Then link and push:
git remote add origin https://github.com/YOUR_USERNAME/ncd-tracker.git
git branch -M main
git push -u origin main
```

---

## ☁️ Step 2: Deploy on Streamlit Cloud

### 2.1 Connect to Streamlit Cloud

1. **Go to**: https://share.streamlit.io
2. **Sign in** with your GitHub account
3. **Authorize** Streamlit Cloud to access your repositories

### 2.2 Create New App

1. Click **"New app"** button
2. Fill in the deployment form:
   - **Repository**: Select `YOUR_USERNAME/ncd-tracker`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL like `ncd-tracker-yourname`

### 2.3 Advanced Settings (Optional)

Click **"Advanced settings"** if you need to:
- Set **Python version**: 3.11 (recommended)
- Add **secrets** (for API keys, credentials)
- Set **resource limits**

### 2.4 Deploy!

1. Click **"Deploy!"** button
2. Wait for deployment (usually 2-5 minutes)
3. Your app will be live at: `https://your-app-name.streamlit.app`

---

## 📊 Step 3: Configure Data Storage

### ⚠️ Important: Streamlit Cloud Storage Limitations

Streamlit Cloud uses **ephemeral storage** - files are reset on app restart. For production use, choose one of these options:

### Option 1: GitHub-Based Storage (Simple, but manual)

**Pros**: Free, simple
**Cons**: Manual updates, not real-time

1. Keep your Excel file in the repository
2. Users download, edit locally, and upload back
3. Commit changes to GitHub
4. App automatically redeploys

**Setup**:
```python
# In config.py (already configured)
DATA_FILE = BASE_DIR / "data" / "Bond_Primary_Deals.xlsx"
```

### Option 2: Google Drive Integration (Recommended)

**Pros**: Real-time sync, persistent
**Cons**: Requires Google API setup

1. **Create Google Cloud Project**:
   - Go to https://console.cloud.google.com
   - Create new project
   - Enable Google Drive API

2. **Create Service Account**:
   - Go to "IAM & Admin" → "Service Accounts"
   - Create service account
   - Download JSON credentials

3. **Add to Streamlit Secrets**:
   - In Streamlit Cloud, go to app settings
   - Click "Secrets"
   - Add:
   ```toml
   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account@project.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   ```

4. **Share Drive folder** with service account email

5. **Update code** to use Google Drive (see code below)

### Option 3: AWS S3 / Azure Blob Storage (Enterprise)

**Pros**: Scalable, reliable
**Cons**: Costs money, more complex

Follow AWS/Azure documentation for Python SDK integration.

---

## 🔐 Step 4: Add Secrets (Optional)

If you need to store sensitive data (API keys, passwords):

1. **In Streamlit Cloud**:
   - Go to your app
   - Click ⚙️ (Settings)
   - Click "Secrets"

2. **Add secrets** in TOML format:
   ```toml
   # Example secrets
   [database]
   host = "your-db-host"
   user = "your-user"
   password = "your-password"
   ```

3. **Access in code**:
   ```python
   import streamlit as st
   
   db_host = st.secrets["database"]["host"]
   ```

---

## 🔄 Step 5: Update Your App

### Automatic Deployment (Recommended)

Every time you push to GitHub, Streamlit Cloud **automatically redeploys**:

```bash
# Make changes to your code
# Then:
git add .
git commit -m "Update checklist items"
git push
```

Your app will redeploy automatically in 1-2 minutes!

### Manual Reboot

1. Go to your app on Streamlit Cloud
2. Click ⚙️ (Settings)
3. Click "Reboot app"

---

## 📱 Step 6: Share Your App

Your app is now live! Share the URL:

```
https://your-app-name.streamlit.app
```

### Custom Domain (Optional)

Streamlit Cloud allows custom domains on certain plans:
1. Go to app settings
2. Click "Custom domain"
3. Follow instructions to configure DNS

---

## 🐛 Troubleshooting

### App Won't Deploy

**Check**:
1. `requirements.txt` is present
2. All imports are listed in requirements.txt
3. `app.py` is in root directory
4. No syntax errors in code

**View logs**:
- Click "Manage app" → "Logs" to see error messages

### Data Not Persisting

**Solution**:
- Use Google Drive integration (see Option 2 above)
- Or commit Excel file to GitHub and download/upload

### Import Errors

**Fix**:
1. Check `requirements.txt` has all packages
2. Versions compatible with Python 3.11
3. Rebuild app in Streamlit Cloud

### Performance Issues

**Optimize**:
1. Use `@st.cache_data` for data loading
2. Minimize Excel file reads
3. Use session state efficiently

---

## 📊 Monitoring & Analytics

### Streamlit Cloud Dashboard

View app metrics:
- **Visits**: Number of users
- **Load time**: Performance
- **Errors**: Runtime errors

Access at: https://share.streamlit.io/YOUR_USERNAME/ncd-tracker

### Add Google Analytics (Optional)

Add to `app.py`:
```python
# In the <head> section of your HTML
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
""", unsafe_allow_html=True)
```

---

## 🔒 Security Best Practices

1. **Never commit secrets** to GitHub
   - Use `.gitignore` for sensitive files
   - Use Streamlit secrets for credentials

2. **Use environment variables**
   ```python
   import os
   SECRET_KEY = os.getenv('SECRET_KEY')
   ```

3. **Validate user inputs**
   - Already implemented in validators.py

4. **Use HTTPS**
   - Streamlit Cloud provides SSL automatically

---

## 💰 Pricing

### Streamlit Cloud Tiers

| Feature | Free | Team | Enterprise |
|---------|------|------|------------|
| Public apps | ✅ Unlimited | ✅ | ✅ |
| Private apps | ❌ | ✅ | ✅ |
| Resources | 1 GB RAM | 8 GB RAM | Custom |
| Support | Community | Email | Dedicated |
| Custom domain | ❌ | ✅ | ✅ |

**Free tier is sufficient** for most use cases!

---

## 🚀 Advanced: Google Drive Integration Code

Add to `requirements.txt`:
```
gspread==5.12.0
google-auth==2.23.0
```

Create `utils/google_drive.py`:
```python
import streamlit as st
from google.oauth2 import service_account
import gspread

def get_google_drive_client():
    """Initialize Google Drive client"""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    return gspread.authorize(credentials)

def load_from_drive(file_id):
    """Load data from Google Drive"""
    client = get_google_drive_client()
    # Implementation here
    pass
```

---

## 📞 Support

### Streamlit Documentation
- Docs: https://docs.streamlit.io
- Forum: https://discuss.streamlit.io
- GitHub: https://github.com/streamlit/streamlit

### App-Specific Issues
- Check app logs in Streamlit Cloud
- Review error messages
- Test locally first

---

## ✅ Deployment Checklist

- [ ] GitHub account created
- [ ] Repository created and pushed
- [ ] Streamlit Cloud account created
- [ ] App deployed successfully
- [ ] Data storage configured
- [ ] Secrets added (if needed)
- [ ] App URL shared with team
- [ ] Monitoring setup
- [ ] Backup strategy in place

---

## 🎉 You're Live!

Your NCD Tracker is now accessible worldwide at your Streamlit Cloud URL!

**Next steps**:
1. Share the URL with your team
2. Set up data backup
3. Monitor usage
4. Gather feedback for improvements

---

**Need help?** Refer to official Streamlit documentation or community forum!
