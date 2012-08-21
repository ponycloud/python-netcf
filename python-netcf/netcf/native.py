#!/usr/bin/python -tt

from ctypes import *
from ctypes.util import find_library

libnetcf = CDLL(find_library('netcf'))
libc = CDLL(find_library('c'))

class netcf_t(Structure):
    pass

class netcf_if_t(Structure):
    pass

# void free(void *)
libc.free.argtypes = (c_void_p,)
libc.free.restype = None

free = libc.free

# int ncf_init(struct netcf **netcf, const char *root)
libnetcf.ncf_init.argtypes = (POINTER(POINTER(netcf_t)), c_char_p)
libnetcf.ncf_init.restype = c_int
ncf_init = libnetcf.ncf_init

# int ncf_close(struct netcf *)
libnetcf.ncf_close.argtypes = (POINTER(netcf_t),)
libnetcf.ncf_close.restype = c_int
ncf_close = libnetcf.ncf_close

# int ncf_num_of_interfaces(struct netcf *, unsigned int flags)
libnetcf.ncf_num_of_interfaces.argtypes = (POINTER(netcf_t), c_uint)
libnetcf.ncf_num_of_interfaces.restype = c_int
ncf_num_of_interfaces = libnetcf.ncf_num_of_interfaces

# int ncf_list_interfaces(struct netcf *, int maxnames, char **names, unsigned int flags)
libnetcf.ncf_list_interfaces.argtypes = (POINTER(netcf_t), c_int, POINTER(c_char_p), c_uint)
libnetcf.ncf_list_interfaces.restype = c_int
ncf_list_interfaces = libnetcf.ncf_list_interfaces

# struct netcf_if *ncf_lookup_by_name(struct netcf *, const char *name)
libnetcf.ncf_lookup_by_name.argtypes = (POINTER(netcf_t), c_char_p)
libnetcf.ncf_lookup_by_name.restype = POINTER(netcf_if_t)
ncf_lookup_by_name = libnetcf.ncf_lookup_by_name

# int ncf_lookup_by_mac_string(struct netcf *, const char *mac, int maxifaces, struct netcf_if **ifaces)
libnetcf.ncf_lookup_by_mac_string.argtypes = (POINTER(netcf_t), c_char_p, c_int, POINTER(POINTER(netcf_if_t)))
libnetcf.ncf_lookup_by_mac_string.restype = c_int
ncf_lookup_by_mac_string = libnetcf.ncf_lookup_by_mac_string

# struct netcf_if *ncf_define(struct netcf *, const char *xml)
libnetcf.ncf_define.argtypes = (POINTER(netcf_t), c_char_p)
libnetcf.ncf_define.restype = POINTER(netcf_if_t)
ncf_define = libnetcf.ncf_define

# const char *ncf_if_name(struct netcf_if *)
libnetcf.ncf_if_name.argtypes = (POINTER(netcf_if_t),)
libnetcf.ncf_if_name.restype = c_char_p
ncf_if_name = libnetcf.ncf_if_name

# const char *ncf_if_mac_string(struct netcf_if *)
libnetcf.ncf_if_mac_string.argtypes = (POINTER(netcf_if_t),)
libnetcf.ncf_if_mac_string.restype = c_char_p
ncf_if_mac_string = libnetcf.ncf_if_mac_string

# int ncf_if_up(struct netcf_if *)
libnetcf.ncf_if_up.argtypes = (POINTER(netcf_if_t),)
libnetcf.ncf_if_up.restype = c_int
ncf_if_up = libnetcf.ncf_if_up

# int ncf_if_down(struct netcf_if *)
libnetcf.ncf_if_down.argtypes = (POINTER(netcf_if_t),)
libnetcf.ncf_if_down.restype = c_int
ncf_if_down = libnetcf.ncf_if_down

# int ncf_if_undefine(struct netcf_if *)
libnetcf.ncf_if_undefine.argtypes = (POINTER(netcf_if_t),)
libnetcf.ncf_if_undefine.restype = c_int
ncf_if_undefine = libnetcf.ncf_if_undefine

# void *ncf_if_xml_desc(struct netcf_if *)
libnetcf.ncf_if_xml_desc.argtypes = (POINTER(netcf_if_t),)
libnetcf.ncf_if_xml_desc.restype = c_void_p
ncf_if_xml_desc = libnetcf.ncf_if_xml_desc

# void *ncf_if_xml_state(struct netcf_if *)
libnetcf.ncf_if_xml_state.argtypes = (POINTER(netcf_if_t),)
libnetcf.ncf_if_xml_state.restype = c_void_p
ncf_if_xml_state = libnetcf.ncf_if_xml_state

# int ncf_if_status(struct netcf_if *nif, unsigned int *flags)
libnetcf.ncf_if_status.argtypes = (POINTER(netcf_if_t), POINTER(c_uint))
libnetcf.ncf_if_status.restype = c_int
ncf_if_status = libnetcf.ncf_if_status

# int ncf_change_begin(struct netcf *ncf, unsigned int flags)
libnetcf.ncf_change_begin.argtypes = (POINTER(netcf_t), c_uint)
libnetcf.ncf_change_begin.restype = c_int
ncf_change_begin = libnetcf.ncf_change_begin

# int ncf_change_rollback(struct netcf *ncf, unsigned int flags)
libnetcf.ncf_change_rollback.argtypes = (POINTER(netcf_t), c_uint)
libnetcf.ncf_change_rollback.restype = c_int
ncf_change_rollback = libnetcf.ncf_change_rollback

# int ncf_change_commit(struct netcf *ncf, unsigned int flags)
libnetcf.ncf_change_commit.argtypes = (POINTER(netcf_t), c_uint)
libnetcf.ncf_change_commit.restype = c_int
ncf_change_commit = libnetcf.ncf_change_commit

# void ncf_if_free(struct netcf_if *)
libnetcf.ncf_if_free.argtypes = (POINTER(netcf_if_t),)
libnetcf.ncf_if_free.restype = None
ncf_if_free = libnetcf.ncf_if_free

# int ncf_error(struct netcf *, const char **errmsg, const char **details)
libnetcf.ncf_error.argtypes = (POINTER(netcf_t), POINTER(c_char_p), POINTER(c_char_p))
libnetcf.ncf_error.restype = c_int
ncf_error = libnetcf.ncf_error


# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-
