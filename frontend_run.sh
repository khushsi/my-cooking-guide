#!/bin/bash
# Check if frontend is responsive
curl -s -I http://localhost:3000 | grep HTTP
