---
description: Complete deployment workflow for Firebase
---

# Complete Firebase Deployment Workflow

Follow these steps to deploy your RAG Chatbot to Firebase Free Tier.

## Prerequisites

Before starting, ensure you have:
- [ ] Node.js and npm installed (for Firebase CLI)
- [ ] Python 3.11 installed locally
- [ ] A Firebase account (free) - sign up at https://console.firebase.google.com/
- [ ] A Groq API key - get it at https://console.groq.com/

## Step 1: Install Firebase CLI

```bash
npm install -g firebase-tools
```

Verify installation:
```bash
firebase --version
```

## Step 2: Login to Firebase

```bash
firebase login
```

This will open your browser for authentication. Sign in with your Google account.

## Step 3: Create Firebase Project

1. Open https://console.firebase.google.com/
2. Click **"Add project"**
3. Enter a project name (e.g., `rag-chatbot-free`)
4. (Optional) Disable Google Analytics for simplicity
5. Click **"Create project"**
6. Wait for project creation (10-30 seconds)
7. **Copy your Project ID** - you'll need this later!

## Step 4: Enable Firebase Services

### 4.1 Enable Authentication
1. In Firebase Console, navigate to **Authentication** → **Get Started**
2. Click on the **Sign-in method** tab
3. Find **Email/Password** in the list
4. Click **Email/Password** → toggle **Enable** → **Save**

### 4.2 Enable Firestore Database
1. Navigate to **Firestore Database** → **Create database**
2. Select **Start in test mode** (security rules will be deployed later)
3. Choose a location closest to your users
4. Click **Enable**
5. Wait for database to initialize

### 4.3 Enable Firebase Storage
1. Navigate to **Storage** → **Get Started**
2. Select **Start in test mode**
3. Use the default location
4. Click **Done**

## Step 5: Get Firebase Web App Configuration

