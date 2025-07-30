from functools import wraps
from multiprocessing.pool import ThreadPool as Pool
from typing import ClassVar

# List of existing resources
# https://docs.paloaltonetworks.com/pan-os/10-2/pan-os-panorama-api/get-started-with-the-pan-os-rest-api/access-the-rest-api

DEFAULT_PARAMS = {
    "location": "device-group",
}


class BasePanoramaResource:
    def __init__(
        self,
        client,
        host,
        resource_type,
        resource,
        version="v10.1",
        default_params=None,
    ):
        """
        client:
        """
        self.DEFAULT_PARAMS = default_params or DEFAULT_PARAMS
        if not host.startswith("http"):
            host = "https://" + host
        self._client = client
        self._name = f"{resource_type}/{resource}"
        self._url = f"{host}/restapi/{version}/{resource_type}/{resource}"

    def __str__(self):
        return self._name

    def __repr__(self):
        return str(self)

    def get(self, params=None, headers=None, data=None, verify=None):
        return self._client.get(
            self._url,
            params=params,
            headers=headers,
            data=data,
            verify=verify,
        )

    def delete(self, params=None, headers=None, data=None, verify=None):
        return self._client.delete(
            self._url,
            params=params,
            headers=headers,
            data=data,
            verify=verify,
        )


class PanoramaResource(BasePanoramaResource):
    def get(
        self,
        device_group=None,
        name=None,
        inherited=True,
        params=None,
        headers=None,
        data=None,
        verify=None,
    ):
        if params is None:
            params = {}
        _params = {**self.DEFAULT_PARAMS, **params}
        if name is not None:
            _params["name"] = name

        def func(params):
            params = {**_params, **params}
            res = self._client.get(
                self._url,
                params=params,
                headers=headers,
                data=data,
                verify=verify,
            )
            if not isinstance(res, list):
                return []  # Error happened
            if not inherited:
                res = [r for r in res if r["@device-group"] == r["@loc"]]
            return res

        if device_group is None:
            return func(params)
        if isinstance(device_group, str):
            device_group = [device_group]
        if len(device_group) == 1:
            params = {"device-group": device_group}
            return func(params)
        if len(device_group) > 1:
            params_list = [{"device-group": dg} for dg in device_group]
            with Pool(len(device_group)) as pool:
                data = pool.map(func, params_list)
            return [record for res in data for record in res]
        return None

    def delete(
        self,
        device_group=None,
        name=None,
        params=None,
        headers=None,
        data=None,
        verify=None,
    ):
        if params is None:
            params = {}
        params = {**self.DEFAULT_PARAMS, **params}
        if device_group is not None:
            params["device-group"] = device_group
        if name is not None:
            params["name"] = name
        return self._client.delete(
            self._url,
            params=params,
            headers=headers,
            data=data,
            verify=verify,
        )


class GroupedResources:
    def __init__(self, *resources):
        self._resources = resources

    def _grouped(self, method, *args, **kwargs):
        params_list = [(getattr(r, method), args, kwargs) for r in self._resources]

        def func(args):
            f, args, kwargs = args
            return f(*args, **kwargs)

        with Pool(len(self._resources)) as pool:
            data = pool.map(func, params_list)
        return [record for res in data for record in res]

    @wraps(PanoramaResource.get)
    def get(self, *args, **kwargs):
        return self._grouped("get", *args, **kwargs)

    # def delete(self, params={}, headers={}, data=None, verify=None):
    #     return self._client.delete(
    #         self._url,
    #         params=params, headers=headers,
    #         data=data, verify=verify
    #     )


class PanoramaResourceType:
    def __init__(self, client, resource_type):
        self._client = client
        self._name = resource_type

    def __str__(self):
        return self._name

    def __repr__(self):
        return str(self)


class PanoramaPanoramaResourceType(PanoramaResourceType):
    resource_type = "Panorama"

    def __init__(self, client, domain, version="v10.1"):
        resource_type = self.resource_type
        super().__init__(client, resource_type)

        def resource(name):
            return BasePanoramaResource(
                client,
                domain,
                resource_type,
                name,
                version=version,
            )

        self.DeviceGroups = resource("DeviceGroups")


