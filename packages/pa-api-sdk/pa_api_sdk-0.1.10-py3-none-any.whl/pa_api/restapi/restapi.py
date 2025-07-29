import json
import logging
from itertools import chain

import requests

# Remove warning for unverified certificate
# https://stackoverflow.com/questions/27981545/suppress-insecurerequestwarning-unverified-https-request-is-being-made-in-pytho
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from pa_api.constants import PANORAMA_ERRORS, SUCCESS_CODE
from pa_api.utils import clean_url_host

from .rest_resources import (
    PanoramaDevicesResourceType,
    PanoramaNetworkResourceType,
    PanoramaObjectsResourceType,
    PanoramaPanoramaResourceType,
    PanoramaPoliciesResourceType,
)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

OBJECT_RESOURCES = [
    "Addresses",
    "AddressGroups",
    "Regions",
    "Applications",
    "ApplicationGroups",
    "ApplicationFilters",
    "Services",
    "ServiceGroups",
    "Tags",
    "GlobalProtectHIPObjects",
    "GlobalProtectHIPProfiles",
    "ExternalDynamicLists",
    "CustomDataPatterns",
    "CustomSpywareSignatures",
    "CustomVulnerabilitySignatures",
    "CustomURLCategories",
    "AntivirusSecurityProfiles",
    "AntiSpywareSecurityProfiles",
    "VulnerabilityProtectionSecurityProfiles",
    "URLFilteringSecurityProfiles",
    "FileBlockingSecurityProfiles",
    "WildFireAnalysisSecurityProfiles",
    "DataFilteringSecurityProfiles",
    "DoSProtectionSecurityProfiles",
    "SecurityProfileGroups",
    "LogForwardingProfiles",
    "AuthenticationEnforcements",
    "DecryptionProfiles",
    "DecryptionForwardingProfiles",
    "Schedules",
    "SDWANPathQualityProfiles",
    "SDWANTrafficDistributionProfiles",
]

POLICY_RESOURCES = [
    "SecurityRules",
    "NATRules",
    "QoSRules",
    "PolicyBasedForwardingRules",
    "DecryptionRules",
    "TunnelInspectionRules",
    "ApplicationOverrideRules",
    "AuthenticationRules",
    "DoSRules",
    "SDWANRules",
]

NETWORK_RESOURCES = [
    "EthernetInterfaces",
    "AggregateEthernetInterfaces",
    "VLANInterfaces",
    "LoopbackInterfaces",
    "TunnelIntefaces",
    "SDWANInterfaces",
    "Zones",
    "VLANs",
    "VirtualWires",
    "VirtualRouters",
    "IPSecTunnels",
    "GRETunnels",
    "DHCPServers",
    "DHCPRelays",
    "DNSProxies",
    "GlobalProtectPortals",
    "GlobalProtectGateways",
    "GlobalProtectGatewayAgentTunnels",
    "GlobalProtectGatewaySatelliteTunnels",
    "GlobalProtectGatewayMDMServers",
    "GlobalProtectClientlessApps",
    "GlobalProtectClientlessAppGroups",
    "QoSInterfaces",
    "LLDP",
    "GlobalProtectIPSecCryptoNetworkProfiles",
    "IKEGatewayNetworkProfiles",
    "IKECryptoNetworkProfiles",
    "MonitorNetworkProfiles",
    "InterfaceManagementNetworkProfiles",
    "ZoneProtectionNetworkProfiles",
    "QoSNetworkProfiles",
    "LLDPNetworkProfiles",
    "SDWANInterfaceProfiles",
]

DEVICE_RESOURCES = [
    "VirtualSystems",
]

DEFAULT_PARAMS = {
    "output-format": "json",
}


