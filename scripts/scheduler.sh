#! /bin/bash
python -m uvicorn contrib.scheduler.app:app --host 0.0.0.0 --port 8000 --reload
