# Deploying to Render.com

This guide will help you deploy the Market Monitor & Productivity System to Render.com.

## Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render.com Account** - Sign up at https://dashboard.render.com

## Step-by-Step Deployment Guide

### 1. Prepare Your Repository

First, initialize git and push to GitHub if you haven't already:

```bash
cd /Users/vijaysambireddy/Documents/playground/MyApp

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Market Monitor System"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/market-monitor.git
git branch -M main
git push -u origin main
```

### 2. Create Render Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the `market-monitor` repository

### 3. Configure Service Settings

**Basic Settings:**
- **Name**: `market-monitor` (or your preferred name)
- **Region**: Choose closest to you (Oregon for US West)
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `./build.sh`
- **Start Command**: `uvicorn api.app:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **Free** (or paid if you need more resources)

### 4. Add Environment Variables

Click **"Advanced"** and add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.10.0` | Python version |
| `DATABASE_URL` | `sqlite:///data/productivity.db` | Database path |

**Optional (for email/Telegram notifications):**
| Key | Value |
|-----|-------|
| `EMAIL_SENDER` | your-email@gmail.com |
| `EMAIL_PASSWORD` | your-app-password |
| `TELEGRAM_BOT_TOKEN` | your-bot-token |
| `TELEGRAM_CHAT_ID` | your-chat-id |

### 5. Add Persistent Disk (Important!)

Since we're using SQLite, you need persistent storage:

1. In the service settings, scroll to **"Disk"**
2. Click **"Add Disk"**
3. Configure:
   - **Name**: `market-monitor-data`
   - **Mount Path**: `/opt/render/project/src/data`
   - **Size**: `1 GB` (free tier)

### 6. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Run `build.sh` (install dependencies, build frontend)
   - Start the service with uvicorn
3. Wait for deployment to complete (5-10 minutes first time)

### 7. Access Your Application

Once deployed, Render will provide a URL like:
```
https://market-monitor-xyz.onrender.com
```

- **Frontend**: https://your-app.onrender.com
- **API Docs**: https://your-app.onrender.com/docs
- **API Health**: https://your-app.onrender.com/api/system/status

## Important Notes

### Free Tier Limitations

- **Spin Down**: Free services spin down after 15 minutes of inactivity
  - First request after spin down takes 30-60 seconds
  - Set up a cron job to ping your app to keep it awake (optional)

- **Build Minutes**: 750 hours/month build time on free tier

### Database Persistence

- The persistent disk ensures your SQLite database survives deployments
- **Backup regularly** - Download database from Render dashboard or via shell

### Scheduled Jobs

The scheduler runs automatically when the service starts. It will:
- Send market summaries at 7:00 AM IST
- Check reminders every minute
- Monitor market during trading hours

### Monitoring

**View Logs:**
1. Go to your service dashboard
2. Click **"Logs"** tab
3. See real-time application logs

**Shell Access:**
1. Click **"Shell"** tab
2. Access your running container
3. Run commands like:
   ```bash
   python main.py status
   python -m todos.cli list
   ```

## Troubleshooting

### Build Fails

**Issue**: `npm: command not found`
- **Solution**: Render auto-installs Node.js for Python services

**Issue**: Permission denied on build.sh
- **Solution**: Run `chmod +x build.sh` locally and commit

### App Won't Start

**Issue**: Port binding error
- **Solution**: Ensure you're using `$PORT` environment variable

**Issue**: Database locked
- **Solution**: Check disk is properly mounted

### Data Not Persisting

**Issue**: Tasks/reminders disappear after restart
- **Solution**: Verify persistent disk is mounted at `/opt/render/project/src/data`

## Updating Your Deployment

When you make changes:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render automatically redeploys when you push to GitHub!

## Alternative: Manual Deploy

If you don't want to use GitHub:

1. Go to **"New"** → **"Web Service"**
2. Choose **"Public Git repository"**
3. Enter your repo URL
4. Follow same configuration steps

## Cost Optimization

**Free Tier Strategy:**
- Use free tier for development/testing
- Upgrade to paid tier ($7/month) for:
  - No spin down
  - More resources
  - Better performance

**Keep Free Tier Active:**
Use a service like UptimeRobot to ping your app every 14 minutes:
```
https://your-app.onrender.com/
```

## Next Steps

After deployment:
1. ✅ Test all features (tasks, reminders, market data)
2. ✅ Set up email/Telegram notifications (optional)
3. ✅ Configure custom domain (optional, paid feature)
4. ✅ Set up monitoring/alerts
5. ✅ Create database backup schedule

## Support

- **Render Docs**: https://render.com/docs
- **Community**: https://community.render.com
- **Status**: https://status.render.com

---

Your Market Monitor system is now live and accessible from anywhere! 🎉
