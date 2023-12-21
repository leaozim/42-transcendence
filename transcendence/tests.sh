#!/bin/bash
#cavalinho
coverage3 run --source='.' manage.py test && coverage3 report && coverage3 xml
