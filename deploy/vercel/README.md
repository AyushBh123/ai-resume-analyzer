# Vercel Deployment Guide

Deploy the frontend to Vercel for fast, global CDN delivery.

## Prerequisites

- Vercel account (free tier available)
- Vercel CLI: `npm install -g vercel`

## Quick Deploy

### Option 1: Vercel CLI

1. **Login to Vercel**
```bash
vercel login
```

2. **Deploy from frontend directory**
```bash
cd frontend
vercel
```

3. **Follow prompts**
- Set up and deploy: Yes
- Which scope: Your account
- Link to existing project: No
- Project name: ai-resume-analyzer
- Directory: ./
- Override settings: No

4. **Set environment variables**
```bash
vercel env add VITE_API_BASE_URL production
# Enter your backend URL when prompted
```

5. **Deploy to production**
```bash
vercel --prod
```

### Option 2: GitHub Integration

1. **Go to vercel.com**
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - Framework Preset: Vite
   - Root Directory: frontend
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Add environment variables:
   - `VITE_API_BASE_URL`: Your backend URL
6. Click "Deploy"

## Configuration

### vercel.json

Create `frontend/vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

## Environment Variables

Set in Vercel Dashboard or CLI:

```bash
vercel env add VITE_API_BASE_URL
# Enter: https://your-backend-url.com

vercel env add VITE_DEBUG
# Enter: false
```

## Custom Domain

1. **Add domain in Vercel Dashboard**
   - Go to Project Settings → Domains
   - Add your domain

2. **Configure DNS**
   - Add CNAME record: `your-domain.com` → `cname.vercel-dns.com`
   - Or A record to Vercel's IP

3. **SSL Certificate**
   - Automatically provisioned by Vercel

## Features

- ✅ **Automatic HTTPS**: Free SSL certificates
- ✅ **Global CDN**: Fast delivery worldwide
- ✅ **Automatic deployments**: On git push
- ✅ **Preview deployments**: For pull requests
- ✅ **Analytics**: Built-in web analytics
- ✅ **Edge Functions**: Serverless at the edge

## Monitoring

- **Analytics**: Built-in web vitals tracking
- **Logs**: Real-time function logs
- **Deployments**: View all deployment history

## Cost

- **Hobby (Free)**: 
  - 100 GB bandwidth
  - Unlimited deployments
  - Perfect for personal projects

- **Pro ($20/month)**:
  - 1 TB bandwidth
  - Advanced analytics
  - Team collaboration

## Troubleshooting

### Build fails
```bash
# Check build locally
cd frontend
npm run build

# Check logs
vercel logs
```

### Environment variables not working
```bash
# List all env vars
vercel env ls

# Pull env vars locally
vercel env pull
```

### 404 errors on refresh
- Ensure rewrites are configured in vercel.json
- Check that all routes redirect to index.html

## Best Practices

1. **Use environment variables** for API URLs
2. **Enable preview deployments** for testing
3. **Set up custom domain** for production
4. **Monitor analytics** for performance
5. **Use edge functions** for API routes if needed

## Integration with Backend

Your frontend on Vercel can connect to:
- Backend on Heroku
- Backend on AWS
- Backend on any cloud provider

Just set `VITE_API_BASE_URL` to your backend URL.