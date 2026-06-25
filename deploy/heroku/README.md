# Heroku Deployment Guide

Deploy AI Resume Analyzer to Heroku quickly and easily.

## Prerequisites

- Heroku CLI installed: `brew install heroku/brew/heroku` (Mac) or download from heroku.com
- Heroku account created

## Quick Deploy

### Backend Deployment

1. **Login to Heroku**
```bash
heroku login
```

2. **Create Heroku app**
```bash
heroku create ai-resume-analyzer-backend
```

3. **Add buildpack**
```bash
heroku buildpacks:set heroku/python
```

4. **Set environment variables**
```bash
heroku config:set OPENAI_API_KEY=your-key-here
heroku config:set ANTHROPIC_API_KEY=your-key-here
heroku config:set ENVIRONMENT=production
heroku config:set LOG_LEVEL=INFO
```

5. **Create Procfile** (already included)
```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

6. **Deploy**
```bash
git push heroku main
```

7. **Open app**
```bash
heroku open
```

### Frontend Deployment

1. **Create frontend app**
```bash
heroku create ai-resume-analyzer-frontend
```

2. **Add Node.js buildpack**
```bash
heroku buildpacks:set heroku/nodejs
```

3. **Set environment variables**
```bash
heroku config:set VITE_API_BASE_URL=https://ai-resume-analyzer-backend.herokuapp.com
```

4. **Add static buildpack for serving**
```bash
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-static.git
```

5. **Create static.json**
```json
{
  "root": "dist",
  "clean_urls": true,
  "routes": {
    "/**": "index.html"
  }
}
```

6. **Deploy**
```bash
git subtree push --prefix frontend heroku main
```

## Using Heroku Postgres (Optional)

If you want to add database for storing analysis history:

```bash
heroku addons:create heroku-postgresql:mini
```

## Monitoring

- **View logs**: `heroku logs --tail`
- **View metrics**: `heroku metrics`
- **Scale dynos**: `heroku ps:scale web=2`

## Cost

- **Free tier**: 550-1000 dyno hours/month
- **Hobby tier**: $7/month per dyno
- **Professional**: $25-500/month

## Automatic Deployment

Connect to GitHub for automatic deployments:

1. Go to Heroku Dashboard
2. Select your app
3. Go to "Deploy" tab
4. Connect to GitHub repository
5. Enable automatic deploys from main branch

## Environment Variables

Required variables:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ENVIRONMENT=production
LOG_LEVEL=INFO
```

Optional variables:
```bash
OLLAMA_BASE_URL=http://your-ollama-server:11434
MAX_UPLOAD_SIZE=10485760
```

## Troubleshooting

### App crashes on startup
```bash
heroku logs --tail
heroku restart
```

### Out of memory
```bash
heroku ps:resize web=standard-2x
```

### Slow response times
```bash
heroku ps:scale web=2
```

## Custom Domain

1. **Add domain**
```bash
heroku domains:add www.your-domain.com
```

2. **Configure DNS**
- Add CNAME record pointing to Heroku DNS target

3. **Add SSL**
```bash
heroku certs:auto:enable