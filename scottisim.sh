#!/bin/sh

mydir=$(cd `dirname $0` && pwd)
ipython -i --matplotlib -- ${mydir}/scottisim.py $1
