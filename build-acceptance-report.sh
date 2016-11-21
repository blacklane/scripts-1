#!/bin/bash
REPORT_PATH="report"

rm -R "$REPORT_PATH/current/"
rm -R "$REPORT_PATH/new/"

mkdir "$REPORT_PATH"
mkdir "$REPORT_PATH/current"
mkdir "$REPORT_PATH/new"

echo "Copy android instrumented tests results if exists"
if [ -e "android-test-log.txt" ]
then
  cp android-test-log.txt "$REPORT_PATH/android-test-log.txt"
fi

echo "Fetching build_acceptance_report.py"
curl https://raw.githubusercontent.com/orhanobut/scripts/master/buildreport/build_acceptance_report.py -o "$REPORT_PATH/build_acceptance_report.py"

echo "Building report"
python "$REPORT_PATH/build_acceptance_report.py" $REPORT_PATH