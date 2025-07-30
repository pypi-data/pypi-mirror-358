#!/bin/bash

set -e

rm -rf dist/*
uv build
uv publish