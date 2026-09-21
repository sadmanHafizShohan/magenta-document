# Magenta Document Web App

PDF, PNG, JPG, and JPEG files into Magenta (`#FF00FF`) and White from a browser.

## Run locally

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser. To use it from another device on the same Wi-Fi, find this computer's local IP address and open:

```text
http://YOUR-COMPUTER-IP:5000
```

The app listens on all network interfaces. Windows Firewall may ask you to allow Python on private networks.

## Deploy online

This project includes `Procfile` for services such as Render, Railway, or Fly.io.

1. Push the project to GitHub.
2. Create a new Web Service from the repository.
3. Use the build command `pip install -r requirements.txt`.
4. Use the start command `gunicorn app:app`.
5. Deploy and open the service URL from any device.

Uploaded files are processed in temporary server storage and removed after the response. The upload limit is 200 MB per request.

## Features

- PDF, PNG, JPG, and JPEG input
- Multiple files in one upload
- ZIP download for multiple converted files
- Brightness threshold, outline mode, border thickness, and DPI controls
- Same conversion logic as the desktop script
