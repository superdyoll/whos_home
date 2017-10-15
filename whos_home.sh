#!/bin/sh
# IP range to check
ip=10.0.0.0/24

# nmap, returns the mac addresses
nmap -sP -n $ip
