#!/usr/bin/env python3
"""
Network Analysis Module for Azure Resource Graph Client
Provides comprehensive network security, compliance, topology, and optimization analysis
"""

from typing import List, Dict, Any, Optional


class NetworkAnalysisQueries:
    """Network analysis related queries for Azure Resource Graph"""

    @staticmethod
    def get_network_security_query() -> str:
        """
        Query for network security compliance across NSGs, Public IPs, and Load Balancers

        Returns:
            KQL query string for network security analysis
        """
        return """
        Resources
        | where type in (
            'microsoft.network/networksecuritygroups',
            'microsoft.network/publicipaddresses',
            'microsoft.network/loadbalancers',
            'microsoft.network/applicationgateways',
            'microsoft.network/virtualnetworks'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            isnotempty(tags['application-name']), tags['application-name'],
            'Untagged/Orphaned'
        )
        | extend NetworkResourceType = case(
            type == 'microsoft.network/networksecuritygroups', 'Network Security Group',
            type == 'microsoft.network/publicipaddresses', 'Public IP Address',
            type == 'microsoft.network/loadbalancers', 'Load Balancer',
            type == 'microsoft.network/applicationgateways', 'Application Gateway',
            type == 'microsoft.network/virtualnetworks', 'Virtual Network',
            type
        )
        | extend SecurityFindings = case(
            type == 'microsoft.network/networksecuritygroups',
                // Check for overly permissive NSG rules
                case(
                    array_length(properties.securityRules) == 0, 'No custom rules defined',
                    'Custom rules present - Manual review needed'
                ),
            type == 'microsoft.network/publicipaddresses',
                // Check public IP configuration
                case(
                    tostring(properties.publicIPAllocationMethod) == 'Static' and isnotempty(properties.ipAddress), 
                        strcat('Static IP: ', tostring(properties.ipAddress)),
                    tostring(properties.publicIPAllocationMethod) == 'Dynamic', 'Dynamic IP allocation',
                    'IP allocation method unknown'
                ),
            type == 'microsoft.network/loadbalancers',
                // Check load balancer configuration
                case(
                    array_length(properties.frontendIPConfigurations) > 0, 'Has frontend IP configurations',
                    'No frontend IP configurations'
                ),
            type == 'microsoft.network/applicationgateways',
                // Check application gateway SSL settings
                case(
                    array_length(properties.sslCertificates) > 0, 'SSL certificates configured',
                    'No SSL certificates found'
                ),
            type == 'microsoft.network/virtualnetworks',
                // Check virtual network configuration
                case(
                    array_length(properties.subnets) > 0, 
                        strcat('Subnets: ', tostring(array_length(properties.subnets))),
                    'No subnets configured'
                ),
            'Unknown configuration'
        )
        | extend ComplianceRisk = case(
            type == 'microsoft.network/networksecuritygroups',
                // High risk if no rules or needs manual review
                case(
                    SecurityFindings contains 'No custom rules', 'High - No security rules',
                    SecurityFindings contains 'Manual review needed', 'Medium - Review required',
                    'Low'
                ),
            type == 'microsoft.network/publicipaddresses',
                // Medium risk for public IPs
                case(
                    tostring(properties.publicIPAllocationMethod) == 'Static', 'Medium - Static public IP',
                    'Low - Dynamic allocation'
                ),
            type == 'microsoft.network/loadbalancers',
                case(
                    SecurityFindings contains 'No frontend', 'High - Misconfigured',
                    'Low'
                ),
            type == 'microsoft.network/applicationgateways',
                case(
                    SecurityFindings contains 'No SSL certificates', 'High - No SSL/TLS',
                    'Low - SSL configured'
                ),
            type == 'microsoft.network/virtualnetworks',
                case(
                    SecurityFindings contains 'No subnets', 'Medium - No subnets',
                    'Low'
                ),
            'Unknown'
        )
        | extend DDoSProtection = case(
            type == 'microsoft.network/publicipaddresses',
                case(
                    tobool(properties.ddosSettings.ddosCustomPolicy.id) != false, 'Custom DDoS Policy',
                    tobool(properties.ddosSettings.protectionCoverage) == true, 'Standard DDoS Protection',
                    'Basic DDoS Protection'
                ),
            type == 'microsoft.network/virtualnetworks',
                case(
                    tobool(properties.enableDdosProtection) == true, 'DDoS Protection Enabled',
                    'DDoS Protection Disabled'
                ),
            'N/A'
        )
        | extend AdditionalDetails = case(
            type == 'microsoft.network/networksecuritygroups',
                strcat('Rules: ', tostring(array_length(properties.securityRules)), 
                       ' | Default Rules: ', tostring(array_length(properties.defaultSecurityRules))),
            type == 'microsoft.network/publicipaddresses',
                strcat('SKU: ', tostring(properties.sku.name), 
                       ' | DDoS: ', DDoSProtection,
                       ' | DNS: ', case(isnotempty(properties.dnsSettings.fqdn), tostring(properties.dnsSettings.fqdn), 'None')),
            type == 'microsoft.network/loadbalancers',
                strcat('SKU: ', tostring(sku.name),
                       ' | Frontend IPs: ', tostring(array_length(properties.frontendIPConfigurations)),
                       ' | Backend Pools: ', tostring(array_length(properties.backendAddressPools))),
            type == 'microsoft.network/applicationgateways',
                strcat('SKU: ', tostring(properties.sku.name),
                       ' | SSL Certs: ', tostring(array_length(properties.sslCertificates)),
                       ' | Listeners: ', tostring(array_length(properties.httpListeners))),
            type == 'microsoft.network/virtualnetworks',
                strcat('Address Space: ', tostring(properties.addressSpace.addressPrefixes[0]),
                       ' | DDoS: ', DDoSProtection,
                       ' | Subnets: ', tostring(array_length(properties.subnets))),
            ''
        )
        | project 
            Application,
            NetworkResource = name,
            NetworkResourceType,
            SecurityFindings,
            ComplianceRisk,
            ResourceGroup = resourceGroup,
            Location = location,
            AdditionalDetails,
            ResourceId = id
        | order by Application, ComplianceRisk desc, NetworkResourceType, NetworkResource
        """

    @staticmethod
    def get_nsg_detailed_query() -> str:
        """
        Detailed query specifically for Network Security Group rule analysis

        Returns:
            KQL query string for detailed NSG analysis
        """
        return """
        Resources
        | where type == 'microsoft.network/networksecuritygroups'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | mv-expand securityRule = properties.securityRules
        | extend 
            RuleName = tostring(securityRule.name),
            Access = tostring(securityRule.properties.access),
            Direction = tostring(securityRule.properties.direction),
            Priority = toint(securityRule.properties.priority),
            Protocol = tostring(securityRule.properties.protocol),
            SourceAddressPrefix = tostring(securityRule.properties.sourceAddressPrefix),
            DestinationAddressPrefix = tostring(securityRule.properties.destinationAddressPrefix),
            SourcePortRange = tostring(securityRule.properties.sourcePortRange),
            DestinationPortRange = tostring(securityRule.properties.destinationPortRange)
        | extend RiskLevel = case(
            Access == 'Allow' and Direction == 'Inbound' and SourceAddressPrefix == '*', 'High - Allow all inbound',
            Access == 'Allow' and Direction == 'Inbound' and SourceAddressPrefix == '0.0.0.0/0', 'High - Allow internet inbound',
            Access == 'Allow' and Direction == 'Inbound' and DestinationPortRange == '*', 'Medium - All ports allowed',
            Access == 'Allow' and Direction == 'Inbound' and (DestinationPortRange contains '22' or DestinationPortRange contains '3389'), 'Medium - Admin ports exposed',
            Access == 'Allow' and Direction == 'Inbound', 'Low - Specific inbound allow',
            'Info'
        )
        | project 
            Application,
            NSGName = name,
            RuleName,
            Access,
            Direction,
            Priority,
            Protocol,
            SourceAddressPrefix,
            DestinationAddressPrefix,
            SourcePortRange,
            DestinationPortRange,
            RiskLevel,
            ResourceGroup = resourceGroup,
            ResourceId = id
        | order by Application, NSGName, Priority
        """

    @staticmethod
    def get_certificate_analysis_query() -> str:
        """
        Enhanced query for certificate analysis across Application Gateways and Load Balancers

        Returns:
            KQL query string for certificate compliance analysis
        """
        return """
        Resources
        | where type in (
            'microsoft.network/applicationgateways',
            'microsoft.network/loadbalancers'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend ResourceType = case(
            type == 'microsoft.network/applicationgateways', 'Application Gateway',
            type == 'microsoft.network/loadbalancers', 'Load Balancer',
            type
        )
        | extend CertificateCount = case(
            type == 'microsoft.network/applicationgateways',
                array_length(properties.sslCertificates),
            type == 'microsoft.network/loadbalancers',
                // Load balancers don't directly store SSL certs, check for HTTPS listeners
                array_length(properties.loadBalancingRules),
            0
        )
        | extend SSLPolicyDetails = case(
            type == 'microsoft.network/applicationgateways',
                case(
                    isnotempty(properties.sslPolicy.policyType), 
                        strcat('Policy: ', tostring(properties.sslPolicy.policyType),
                               ' | Min Protocol: ', tostring(properties.sslPolicy.minProtocolVersion)),
                    'Default SSL Policy'
                ),
            type == 'microsoft.network/loadbalancers',
                'Check Load Balancing Rules',
            'N/A'
        )
        | extend ComplianceStatus = case(
            type == 'microsoft.network/applicationgateways',
                case(
                    CertificateCount == 0, 'Non-Compliant - No SSL Certificates',
                    isnotempty(properties.sslPolicy.minProtocolVersion) and 
                        tostring(properties.sslPolicy.minProtocolVersion) in ('TLSv1_2', 'TLSv1_3'), 'Compliant - Modern TLS',
                    isnotempty(properties.sslPolicy.minProtocolVersion), 'Partially Compliant - Legacy TLS',
                    'Review Required - Default Policy'
                ),
            type == 'microsoft.network/loadbalancers',
                case(
                    array_length(properties.loadBalancingRules) > 0, 'Review Required - Check Rules',
                    'Non-Compliant - No Rules'
                ),
            'Unknown'
        )
        | extend SecurityRisk = case(
            ComplianceStatus contains 'Non-Compliant', 'High',
            ComplianceStatus contains 'Legacy TLS', 'Medium',
            ComplianceStatus contains 'Review Required', 'Medium',
            'Low'
        )
        | extend ListenerDetails = case(
            type == 'microsoft.network/applicationgateways',
                strcat('HTTP Listeners: ', tostring(array_length(properties.httpListeners)),
                       ' | Backend Pools: ', tostring(array_length(properties.backendAddressPools))),
            type == 'microsoft.network/loadbalancers',
                strcat('LB Rules: ', tostring(array_length(properties.loadBalancingRules)),
                       ' | Probes: ', tostring(array_length(properties.probes))),
            ''
        )
        | project
            Application,
            ResourceName = name,
            ResourceType,
            CertificateCount,
            SSLPolicyDetails,
            ComplianceStatus,
            SecurityRisk,
            ListenerDetails,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, SecurityRisk desc, ResourceType, ResourceName
        """

    @staticmethod
    def get_network_topology_query() -> str:
        """
        Query for network topology analysis including VNet peering and configuration

        Returns:
            KQL query string for network topology analysis
        """
        return """
        Resources
        | where type in (
            'microsoft.network/virtualnetworks',
            'microsoft.network/virtualnetworkpeerings'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend TopologyType = case(
            type == 'microsoft.network/virtualnetworks', 'Virtual Network',
            type == 'microsoft.network/virtualnetworkpeerings', 'VNet Peering',
            type
        )
        | extend NetworkConfiguration = case(
            type == 'microsoft.network/virtualnetworks',
                strcat('Address Space: ', tostring(properties.addressSpace.addressPrefixes[0]),
                       ' | Subnets: ', tostring(array_length(properties.subnets)),
                       ' | DNS Servers: ', case(
                           isnotempty(properties.dhcpOptions.dnsServers), 
                           tostring(array_length(properties.dhcpOptions.dnsServers)), 
                           'Default')),
            type == 'microsoft.network/virtualnetworkpeerings',
                strcat('Remote VNet: ', tostring(properties.remoteVirtualNetwork.id),
                       ' | State: ', tostring(properties.peeringState),
                       ' | Gateway Transit: ', tostring(properties.allowGatewayTransit)),
            'Unknown'
        )
        | extend ConfigurationRisk = case(
            type == 'microsoft.network/virtualnetworks',
                case(
                    array_length(properties.subnets) == 0, 'High - No subnets configured',
                    tobool(properties.enableDdosProtection) != true, 'Medium - No DDoS protection',
                    isempty(properties.dhcpOptions.dnsServers), 'Low - Using default DNS',
                    'Low'
                ),
            type == 'microsoft.network/virtualnetworkpeerings',
                case(
                    tostring(properties.peeringState) != 'Connected', 'High - Peering not connected',
                    tobool(properties.allowForwardedTraffic) == true, 'Medium - Forwarded traffic allowed',
                    'Low'
                ),
            'Unknown'
        )
        | extend SecurityImplications = case(
            type == 'microsoft.network/virtualnetworks',
                case(
                    tobool(properties.enableDdosProtection) != true, 'Vulnerable to DDoS attacks',
                    isempty(properties.dhcpOptions.dnsServers), 'Using default Azure DNS',
                    'Standard configuration'
                ),
            type == 'microsoft.network/virtualnetworkpeerings',
                case(
                    tobool(properties.allowForwardedTraffic) == true, 'Traffic forwarding enabled',
                    tobool(properties.allowGatewayTransit) == true, 'Gateway transit enabled',
                    'Standard peering'
                ),
            'Review required'
        )
        | project
            Application,
            NetworkResource = name,
            TopologyType,
            NetworkConfiguration,
            ConfigurationRisk,
            SecurityImplications,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, ConfigurationRisk desc, TopologyType, NetworkResource
        """

    @staticmethod
    def get_resource_optimization_query() -> str:
        """
        Query for network resource optimization including orphaned and unused resources

        Returns:
            KQL query string for network resource optimization analysis
        """
        return """
        Resources
        | where type in (
            'microsoft.network/publicipaddresses',
            'microsoft.network/networkinterfaces',
            'microsoft.network/loadbalancers',
            'microsoft.network/applicationgateways'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend OptimizationType = case(
            type == 'microsoft.network/publicipaddresses', 'Public IP Address',
            type == 'microsoft.network/networkinterfaces', 'Network Interface',
            type == 'microsoft.network/loadbalancers', 'Load Balancer',
            type == 'microsoft.network/applicationgateways', 'Application Gateway',
            type
        )
        | extend UtilizationStatus = case(
            type == 'microsoft.network/publicipaddresses',
                case(
                    isempty(properties.ipConfiguration.id), 'Unused - No IP Configuration',
                    tostring(properties.publicIPAllocationMethod) == 'Static' and isempty(properties.ipAddress), 'Potentially Unused',
                    'In Use'
                ),
            type == 'microsoft.network/networkinterfaces',
                case(
                    isempty(properties.virtualMachine.id), 'Unused - No VM Attached',
                    array_length(properties.ipConfigurations) == 0, 'Misconfigured - No IP Config',
                    'In Use'
                ),
            type == 'microsoft.network/loadbalancers',
                case(
                    array_length(properties.backendAddressPools) == 0, 'Unused - No Backend Pools',
                    array_length(properties.loadBalancingRules) == 0, 'Misconfigured - No Rules',
                    'In Use'
                ),
            type == 'microsoft.network/applicationgateways',
                case(
                    array_length(properties.backendAddressPools) == 0, 'Unused - No Backend Pools',
                    array_length(properties.httpListeners) == 0, 'Misconfigured - No Listeners',
                    'In Use'
                ),
            'Unknown'
        )
        | extend CostOptimizationPotential = case(
            UtilizationStatus contains 'Unused', 'High - Consider deletion',
            UtilizationStatus contains 'Misconfigured', 'Medium - Review configuration',
            UtilizationStatus contains 'Potentially Unused', 'Medium - Verify usage',
            'Low - Active resource'
        )
        | extend ResourceDetails = case(
            type == 'microsoft.network/publicipaddresses',
                strcat('SKU: ', tostring(properties.sku.name),
                       ' | Allocation: ', tostring(properties.publicIPAllocationMethod),
                       ' | IP: ', case(isnotempty(properties.ipAddress), tostring(properties.ipAddress), 'Not Assigned')),
            type == 'microsoft.network/networkinterfaces',
                strcat('VM: ', case(isnotempty(properties.virtualMachine.id), 'Attached', 'None'),
                       ' | IPs: ', tostring(array_length(properties.ipConfigurations))),
            type == 'microsoft.network/loadbalancers',
                strcat('SKU: ', tostring(sku.name),
                       ' | Backend Pools: ', tostring(array_length(properties.backendAddressPools)),
                       ' | Rules: ', tostring(array_length(properties.loadBalancingRules))),
            type == 'microsoft.network/applicationgateways',
                strcat('SKU: ', tostring(properties.sku.name),
                       ' | Backend Pools: ', tostring(array_length(properties.backendAddressPools)),
                       ' | Listeners: ', tostring(array_length(properties.httpListeners))),
            ''
        )
        | project
            Application,
            ResourceName = name,
            OptimizationType,
            UtilizationStatus,
            CostOptimizationPotential,
            ResourceDetails,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, CostOptimizationPotential desc, OptimizationType, ResourceName
        """

    @staticmethod
    def get_network_compliance_summary_query() -> str:
        """
        Query for network security compliance summary by application

        Returns:
            KQL query string for compliance summary
        """
        return """
        Resources
        | where type in (
            'microsoft.network/networksecuritygroups',
            'microsoft.network/publicipaddresses',
            'microsoft.network/applicationgateways'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend HasSecurityIssue = case(
            type == 'microsoft.network/networksecuritygroups', 
                array_length(properties.securityRules) == 0,
            type == 'microsoft.network/publicipaddresses', 
                (tostring(properties.publicIPAllocationMethod) == 'Static' and tobool(properties.ddosSettings.protectionCoverage) != true),
            type == 'microsoft.network/applicationgateways', 
                array_length(properties.sslCertificates) == 0,
            false
        )
        | summarize 
            TotalNetworkResources = count(),
            NSGCount = countif(type == 'microsoft.network/networksecuritygroups'),
            PublicIPCount = countif(type == 'microsoft.network/publicipaddresses'),
            AppGatewayCount = countif(type == 'microsoft.network/applicationgateways'),
            ResourcesWithIssues = countif(HasSecurityIssue == true),
            SecurityScore = round((count() - countif(HasSecurityIssue == true)) * 100.0 / count(), 1)
        by Application
        | extend SecurityStatus = case(
            SecurityScore >= 90, 'Excellent',
            SecurityScore >= 75, 'Good',
            SecurityScore >= 50, 'Needs Improvement',
            'Critical Issues'
        )
        | project 
            Application,
            TotalNetworkResources,
            NSGCount,
            PublicIPCount,
            AppGatewayCount,
            ResourcesWithIssues,
            SecurityScore,
            SecurityStatus
        | order by Application
        """
