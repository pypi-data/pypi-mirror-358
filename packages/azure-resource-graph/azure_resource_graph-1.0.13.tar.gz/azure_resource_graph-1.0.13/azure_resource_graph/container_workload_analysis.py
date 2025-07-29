#!/usr/bin/env python3
"""
Container & Modern Workloads Analysis Module for Azure Resource Graph Client
Provides comprehensive analysis for AKS clusters, Container Registries, and App Services
"""

from typing import List, Dict, Any, Optional


class ContainerWorkloadsAnalysisQueries:
    """Container & Modern Workloads analysis related queries for Azure Resource Graph"""

    @staticmethod
    def get_aks_cluster_security_query() -> str:
        """
        Query for AKS cluster security analysis including RBAC, network policies, and configurations

        Returns:
            KQL query string for AKS cluster security analysis
        """
        return """
        Resources
        | where type == 'microsoft.containerservice/managedclusters'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            isnotempty(tags['application-name']), tags['application-name'],
            'Untagged/Orphaned'
        )
        | extend ClusterVersion = tostring(properties.kubernetesVersion)
        | extend NodeResourceGroup = tostring(properties.nodeResourceGroup)
        | extend DNSPrefix = tostring(properties.dnsPrefix)
        | extend FQDN = tostring(properties.fqdn)
        | extend PrivateCluster = tobool(properties.apiServerAccessProfile.enablePrivateCluster)
        | extend NetworkPlugin = tostring(properties.networkProfile.networkPlugin)
        | extend NetworkPolicy = tostring(properties.networkProfile.networkPolicy)
        | extend ServiceCIDR = tostring(properties.networkProfile.serviceCidr)
        | extend PodCIDR = tostring(properties.networkProfile.podCidr)
        | extend LoadBalancerSKU = tostring(properties.networkProfile.loadBalancerSku)
        | extend RBACEnabled = tobool(properties.enableRBAC)
        | extend AADEnabled = case(
            isnotempty(properties.aadProfile.managed), tobool(properties.aadProfile.managed),
            false
        )
        | extend AdminGroupObjectIDs = array_length(properties.aadProfile.adminGroupObjectIDs)
        | extend AuthorizedIPRanges = array_length(properties.apiServerAccessProfile.authorizedIPRanges)
        | extend DiskEncryptionSetID = case(
            isnotempty(properties.diskEncryptionSetID), 'Customer Managed Key',
            'Platform Managed Key'
        )
        | extend AutoUpgradeChannel = tostring(properties.autoUpgradeProfile.upgradeChannel)
        | extend SecurityProfile = case(
            isnotempty(properties.securityProfile.defender.logAnalyticsWorkspaceResourceId), 'Defender Enabled',
            'Basic Security'
        )
        | extend ClusterCompliance = case(
            RBACEnabled != true, 'Non-Compliant - RBAC Disabled',
            AADEnabled != true, 'Non-Compliant - No Azure AD Integration',
            PrivateCluster != true and AuthorizedIPRanges == 0, 'Non-Compliant - Public API Server',
            NetworkPolicy == '', 'Partially Compliant - No Network Policy',
            'Compliant - Security Configured'
        )
        | extend SecurityRisk = case(
            RBACEnabled != true, 'High - No RBAC protection',
            AADEnabled != true, 'High - No centralized authentication',
            PrivateCluster != true and AuthorizedIPRanges == 0, 'High - Public API server access',
            NetworkPolicy == '' or NetworkPolicy == 'none', 'Medium - No network segmentation',
            ClusterVersion contains '1.26' or ClusterVersion contains '1.25', 'Medium - Older Kubernetes version',
            'Low - Secure configuration'
        )
        | extend SecurityFindings = case(
            RBACEnabled != true, 'Role-based access control disabled',
            AADEnabled != true, 'Azure AD integration not configured',
            PrivateCluster != true, 'API server publicly accessible',
            NetworkPolicy == '', 'Network policies not implemented',
            'Standard security configuration'
        )
        | extend ClusterDetails = strcat(
            'K8s: ', ClusterVersion,
            ' | Network: ', NetworkPlugin,
            ' | Policy: ', case(NetworkPolicy != '', NetworkPlugin, 'None'),
            ' | RBAC: ', case(RBACEnabled == true, 'Enabled', 'Disabled'),
            ' | AAD: ', case(AADEnabled == true, 'Enabled', 'Disabled')
        )
        | project
            Application,
            ClusterName = name,
            ClusterVersion,
            NetworkConfiguration = strcat('Plugin: ', NetworkPlugin, ' | Policy: ', NetworkPolicy),
            RBACConfiguration = case(
                RBACEnabled == true and AADEnabled == true, 'RBAC + Azure AD',
                RBACEnabled == true, 'RBAC Only',
                'No RBAC'
            ),
            APIServerAccess = case(
                PrivateCluster == true, 'Private Endpoint',
                AuthorizedIPRanges > 0, strcat('Restricted (', tostring(AuthorizedIPRanges), ' ranges)'),
                'Public Access'
            ),
            SecurityFindings,
            SecurityRisk,
            ClusterCompliance,
            ClusterDetails,
            NodePoolCount = array_length(properties.agentPoolProfiles),
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, SecurityRisk desc, ClusterName
        """

    @staticmethod
    def get_aks_node_pool_analysis_query() -> str:
        """
        Query for detailed AKS node pool analysis including VM sizes, scaling, and security

        Returns:
            KQL query string for AKS node pool analysis
        """
        return """
        Resources
        | where type == 'microsoft.containerservice/managedclusters'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | where array_length(properties.agentPoolProfiles) > 0
        | mv-expand nodePool = properties.agentPoolProfiles
        | extend NodePoolName = tostring(nodePool.name)
        | extend NodePoolType = tostring(nodePool.type)
        | extend VMSize = tostring(nodePool.vmSize)
        | extend VMSizeCategory = case(
            VMSize startswith 'Standard_A', 'Basic/Legacy',
            VMSize startswith 'Standard_B', 'Burstable',
            VMSize startswith 'Standard_D', 'General Purpose',
            VMSize startswith 'Standard_E', 'Memory Optimized',
            VMSize startswith 'Standard_F', 'Compute Optimized',
            'Standard'
        )
        | extend NodeCount = toint(nodePool.count)
        | extend MinCount = case(
            isnotempty(nodePool.minCount), toint(nodePool.minCount),
            0
        )
        | extend MaxCount = case(
            isnotempty(nodePool.maxCount), toint(nodePool.maxCount), 
            NodeCount
        )
        | extend EnableAutoScaling = case(
            isnotempty(nodePool.enableAutoScaling), tobool(nodePool.enableAutoScaling),
            false
        )
        | extend NodePoolMode = case(
            isnotempty(nodePool.mode), tostring(nodePool.mode),
            'User'
        )
        | extend OSType = case(
            isnotempty(nodePool.osType), tostring(nodePool.osType),
            'Linux'
        )
        | extend OSDiskSizeGB = case(
            isnotempty(nodePool.osDiskSizeGB), toint(nodePool.osDiskSizeGB),
            30
        )
        | extend OSDiskType = case(
            isnotempty(nodePool.osDiskType), tostring(nodePool.osDiskType),
            'Managed'
        )
        | extend EnableEncryptionAtHost = case(
            isnotempty(nodePool.enableEncryptionAtHost), tobool(nodePool.enableEncryptionAtHost),
            false
        )
        | extend EnableFIPS = case(
            isnotempty(nodePool.enableFIPS), tobool(nodePool.enableFIPS),
            false
        )
        | extend NodeImageVersion = case(
            isnotempty(nodePool.nodeImageVersion), tostring(nodePool.nodeImageVersion),
            'Not Available'
        )
        | extend NodeTaints = case(
            isnotempty(nodePool.nodeTaints), array_length(nodePool.nodeTaints),
            0
        )
        | extend SpotMaxPrice = case(
            isnotempty(nodePool.spotMaxPrice), tostring(nodePool.spotMaxPrice),
            'Not Spot Instance'
        )
        | extend ScalingConfiguration = case(
            EnableAutoScaling == true, strcat('Auto: ', tostring(MinCount), '-', tostring(MaxCount)),
            strcat('Manual: ', tostring(NodeCount))
        )
        | extend SecurityConfiguration = case(
            EnableEncryptionAtHost == true and EnableFIPS == true, 'Enhanced Security (Encryption + FIPS)',
            EnableEncryptionAtHost == true, 'Host Encryption Enabled',
            EnableFIPS == true, 'FIPS Enabled',
            'Standard Security'
        )
        | extend OptimizationPotential = case(
            VMSizeCategory == 'Basic/Legacy', 'High - Upgrade to modern VM sizes',
            EnableAutoScaling != true and NodePoolMode == 'User', 'Medium - Enable auto-scaling',
            NodeCount > 10 and MaxCount == NodeCount, 'Medium - Consider auto-scaling limits',
            SpotMaxPrice != 'Not Spot Instance' and NodePoolMode == 'System', 'High - Spot VMs not recommended for system pools',
            'Low - Configuration appears optimal'
        )
        | extend NodePoolRisk = case(
            VMSizeCategory == 'Basic/Legacy', 'Medium - Legacy VM sizes',
            EnableEncryptionAtHost != true, 'Medium - No host encryption',
            SpotMaxPrice != 'Not Spot Instance' and NodePoolMode == 'System', 'High - System pool on Spot VMs',
            NodeCount == 1 and NodePoolMode == 'System', 'High - Single node system pool',
            'Low - Standard configuration'
        )
        | extend NodePoolDetails = strcat(
            'VM: ', VMSize,
            ' | Count: ', tostring(NodeCount),
            ' | Mode: ', NodePoolMode,
            ' | OS: ', OSType,
            ' | Disk: ', tostring(OSDiskSizeGB), 'GB'
        )
        | project
            Application,
            ClusterName = name,
            NodePoolName,
            NodePoolType,
            VMSize,
            VMSizeCategory,
            ScalingConfiguration,
            SecurityConfiguration,
            OptimizationPotential,
            NodePoolRisk,
            NodePoolDetails,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = strcat(id, '/agentPools/', NodePoolName)
        | order by Application, ClusterName, NodePoolRisk desc, NodePoolName
        """

    @staticmethod
    def get_container_registry_security_query() -> str:
        """
        Query for Container Registry security analysis including access controls and scanning

        Returns:
            KQL query string for Container Registry security analysis
        """
        return """
        Resources
        | where type == 'microsoft.containerregistry/registries'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend RegistrySKU = tostring(sku.name)
        | extend AdminUserEnabled = tobool(properties.adminUserEnabled)
        | extend PublicNetworkAccess = tostring(properties.publicNetworkAccess)
        | extend NetworkRuleSetDefaultAction = tostring(properties.networkRuleSet.defaultAction)
        | extend IPRulesCount = array_length(properties.networkRuleSet.ipRules)
        | extend VirtualNetworkRulesCount = array_length(properties.networkRuleSet.virtualNetworkRules)
        | extend PrivateEndpointConnections = array_length(properties.privateEndpointConnections)
        | extend ZoneRedundancy = case(
            tostring(properties.zoneRedundancy) == 'Enabled', 'Zone Redundant',
            'Single Zone'
        )
        | extend DataEndpointEnabled = tobool(properties.dataEndpointEnabled)
        | extend PoliciesRetentionEnabled = case(
            isnotempty(properties.policies.retentionPolicy.status), 
            tostring(properties.policies.retentionPolicy.status),
            'Not Configured'
        )
        | extend PoliciesTrustEnabled = case(
            isnotempty(properties.policies.trustPolicy.status),
            tostring(properties.policies.trustPolicy.status),
            'Not Configured'
        )
        | extend QuarantineEnabled = case(
            isnotempty(properties.policies.quarantinePolicy.status),
            tostring(properties.policies.quarantinePolicy.status),
            'Not Configured'
        )
        | extend NetworkSecurity = case(
            PublicNetworkAccess == 'Disabled' and PrivateEndpointConnections > 0, 'Private Access Only',
            PublicNetworkAccess == 'Enabled' and NetworkRuleSetDefaultAction == 'Deny' and (IPRulesCount > 0 or VirtualNetworkRulesCount > 0), 'Restricted Public Access',
            PublicNetworkAccess == 'Enabled' and NetworkRuleSetDefaultAction == 'Allow', 'Unrestricted Public Access',
            'Unknown Configuration'
        )
        | extend SecurityPolicies = case(
            PoliciesTrustEnabled == 'enabled' and QuarantineEnabled == 'enabled', 'Enhanced Security (Trust + Quarantine)',
            PoliciesTrustEnabled == 'enabled', 'Content Trust Enabled',
            QuarantineEnabled == 'enabled', 'Quarantine Enabled',
            'Basic Security'
        )
        | extend AccessControl = case(
            AdminUserEnabled == true, 'Admin User + RBAC',
            'RBAC Only'
        )
        | extend SecurityRisk = case(
            NetworkSecurity == 'Unrestricted Public Access', 'High - Public access without restrictions',
            AdminUserEnabled == true, 'High - Admin user enabled',
            RegistrySKU == 'Basic' and NetworkSecurity != 'Private Access Only', 'Medium - Basic SKU with public access',
            PoliciesTrustEnabled != 'enabled' and RegistrySKU != 'Basic', 'Medium - No content trust policy',
            'Low - Secure configuration'
        )
        | extend ComplianceStatus = case(
            SecurityRisk contains 'High', 'Non-Compliant',
            SecurityRisk contains 'Medium', 'Partially Compliant',
            'Compliant'
        )
        | extend SecurityFindings = case(
            AdminUserEnabled == true, 'Admin user account enabled',
            NetworkSecurity == 'Unrestricted Public Access', 'Registry publicly accessible',
            PoliciesTrustEnabled != 'enabled', 'Content trust not configured',
            QuarantineEnabled != 'enabled', 'Quarantine policy not enabled',
            'Standard security configuration'
        )
        | extend RegistryDetails = strcat(
            'SKU: ', RegistrySKU,
            ' | Network: ', case(
                PublicNetworkAccess == 'Disabled', 'Private',
                NetworkRuleSetDefaultAction == 'Deny', 'Restricted',
                'Public'
            ),
            ' | Policies: ', case(
                PoliciesTrustEnabled == 'enabled', 'Trust',
                'Basic'
            )
        )
        | project
            Application,
            RegistryName = name,
            RegistrySKU,
            NetworkSecurity,
            AccessControl,
            SecurityPolicies,
            SecurityFindings,
            SecurityRisk,
            ComplianceStatus,
            RegistryDetails,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, SecurityRisk desc, RegistryName
        """

    @staticmethod
    def get_app_service_security_query() -> str:
        """
        Query for App Service security analysis including TLS, authentication, and configurations

        Returns:
            KQL query string for App Service security analysis
        """
        return """
        Resources
        | where type == 'microsoft.web/sites'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend AppServiceKind = tostring(kind)
        | extend AppServiceState = tostring(properties.state)
        | extend DefaultHostName = tostring(properties.defaultHostName)
        | extend HTTPSOnly = tobool(properties.httpsOnly)
        | extend FTPSState = tostring(properties.siteConfig.ftpsState)
        | extend MinTLSVersion = tostring(properties.siteConfig.minTlsVersion)
        | extend HTTP20Enabled = tobool(properties.siteConfig.http20Enabled)
        | extend ClientAffinityEnabled = tobool(properties.clientAffinityEnabled)
        | extend PublicNetworkAccess = case(
            isnotempty(tostring(properties.publicNetworkAccess)), 
            tostring(properties.publicNetworkAccess),
            'Enabled'
        )
        | extend VnetRouteAllEnabled = tobool(properties.vnetRouteAllEnabled)
        | extend PrivateEndpointConnections = array_length(properties.privateEndpointConnections)
        | extend IPSecurityRestrictions = array_length(properties.siteConfig.ipSecurityRestrictions)
        | extend ScmIPSecurityRestrictions = array_length(properties.siteConfig.scmIpSecurityRestrictions)
        | extend AuthEnabled = case(
            isnotempty(properties.siteConfig.authSettings.enabled),
            tobool(properties.siteConfig.authSettings.enabled),
            false
        )
        | extend AuthProvider = case(
            AuthEnabled == true and isnotempty(properties.siteConfig.authSettings.defaultProvider),
            tostring(properties.siteConfig.authSettings.defaultProvider),
            'Not Configured'
        )
        | extend ManagedServiceIdentity = case(
            isnotempty(identity.type) and tostring(identity.type) != 'None', 
            tostring(identity.type),
            'None'
        )
        | extend CustomDomainCount = array_length(properties.hostNames) - 1  // Subtract default hostname
        | extend SSLBindings = case(
            isnotempty(properties.hostNameSslStates),
            array_length(properties.hostNameSslStates),
            0
        )
        | extend TLSConfiguration = case(
            HTTPSOnly == true and MinTLSVersion == '1.2', 'HTTPS Only + TLS 1.2',
            HTTPSOnly == true and MinTLSVersion == '1.1', 'HTTPS Only + TLS 1.1 (Legacy)',
            HTTPSOnly == true and MinTLSVersion == '1.0', 'HTTPS Only + TLS 1.0 (Deprecated)',
            HTTPSOnly == true, 'HTTPS Only + Default TLS',
            'HTTP + HTTPS Allowed'
        )
        | extend NetworkSecurity = case(
            PublicNetworkAccess == 'Disabled' and PrivateEndpointConnections > 0, 'Private Access Only',
            IPSecurityRestrictions > 1, strcat('IP Restricted (', tostring(IPSecurityRestrictions), ' rules)'),  // >1 because default allow rule
            'Public Access'
        )
        | extend AuthenticationMethod = case(
            AuthEnabled == true, strcat('App Service Auth (', AuthProvider, ')'),
            ManagedServiceIdentity != 'None', strcat('Managed Identity (', ManagedServiceIdentity, ')'),
            'No Centralized Auth'
        )
        | extend SecurityRisk = case(
            HTTPSOnly != true, 'High - HTTP traffic allowed',
            MinTLSVersion == '1.0', 'High - TLS 1.0 enabled (deprecated)',
            MinTLSVersion == '1.1', 'Medium - TLS 1.1 enabled (legacy)',
            FTPSState == 'AllAllowed', 'Medium - Insecure FTP allowed',
            AuthEnabled != true and NetworkSecurity == 'Public Access', 'Medium - No authentication on public app',
            'Low - Secure configuration'
        )
        | extend ComplianceStatus = case(
            SecurityRisk contains 'High', 'Non-Compliant',
            SecurityRisk contains 'Medium', 'Partially Compliant',
            'Compliant'
        )
        | extend SecurityFindings = case(
            HTTPSOnly != true, 'HTTP traffic permitted',
            MinTLSVersion in ('1.0', '1.1'), strcat('Legacy TLS version: ', MinTLSVersion),
            FTPSState == 'AllAllowed', 'Insecure FTP access enabled',
            AuthEnabled != true, 'No App Service authentication configured',
            'Standard security configuration'
        )
        | extend AppServiceDetails = strcat(
            'Kind: ', AppServiceKind,
            ' | TLS: ', case(HTTPSOnly == true, MinTLSVersion, 'HTTP+HTTPS'),
            ' | Auth: ', case(AuthEnabled == true, AuthProvider, 'None'),
            ' | Identity: ', ManagedServiceIdentity
        )
        | project
            Application,
            AppServiceName = name,
            AppServiceKind,
            TLSConfiguration,
            NetworkSecurity,
            AuthenticationMethod,
            SecurityFindings,
            SecurityRisk,
            ComplianceStatus,
            AppServiceDetails,
            CustomDomainCount,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, SecurityRisk desc, AppServiceName
        """

    @staticmethod
    def get_app_service_deployment_slots_query() -> str:
        """
        Query for App Service deployment slots analysis

        Returns:
            KQL query string for deployment slots analysis
        """
        return """
        Resources
        | where type == 'microsoft.web/sites/slots'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend ParentAppService = tostring(split(id, '/slots/')[0])
        | extend SlotName = tostring(split(id, '/slots/')[1])
        | extend SlotState = tostring(properties.state)
        | extend HTTPSOnly = tobool(properties.httpsOnly)
        | extend MinTLSVersion = tostring(properties.siteConfig.minTlsVersion)
        | extend SlotTrafficPercentage = case(
            isnotempty(properties.trafficManagerHostNames),
            'Traffic Manager Configured',
            'Manual Deployment'
        )
        | extend SlotConfiguration = case(
            HTTPSOnly == true and MinTLSVersion == '1.2', 'Secure Configuration',
            HTTPSOnly == true, 'HTTPS Enabled',
            'Insecure Configuration'
        )
        | extend SlotRisk = case(
            HTTPSOnly != true, 'High - HTTP allowed in slot',
            MinTLSVersion != '1.2', 'Medium - Legacy TLS in slot',
            'Low - Secure slot configuration'
        )
        | extend SlotDetails = strcat(
            'State: ', SlotState,
            ' | HTTPS: ', case(HTTPSOnly == true, 'Required', 'Optional'),
            ' | TLS: ', MinTLSVersion
        )
        | project
            Application,
            AppServiceName = tostring(split(split(id, '/')[8], '/')[0]),
            SlotName,
            SlotState,
            SlotConfiguration,
            SlotRisk,
            SlotDetails,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, AppServiceName, SlotRisk desc, SlotName
        """

    @staticmethod
    def get_container_workloads_compliance_summary_query() -> str:
        """
        Query for Container & Modern Workloads compliance summary by application

        Returns:
            KQL query string for compliance summary
        """
        return """
        // AKS Clusters Analysis
        Resources
        | where type == 'microsoft.containerservice/managedclusters'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend RBACEnabled = tobool(properties.enableRBAC)
        | extend AADEnabled = case(
            isnotempty(properties.aadProfile.managed), tobool(properties.aadProfile.managed),
            false
        )
        | extend PrivateCluster = tobool(properties.apiServerAccessProfile.enablePrivateCluster)
        | extend NetworkPolicy = tostring(properties.networkProfile.networkPolicy)
        | extend HasSecurityIssue = not(RBACEnabled and AADEnabled and (PrivateCluster or array_length(properties.apiServerAccessProfile.authorizedIPRanges) > 0))
        | summarize 
            TotalAKSClusters = count(),
            SecureAKSClusters = countif(HasSecurityIssue == false),
            AKSClustersWithIssues = countif(HasSecurityIssue == true)
        by Application
        | join kind=fullouter (
            // Container Registries Analysis
            Resources
            | where type == 'microsoft.containerregistry/registries'
            | extend Application = case(
                isnotempty(tags.Application), tags.Application,
                isnotempty(tags.app), tags.app,
                'Untagged/Orphaned'
            )
            | extend AdminUserEnabled = tobool(properties.adminUserEnabled)
            | extend PublicNetworkAccess = tostring(properties.publicNetworkAccess)
            | extend NetworkRuleSetDefaultAction = tostring(properties.networkRuleSet.defaultAction)
            | extend HasSecurityIssue = (AdminUserEnabled == true or 
                                       (PublicNetworkAccess == 'Enabled' and NetworkRuleSetDefaultAction == 'Allow'))
            | summarize 
                TotalContainerRegistries = count(),
                SecureContainerRegistries = countif(HasSecurityIssue == false),
                ContainerRegistriesWithIssues = countif(HasSecurityIssue == true)
            by Application
        ) on Application
        | join kind=fullouter (
            // App Services Analysis
            Resources
            | where type == 'microsoft.web/sites'
            | extend Application = case(
                isnotempty(tags.Application), tags.Application,
                isnotempty(tags.app), tags.app,
                'Untagged/Orphaned'
            )
            | extend HTTPSOnly = tobool(properties.httpsOnly)
            | extend MinTLSVersion = tostring(properties.siteConfig.minTlsVersion)
            | extend HasSecurityIssue = (HTTPSOnly != true or MinTLSVersion in ('1.0', '1.1'))
            | summarize 
                TotalAppServices = count(),
                SecureAppServices = countif(HasSecurityIssue == false),
                AppServicesWithIssues = countif(HasSecurityIssue == true)
            by Application
        ) on Application
        | extend Application = coalesce(Application, Application1, Application2)
        | extend TotalAKSClusters = coalesce(TotalAKSClusters, 0)
        | extend SecureAKSClusters = coalesce(SecureAKSClusters, 0)
        | extend AKSClustersWithIssues = coalesce(AKSClustersWithIssues, 0)
        | extend TotalContainerRegistries = coalesce(TotalContainerRegistries, 0)
        | extend SecureContainerRegistries = coalesce(SecureContainerRegistries, 0)
        | extend ContainerRegistriesWithIssues = coalesce(ContainerRegistriesWithIssues, 0)
        | extend TotalAppServices = coalesce(TotalAppServices, 0)
        | extend SecureAppServices = coalesce(SecureAppServices, 0)
        | extend AppServicesWithIssues = coalesce(AppServicesWithIssues, 0)
        | extend TotalContainerWorkloads = TotalAKSClusters + TotalContainerRegistries + TotalAppServices
        | extend SecureContainerWorkloads = SecureAKSClusters + SecureContainerRegistries + SecureAppServices
        | extend ContainerWorkloadsWithIssues = AKSClustersWithIssues + ContainerRegistriesWithIssues + AppServicesWithIssues
        | extend ContainerWorkloadsComplianceScore = case(
            TotalContainerWorkloads == 0, 100.0,
            round((SecureContainerWorkloads * 100.0 / TotalContainerWorkloads), 1)
        )
        | extend ContainerWorkloadsComplianceStatus = case(
            ContainerWorkloadsComplianceScore >= 95, 'Excellent',
            ContainerWorkloadsComplianceScore >= 85, 'Good',
            ContainerWorkloadsComplianceScore >= 70, 'Acceptable',
            ContainerWorkloadsComplianceScore >= 50, 'Needs Improvement',
            'Critical Issues'
        )
        | project 
            Application,
            TotalContainerWorkloads,
            TotalAKSClusters,
            SecureAKSClusters,
            TotalContainerRegistries,
            SecureContainerRegistries,
            TotalAppServices,
            SecureAppServices,
            ContainerWorkloadsWithIssues,
            ContainerWorkloadsComplianceScore,
            ContainerWorkloadsComplianceStatus
        | where Application != ""
        | order by Application
        """
