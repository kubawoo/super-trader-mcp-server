#!/bin/bash -e

uv sync --upgrade
uv lock
uv audit --preview-features audit
