#!/usr/bin/python -tt

__all__ = ['NetCF', 'NetCFError', 'Interface']

from native import *
from finalize import track_for_finalization

class NetCFError(Exception):
    """
    Generic NetCF Exception

    We provide just one exception type, since it's not very probably that
    you will need to react to different problems differently. If you need
    some more, let us know via github.

    This class defines bunch of error codes you can use to test for specific
    conditions if it's enough for you.
    """

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
        """
        Saves exception data.

        :param code: is the NetCF error code.
        :param message: is the generic message.
        :param details: is any additional description (such as output of a
                        system command that failed to bring an interface up).
        """
        super(NetCFError, self).__init__(self, '%s\n%s' % (message, details))
        self.code = code
        self.message = message
        self.details = details

def check_result(ncf):
    """
    Raises an exception if previous ncf command failed.

    :param ncf: the netcf context to examine.
    """

    errmsgp = c_char_p()
    detailsp = c_char_p()
    code = ncf_error(ncf, pointer(errmsgp), pointer(detailsp))

    if NetCFError.NOERROR != code:
        raise NetCFError(code, errmsgp.value, detailsp.value)

class Interface(object):
    """
    Network Interface

    Abstraction of a network interface.
    Can be used to query state and definition.
    """

    INACTIVE = 1
    ACTIVE = 2

    def __init__(self, parent, name):
        """
        Constructs network interface proxy.

        :param parent: pointer to parent NetCF context.
        :param name: name of the interface.
        """

        self.parent = parent

        self.iface = ncf_lookup_by_name(self.parent.ncf, name)
        if self.iface is None:
            check_result(self.parent.ncf)
            raise KeyError('interface %s not found' % name)

        track_for_finalization(self, self.iface, ncf_if_free)

    @property
    def name(self):
        """Returns name of the interface."""
        name = ncf_if_name(self.iface)
        check_result(self.parent.ncf)
        return cast(name, c_char_p).value

    @property
    def mac(self):
        """Returns mac address of the interface."""
        mac = ncf_if_mac_string(self.iface)
        check_result(self.parent.ncf)
        return cast(mac, c_char_p).value

    @property
    def xml_desc(self):
        """
        Returns XML definition of the interface.

        This XML can be then passed to `NetCF.create()` in order to create
        the exactly same interface.
        """

        desc = ncf_if_xml_desc(self.iface)
        check_result(self.parent.ncf)
        if desc is None:
            return None
        strval = cast(desc, c_char_p).value
        free(desc)
        return strval

    @property
    def xml_state(self):
        """Returns XML with current state of the interface."""
        state = ncf_if_xml_state(self.iface)
        check_result(self.parent.ncf)
        if state is None:
            return None
        strval = cast(state, c_char_p).value
        free(state)
        return strval

    @property
    def status(self):
        """
        Returns interface status.

        You might want to check the returned status against `Interface.UP`
        or `Interface.DOWN`.
        """

        status = c_uint(0)
        ncf_if_status(self.iface, pointer(status))
        check_result(self.parent.ncf)
        return int(status.value)

    def up(self):
        """Brings the interface up."""
        ncf_if_up(self.iface)
        check_result(self.parent.ncf)

    def down(self):
        """Tears the interface down."""
        ncf_if_down(self.iface)
        check_result(self.parent.ncf)

    def undefine(self):
        """Undefines this interface."""
        ncf_if_undefine(self.iface)
        check_result(self.parent.ncf)

    def __repr__(self):
        return '<Interface "%s">' % self.name

class NetCF(object):
    """
    Network Configuration Wrapper
    """

    def __init__(self, root='/'):
        """
        Opens system at given path.

        :param root: path to system to operate on.
        """

        self.ncf = c_void_p()
        if 0 != ncf_init(self.ncf, root):
            raise RuntimeError('failed to initialize netcf context')
        check_result(self.ncf)
        track_for_finalization(self, self.ncf, ncf_close)

    def define(self, xml):
        """
        Defines new interface.

        :param xml: description of the new interface. Can be dumped from
                    existing ones using `Interface.xml_desc`.
        """

        iface = ncf_define(self.ncf, xml)
        check_result(self.ncf)

    def __len__(self):
        """
        Returns number of all known interfaces.
        """
        num = ncf_num_of_interfaces(self.ncf, Interface.ACTIVE | Interface.INACTIVE)
        check_result(self.ncf)
        return num

    def __getitem__(self, name):
        """
        Returns Interface instance for given name.

        :param name: name of the interface.
        """
        return Interface(self, name)

    def __iter__(self):
        """
        Returns iterator over interface names.
        """
        count = len(self)
        names = (c_char_p * count)()
        count = ncf_list_interfaces(self.ncf, count, names, Interface.ACTIVE | Interface.INACTIVE)
        check_result(self.ncf)
        return iter([names[i] for i in xrange(count)])

    def lookup_by_mac(self, macaddr):
        """
        Returns list of interfaces matching given mac address.

        :param macaddr: the mac address to look for.
        """
        count = len(self)
        ifaces = (c_void_p * count)()
        count = ncf_lookup_by_mac_string(self.ncf, macaddr, count, cast(pointer(ifaces), POINTER(c_void_p)))
        check_result(self.ncf)
        return iter([Interface(self, ifaces[x]) for x in xrange(count)])

    def __enter__(self):
        """
        Starts transaction.

        Example::
            with nc:
                del nc['em1']
                nc.define(new_em1_xml)

        The `__exit__()` then takes care of the commit or revert.
        """
        ncf_change_begin(self.ncf, 0)
        check_result(self.ncf)

    def __exit__(self, exc_type, value, traceback):
        """
        Commits or reverts transaction.

        If the exc_type is not None, transaction is reverted.
        Otherwise it is commited and the changes are made permanent.
        """

        if exc_type is None:
            ncf_change_commit(self.ncf, 0)
        else:
            ncf_change_rollback(self.ncf, 0)
        check_result(self.ncf)


# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-
