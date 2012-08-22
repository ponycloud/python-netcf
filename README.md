# Python bindings for the NetCF library

The [NetCF][] library provides relatively high-level API to configuration of
Linux network interfaces. Since sometimes it is useful to be able to plug
into this interface without `NetworkManager` or `libvirt`, we bring you these
simple bindings based on `python-ctypes`.

See the pydoc for details on it's usage.

## Quick Examples

    from netcf import NetCF

    nc = NetCF()

    # List all interface hardware addresses.
    for ifname in nc:
        print '%s mac=%s' % (ifname, nc[ifname].mac)

    # Print definition and state of loopback interface.
    print nc['lo'].xml_desc
    print nc['lo'].xml_state

    # Shutdown and remove an interface.
    saved_em1 = nc['em1'].xml_desc
    nc['em1'].down()
    del nc['em1']

    # Configure and bring it up again.
    nc.define(saved_em1)
    nc['em1'].up()


[NetCF]: https://fedorahosted.org/netcf/
