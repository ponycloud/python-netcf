#!/usr/bin/python -tt

__all__ = ['NetCF', 'NetCFError', 'Interface']

from native import *
from finalize import track_for_finalization

class NetCFError(Exception):
    NOERROR = 0
    EINTERNAL = 1
    EOTHER = 2
    ENOMEM = 3
    EXMLPARSER = 4
    EXMLINVALID = 5
    ENOENT = 6
    EEXEC = 7
    EINUSE = 8
    EXSLTFAILED = 9
    EFILE = 10
    EIOCTL = 11
    ENETLINK = 12
    EINVALIDOP = 13

    def __init__(self, code, message, details):
        self.code = code
        self.message = message
        self.details = details

    def __str__(self):
        return '%s; %s' % (self.message, self.details)

def check_result(ncf, res):
    if res is None or res < 0:
        errmsgp = c_char_p()
        detailsp = c_char_p()
        code = ncf_error(ncf, pointer(errmsgp), pointer(detailsp))
        raise NetCFError(code, errmsgp.value, detailsp.value)

class Interface(object):
    INACTIVE = 1
    ACTIVE = 2

    def __init__(self, parent, iface):
        self.parent = parent
        self.iface = iface
        track_for_finalization(self, self.iface, ncf_if_free)

    @property
    def name(self):
        return ncf_if_name(self.iface)

    @property
    def mac(self):
        return ncf_if_mac_string(self.iface)

    @property
    def xml_desc(self):
        desc = ncf_if_xml_desc(self.iface)
        strval = cast(desc, c_char_p).value
        free(desc)
        return strval

    @property
    def xml_state(self):
        state = ncf_if_xml_state(self.iface)
        strval = cast(state, c_char_p).value
        free(state)
        return strval

    @property
    def status(self):
        status = c_uint()
        check_result(self.parent.ncf, ncf_if_status(self.iface, pointer(status)))
        return int(status.value)

    def up(self):
        check_result(self.parent.ncf, ncf_if_up(self.iface))

    def down(self):
        check_result(self.parent.ncf, ncf_if_down(self.iface))

    def __repr__(self):
        return '<Interface "%s">' % self.name

class NetCF(object):

    def __init__(self, root='/'):
        self.ncf = POINTER(netcf_t)()
        check_result(self.ncf, ncf_init(self.ncf, root))
        track_for_finalization(self, self.ncf, ncf_close)

    def define(self, xml):
        iface = ncf_define(self.ncf, xml)
        check_result(self.ncf, iface)
        return Interface(self, iface)

    def __len__(self):
        return ncf_num_of_interfaces(self.ncf, Interface.ACTIVE | Interface.INACTIVE)

    def __getitem__(self, item):
        if item not in self:
            raise KeyError
        return Interface(self, ncf_lookup_by_name(self.ncf, item))

    def __iter__(self):
        count = len(self)
        names = (c_char_p * count)()
        count = ncf_list_interfaces(self.ncf, count, names, Interface.ACTIVE | Interface.INACTIVE)
        return iter([names[i] for i in xrange(count)])

    def lookup_by_mac(self, macaddr):
        count = len(self)
        ifaces = (POINTER(netcf_if_t) * count)()
        count = ncf_lookup_by_mac_string(self.ncf, macaddr, count, cast(pointer(ifaces), POINTER(POINTER(netcf_if_t))))
        return iter([Interface(self, ifaces[x]) for x in xrange(count)])

    def __delitem__(self, item):
        iface = self[item]
        check_result(self.ncf, ncf_if_undefine(iface.iface))

    def __enter__(self):
        check_result(self.ncf, ncf_change_begin(self.ncf, 0))

    def __exit__(self, exc_type, value, traceback):
        if exc_type is None:
            check_result(self.ncf, ncf_change_commit(self.ncf, 0))
        else:
            check_result(self.ncf, ncf_change_rollback(self.ncf, 0))


# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-