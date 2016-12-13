#!/bin/bash

PACKAGE_NAME=$1
REPORT_PATH="report"

rm -R "$REPORT_PATH/current/"
rm -R "$REPORT_PATH/new/"

mkdir "$REPORT_PATH"
mkdir "$REPORT_PATH/current"
mkdir "$REPORT_PATH/new"

echo "Copy checkstyle report"
cp app/build/reports/checkstyle/checkstyle.html "$REPORT_PATH/checkstyle.html"

echo "Copy lint report"
cp app/build/outputs/lint-results-debug.html "$REPORT_PATH/lint.html"

echo "Copy unit tests report"
cp app/build/reports/tests/debug/index.html "$REPORT_PATH/unittests.html"

echo "Copy android instrumented test results"
cp android-test-log.txt "$REPORT_PATH/android-test-log.txt"

echo "Fetching build_report.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/build_report.py -o "$REPORT_PATH/build_report.py"

echo "Fetching apk_info.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/apk_info.py -o "$REPORT_PATH/apk_info.py"

# copy new apk
echo "Copying new apk"
cp "app/build/outputs/apk/app-release.apk" "$REPORT_PATH/new/app.apk"
echo "Unzipping new apk"
unzip "$REPORT_PATH/new/app.apk" -d "$REPORT_PATH/new" > "$REPORT_PATH/new/log.txt"

# build apk from master and fetch apk info
git checkout master
echo "Building current apk"
./gradlew clean assembleRelease > "$REPORT_PATH/current/log.txt"
echo "Copying current apk"
cp "app/build/outputs/apk/app-release.apk" "$REPORT_PATH/current/app.apk"
echo "Unzipping current apk"
unzip "$REPORT_PATH/current/app.apk" -d "$REPORT_PATH/current" >> "$REPORT_PATH/current/log.txt"

echo "Building report"
python "$REPORT_PATH/build_report.py" $REPORT_PATH $PACKAGE_NAME
