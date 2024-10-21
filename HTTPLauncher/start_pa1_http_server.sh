#!/bin/bash

PORT=$1

DIR_GRADING=/projects/CSE489-GRADER
DIR_SUBMISSION=/local/CSE489-GRADER

UPLOAD_DIR=$DIR_SUBMISSION/upload
GRADING_DIR=$DIR_SUBMISSION/grading

PYTHON=/util/bin/python3.7

rm -rf $UPLOAD_DIR && mkdir $UPLOAD_DIR
rm -rf $GRADING_DIR && mkdir $GRADING_DIR

$PYTHON $DIR_GRADING/pa1_http_server/cse4589-pa1/HTTPLauncher/grader_launcher.py -p $PORT -u $UPLOAD_DIR -g $GRADING_DIR

#/local/CSE489-GRADER/upload
#/local/CSE489-GRADER/grading