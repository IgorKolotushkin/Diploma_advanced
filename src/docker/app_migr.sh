#!/bin/bash

cd app

alembic upgrade head

uvicorn src.main:app_api --host 0.0.0.0