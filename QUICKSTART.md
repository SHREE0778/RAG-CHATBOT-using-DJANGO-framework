# Quick Start - Firebase Deployment

## 🚀 5-Minute Setup

### 1. Install Firebase CLI
```bash
npm install -g firebase-tools
```

### 2. Login to Firebase
```bash
firebase login
```

### 3. Create Firebase Project
- Visit https://console.firebase.google.com/
- Create new project
- Enable Authentication (Email/Password)
- Enable Firestore Database
- Enable Storage

### 4. Configure Project

```bash
# Update .firebaserc with your project ID
# Edit public/firebase-config.js with your Firebase config
# Copy .env.yaml.example to .env.yaml and add your GROQ_API_KEY
```

### 5. Deploy

```bash
# Deploy everything
firebase deploy
```

### 6. Access Your App
```
https://YOUR-PROJECT-ID.web.app
```

## 📖 Full Documentation

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete instructions.

## ⚠️ Important Files to Configure

Before deploying, you MUST update these files:

1. **`.firebaserc`** - Add your Firebase project ID
2. **`public/firebase-config.js`** - Add your Firebase web app config  
3. **`.env.yaml`** - Add your Groq API key (copy from `.env.yaml.example`)

## 🧪 Test Locally First

```bash
firebase emulators:start
```

Visit http://localhost:5000 to test locally.

## 📊 Project Structure

```
.
├── functions/              # Cloud Functions (Python)
│   ├── main.py            # Main API endpoints
│   ├── services/          # Backend services
│   └── requirements.txt   # Python dependencies
├── public/                # Frontend (Firebase Hosting)
│   ├── index.html         # Main app
│   ├── css/style.css      # Styles
│   ├── js/app.js          # App logic
│   └── firebase-config.js # Firebase config (gitignored)
├── firebase.json          # Firebase configuration
├── firestore.rules        # Firestore security rules
├── storage.rules          # Storage security rules
└── .env.yaml              # Environment variables (gitignored)
```

## 🆓 Free Tier Limits

- **Functions**: 125K invocations/month
- **Firestore**: 50K reads, 20K writes/day
- **Storage**: 5GB total
- **Hosting**: 10GB bandwidth/month

Perfect for personal use, demos, and small projects!

## ❓ Need Help?

See [DEPLOYMENT.md](./DEPLOYMENT.md) for troubleshooting and detailed instructions.
