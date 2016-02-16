#!/bin/bash -eux

aws autoscaling set-instance-health --instance-id "$1" --health-status Unhealthy --no-should-respect-grace-period