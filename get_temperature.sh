#!/bin/sh
#
# from http://www.kkn.net/~n6tv/xadc.sh
# updated by Michael Hirsch, Ph.D.
#
# works in Ash (Red Pitaya ecosystem 0.95) and Bash (ecosystem 0.97)

# path to IIO device
XADC_PATH=/sys/bus/iio/devices/iio:device0

# Note: used "cat" to work in Ash instead of the typically recommended Bash "<".

OFF=$(cat $XADC_PATH/in_temp0_offset)
RAW=$(cat $XADC_PATH/in_temp0_raw)
SCL=$(cat $XADC_PATH/in_temp0_scale)

FORMULA="(($OFF+$RAW)*$SCL)/1000.0"
VAL=$(echo "scale=2;${FORMULA}" | bc)
echo "in_temp0 = ${VAL} °C"


