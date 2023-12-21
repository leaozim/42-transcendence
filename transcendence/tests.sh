#!/bin/bash
#cavalinho
coverage3 run --source='.' manage.py test && coverage3 report && coverage3 xml
docker run --rm --network=42-transcendence_sonarnet -e SONAR_HOST_URL="http://sonarqube:9000" -e SONAR_SCANNER_OPTS="-Dsonar.projectKey=transcendence -Dsonar.python.coverage.reportPaths=./coverage.xml" -e SONAR_TOKEN="sqp_270bf39358c1c28bc30df3f4758562643a67a6d1" -v ".:/usr/src" sonarsource/sonar-scanner-cli