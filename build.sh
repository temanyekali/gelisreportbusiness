#!/bin/bash
  cd frontend
  yarn install --frozen-lockfile
  yarn build
  cp -r build/* ../public/
  2. Make executable:
  chmod +x build.sh
  3. Di Coolify set:
  Build Command: ./build.sh
  Start Command: nginx -g 'daemon off;'
