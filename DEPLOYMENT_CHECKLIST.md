# Quick Deployment Checklist

## Pre-Deployment

- [ ] Test application locally
- [ ] Build frontend: `cd frontend && npm run build`
- [ ] Test production build locally
- [ ] Ensure `.gitignore` is correct
- [ ] Update `README.md` with deployment info

## Git Setup

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/market-monitor.git
git push -u origin main
```

## Render.com Setup

### 1. Create Service
- Go to https://dashboard.render.com
- New + → Web Service
- Connect GitHub repo

### 2. Configure
- **Build Command**: `./build.sh`
- **Start Command**: `uvicorn api.app:app --host 0.0.0.0 --port $PORT`
- **Python Version**: 3.10

### 3. Add Disk
- Name: `market-monitor-data`
- Mount: `/opt/render/project/src/data`
- Size: 1GB

### 4. Environment Variables (Optional)
- `EMAIL_SENDER`
- `EMAIL_PASSWORD`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### 5. Deploy
- Click "Create Web Service"
- Wait 5-10 minutes

## Post-Deployment

- [ ] Test frontend at your Render URL
- [ ] Test API at `/docs`
- [ ] Create a test task
- [ ] Create a test reminder
- [ ] Check market data
- [ ] Verify scheduler is running

## Your URL
```
https://[your-service-name].onrender.com
```

## Need Help?
See `DEPLOY_RENDER.md` for full documentation
