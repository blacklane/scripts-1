#!/usr/bin/env bash

EMULATOR_PORT=$1
EMULATOR_ID="emulator-$EMULATOR_PORT"
EMULATOR_AVD=$2

start_time=`date +%s`
printf "Launching $EMULATOR_ID..\n"

adb start-server
printf "adb server started"
emulator @${EMULATOR_AVD} -port ${EMULATOR_PORT} &> .emulator_log.txt &
printf "Waiting for device"
adb -s ${EMULATOR_ID} wait-for-device

printf "adb connected. waiting for bootanim.."

A=$(adb -s ${EMULATOR_ID} shell getprop init.svc.bootanim | tr -d '\r')

SECONDS=0
RESTART_COUNT=0
while [ "$A" != "stopped" ]; do
  if [ $SECONDS -gt 120 ]; then
    if [ ${RESTART_COUNT} -eq 1 ] ; then
      printf "\nwipe-data also didn't work, I give up..\n"
      exit 1
    fi
    printf "\nbootanim taking too long, attempting to restart with wipe-data\n"
    SECONDS=0
    RESTART_COUNT=1
    adb -s ${EMULATOR_ID} emu kill || true
    emulator @${EMULATOR_AVD} -port ${EMULATOR_PORT} -wipe-data &> .emulator_log.txt &
    adb -s ${EMULATOR_ID} wait-for-device
    printf "adb connected. waiting for bootanim (again).."
  else
    sleep 2
    printf "."
    A=$(adb -s ${EMULATOR_ID} shell getprop init.svc.bootanim | tr -d '\r')
  fi
done

adb -s ${EMULATOR_ID} shell wm dismiss-keyguard

end_time=`date +%s`
printf "\n$EMULATOR_ID is ready. Took `expr $end_time - $start_time` seconds\n"
