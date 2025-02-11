"""OnboardingTask Django model."""

import socket

import netaddr
from netaddr.core import AddrFormatError

from nautobot_device_onboarding.exceptions import OnboardException


def onboarding_task_fqdn_to_ip(onboarding_task):
    """Method to assure OT has FQDN resolved to IP address and rewritten into OT.

    If it is a DNS name, attempt to resolve the DNS address and assign the IP address to the
    name.

    Returns:
        None

    Raises:
      OnboardException("fail-general"):
        When a prefix was entered for an IP address
      OnboardException("fail-dns"):
        When a Name lookup via DNS fails to resolve an IP address
    """
    try:
        # If successful, this is an IP address and can pass
        netaddr.IPAddress(onboarding_task.ip_address)
    # Raise an Exception for Prefix values
    except ValueError as err:
        raise OnboardException(
            reason="fail-general", message=f"ERROR appears a prefix was entered: {onboarding_task.ip_address}"
        ) from err
    # An AddrFormatError exception means that there is not an IP address in the field, and should continue on
    except AddrFormatError:
        try:
            # Perform DNS Lookup
            onboarding_task.ip_address = socket.gethostbyname(onboarding_task.ip_address)
            onboarding_task.save()
        except socket.gaierror as err:
            # DNS Lookup has failed, Raise an exception for unable to complete DNS lookup
            raise OnboardException(
                reason="fail-dns", message=f"ERROR failed to complete DNS lookup: {onboarding_task.ip_address}"
            ) from err
