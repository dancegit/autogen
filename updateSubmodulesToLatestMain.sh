#!/bin/bash
git submodule foreach --recursive 'git checkout main && git pull origin main && git submodule update --init --merge'
