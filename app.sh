#!/bin/bash

cd ~/learn-english-word

export FLASK_ENV=development
export FLASK_APP=memo
flask run --host=0.0.0.0
