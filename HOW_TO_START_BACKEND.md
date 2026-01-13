# How to Start the Backend API

## Quick Method (Recommended)

1. Open **File Explorer**
2. Navigate to: `C:\Users\USER\OneDrive\LinkedIn_PersonalBrand\Post_Factory`
3. **Double-click** `start_api.bat`
4. A terminal window will open showing the API starting
5. Wait until you see: `Uvicorn running on http://0.0.0.0:8000`
6. **Keep that window open** - the API is now running!

## Alternative: PowerShell Method

If the batch file doesn't work, open PowerShell and run:

```powershell
cd "C:\Users\USER\OneDrive\LinkedIn_PersonalBrand\Post_Factory"

# Install missing packages (one-time only)
pip install anthropic

# Start the API
python -m uvicorn api.main:app --reload --port 8000
```

## Verify It's Working

Once the API starts, you'll see:
```
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO: Started reloader process
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
```

Then visit: **http://localhost:8000/docs** in your browser to see the interactive API documentation.

## Testing from the Frontend

1. Make sure the **backend is running** (see above)
2. Open your **frontend** at: http://localhost:3000
3. Go to the **Generate** tab
4. Select a Content Pillar and Format  
5. Click **"Generate Post"**
6. You should see a new post appear!

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'anthropic'"

**Solution**: Install the package
```powershell
pip install anthropic
```

### Issue: "Port 8000 is already in use"

**Solution**: Another process is using port 8000
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill that process (use the PID from above command)
taskkill /PID <PID> /F
```

### Issue: API starts but crashes immediately

**Solution**: Check if you have API keys configured

The backend needs these environment variables (check `Post_Factory/.env` if it exists):
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`

## What's Running?

When both are running, you'll have:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Next.js UI |
| **Backend API** | http://localhost:8000 | FastAPI server |
| **API Docs** | http://localhost:8000/docs | Interactive documentation |

## Stopping the Services

- **Frontend**: Press `Ctrl+C` in the terminal running npm
- **Backend**: Press `Ctrl+C` in the terminal/window running the API

---

💡 **Pro Tip**: Open two terminal windows side-by-side - one for frontend, one for backend!
