#!/usr/bin/bash
set -x

CODE_BUCKET=$1
SOURCE=$2
PREFIX=lambda_code

[ -f ${SOURCE}.zip ] && rm ${SOURCE}.zip
zip ${SOURCE}.zip $SOURCE
aws s3 cp $SOURCE.zip s3://${CODE_BUCKET}/${PREFIX}/${SOURCE}.zip

