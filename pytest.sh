#!/bin/sh
pytest tests --cov-config=tests/.coveragerc --cov --cov-branch --cov-report term-missing | tee pytest-coverage.txt