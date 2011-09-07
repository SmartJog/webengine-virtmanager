# -*- coding: utf-8 -*-

import webengine.utils.log
from webengine.utils.decorators import exportable

import libvirt
import logging

@exportable
def get_status(_request):
    """ Return status of all virtual machine instances. """

    ret = {}
    conn = libvirt.open('qemu:///system')
    try:
        # List non-running domains
        ret.update((conn.lookupByID(domid).name(), 'online') for domid in conn.listDomainsID())

        # List running domains
        for domid in conn.listDefinedDomains():
            dom = conn.lookupByName(domid)
            ret[dom.name()] = 'offline'
    finally:
        conn.close()

    return ret

@exportable
def domain_stop(_request, domain, kill=False):
    """ Stop a currently running domain.
    
    if @kill is set to True, the VM is forcefully shut down instead of sending
    an ACPI signal.
    """

    conn = libvirt.open('qemu:///system')
    try:
        dom = conn.lookupByName(domain)
        
        if dom.isActive():
            dom.shutdown()
            logging.getLogger('webengine.libvirt.services').info('VM %s stopped', dom.name())

        if dom.isActive() and kill:
            dom.destroy()
            logging.getLogger('webengine.libvirt.services').info('VM %s forcefully shutdown', dom.name())

        ret = dom.isActive()
    finally:
        conn.close()

    return not ret

@exportable
def domain_start(_request, domain):
    """ Start a domain. """

    conn = libvirt.open('qemu:///system')
    try:
        dom = conn.lookupByName(domain)

        if not dom.isActive():
            dom.create()
            logging.getLogger('webengine.libvirt.services').info('VM %s started', dom.name())

        ret = dom.isActive()
    finally:
        conn.close()

    return bool(ret)

