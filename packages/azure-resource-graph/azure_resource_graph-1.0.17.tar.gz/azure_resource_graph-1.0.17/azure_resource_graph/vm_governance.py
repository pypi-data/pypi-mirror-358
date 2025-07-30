#!/usr/bin/env python3
"""
Improved VM Governance Analysis with better error handling and performance
"""


class VMGovernanceQueries:
    """Optimized VM governance queries that avoid problematic properties"""

    @staticmethod
    def get_vm_security_query() -> str:
        """
        Optimized VM security query that handles missing properties gracefully
        and performs better with large result sets
        """
        return """
        Resources
        | where type == 'microsoft.compute/virtualmachines'
        | extend Application = coalesce(
            tags.Application, 
            tags.app, 
            tags['application-name'], 
            'Untagged/Orphaned'
        )
        | extend OSType = case(
            tostring(properties.storageProfile.osDisk.osType) != '', tostring(properties.storageProfile.osDisk.osType),
            properties.osProfile.windowsConfiguration != '', 'Windows',
            properties.osProfile.linuxConfiguration != '', 'Linux',
            'Unknown'
        )
        | extend VMSize = tostring(properties.hardwareProfile.vmSize)
        | extend VMSizeCategory = case(
            VMSize startswith 'Standard_A', 'Basic/Legacy',
            VMSize startswith 'Standard_B', 'Burstable', 
            VMSize startswith 'Standard_D', 'General Purpose',
            VMSize startswith 'Standard_E', 'Memory Optimized',
            VMSize startswith 'Standard_F', 'Compute Optimized',
            'Standard'
        )
        // Simplified disk encryption check
        | extend DiskEncryption = case(
            properties.storageProfile.osDisk.encryptionSettings.enabled == true, 'OS Disk Encrypted',
            properties.storageProfile.osDisk.managedDisk.diskEncryptionSet.id != '', 'Managed Disk Encryption Set',
            'Platform Managed Keys Only'
        )
        // Basic power state from provisioning state
        | extend PowerState = case(
            tostring(properties.provisioningState) == 'Succeeded', 'Running',
            tostring(properties.provisioningState) == 'Failed', 'Failed',
            tostring(properties.provisioningState) == 'Creating', 'Creating',
            tostring(properties.provisioningState)
        )
        // Security risk assessment
        | extend SecurityRisk = case(
            DiskEncryption == 'Platform Managed Keys Only' and OSType == 'Windows', 'High - Windows VM without additional encryption',
            DiskEncryption == 'Platform Managed Keys Only' and OSType == 'Linux', 'High - Linux VM without additional encryption', 
            VMSizeCategory == 'Basic/Legacy', 'Medium - Legacy VM size',
            PowerState == 'Failed', 'Medium - VM in failed state',
            'Low - Standard security configuration'
        )
        | extend ComplianceStatus = case(
            SecurityRisk startswith 'High', 'Non-Compliant',
            SecurityRisk startswith 'Medium', 'Needs Review',
            'Compliant'
        )
        | extend SecurityFindings = case(
            DiskEncryption == 'Platform Managed Keys Only', 'Using platform managed keys only',
            VMSizeCategory == 'Basic/Legacy', 'Using legacy VM size',
            PowerState == 'Failed', 'VM provisioning failed',
            'Standard security configuration'
        )
        | project
            Application,
            VMName = name,
            OSType,
            VMSize,
            VMSizeCategory,
            PowerState,
            DiskEncryption,
            SecurityFindings,
            SecurityRisk,
            ComplianceStatus,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, SecurityRisk desc, VMName
        """

    @staticmethod
    def get_vm_optimization_query() -> str:
        """
        VM cost optimization analysis focusing on actionable insights
        """
        return """
        Resources
        | where type == 'microsoft.compute/virtualmachines'
        | extend Application = coalesce(
            tags.Application, 
            tags.app, 
            tags['application-name'], 
            'Untagged/Orphaned'
        )
        | extend VMSize = tostring(properties.hardwareProfile.vmSize)
        | extend OSType = case(
            tostring(properties.storageProfile.osDisk.osType) != '', tostring(properties.storageProfile.osDisk.osType),
            properties.osProfile.windowsConfiguration != '', 'Windows',
            properties.osProfile.linuxConfiguration != '', 'Linux',
            'Unknown'
        )
        | extend PowerState = case(
            tostring(properties.provisioningState) == 'Succeeded', 'Running',
            tostring(properties.provisioningState) == 'Deallocated', 'Deallocated',
            tostring(properties.provisioningState) == 'Failed', 'Failed',
            tostring(properties.provisioningState)
        )
        // Estimate creation time from resource creation if available
        | extend CreatedTime = case(
            properties.timeCreated != '', todatetime(properties.timeCreated),
            datetime(2024-01-01)  // Fallback
        )
        | extend DaysOld = datetime_diff('day', now(), CreatedTime)
        | extend VMSizeCategory = case(
            VMSize contains 'A0' or VMSize contains 'A1', 'Basic/Legacy',
            VMSize startswith 'Standard_B', 'Burstable',
            VMSize startswith 'Standard_D', 'General Purpose',
            VMSize startswith 'Standard_E', 'Memory Optimized',
            VMSize startswith 'Standard_F', 'Compute Optimized',
            VMSize startswith 'Standard_G', 'Memory/Storage Optimized',
            VMSize startswith 'Standard_H', 'High Performance Compute',
            VMSize startswith 'Standard_L', 'Storage Optimized',
            VMSize startswith 'Standard_M', 'Memory Optimized Large',
            VMSize startswith 'Standard_N', 'GPU Enabled',
            'Standard'
        )
        // Cost estimation based on VM size category
        | extend EstimatedMonthlyCost = case(
            VMSizeCategory == 'Basic/Legacy', 'Low',
            VMSizeCategory == 'Burstable', 'Low-Medium',
            VMSizeCategory == 'General Purpose', 'Medium',
            VMSizeCategory contains 'Memory Optimized' or VMSizeCategory contains 'Compute Optimized', 'High',
            VMSizeCategory == 'GPU Enabled' or VMSizeCategory contains 'High Performance', 'Very High',
            'Medium'
        )
        // Optimization recommendations
        | extend OptimizationPotential = case(
            PowerState == 'Failed', 'High - VM failed, investigate or delete',
            VMSizeCategory == 'Basic/Legacy', 'High - Upgrade to modern VM sizes',
            PowerState == 'Deallocated' and DaysOld > 30, 'High - Deallocated VM for >30 days, consider deletion',
            VMSize contains 'Standard_D64' or VMSize contains 'Standard_E64', 'Medium - Very large VM, verify utilization',
            VMSizeCategory == 'GPU Enabled' and OSType == 'Windows', 'Medium - GPU VM, verify GPU utilization need',
            DaysOld < 7, 'Low - Recently created, monitor usage',
            'Low - Current configuration appears appropriate'
        )
        | extend OptimizationRecommendation = case(
            PowerState == 'Failed', 'Investigate VM failure, fix issues or delete if no longer needed',
            VMSizeCategory == 'Basic/Legacy', 'Migrate to Standard_B (burstable) or Standard_D series for better performance',
            PowerState == 'Deallocated' and DaysOld > 30, 'Consider deleting if VM is no longer needed to save costs',
            VMSize contains 'Standard_D64', 'Monitor CPU/memory utilization and consider downsizing if underutilized',
            VMSizeCategory == 'GPU Enabled', 'Verify GPU workload requirements justify the additional cost',
            DaysOld < 7, 'Monitor resource utilization patterns for 30+ days before optimization',
            'Current VM size appears appropriate for workload'
        )
        | extend UtilizationStatus = case(
            PowerState == 'Failed', 'Failed - Requires Investigation',
            PowerState == 'Deallocated', 'Deallocated - Not Running',
            VMSizeCategory == 'Basic/Legacy', 'Legacy Size - Consider Upgrade',
            DaysOld < 7, 'Recently Created - Monitor Usage',
            'Active'
        )
        | project
            Application,
            VMName = name,
            VMSize,
            VMSizeCategory,
            PowerState,
            OSType,
            UtilizationStatus,
            OptimizationPotential,
            OptimizationRecommendation,
            EstimatedMonthlyCost,
            DaysOld,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, OptimizationPotential desc, EstimatedMonthlyCost desc, VMName
        """

    @staticmethod
    def get_vm_governance_summary_query() -> str:
        """
        VM governance summary with better performance and error handling
        """
        return """
        Resources
        | where type == 'microsoft.compute/virtualmachines'
        | extend Application = coalesce(
            tags.Application, 
            tags.app, 
            tags['application-name'], 
            'Untagged/Orphaned'
        )
        | extend OSType = case(
            tostring(properties.storageProfile.osDisk.osType) != '', tostring(properties.storageProfile.osDisk.osType),
            properties.osProfile.windowsConfiguration != '', 'Windows',
            properties.osProfile.linuxConfiguration != '', 'Linux',
            'Unknown'
        )
        | extend PowerState = case(
            tostring(properties.provisioningState) == 'Succeeded', 'Running',
            tostring(properties.provisioningState) == 'Deallocated', 'Deallocated',
            tostring(properties.provisioningState) == 'Failed', 'Failed',
            'Other'
        )
        | extend VMSize = tostring(properties.hardwareProfile.vmSize)
        | extend IsLegacySize = case(
            VMSize contains 'A0' or VMSize contains 'A1' or VMSize startswith 'Basic_', true,
            false
        )
        // Simplified encryption check (assume managed disks have platform encryption)
        | extend HasBasicEncryption = case(
            properties.storageProfile.osDisk.managedDisk.id != '', true,
            false
        )
        | extend IsOptimized = case(
            PowerState == 'Running' and not(IsLegacySize), true,
            false
        )
        | extend HasIssues = case(
            PowerState == 'Failed' or IsLegacySize or PowerState == 'Other', true,
            false
        )
        // Create summary by application
        | summarize 
            TotalVMs = count(),
            WindowsVMs = countif(OSType == 'Windows'),
            LinuxVMs = countif(OSType == 'Linux'),
            UnknownOSVMs = countif(OSType == 'Unknown'),
            RunningVMs = countif(PowerState == 'Running'),
            DeallocatedVMs = countif(PowerState == 'Deallocated'),
            FailedVMs = countif(PowerState == 'Failed'),
            EncryptedVMs = countif(HasBasicEncryption == true),
            LegacySizeVMs = countif(IsLegacySize == true),
            OptimizedVMs = countif(IsOptimized == true),
            VMsWithIssues = countif(HasIssues == true)
        by Application
        | extend GovernanceScore = round(
            case(
                TotalVMs == 0, 0.0,
                (TotalVMs - VMsWithIssues) * 100.0 / TotalVMs
            ), 1
        )
        | extend GovernanceStatus = case(
            GovernanceScore >= 95, 'Excellent',
            GovernanceScore >= 85, 'Good', 
            GovernanceScore >= 70, 'Acceptable',
            GovernanceScore >= 50, 'Needs Improvement',
            'Critical Issues'
        )
        | project 
            Application,
            TotalVMs,
            WindowsVMs,
            LinuxVMs,
            RunningVMs,
            DeallocatedVMs,
            FailedVMs,
            EncryptedVMs,
            LegacySizeVMs,
            OptimizedVMs,
            VMsWithIssues,
            GovernanceScore,
            GovernanceStatus
        | order by GovernanceScore asc, Application
        """

    @staticmethod
    def get_vm_extensions_query() -> str:
        """
        Query VM extensions with focus on security and monitoring extensions
        """
        return """
        Resources
        | where type == 'microsoft.compute/virtualmachines/extensions'
        | extend Application = coalesce(
            tags.Application, 
            tags.app, 
            'Untagged/Orphaned'
        )
        | extend VMName = tostring(split(id, '/')[8])
        | extend ExtensionType = tostring(properties.type)
        | extend ExtensionPublisher = tostring(properties.publisher)
        | extend ExtensionVersion = tostring(properties.typeHandlerVersion)
        | extend ProvisioningState = tostring(properties.provisioningState)
        | extend ExtensionCategory = case(
            ExtensionType in ('MicrosoftMonitoringAgent', 'OmsAgentForLinux', 'AzureMonitorWindowsAgent', 'AzureMonitorLinuxAgent'), 'Monitoring',
            ExtensionType in ('DependencyAgentWindows', 'DependencyAgentLinux'), 'Dependency Tracking',
            ExtensionType in ('IaaSAntimalware', 'LinuxDiagnostic'), 'Security',
            ExtensionType in ('AzureDiskEncryption', 'AzureDiskEncryptionForLinux'), 'Encryption',
            ExtensionType in ('CustomScript', 'CustomScriptExtension', 'CustomScriptForLinux'), 'Management',
            ExtensionType in ('JsonADDomainExtension', 'AADLoginForWindows', 'AADLoginForLinux'), 'Identity',
            'Other'
        )
        | extend SecurityImportance = case(
            ExtensionCategory in ('Security', 'Encryption'), 'Critical',
            ExtensionCategory in ('Monitoring', 'Identity'), 'Important',
            ExtensionCategory == 'Dependency Tracking', 'Important',
            'Standard'
        )
        | extend ExtensionStatus = case(
            ProvisioningState == 'Succeeded', 'Healthy',
            ProvisioningState == 'Failed', 'Failed',
            ProvisioningState in ('Creating', 'Updating'), 'In Progress',
            'Unknown'
        )
        | extend ComplianceImpact = case(
            ExtensionCategory == 'Security' and ExtensionStatus != 'Healthy', 'High - Security extension not working',
            ExtensionCategory == 'Monitoring' and ExtensionStatus != 'Healthy', 'Medium - Monitoring gap',
            ExtensionCategory == 'Encryption' and ExtensionStatus != 'Healthy', 'High - Encryption extension failed',
            ExtensionStatus == 'Failed', 'Medium - Extension failure requires investigation',
            'Low - Extension working normally'
        )
        | project
            Application,
            VMName,
            ExtensionName = name,
            ExtensionType,
            ExtensionCategory,
            ExtensionPublisher,
            ExtensionVersion,
            ProvisioningState,
            ExtensionStatus,
            SecurityImportance,
            ComplianceImpact,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, VMName, SecurityImportance desc, ExtensionCategory
        """

    @staticmethod
    def get_vm_patch_compliance_query() -> str:
        """
        SIMPLIFIED VM patch compliance query that avoids problematic Azure Resource Graph properties
        This version focuses on basic patch configuration without deep nested properties
        """
        return """
        Resources
        | where type == 'microsoft.compute/virtualmachines'
        | extend Application = coalesce(
            tags.Application, 
            tags.app, 
            tags['application-name'], 
            'Untagged/Orphaned'
        )
        | extend OSType = case(
            tostring(properties.storageProfile.osDisk.osType) != '', tostring(properties.storageProfile.osDisk.osType),
            properties.osProfile.windowsConfiguration != '', 'Windows',
            properties.osProfile.linuxConfiguration != '', 'Linux',
            'Unknown'
        )
        | extend PowerState = case(
            tostring(properties.provisioningState) == 'Succeeded', 'Running',
            tostring(properties.provisioningState) == 'Deallocated', 'Deallocated',
            tostring(properties.provisioningState) == 'Failed', 'Failed',
            'Other'
        )
        // Simplified automatic updates detection for Windows
        | extend AutomaticUpdatesEnabled = case(
            OSType == 'Windows' and properties.osProfile.windowsConfiguration.enableAutomaticUpdates == true, 'Enabled',
            OSType == 'Windows' and properties.osProfile.windowsConfiguration.enableAutomaticUpdates == false, 'Disabled',
            OSType == 'Linux', 'OS Managed',
            'Unknown'
        )
        // Basic patch mode detection (simplified)
        | extend PatchMode = case(
            OSType == 'Windows' and AutomaticUpdatesEnabled == 'Enabled', 'AutomaticByOS',
            OSType == 'Windows' and AutomaticUpdatesEnabled == 'Disabled', 'Manual',
            OSType == 'Linux', 'AutomaticByOS',
            'Manual'
        )
        | extend PatchComplianceStatus = case(
            PatchMode == 'AutomaticByOS' and OSType == 'Windows' and AutomaticUpdatesEnabled == 'Enabled', 'Automated - OS Managed',
            PatchMode == 'AutomaticByOS' and OSType == 'Linux', 'Automated - OS Managed',
            PatchMode == 'Manual' or AutomaticUpdatesEnabled == 'Disabled', 'Manual - Requires Attention',
            'Configuration Review Required'
        )
        | extend PatchRisk = case(
            PatchComplianceStatus contains 'Manual', 'High - Manual patching required',
            PowerState != 'Running', 'Medium - VM not running for updates',
            OSType == 'Unknown', 'Medium - Unknown OS type',
            'Low - Automated patching appears configured'
        )
        | project
            Application,
            VMName = name,
            OSType,
            PowerState,
            AutomaticUpdatesEnabled,
            PatchMode,
            PatchComplianceStatus,
            PatchRisk,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, PatchRisk desc, VMName
        """