class PanoramaObjectsResourceType(PanoramaResourceType):
    """
    Represent the 'Objects' subsection in the API.
    """

    resource_type = "Objects"

    def __init__(self, client, domain, version="v10.1"):
        resource_type = self.resource_type
        super().__init__(client, resource_type)

        def resource(name):
            return PanoramaResource(
                client,
                domain,
                resource_type,
                name,
                version=version,
            )

        self.Addresses = resource("Addresses")
        self.AddressGroups = resource("AddressGroups")
        self.Regions = resource("Regions")
        self.Applications = resource("Applications")
        self.ApplicationGroups = resource("ApplicationGroups")
        self.ApplicationFilters = resource("ApplicationFilters")
        self.Services = resource("Services")
        self.ServiceGroups = resource("ServiceGroups")
        self.Tags = resource("Tags")
        self.GlobalProtectHIPObjects = resource("GlobalProtectHIPObjects")
        self.GlobalProtectHIPProfiles = resource("GlobalProtectHIPProfiles")
        self.ExternalDynamicLists = resource("ExternalDynamicLists")
        self.CustomDataPatterns = resource("CustomDataPatterns")
        self.CustomSpywareSignatures = resource("CustomSpywareSignatures")
        self.CustomVulnerabilitySignatures = resource("CustomVulnerabilitySignatures")
        self.CustomURLCategories = resource("CustomURLCategories")
        self.AntivirusSecurityProfiles = resource("AntivirusSecurityProfiles")
        self.AntiSpywareSecurityProfiles = resource("AntiSpywareSecurityProfiles")
        self.VulnerabilityProtectionSecurityProfiles = resource(
            "VulnerabilityProtectionSecurityProfiles",
        )
        self.URLFilteringSecurityProfiles = resource("URLFilteringSecurityProfiles")
        self.FileBlockingSecurityProfiles = resource("FileBlockingSecurityProfiles")
        self.WildFireAnalysisSecurityProfiles = resource(
            "WildFireAnalysisSecurityProfiles",
        )
        self.DataFilteringSecurityProfiles = resource("DataFilteringSecurityProfiles")
        self.DoSProtectionSecurityProfiles = resource("DoSProtectionSecurityProfiles")
        self.SecurityProfileGroups = resource("SecurityProfileGroups")
        self.LogForwardingProfiles = resource("LogForwardingProfiles")
        self.AuthenticationEnforcements = resource("AuthenticationEnforcements")
        self.DecryptionProfiles = resource("DecryptionProfiles")
        self.DecryptionForwardingProfiles = resource("DecryptionForwardingProfiles")
        self.Schedules = resource("Schedules")
        self.SDWANPathQualityProfiles = resource("SDWANPathQualityProfiles")
        self.SDWANTrafficDistributionProfiles = resource(
            "SDWANTrafficDistributionProfiles",
        )


class PanoramaPoliciesResourceType(PanoramaResourceType):
    """
    Represent the 'Policies' subsection in the API.
    """

    resource_type = "Policies"

    def __init__(self, client, domain, version="v10.1"):
        resource_type = self.resource_type
        super().__init__(client, resource_type)

        def resource(name):
            return PanoramaResource(
                client,
                domain,  # host
                resource_type,
                name,
                version=version,
            )

        self.SecurityPreRules = resource("SecurityPreRules")
        self.SecurityPostRules = resource("SecurityPostRules")
        self.SecurityRules = GroupedResources(
            self.SecurityPreRules,
            self.SecurityPostRules,
        )
        self.NATPreRules = resource("NATPreRules")
        self.NATPostRules = resource("NATPostRules")
        self.NATRules = GroupedResources(self.NATPreRules, self.NATPostRules)
        self.QoSPreRules = resource("QoSPreRules")
        self.QoSPostRules = resource("QoSPostRules")
        self.QoSRules = GroupedResources(self.QoSPreRules, self.QoSPostRules)
        self.PolicyBasedForwardingPreRules = resource("PolicyBasedForwardingPreRules")
        self.PolicyBasedForwardingPostRules = resource("PolicyBasedForwardingPostRules")
        self.PolicyBasedForwardingRules = GroupedResources(
            self.PolicyBasedForwardingPreRules,
            self.PolicyBasedForwardingPostRules,
        )
        self.DecryptionPreRules = resource("DecryptionPreRules")
        self.DecryptionPostRules = resource("DecryptionPostRules")
        self.DecryptionRules = GroupedResources(
            self.DecryptionPreRules,
            self.DecryptionPostRules,
        )
        self.TunnelInspectionPreRules = resource("TunnelInspectionPreRules")
        self.TunnelInspectionPostRules = resource("TunnelInspectionPostRules")
        self.TunnelInspectionRules = GroupedResources(
            self.TunnelInspectionPreRules,
            self.TunnelInspectionPostRules,
        )
        self.ApplicationOverridePreRules = resource("ApplicationOverridePreRules")
        self.ApplicationOverridePostRules = resource("ApplicationOverridePostRules")
        self.ApplicationOverrideRules = GroupedResources(
            self.ApplicationOverridePreRules,
            self.ApplicationOverridePostRules,
        )
        self.AuthenticationPreRules = resource("AuthenticationPreRules")
        self.AuthenticationPostRules = resource("AuthenticationPostRules")
        self.AuthenticationRules = GroupedResources(
            self.AuthenticationPreRules,
            self.AuthenticationPostRules,
        )
        self.DoSPreRules = resource("DoSPreRules")
        self.DoSPostRules = resource("DoSPostRules")
        self.DoSRules = GroupedResources(self.DoSPreRules, self.DoSPostRules)
        self.SDWANPreRules = resource("SDWANPreRules")
        self.SDWANPostRules = resource("SDWANPostRules")
        self.SDWANRules = GroupedResources(self.SDWANPreRules, self.SDWANPostRules)


