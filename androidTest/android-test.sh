#!/usr/bin/env bash

PACKAGE_NAME=""
RUNNER=""
APP_ID=""

while (( "$#" )); do
  case "$1" in 
  "--package") 
     shift
     PACKAGE_NAME=$1
     ;;
  "--app-id")
     shift
     APP_ID=$1
     ;;
  "--runner")
     shift
     RUNNER=$1
     ;;
  esac
  shift
done

if [[ ( $PACKAGE_NAME == "" ) || ( $APP_ID == "" ) || ( $RUNNER == "") ]]
then
  echo "Required parameters are missing, --package, --app-id and --runner must be set"
  exit 1
fi

echo "Package name under test = $PACKAGE_NAME"
echo "App id under test = $APP_ID"
echo "Runner for tests = $RUNNER"

DEBUG_APK=app/build/outputs/apk/app-debug.apk
TEST_APK=app/build/outputs/apk/app-debug-androidTest.apk

if [ ! -e $DEBUG_APK ]
then
  echo "$DEBUG_APK not found, building again..."
  ./gradlew assembleDebug &> /dev/null
fi
echo "Installing debug apk..."
adb push $DEBUG_APK "/data/local/tmp/$APP_ID"
adb shell pm install -r "/data/local/tmp/$APP_ID"

if [ ! -e $TEST_APK ]
then
  echo "Building test apk..."
  ./gradlew assembleAndroidTest &> /dev/null
fi
echo "Installing test apk..."
adb push $TEST_APK "/data/local/tmp/$APP_ID.test"
adb shell pm install -r "/data/local/tmp/$APP_ID.test"

echo "Running tests..."
adb shell am instrument -w -e package "$PACKAGE_NAME" -e debug false "$APP_ID.test/$RUNNER" | tee android-test-log.txt

if grep "OK (" android-test-log.txt
then
  echo "FUNCTIONAL TESTS SUCCESS" | tee -a android-test-log.txt
else
  echo "FUNCTIONAL TESTS FAILED" | tee -a android-test-log.txt
fi
