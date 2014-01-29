# -*- coding: utf-8 -*-

from webengine.utils.decorators import exportable

import libvirt
import logging
import os
import ConfigParser

# Due to libvirt API bug which leak fds.
# We change use of python bindings by calling virsh binary directly only for start and stop operations


class AddSection(object):
    """Add dummy section to ini file since ConfigParser require at least one"""
    def __init__(self, ini_file):
        self.ini_file = ini_file
        self.temp = 1
        self.sechead = '[asection]\n'

    def readline(self):
        """Overide the readline method to add a section"""
        if self.temp == 1:
            self.temp = 0
            return self.sechead
        else:
            return self.ini_file.readline()


def is_libvirt_on():
    """Check if a virtualization was required"""
    with open('/etc/default/libvirt-bin') as ini_file:
        config = ConfigParser.ConfigParser({'start_libvirtd': 'no'})
        config.readfp(AddSection(ini_file))
        return config.get('asection', 'start_libvirtd').strip('"\'') == 'yes'


@exportable
def get_status(_request):
    """ Return status of all virtual machine instances. """
    ret = {}
    if is_libvirt_on():
        dom = None
        conn = libvirt.open('qemu:///system')
        try:
            # List non-running domains
            ret.update((conn.lookupByID(domid).name(), 'online') for domid in conn.listDomainsID())

            # List running domains
            for domid in conn.listDefinedDomains():
                dom = conn.lookupByName(domid)
                ret[dom.name()] = 'offline'
        finally:
            if dom:
                del dom
            conn.close()

    return ret


@exportable
def domain_stop(_request, domain, kill=False):
    """ Stop a currently running domain.

    if @kill is set to True, the VM is forcefully shut down instead of sending
    an ACPI signal.
    """

    conn = libvirt.open('qemu:///system')
    dom = None
    cmd = None
    try:
        dom = conn.lookupByName(domain)

        if dom.isActive():
            cmd = "virsh -c 'qemu:///system' shutdown '%s'" % domain

        if dom.isActive() and kill:
            cmd = "virsh -c 'qemu:///system' destroy '%s'" % domain

        if cmd is not None:
            logging.getLogger('webengine.libvirt.services').info(cmd)
            os.system(cmd)

        ret = dom.isActive()
    finally:
        if dom:
            del dom
        conn.close()

    return not bool(ret)


@exportable
def domain_start(_request, domain):
    """ Start a domain. """

    conn = libvirt.open('qemu:///system')
    dom = None
    try:
        dom = conn.lookupByName(domain)

        if not dom.isActive():
            cmd = "virsh -c 'qemu:///system' start '%s'" % domain
            logging.getLogger('webengine.libvirt.services').info(cmd)
            os.system(cmd)

        ret = dom.isActive()
    finally:
        if dom:
            del dom
        conn.close()
    return bool(ret)