class PanoramaNetworkResourceType(PanoramaResourceType):
    """
    Represent the 'Network' subsection in the API.
    """

    DEFAULT_PARAMS: ClassVar = {
        "location": "template",
    }
    resource_type = "Network"

    def __init__(self, client, domain, version="v10.1"):
        resource_type = self.resource_type
        super().__init__(client, resource_type)

        def resource(name):
            return PanoramaResource(
                client,
                domain,
                resource_type,
                name,
                version=version,
                default_params=self.DEFAULT_PARAMS,
            )

        self.EthernetInterfaces = resource("EthernetInterfaces")
        self.AggregateEthernetInterfaces = resource("AggregateEthernetInterfaces")
        self.VLANInterfaces = resource("VLANInterfaces")
        self.LoopbackInterfaces = resource("LoopbackInterfaces")
        self.TunnelIntefaces = resource("TunnelIntefaces")
        self.SDWANInterfaces = resource("SDWANInterfaces")
        self.Zones = resource("Zones")
        self.VLANs = resource("VLANs")
        self.VirtualWires = resource("VirtualWires")
        self.VirtualRouters = resource("VirtualRouters")
        self.IPSecTunnels = resource("IPSecTunnels")
        self.GRETunnels = resource("GRETunnels")
        self.DHCPServers = resource("DHCPServers")
        self.DHCPRelays = resource("DHCPRelays")
        self.DNSProxies = resource("DNSProxies")
        self.GlobalProtectPortals = resource("GlobalProtectPortals")
        self.GlobalProtectGateways = resource("GlobalProtectGateways")
        self.GlobalProtectGatewayAgentTunnels = resource(
            "GlobalProtectGatewayAgentTunnels",
        )
        self.GlobalProtectGatewaySatelliteTunnels = resource(
            "GlobalProtectGatewaySatelliteTunnels",
        )
        self.GlobalProtectGatewayMDMServers = resource("GlobalProtectGatewayMDMServers")
        self.GlobalProtectClientlessApps = resource("GlobalProtectClientlessApps")
        self.GlobalProtectClientlessAppGroups = resource(
            "GlobalProtectClientlessAppGroups",
        )
        self.QoSInterfaces = resource("QoSInterfaces")
        self.LLDP = resource("LLDP")
        self.GlobalProtectIPSecCryptoNetworkProfiles = resource(
            "GlobalProtectIPSecCryptoNetworkProfiles",
        )
        self.IKEGatewayNetworkProfiles = resource("IKEGatewayNetworkProfiles")
        self.IKECryptoNetworkProfiles = resource("IKECryptoNetworkProfiles")
        self.MonitorNetworkProfiles = resource("MonitorNetworkProfiles")
        self.InterfaceManagementNetworkProfiles = resource(
            "InterfaceManagementNetworkProfiles",
        )
        self.ZoneProtectionNetworkProfiles = resource("ZoneProtectionNetworkProfiles")
        self.QoSNetworkProfiles = resource("QoSNetworkProfiles")
        self.LLDPNetworkProfiles = resource("LLDPNetworkProfiles")
        self.SDWANInterfaceProfiles = resource("SDWANInterfaceProfiles")


class PanoramaDevicesResourceType(PanoramaResourceType):
    """
    Represent the 'Devices' subsection in the API.
    """

    DEFAULT_PARAMS: ClassVar = {
        "location": "template",
    }
    resource_type = "Device"

    def __init__(self, client, domain, version="v10.1"):
        resource_type = self.resource_type
        super().__init__(client, resource_type)

        def resource(name):
            return PanoramaResource(
                client,
                domain,
                resource_type,
                name,
                version=version,
                default_params=self.DEFAULT_PARAMS,
            )

        self.VirtualSystems = resource("VirtualSystems")


__all__ = [
    "PanoramaDevicesResourceType",
    "PanoramaNetworkResourceType",
    "PanoramaObjectsResourceType",
    "PanoramaPanoramaResourceType",
    "PanoramaPoliciesResourceType",
]
