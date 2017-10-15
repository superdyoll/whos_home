#!/bin/sh
# IP range to check
ip=10.0.0.0/24
# File to output to
outfile=/tmp/whos_home_output.txt

# MUST BE RUN WITH SUDO
if [ "$EUID" -ne 0 ]
  then echo "This script must be run as root!"
  exit
fi

# Commands:
# nmap, returns the mac addresses
nmap -sP -n $ip > $outfile
# date, prints the time in unix time
date +%s >> $outfile