1. In Firebase Console, click the **Settings gear icon** → **Project settings**
2. Scroll down to **Your apps** section
3. Click the **Web icon** (`</>`) to add a web app
4. Enter an app nickname (e.g., "RAG Chatbot Web")
5. **Do not** check "Also set up Firebase Hosting" (we'll do this later)
6. Click **Register app**
7. **Copy the entire `firebaseConfig` object** - you'll need this in Step 7

It should look like:
```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123:web:abc..."
};
```

## Step 6: Configure Project Files

### 6.1 Update `.firebaserc`

Open `.firebaserc` and replace `your-project-id` with your actual Firebase Project ID from Step 3:

```json
{
  "projects": {
    "default": "your-actual-project-id"
  }
}
```

### 6.2 Create `.env.yaml`

```bash
cp .env.yaml.example .env.yaml
```

Then edit `.env.yaml` and add your Groq API key:
```yaml
GROQ_API_KEY: "your-actual-groq-api-key-here"
LLM_MODEL: "llama-3.1-8b-instant"
EMBEDDING_MODEL: "paraphrase-MiniLM-L3-v2"
CHUNK_SIZE: "500"
CHUNK_OVERLAP: "50"
```

**Note**: Never commit `.env.yaml` to git! It's already in `.gitignore`.

### 6.3 Update `public/firebase-config.js`

Open `public/firebase-config.js` and replace the placeholder values with the `firebaseConfig` you copied in Step 5:

```javascript
// Replace with your Firebase configuration from Step 5
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123:web:abc..."
};
```

**Note**: This file is gitignored for security.

## Step 7: Test Locally with Firebase Emulators (Optional but Recommended)

```bash
firebase emulators:start
```

This will start local emulators:
- **Hosting**: http://localhost:5000 (your app UI)
- **Functions**: http://localhost:5001 (API endpoints)
- **Firestore**: http://localhost:8080
- **Auth**: http://localhost:9099
- **Storage**: http://localhost:9199
- **Emulator UI**: http://localhost:4000 (view all services)

**Test your app:**
1. Open http://localhost:5000 in your browser
2. Click "Sign Up" and create a test account
3. Upload a small PDF document (test with 1-2 pages)
4. Send a chat message about the document
5. Verify you get a response

**Expected behavior:**
- First request after emulator start: 10-20 seconds (loading ML models)
- Subsequent requests: 2-5 seconds

Press `Ctrl+C` when done testing.

## Step 8: Deploy to Firebase Production

### 8.1 Deploy Firestore Rules and Indexes
```bash
firebase deploy --only firestore
```

Expected output: "✔ Deploy complete!"

### 8.2 Deploy Storage Rules
```bash
firebase deploy --only storage
```

Expected output: "✔ Deploy complete!"

### 8.3 Deploy Cloud Functions
```bash
firebase deploy --only functions
```

**Note**: This will take 5-10 minutes on first deployment (installing Python dependencies).

If prompted about deleting functions, type `N` (No).

Expected output: 
```
✔ functions[api(us-central1)] Successful create operation.
Function URL: https://us-central1-YOUR-PROJECT-ID.cloudfunctions.net/api
```

### 8.4 Deploy Hosting (Frontend)
```bash
firebase deploy --only hosting
```

Expected output: 
```
✔ hosting[your-project-id]: successfully uploaded X files
✔ Deploy complete!

Hosting URL: https://YOUR-PROJECT-ID.web.app
```

### Alternative: Deploy Everything at Once
```bash
firebase deploy
```

This deploys firestore, storage, functions, and hosting in one command.

## Step 9: Verify Deployment

### 9.1 Check Deployment Status
```bash
firebase deploy:status
```

### 9.2 Access Your Live App

Open your browser and navigate to:
```
https://YOUR-PROJECT-ID.web.app
```

Or:
```
https://YOUR-PROJECT-ID.firebaseapp.com
```

### 9.3 Test the Live App

1. **Sign Up**: Create a new account with email/password
2. **Upload Document**: Upload a small PDF (1-2 pages recommended for first test)
3. **Chat**: Ask a question about your document
4. **Verify Response**: Should get a response in 10-30 seconds (first request is slower)

**Note**: The first API call after deployment or 15+ minutes of inactivity will be slow (10-30 seconds) due to cold start and ML model loading. This is expected on the free tier.

## Step 10: Monitor Your Application

### 10.1 View Function Logs
```bash
firebase functions:log
```

For real-time logs:
```bash
firebase functions:log --follow
```

### 10.2 Monitor Usage in Firebase Console

1. Open Firebase Console → **Usage and billing**
2. Monitor these metrics:
   - **Cloud Functions**: 125K invocations/month (free tier limit)
   - **Firestore**: 50K reads, 20K writes per day (free tier limit)
   - **Storage**: 5GB total (free tier limit)
   - **Hosting**: 10GB bandwidth/month (free tier limit)

**Recommendation**: Set up budget alerts even for free tier to avoid surprises!

## Troubleshooting Common Issues

### Issue 1: Functions Timeout
**Symptom**: "Function timeout" or "DEADLINE_EXCEEDED"
**Solution**: 
- First request after 15+ minutes idle will be slow (10-30 seconds)
- This is normal for free tier with ML models
- Subsequent requests will be faster (2-5 seconds)

### Issue 2: Memory Limit Exceeded
**Symptom**: "Function crashed" or "Memory limit exceeded"
**Solution**:
- Reduce document size (max 5MB recommended)
- Use smaller embedding model: Change `EMBEDDING_MODEL: "all-MiniLM-L6-v2"` in `.env.yaml`
- Redeploy functions: `firebase deploy --only functions`

### Issue 3: Authentication Not Working
**Symptom**: Can't sign up or sign in
**Solution**:
- Verify Email/Password is enabled in Firebase Console → Authentication
- Check browser console (F12) for errors
- Verify `public/firebase-config.js` has correct credentials
- Clear browser cache and try again

### Issue 4: CORS Errors
**Symptom**: API calls fail with CORS errors in browser console
**Solution**:
- Already configured in `functions/main.py`
- If still occurring, check Firebase Console → Functions → Logs for details
- Try hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### Issue 5: "Permission Denied" in Firestore
**Symptom**: Cannot read/write to database
**Solution**:
- Ensure you're logged in (check if token is present)
- Verify `firestore.rules` was deployed: `firebase deploy --only firestore`
- Test rules in Firebase Console → Firestore → Rules → Rules Playground

## Updating Your Application

### Update Frontend Only
```bash
# 1. Make changes to files in public/
# 2. Deploy
firebase deploy --only hosting
```

### Update Backend Only
```bash
# 1. Make changes to files in functions/
# 2. Deploy
firebase deploy --only functions
```

### Update Environment Variables
```bash
# 1. Edit .env.yaml with new values
# 2. Redeploy functions (env vars are bundled with functions)
firebase deploy --only functions
```

### Update Database Rules
```bash
# 1. Edit firestore.rules or storage.rules
# 2. Deploy
firebase deploy --only firestore:rules
# or
firebase deploy --only storage:rules
```

## Rollback Deployment

If something goes wrong:

```bash
# View deployment history
firebase hosting:releases:list

# Rollback hosting to previous version
firebase hosting:rollback
```

For functions, you need to redeploy the previous code version.

## Performance Optimization Tips

1. **Use Smaller Embedding Model**: 
   - Current: `paraphrase-MiniLM-L3-v2` (~66MB)
   - Alternative: `all-MiniLM-L6-v2` (~60MB, slightly faster)

2. **Limit Document Size**: 
   - Enforce max 5MB per file
   - Recommend users upload only relevant pages

3. **Clear Old Data**: 
   - Implement auto-deletion of chat history after 30 days
   - Delete unused documents

4. **Reduce API Calls**:
   - Cache chat history in browser localStorage
   - Batch Firestore operations when possible

## Security Checklist

Before sharing your app publicly, verify:

- [ ] `.env.yaml` is NOT committed to git (check `.gitignore`)
- [ ] `public/firebase-config.js` is NOT committed to git
- [ ] Firestore rules are deployed and tested
- [ ] Storage rules are deployed and tested
- [ ] Email/Password authentication is enabled
- [ ] File upload size limits are enforced in frontend
- [ ] Monitoring and usage alerts are set up
- [ ] You've tested signup, upload, and chat flows

## Next Steps

1. **Share Your App**: Send the URL to users: `https://YOUR-PROJECT-ID.web.app`
2. **Monitor Usage**: Check Firebase Console daily for the first week
3. **Collect Feedback**: Test with real users and iterate
4. **Optimize**: Based on usage patterns, adjust settings and limits

## Getting Help

- **Detailed Troubleshooting**: See [DEPLOYMENT.md](../DEPLOYMENT.md)
- **Quick Reference**: See [QUICKSTART.md](../QUICKSTART.md)
- **Firebase Documentation**: https://firebase.google.com/docs
- **Cloud Functions Python**: https://firebase.google.com/docs/functions/python
- **Firestore**: https://firebase.google.com/docs/firestore

---

**🎉 Congratulations! Your RAG Chatbot is now live on Firebase!**

Your app is now accessible at: `https://YOUR-PROJECT-ID.web.app`
