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

def check_result(ncf, res):
    """
    Raises an exception if passed unsuccessfull netcf result.

    :param res: is the result to examine.
                None or numbers below zero are treated as failures.
    """

    if res is None or res < 0:
        errmsgp = c_char_p()
        detailsp = c_char_p()
        code = ncf_error(ncf, pointer(errmsgp), pointer(detailsp))
        raise NetCFError(code, errmsgp.value, detailsp.value)

class Interface(object):
    """
    Network Interface

    Abstraction of a network interface.
    Can be used to query state and definition.
    """

    INACTIVE = 1
    ACTIVE = 2

    def __init__(self, parent, iface):
        """
        Constructs network interface proxy.

        You don't need to instantiate this class directly. You probably
        want to ask NetCF to give it to you using e.g. ``nc['eth0']``.

        :param parent: points to netcf instance required for error handling.
        :param iface: C pointer to netcf_if structure.
        """

        # Make extra sure, since otherwise it's a sure segfault.
        assert isinstance(iface, POINTER(netcf_if_t))

        self.parent = parent
        self.iface = iface
        track_for_finalization(self, self.iface, ncf_if_free)

    @property
    def name(self):
        """Returns name of the interface."""
        return ncf_if_name(self.iface)

    @property
    def mac(self):
        """Returns mac address of the interface."""
        return ncf_if_mac_string(self.iface)

    @property
    def xml_desc(self):
        """
        Returns XML definition of the interface.

        This XML can be then passed to `NetCF.create()` in order to create
        the exactly same interface.
        """

        desc = ncf_if_xml_desc(self.iface)
        strval = cast(desc, c_char_p).value
        free(desc)
        return strval

    @property
    def xml_state(self):
        """Returns XML with current state of the interface."""
        state = ncf_if_xml_state(self.iface)
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

        status = c_uint()
        check_result(self.parent.ncf, ncf_if_status(self.iface, pointer(status)))
        return int(status.value)

    def up(self):
        """Brings the interface up."""
        check_result(self.parent.ncf, ncf_if_up(self.iface))

    def down(self):
        """Tears the interface down."""
        check_result(self.parent.ncf, ncf_if_down(self.iface))

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

        self.ncf = POINTER(netcf_t)()
        check_result(self.ncf, ncf_init(self.ncf, root))
        track_for_finalization(self, self.ncf, ncf_close)

    def define(self, xml):
        """
        Defines new interface.

        :param xml: description of the new interface. Can be dumped from
                    existing ones using `Interface.xml_desc`.
        """

        iface = ncf_define(self.ncf, xml)
        check_result(self.ncf, iface)
        return Interface(self, iface)

    def __len__(self):
        """
        Returns number of all known interfaces.
        """
        return ncf_num_of_interfaces(self.ncf, Interface.ACTIVE | Interface.INACTIVE)

    def __getitem__(self, name):
        """
        Returns Interface instance for given name.

        :param name: name of the interface.
        """
        if name not in self:
            raise KeyError
        return Interface(self, ncf_lookup_by_name(self.ncf, name))

    def __iter__(self):
        """
        Returns iterator over interface names.
        """
        count = len(self)
        names = (c_char_p * count)()
        count = ncf_list_interfaces(self.ncf, count, names, Interface.ACTIVE | Interface.INACTIVE)
        return iter([names[i] for i in xrange(count)])

    def lookup_by_mac(self, macaddr):
        """
        Returns list of interfaces matching given mac address.

        :param macaddr: the mac address to look for.
        """
        count = len(self)
        ifaces = (POINTER(netcf_if_t) * count)()
        count = ncf_lookup_by_mac_string(self.ncf, macaddr, count, cast(pointer(ifaces), POINTER(POINTER(netcf_if_t))))
        return iter([Interface(self, ifaces[x]) for x in xrange(count)])

    def __delitem__(self, name):
        """
        Undefines specified interface.

        :param name: name of the interface.
        """
        iface = self[name]
        check_result(self.ncf, ncf_if_undefine(iface.iface))

    def __enter__(self):
        """
        Starts transaction.

        Example::
            with nc:
                del nc['em1']
                nc.define(new_em1_xml)

        The `__exit__()` then takes care of the commit or revert.
        """
        check_result(self.ncf, ncf_change_begin(self.ncf, 0))

    def __exit__(self, exc_type, value, traceback):
        """
        Commits or reverts transaction.

        If the exc_type is not None, transaction is reverted.
        Otherwise it is commited and the changes are made permanent.
        """

        if exc_type is None:
            check_result(self.ncf, ncf_change_commit(self.ncf, 0))
        else:
            check_result(self.ncf, ncf_change_rollback(self.ncf, 0))


# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-
