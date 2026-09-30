# Troubleshooting & Operational FAQ

Common diagnostic steps and solutions for operating ETHIO-CYBERGUARD.

---

## 1. Backend API Issues

### `Port 8000 already in use`
- **Cause**: Another process or background server is bound to port 8000.
- **Solution**:
  ```bash
  # Find and kill process on port 8000 (Linux/macOS):
  lsof -i :8000 | awk 'NR>1 {print $2}' | xargs kill -9

  # On Windows PowerShell:
  Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
  ```

### `ModuleNotFoundError: No module named 'services'`
- **Cause**: Project root directory is not in `PYTHONPATH`.
- **Solution**: Run uvicorn from the project root:
  ```bash
  python -m uvicorn apps.api.main:app --reload
  ```

---

## 2. Frontend Web Console Issues

### `Vite build fails: TypeScript error`
- **Solution**: Ensure dependencies are installed and run build check:
  ```bash
  cd apps/web
  npm install
  npm run build
  ```

### WebSocket connection fails to establish
- Check that the backend server is running on `http://localhost:8000`.
- Verify CORS allowed origins in `.env` includes your frontend port (e.g. `http://localhost:5173`).

---

## 3. Threat Intelligence Feed Sync

### `Indicator lookup returns UNKNOWN`
- This is expected for clean or unobserved observables.
- To add a custom IOC manually, use `db.add_indicator(...)` or submit it via the SOC Console.
