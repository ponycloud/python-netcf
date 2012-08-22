#!/usr/bin/python -tt

"""
Small utility to configure network using pxelinux info.

When you boot with IPAPPEND 2, pxelinux adds BOOTIF= option to the kernel
command line readable through /proc/cmdline. This tool takes the option
and configures matching interface to use DHCP.

Since netcf cannot enumerate completely unknown interfaces,
we need to do it ourselves through sysfs.
"""

import os
import re
import netcf

def find_interface(mac):
    """
    Returns name of interface with given MAC address.
    """
    for name in os.listdir('/sys/class/net'):
        with open('/sys/class/net/' + name + '/address') as fp:
            if fp.read().strip() == mac:
                return name

    raise Exception('interface with MAC address %s not found' % mac)

def get_boot_hwaddr():
    """
    Finds out hardware address of the boot interface.
    """
    with open('/proc/cmdline') as fp:
        for opt in re.split(' +', fp.read()):
            parts = re.split('=', opt, 1)

            if len(parts) < 2:
                continue

            if parts[0] != 'BOOTIF':
                continue

            mac = re.split('[^0-9a-f]', parts[1].lower())
            return ':'.join(mac[-6:])

    raise Exception('/proc/cmdline: BOOTIF= not found')

if __name__ == '__main__':
    mac = get_boot_hwaddr()
    iface = find_interface(mac)

    print 'We have booted from %s (%s)' % (iface, mac)

    NetCF().define('''
        <?xml version="1.0"?>
        <interface type="ethernet" name="%(iface)s">
          <start mode="onboot"/>
          <mac address="%(mac)s"/>
          <protocol family="ipv4">
            <dhcp peerdns="yes"/>
          </protocol>
        </interface>
    ''' % locals()).up()

    print 'Interface configured.'

# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-
