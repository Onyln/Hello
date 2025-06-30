# Discord Bot Deployment Guide

## External Hosting Options

This bot is designed for external hosting. Here are the recommended platforms:

### 1. VPS/Cloud Servers (Recommended)

#### DigitalOcean Droplet
- **Cost**: $4-6/month
- **Specs**: 1GB RAM, 1 vCPU
- **Setup**: Ubuntu 20.04+
```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip ffmpeg git
git clone <your-bot-repo>
cd discord-bot
pip3 install -r requirements.txt
```

#### AWS EC2
- **Cost**: Free tier available
- **Instance**: t2.micro
- **OS**: Amazon Linux 2

#### Linode
- **Cost**: $5/month
- **Specs**: 1GB RAM
- **OS**: Ubuntu/Debian

### 2. Platform-as-a-Service

#### Heroku
```bash
# Create Procfile
echo "worker: python main.py" > Procfile

# Deploy
git init
git add .
git commit -m "Initial commit"
heroku create your-bot-name
heroku config:set DISCORD_TOKEN=your_token_here
git push heroku main
```

#### Railway
- Connect GitHub repository
- Set environment variable `DISCORD_TOKEN`
- Auto-deploys on git push

#### Render
- Connect repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `python main.py`

### 3. Container Deployment

#### Docker Setup
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install discord.py python-dotenv gtts aiohttp psutil

CMD ["python", "main.py"]
```

## Production Configuration

### Environment Variables
Set these on your hosting platform:
```
DISCORD_TOKEN=your_bot_token_here
BOT_PREFIX=!
```

### Process Management
For VPS deployments, use a process manager:

#### systemd (Linux)
Create `/etc/systemd/system/discord-bot.service`:
```ini
[Unit]
Description=Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/discord-bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5
Environment=PATH=/usr/bin:/usr/local/bin
EnvironmentFile=/home/ubuntu/discord-bot/.env

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
```

#### PM2 (Node.js Process Manager)
```bash
npm install -g pm2
pm2 start main.py --name discord-bot --interpreter python3
pm2 startup
pm2 save
```

### File Permissions
Ensure the bot can write to data directory:
```bash
chmod 755 data/
chmod 644 data/*.json
```

## Monitoring and Logging

### Log Configuration
The bot automatically logs to:
- Console output
- `bot.log` file

For production, consider log rotation:
```bash
# Install logrotate configuration
sudo nano /etc/logrotate.d/discord-bot
```

### Health Monitoring
Monitor bot uptime with:
- `!uptime` command
- `!botinfo` command
- Server monitoring tools (htop, PM2 status)

## Security Best Practices

### Token Security
- Never commit tokens to version control
- Use environment variables only
- Regenerate token if compromised
- Restrict bot permissions to minimum required

### Server Security
- Keep system updated: `sudo apt update && sudo apt upgrade`
- Use SSH keys instead of passwords
- Configure firewall: `sudo ufw enable`
- Regular backups of data directory

### Bot Permissions
Grant only necessary permissions:
- Remove admin if not needed for moderation
- Limit channel access where possible
- Regular permission audits

## Backup Strategy

### Data Backup
```bash
# Backup data directory
tar -czf bot-backup-$(date +%Y%m%d).tar.gz data/

# Automated daily backup
echo "0 2 * * * cd /path/to/bot && tar -czf backup-\$(date +\%Y\%m\%d).tar.gz data/" | crontab -
```

### Configuration Backup
- Save .env file securely
- Document server configuration
- Keep deployment scripts versioned

## Scaling Considerations

### Single Server Limits
- ~1000 concurrent users
- Multiple small/medium Discord servers
- Light to moderate usage

### Multi-Server Setup
For larger deployments:
- Database backend (PostgreSQL/MongoDB)
- Redis for caching
- Load balancer
- Separate voice processing servers

## Troubleshooting Deployment

### Common Issues
1. **Permission Denied**: Check file permissions and user privileges
2. **Module Not Found**: Verify all dependencies installed
3. **FFmpeg Missing**: Install system package
4. **Memory Issues**: Increase server RAM or optimize code

### Debugging Commands
```bash
# Check bot process
ps aux | grep python

# View logs
tail -f bot.log

# Check system resources
htop

# Test network connectivity
ping discord.com
```

### Performance Optimization
- Use SSD storage for faster I/O
- Enable gzip compression for logs
- Monitor memory usage patterns
- Regular data cleanup (old giveaways, logs)

## Cost Estimates

### Monthly Hosting Costs
- **VPS (1GB RAM)**: $4-6
- **Heroku Hobby**: $7
- **Railway**: $5-10
- **AWS t2.micro**: Free tier / $8.50

### Additional Costs
- Domain name (optional): $10-15/year
- SSL certificate: Usually free (Let's Encrypt)
- Monitoring services: $0-5/month

## Maintenance Schedule

### Daily
- Check bot status
- Monitor error logs
- Verify core functions

### Weekly
- Review performance metrics
- Check disk space
- Update dependencies if needed

### Monthly
- Security updates
- Backup verification
- Performance analysis
- Cost review

## Support and Updates

### Updating the Bot
```bash
# Pull latest changes
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Restart bot
systemctl restart discord-bot
```

### Version Control
- Use semantic versioning
- Tag releases
- Keep changelog updated
- Test updates in staging environment first