class PanoramaAPI:
    def __init__(self, api_key=None, verbose=False, verify=False, logger=None):
        self._verbose = verbose
        self._verify = verify
        self._api_key = api_key
        self.logger = logger or logging

    def _inner_request(
        self,
        method,
        url,
        params=None,
        headers=None,
        data=None,
        verify=None,
    ):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if verify is None:
            verify = self._verify
        default_headers = {
            "X-PAN-KEY": self._api_key,
            # 'Accept': 'application/json, application/xml',
            # 'Content-Type': 'application/json'
        }
        headers = {**default_headers, **headers}
        params = {**DEFAULT_PARAMS, **params}
        res = requests.request(
            method,
            url,
            params=params,
            headers=headers,
            verify=verify,
        )
        # The API always returns a json, no matter what
        # if not res.ok:
        #     return None
        try:
            data = res.json()
            code = int(
                data.get("@code") or data.get("code") or SUCCESS_CODE,
            )  # Sometimes, the code is a string, some other times it is a int
            status = data.get("@status", "")
            success = status == "success"
            error_occured = (
                not res.ok
                or (
                    not success and code < SUCCESS_CODE
                )  # In case of success, the value 19 is used
            )
            if not error_occured:
                return data, None
            message = (
                data.get("message")
                or PANORAMA_ERRORS.get(data["@code"])
                or "Something happened: " + json.dumps(data)
            )
            error = f"(CODE: {code}) {message}"
            if self._verbose:
                causes = list(
                    chain(
                        *(
                            details.get("causes", {})
                            for details in data.get("details", [])
                        ),
                    ),
                )
                details = "".join(c.get("description") for c in causes)
                error = f"{error} {details}"
            return data, error
        except Exception as e:
            return None, str(e)

    def _request(
        self,
        method,
        url,
        params=None,
        headers=None,
        data=None,
        verify=None,
        no_exception=False,
    ):
        data, error = (
            self._inner_request(
                method,
                url,
                params=params,
                headers=headers,
                data=data,
                verify=verify,
            )
            or {}
        )
        if error:
            if no_exception:
                self.logger.error(f"Could not {method.lower()} {url}: {error}")
                return data, error
            raise Exception(error)
        data = data.get("result", {}).get("entry") or []
        return data, error

    def request(self, method, url, params=None, headers=None, data=None, verify=None):
        data, _ = (
            self._request(
                method,
                url,
                params=params,
                headers=headers,
                data=data,
                verify=verify,
            )
            or {}
        )
        return data

    def get(self, url, params=None, headers=None, data=None, verify=None):
        data, _ = (
            self._request(
                "GET",
                url,
                params=params,
                headers=headers,
                data=data,
                verify=verify,
            )
            or {}
        )
        return data
        # return data.get("result", {}).get("entry") or []

    def delete(self, url, params=None, headers=None, data=None, verify=None):
        data, _ = (
            self._request(
                "DELETE",
                url,
                params=params,
                headers=headers,
                data=data,
                verify=verify,
            )
            or {}
        )
        return data


class PanoramaClient:
    """
    Wrapper for the PaloAlto REST API
    Resources (e.g. Addresses, Tags, ..) are grouped under their resource types.
    See https://docs.paloaltonetworks.com/pan-os/10-1/pan-os-panorama-api/get-started-with-the-pan-os-rest-api/access-the-rest-api#id0e536ca4-6154-4188-b70f-227c2c113ec4

    Attributes:

        - objects: groups all the objects (Address, Tag, Service, ...)
        - policies: groups all the policies (Security, NAT, ...)
        - network: groups all the network resources (e.g. EthernetInterfaces, VLANInterfaces, ...)
        - device: groups all device-related resources (only VirtualSystems)
        - panorama: groups all panorama-management-related resources (only DeviceGroups)
    """

    objects: PanoramaObjectsResourceType
    policies: PanoramaPoliciesResourceType
    network: PanoramaNetworkResourceType
    device: PanoramaDevicesResourceType
    panorama: PanoramaPanoramaResourceType

    def __init__(
        self,
        domain,
        api_key=None,
        version="v10.1",
        verify=False,
        verbose=False,
    ):
        domain, _, _ = clean_url_host(domain)
        client = PanoramaAPI(api_key=api_key, verbose=verbose, verify=verify)
        self.client = client
        self.objects = PanoramaObjectsResourceType(client, domain, version=version)
        self.policies = PanoramaPoliciesResourceType(client, domain, version=version)
        self.network = PanoramaNetworkResourceType(client, domain, version=version)
        self.device = PanoramaDevicesResourceType(client, domain, version=version)
        self.panorama = PanoramaPanoramaResourceType(client, domain, version=version)


__all__ = [
    "PanoramaClient",
]
