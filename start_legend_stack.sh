#!/bin/bash
echo "🧠 [GLYTCH] Starting Full CloudConnect Stack..."

# === Activate Backend Environment ===
cd ~/legend_stack || exit 1
echo "🔁 Activating Python venv..."
source venv/bin/activate || python3 -m venv venv && source venv/bin/activate
echo "📦 Installing backend requirements..."
pip install -r requirements.txt

# === Start FastAPI Backend ===
echo "🚀 Launching FastAPI API..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# === Start PostgreSQL Docker Container ===
echo "🐘 Launching PostgreSQL with Docker..."
if command -v docker &> /dev/null; then
  docker start legend-postgres || docker run --name legend-postgres -e POSTGRES_PASSWORD=legendadmin -p 5432:5432 -d postgres
else
  echo "⚠️  Docker not found. PostgreSQL container not started."
fi

# === Start Stable Diffusion WebUI ===
echo "🎨 Launching Stable Diffusion WebUI..."
cd ~/stable-diffusion-webui && nohup ./webui.sh --listen > ~/frontend.log 2>&1 &

# === Start Open WebUI ===
echo "🧠 Launching Open WebUI..."
cd ~/open-webui && docker compose up -d || echo "⚠️  Docker not available for Open WebUI."

# === Start Cloudflare Tunnel ===
echo "🌐 Launching Cloudflare Tunnel..."
if [ -f ~/.cloudflared/cert.pem ]; then
  nohup cloudflared tunnel run legend-tunnel > ~/cloudflare.log 2>&1 &
  echo "🌐 Tunnel started. Logs: ~/cloudflare.log"
else
  echo "❌ Cloudflare cert.pem missing. Run 'cloudflared tunnel login' first."
fi

echo "✅ All systems launched. API: http://localhost:8000 or https://api.legendaryleads.online"
