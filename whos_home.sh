#!/bin/sh
# IP range to check
ip=10.0.0.0/24

# MUST BE RUN WITH SUDO
if [ "$EUID" -ne 0 ]
  then echo "This script must be run as root!"
  exit
fi
# nmap, returns the mac addresses
nmap -sP -n $ip
