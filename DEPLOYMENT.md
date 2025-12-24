# Firebase Deployment Guide

This guide will help you deploy your RAG Chatbot to Firebase Free Tier.

## Prerequisites

1. **Node.js and npm** installed (for Firebase CLI)
2. **Python 3.11** installed locally
3. **Firebase account** (free)
4. **Groq API key** ([Get it here](https://console.groq.com/))

## Step 1: Install Firebase CLI

```bash
npm install -g firebase-tools
```

## Step 2: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter project name (e.g., `rag-chatbot-free`)
4. Disable Google Analytics (optional for free tier)
5. Click "Create project"

## Step 3: Enable Firebase Services

### 3.1 Enable Authentication
1. In Firebase Console, go to **Authentication** > **Get Started**
2. Click on **Sign-in method** tab
3. Enable **Email/Password** provider
4. Click **Save**

### 3.2 Enable Firestore
1. Go to **Firestore Database** > **Create database**
2. Start in **test mode** (we'll deploy rules later)
3. Choose location closest to you
4. Click **Enable**

### 3.3 Enable Storage
1. Go to **Storage** > **Get Started**
2. Start in **test mode**
3. Use default location
4. Click **Done**

## Step 4: Configure Firebase Project

### 4.1 Login to Firebase CLI
```bash
firebase login
```

### 4.2 Initialize Firebase in your project
```bash
cd path/to/RAG-CHATBOT-using-DJANGO-framework
firebase init
```

Select:
- **Firestore**: Configure security rules and indexes
- **Functions**: Configure Cloud Functions
- **Hosting**: Configure hosting
- **Storage**: Configure storage rules

When prompted:
- Use existing project: Select your project from list
- Firestore rules file: Press Enter (use default `firestore.rules`)
- Firestore indexes file: Press Enter (use default `firestore.indexes.json`)
- Functions language: **Python**
- Functions source directory: `functions`
- Install dependencies: **No** (we'll do it manually)
- Hosting public directory: `public`
- Configure as single-page app: **No**
- Set up automatic builds: **No**
- Storage rules file: Press Enter (use default `storage.rules`)

### 4.3 Update .firebaserc with your project ID
Edit `.firebaserc` and replace `your-project-id` with your actual Firebase project ID.

## Step 5: Configure Environment Variables

### 5.1 Create .env.yaml for Cloud Functions
```bash
# Copy the example file
cp .env.yaml.example .env.yaml
```

### 5.2 Edit .env.yaml and add your Groq API key
```yaml
GROQ_API_KEY: "your-actual-groq-api-key"
LLM_MODEL: "llama-3.1-8b-instant"
EMBEDDING_MODEL: "paraphrase-MiniLM-L3-v2"
CHUNK_SIZE: "500"
CHUNK_OVERLAP: "50"
```

### 5.3 Get Firebase Web App Config
1. In Firebase Console, go to **Project Settings** (gear icon)
2. Scroll to **Your apps** section
3. Click **Web** icon (</>) to add a web app
4. Register app with nickname (e.g., "RAG Chatbot Web")
5. Copy the `firebaseConfig` object

### 5.4 Update public/firebase-config.js
Replace the placeholder values with your actual Firebase config:

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

## Step 6: Test Locally with Emulators

```bash
# Start Firebase emulators
firebase emulators:start
```

This will start:
- Hosting: http://localhost:5000
- Functions: http://localhost:5001
- Firestore: http://localhost:8080
- Auth: http://localhost:9099
- Storage: http://localhost:9199
- Emulator UI: http://localhost:4000

Test the application:
1. Open http://localhost:5000
2. Create a test account
3. Upload a small PDF
4. Send a chat message

**Note**: Emulator cold starts will be slow (~10-20 seconds) due to loading ML models. This is expected.

## Step 7: Deploy to Firebase

### 7.1 Deploy Firestore Rules and Indexes
```bash
firebase deploy --only firestore
```

### 7.2 Deploy Storage Rules
```bash
firebase deploy --only storage
```

### 7.3 Deploy Cloud Functions
```bash
# This will take 5-10 minutes (installing dependencies)
firebase deploy --only functions
```

### 7.4 Deploy Hosting
```bash
firebase deploy --only hosting
```

Or deploy everything at once:
```bash
firebase deploy
```

## Step 8: Post-Deployment Configuration

### 8.1 Update Firestore Security Rules (Optional but Recommended)
The default rules we deployed allow authenticated users to access only their own data. If you need to customize, edit `firestore.rules` and redeploy:
```bash
firebase deploy --only firestore:rules
```

### 8.2 Monitor Usage
1. Go to Firebase Console > **Usage and billing**
2. Monitor:
   - Cloud Functions invocations (125K/month free)
   - Firestore reads/writes (50K reads, 20K writes/day free)
   - Storage (5GB total free)
   - Hosting bandwidth (10GB/month free)

## Step 9: Access Your App

Your app will be available at:
```
https://YOUR-PROJECT-ID.web.app
```

Or the custom domain:
```
https://YOUR-PROJECT-ID.firebaseapp.com
```

## Troubleshooting

### Cold Start Timeout
**Problem**: Functions timeout on first request after idle period  
**Solution**: 
- The first request after 15+ minutes may take 15-20 seconds
- Subsequent requests will be faster (~2-5 seconds)
- Consider using a smaller embedding model in `.env.yaml`:  
  `EMBEDDING_MODEL: "all-MiniLM-L6-v2"` (even smaller, ~60MB)

### Memory Limit Exceeded
**Problem**: Functions crash with "memory limit exceeded"  
**Solution**:
- Current config uses 512MB (max for free tier)
- Reduce concurrent document uploads
- Use smaller embedding model (see above)
- For production, upgrade to Blaze plan and increase memory to 1GB

### Authentication Not Working
**Problem**: Can't sign up/sign in  
**Solution**:
- Verify Email/Password is enabled in Firebase Console > Authentication
- Check browser console for errors
- Verify `public/firebase-config.js` has correct credentials

### CORS Errors
**Problem**: API calls fail with CORS errors  
**Solution**:
- Already configured in `functions/main.py` with `cors=cross_origin()`
- If still occurring, check browser console for specific error

### Function Not Found
**Problem**: `/api/*` returns 404  
**Solution**:
- Verify functions deployed successfully: `firebase deploy --only functions`
- Check `firebase.json` has correct rewrite rules
- View function logs: `firebase functions:log`

### Firestore Permission Denied
**Problem**: Cannot read/write to Firestore  
**Solution**:
- Ensure user is authenticated
- Check `firestore.rules` allows user access
- Test rules in Firebase Console > Firestore > Rules > Rules Playground

## Free Tier Limits and Best Practices

### Limits
- **Cloud Functions**:
  - 125,000 invocations/month
  - 40,000 GB-seconds compute time/month
  - 40,000 CPU-seconds/month
  - 5GB network egress/month
  
- **Firestore**:
  - 50,000 reads/day
  - 20,000 writes/day
  - 20,000 deletes/day
  - 1 GiB storage
  
- **Storage**:
  - 5 GB storage
  - 1 GB/day download
  - 50,000 operations/day
  
- **Hosting**:
  - 10 GB storage
  - 360 MB/day bandwidth

### Best Practices to Stay Within Free Tier
1. **Limit document uploads**: Max 10-20 documents per user
2. **Cache chat history**: Store in client to reduce Firestore reads
3. **Batch operations**: Group Firestore writes when possible
4. **Monitor usage**: Set up budget alerts in Firebase Console
5. **Optimize vector data**: Compress ChromaDB archives before upload
6. **Limit concurrent users**: Free tier best for personal use or demos

## Updating Your Application

### Update Frontend
```bash
# Make changes to public/ files
firebase deploy --only hosting
```

### Update Backend
```bash
# Make changes to functions/ files
firebase deploy --only functions
```

### Update Environment Variables
```bash
# Edit .env.yaml, then redeploy functions
firebase deploy --only functions
```

## Logs and Debugging

### View Function Logs
```bash
firebase functions:log
```

### View Specific Function Logs
```bash
firebase functions:log --only api
```

### Real-time Logs
```bash
firebase functions:log --only api --follow
```

## Rolling Back

If deployment fails or causes issues:

```bash
# View deployment history
firebase hosting:releases:list

# Rollback to previous version
firebase hosting:rollback
```

For functions, redeploy the previous version by checking out the old code and deploying again.

## Cost Optimization Tips

1. **Use smaller embedding model**: `paraphrase-MiniLM-L3-v2` uses ~60MB less memory
2. **Limit document size**: Enforce max 5MB per file in frontend
3. **Clear old chat history**: Implement auto-deletion after 30 days
4. **Use CDN caching**: Enable for static assets in `firebase.json`
5. **Lazy load services**: Already implemented in `functions/main.py`

## Getting Help

- **Firebase Docs**: https://firebase.google.com/docs
- **Cloud Functions Python**: https://firebase.google.com/docs/functions/python
- **Firestore**: https://firebase.google.com/docs/firestore
- **Firebase Support**: https://firebase.google.com/support

## Security Checklist

- [ ] Environment variables in `.env.yaml` (NOT in git)
- [ ] Firebase config in `public/firebase-config.js` (gitignored)
- [ ] Firestore rules deployed and tested
- [ ] Storage rules deployed and tested
- [ ] Email/Password auth enabled
- [ ] File upload size limits enforced
- [ ] CORS configured correctly
- [ ] Monitoring and alerts set up

---

**Your RAG Chatbot is now deployed on Firebase Free Tier! 🎉**
