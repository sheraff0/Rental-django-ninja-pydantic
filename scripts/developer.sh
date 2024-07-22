#! /bin/bash
python -m uvicorn developer.app:app --host 0.0.0.0 --port 8000 --reload
