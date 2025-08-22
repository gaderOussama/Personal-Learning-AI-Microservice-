Thank you for contributing!

Steps to get the project running locally:

1. Create and activate a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies
```powershell
pip install -r requirements.txt
```

3. Configure credentials
- Place your Google OAuth client JSON at `credentials.json` or set `GOOGLE_CREDENTIALS_JSON_PATH` in environment variables.
- Set any API keys in a `.env` file or environment variables.

4. Run the service
```powershell
# Start the FastAPI app
uvicorn main:app --reload
```

Pull requests
- Fork the repo, create a branch, and open a PR. Keep changes focused and include tests for new functionality when possible.
