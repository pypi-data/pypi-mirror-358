#!/usr/bin/env python3
"""
Storage Analysis Module for Azure Resource Graph Client
Provides comprehensive storage security, compliance, optimization, and governance analysis
"""


class StorageAnalysisQueries:
    """Storage analysis related queries for Azure Resource Graph"""

    @staticmethod
    def get_storage_security_query() -> str:
        """
        Query for storage security compliance across storage accounts, SQL databases, and Cosmos DB

        Returns:
            KQL query string for storage security analysis
        """
        return """
        Resources
        | where type in (
            'microsoft.storage/storageaccounts',
            'microsoft.sql/servers/databases',
            'microsoft.documentdb/databaseaccounts', 
            'microsoft.compute/disks',
            'microsoft.keyvault/vaults'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            isnotempty(tags['application-name']), tags['application-name'],
            'Untagged/Orphaned'
        )
        | extend StorageType = case(
            type == 'microsoft.storage/storageaccounts', 'Storage Account',
            type == 'microsoft.sql/servers/databases', 'SQL Database',
            type == 'microsoft.documentdb/databaseaccounts', 'Cosmos DB',
            type == 'microsoft.compute/disks', 'Managed Disk',
            type == 'microsoft.keyvault/vaults', 'Key Vault',
            type
        )
        | extend EncryptionMethod = case(
            type == 'microsoft.storage/storageaccounts',
                case(
                    tostring(properties.encryption.keySource) == 'Microsoft.Keyvault', 'Customer Managed Key (CMK)',
                    tobool(properties.encryption.services.blob.enabled) == true and tobool(properties.supportsHttpsTrafficOnly) == true, 'Platform Managed + HTTPS',
                    tobool(properties.encryption.services.blob.enabled) == true and tobool(properties.supportsHttpsTrafficOnly) == false, 'Platform Managed + HTTP Allowed',
                    'Not Encrypted'
                ),
            type == 'microsoft.compute/disks',
                case(
                    tostring(properties.encryption.type) == 'EncryptionAtRestWithCustomerKey', 'Customer Managed Key (CMK)',
                    tostring(properties.encryption.type) == 'EncryptionAtRestWithPlatformKey', 'Platform Managed Key (PMK)',
                    tostring(properties.encryption.type) == 'EncryptionAtRestWithPlatformAndCustomerKeys', 'Double Encryption (PMK + CMK)',
                    'Not Encrypted'
                ),
            type == 'microsoft.documentdb/databaseaccounts',
                case(
                    isnotempty(tostring(properties.keyVaultKeyUri)), 'Customer Managed Key (CMK)',
                    'Platform Managed Key (PMK)'
                ),
            type == 'microsoft.sql/servers/databases', 'TDE - Check Manually',
            type == 'microsoft.keyvault/vaults', 'Hardware Security Module (HSM)',
            'Unknown'
        )
        | extend SecurityFindings = case(
            type == 'microsoft.storage/storageaccounts',
                case(
                    tobool(properties.allowBlobPublicAccess) == true, 'Public blob access allowed',
                    tobool(properties.supportsHttpsTrafficOnly) == false, 'HTTP traffic allowed',
                    isempty(properties.networkAcls) or tostring(properties.networkAcls.defaultAction) == 'Allow', 'No network restrictions',
                    'Secure configuration'
                ),
            type == 'microsoft.compute/disks',
                case(
                    tostring(properties.diskState) == 'Unattached', 'Disk not attached to VM',
                    tostring(properties.networkAccessPolicy) == 'AllowAll', 'Network access unrestricted',
                    'Standard configuration'
                ),
            type == 'microsoft.documentdb/databaseaccounts',
                case(
                    tobool(properties.publicNetworkAccess) == true, 'Public network access enabled',
                    array_length(properties.ipRules) == 0 and array_length(properties.virtualNetworkRules) == 0, 'No network restrictions',
                    'Network restrictions configured'
                ),
            type == 'microsoft.keyvault/vaults',
                case(
                    tobool(properties.enabledForDeployment) == true, 'Enabled for VM deployment',
                    tobool(properties.enabledForTemplateDeployment) == true, 'Enabled for ARM templates',
                    tostring(properties.networkAcls.defaultAction) == 'Allow', 'No network restrictions',
                    'Secure configuration'
                ),
            'Review required'
        )
        | extend ComplianceRisk = case(
            EncryptionMethod contains 'Not Encrypted', 'High - No encryption',
            EncryptionMethod contains 'HTTP Allowed', 'High - Insecure transport', 
            SecurityFindings contains 'Public blob access allowed', 'High - Public access',
            SecurityFindings contains 'No network restrictions', 'Medium - Network exposure',
            SecurityFindings contains 'Disk not attached', 'Medium - Orphaned resource',
            EncryptionMethod contains 'Platform Managed' or EncryptionMethod contains 'Customer Managed', 'Low - Encrypted',
            'Manual review required'
        )
        | extend AdditionalDetails = case(
            type == 'microsoft.storage/storageaccounts', 
                strcat('HTTPS: ', case(tobool(properties.supportsHttpsTrafficOnly) == true, 'Required', 'Optional'), 
                       ' | Public: ', case(tobool(properties.allowBlobPublicAccess) == true, 'Allowed', 'Blocked'),
                       ' | Tier: ', tostring(properties.accessTier)),
            type == 'microsoft.compute/disks',
                strcat(tostring(properties.diskSizeGB), 'GB | State: ', tostring(properties.diskState),
                       ' | SKU: ', tostring(sku.name)),
            type == 'microsoft.documentdb/databaseaccounts',
                strcat('Consistency: ', tostring(properties.defaultConsistencyLevel),
                       ' | Multi-region: ', case(array_length(properties.locations) > 1, 'Yes', 'No')),
            type == 'microsoft.keyvault/vaults',
                strcat('SKU: ', tostring(properties.sku.name),
                       ' | Soft Delete: ', case(tobool(properties.enableSoftDelete) == true, 'Enabled', 'Disabled')),
            ''
        )
        | project 
            Application,
            StorageResource = name,
            StorageType,
            EncryptionMethod,
            SecurityFindings,
            ComplianceRisk,
            ResourceGroup = resourceGroup,
            Location = location,
            AdditionalDetails,
            ResourceId = id
        | order by Application, ComplianceRisk desc, StorageType, StorageResource
        """

    @staticmethod
    def get_storage_access_control_query() -> str:
        """
        Detailed query for storage access control and network security analysis

        Returns:
            KQL query string for storage access control analysis
        """
        return """
        Resources
        | where type in (
            'microsoft.storage/storageaccounts',
            'microsoft.sql/servers',
            'microsoft.documentdb/databaseaccounts'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend ResourceType = case(
            type == 'microsoft.storage/storageaccounts', 'Storage Account',
            type == 'microsoft.sql/servers', 'SQL Server',
            type == 'microsoft.documentdb/databaseaccounts', 'Cosmos DB Account',
            type
        )
        | extend PublicAccess = case(
            type == 'microsoft.storage/storageaccounts',
                case(
                    properties.allowBlobPublicAccess == true, 'Blob Public Access Enabled',
                    tostring(properties.networkAcls.defaultAction) == 'Allow', 'Network Access Unrestricted',
                    'Public Access Restricted'
                ),
            type == 'microsoft.sql/servers',
                case(
                    properties.publicNetworkAccess == 'Enabled', 'Public Network Access Enabled',
                    'Public Network Access Disabled'
                ),
            type == 'microsoft.documentdb/databaseaccounts',
                case(
                    properties.publicNetworkAccess == 'Enabled', 'Public Network Access Enabled',
                    'Public Network Access Disabled'
                ),
            'Unknown'
        )
        | extend NetworkRestrictions = case(
            type == 'microsoft.storage/storageaccounts',
                case(
                    array_length(properties.networkAcls.ipRules) > 0 or array_length(properties.networkAcls.virtualNetworkRules) > 0,
                        strcat('IP Rules: ', tostring(array_length(properties.networkAcls.ipRules)),
                               ' | VNet Rules: ', tostring(array_length(properties.networkAcls.virtualNetworkRules))),
                    'No Network Restrictions'
                ),
            type == 'microsoft.sql/servers',
                case(
                    array_length(properties.privateEndpointConnections) > 0,
                        strcat('Private Endpoints: ', tostring(array_length(properties.privateEndpointConnections))),
                    'No Private Endpoints'
                ),
            type == 'microsoft.documentdb/databaseaccounts',
                case(
                    array_length(properties.ipRules) > 0 or array_length(properties.virtualNetworkRules) > 0,
                        strcat('IP Rules: ', tostring(array_length(properties.ipRules)),
                               ' | VNet Rules: ', tostring(array_length(properties.virtualNetworkRules))),
                    'No Network Restrictions'
                ),
            'Unknown'
        )
        | extend AuthenticationMethod = case(
            type == 'microsoft.storage/storageaccounts',
                case(
                    isnotempty(tostring(properties.azureFilesIdentityBasedAuthentication.directoryServiceOptions)),
                        strcat('Identity-based: ', tostring(properties.azureFilesIdentityBasedAuthentication.directoryServiceOptions)),
                    'Access Keys Only'
                ),
            type == 'microsoft.sql/servers',
                case(
                    properties.azureADOnlyAuthentication.azureADOnlyAuthentication == true,
                        'Azure AD Only',
                    'Mixed Authentication'
                ),
            type == 'microsoft.documentdb/databaseaccounts',
                'Account Keys + AAD (Check RBAC)',
            'Unknown'
        )
        | extend SecurityRisk = case(
            PublicAccess contains 'Enabled' and NetworkRestrictions contains 'No Network', 'High - Public + No Restrictions',
            PublicAccess contains 'Enabled', 'Medium - Public Access Enabled',
            NetworkRestrictions contains 'No Network', 'Medium - No Network Restrictions',
            AuthenticationMethod contains 'Access Keys Only', 'Medium - Key-based Auth Only',
            'Low - Secured'
        )
        | extend AccessDetails = case(
            type == 'microsoft.storage/storageaccounts',
                strcat('Min TLS: ', tostring(properties.minimumTlsVersion),
                       ' | Key Policy: ', case(properties.allowSharedKeyAccess == false, 'Disabled', 'Enabled')),
            type == 'microsoft.sql/servers',
                strcat('Version: ', tostring(properties.version),
                       ' | Admin: ', tostring(properties.administratorLogin)),
            type == 'microsoft.documentdb/databaseaccounts',
                strcat('Offer Type: ', tostring(properties.databaseAccountOfferType),
                       ' | Locations: ', tostring(array_length(properties.locations))),
            ''
        )
        | project
            Application,
            ResourceName = name,
            ResourceType,
            PublicAccess,
            NetworkRestrictions,
            AuthenticationMethod,
            SecurityRisk,
            AccessDetails,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, SecurityRisk desc, ResourceType, ResourceName
        """

    @staticmethod
    def get_storage_backup_analysis_query() -> str:
        """
        Query for storage backup and disaster recovery analysis

        Returns:
            KQL query string for backup analysis
        """
        return """
        Resources
        | where type in (
            'microsoft.storage/storageaccounts',
            'microsoft.sql/servers/databases',
            'microsoft.documentdb/databaseaccounts',
            'microsoft.recoveryservices/vaults'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend ResourceType = case(
            type == 'microsoft.storage/storageaccounts', 'Storage Account',
            type == 'microsoft.sql/servers/databases', 'SQL Database',
            type == 'microsoft.documentdb/databaseaccounts', 'Cosmos DB',
            type == 'microsoft.recoveryservices/vaults', 'Recovery Services Vault',
            type
        )
        | extend BackupConfiguration = case(
            type == 'microsoft.storage/storageaccounts',
                case(
                    properties.blobRestorePolicy.enabled == true,
                        strcat('Point-in-time restore: ', tostring(properties.blobRestorePolicy.days), ' days'),
                    properties.isVersioningEnabled == true, 'Blob versioning enabled',
                    'No backup configuration'
                ),
            type == 'microsoft.sql/servers/databases',
                case(
                    isnotempty(tostring(properties.requestedBackupStorageRedundancy)), 
                        strcat('Backup redundancy: ', tostring(properties.requestedBackupStorageRedundancy)),
                    'Default backup configuration'
                ),
            type == 'microsoft.documentdb/databaseaccounts',
                case(
                    isnotempty(tostring(properties.backupPolicy.type)),
                        strcat('Backup type: ', tostring(properties.backupPolicy.type),
                               ' | Interval: ', case(
                                   tostring(properties.backupPolicy.type) == 'Periodic',
                                   strcat(tostring(properties.backupPolicy.periodicModeProperties.backupIntervalInMinutes), ' min'),
                                   'Continuous')),
                    'Default backup policy'
                ),
            type == 'microsoft.recoveryservices/vaults',
                strcat('SKU: ', tostring(sku.name),
                       ' | Cross Region: ', case(
                           isnotempty(tostring(properties.crossRegionRestore)), 
                           tostring(properties.crossRegionRestore), 
                           'Unknown')),
            'Unknown'
        )
        | extend RetentionPolicy = case(
            type == 'microsoft.storage/storageaccounts',
                case(
                    properties.deleteRetentionPolicy.enabled == true,
                        strcat('Soft delete: ', tostring(properties.deleteRetentionPolicy.days), ' days'),
                    'No retention policy'
                ),
            type == 'microsoft.sql/servers/databases',
                strcat('Retention: ', tostring(properties.earliestRestoreDate)),
            type == 'microsoft.documentdb/databaseaccounts',
                case(
                    tostring(properties.backupPolicy.type) == 'Periodic',
                        strcat('Retention: ', tostring(properties.backupPolicy.periodicModeProperties.backupRetentionIntervalInHours), ' hours'),
                    'Continuous backup'
                ),
            'Unknown'
        )
        | extend ComplianceStatus = case(
            BackupConfiguration contains 'No backup', 'Non-Compliant - No Backup',
            BackupConfiguration contains 'Default backup', 'Partially Compliant - Default Policy',
            RetentionPolicy contains 'No retention', 'Partially Compliant - No Retention',
            BackupConfiguration contains 'Point-in-time' or BackupConfiguration contains 'Continuous', 'Compliant - Advanced Backup',
            'Compliant - Basic Backup'
        )
        | extend DisasterRecoveryRisk = case(
            ComplianceStatus contains 'Non-Compliant', 'High - No Backup Protection',
            ComplianceStatus contains 'Partially Compliant', 'Medium - Limited Protection',
            BackupConfiguration contains 'Continuous' or RetentionPolicy contains 'Cross Region', 'Low - Comprehensive Protection',
            'Medium - Basic Protection'
        )
        | project
            Application,
            ResourceName = name,
            ResourceType,
            BackupConfiguration,
            RetentionPolicy,
            ComplianceStatus,
            DisasterRecoveryRisk,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, DisasterRecoveryRisk desc, ResourceType, ResourceName
        """

    @staticmethod
    def get_storage_optimization_query() -> str:
        """
        Query for storage cost optimization opportunities

        Returns:
            KQL query string for storage optimization analysis
        """
        return """
        Resources
        | where type in (
            'microsoft.storage/storageaccounts',
            'microsoft.compute/disks',
            'microsoft.sql/servers/databases'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend OptimizationType = case(
            type == 'microsoft.storage/storageaccounts', 'Storage Account',
            type == 'microsoft.compute/disks', 'Managed Disk',
            type == 'microsoft.sql/servers/databases', 'SQL Database',
            type
        )
        | extend CurrentConfiguration = case(
            type == 'microsoft.storage/storageaccounts',
                strcat('SKU: ', tostring(sku.name),
                       ' | Tier: ', tostring(properties.accessTier),
                       ' | Kind: ', tostring(kind)),
            type == 'microsoft.compute/disks',
                strcat('SKU: ', tostring(sku.name),
                       ' | Size: ', tostring(properties.diskSizeGB), 'GB',
                       ' | State: ', tostring(properties.diskState)),
            type == 'microsoft.sql/servers/databases',
                strcat('SKU: ', tostring(sku.name),
                       ' | Tier: ', tostring(sku.tier),
                       ' | Capacity: ', tostring(sku.capacity)),
            'Unknown'
        )
        | extend UtilizationStatus = case(
            type == 'microsoft.storage/storageaccounts',
                case(
                    datetime_diff('day', now(), todatetime(properties.creationTime)) < 30, 'Recently Created - Monitor Usage',
                    tostring(sku.name) contains 'Premium' and tostring(properties.accessTier) == 'Cool', 'Premium + Cool Tier - Review',
                    'Active Storage Account'
                ),
            type == 'microsoft.compute/disks',
                case(
                    tostring(properties.diskState) == 'Unattached', 'Unused - Not Attached to VM',
                    tostring(sku.name) == 'Premium_LRS' and toint(properties.diskSizeGB) < 128, 'Over-provisioned Premium Disk',
                    'In Use'
                ),
            type == 'microsoft.sql/servers/databases',
                case(
                    tostring(sku.tier) == 'Premium' and toint(sku.capacity) > 100, 'High-capacity Premium - Review Usage',
                    name == 'master', 'System Database',
                    'Active Database'
                ),
            'Unknown'
        )
        | extend CostOptimizationPotential = case(
            UtilizationStatus contains 'Unused', 'High - Delete unused resource',
            UtilizationStatus contains 'Over-provisioned', 'High - Downsize or change SKU',
            UtilizationStatus contains 'Premium + Cool', 'Medium - Consider Standard tier',
            UtilizationStatus contains 'High-capacity Premium', 'Medium - Review DTU/vCore usage',
            UtilizationStatus contains 'Recently Created', 'Low - Monitor for 30+ days',
            'Low - Optimized configuration'
        )
        | extend OptimizationRecommendation = case(
            type == 'microsoft.storage/storageaccounts' and UtilizationStatus contains 'Premium + Cool',
                'Consider Standard_LRS or Standard_GRS for cool tier storage',
            type == 'microsoft.compute/disks' and UtilizationStatus contains 'Unused',
                'Delete unattached disk or create snapshot for backup',
            type == 'microsoft.compute/disks' and UtilizationStatus contains 'Over-provisioned',
                'Consider Standard_LRS for smaller workloads',
            type == 'microsoft.sql/servers/databases' and UtilizationStatus contains 'High-capacity',
                'Monitor DTU/CPU usage and consider scaling down',
            'No immediate optimization needed'
        )
        | extend EstimatedMonthlyCost = case(
            type == 'microsoft.storage/storageaccounts',
                case(
                    tostring(sku.name) contains 'Premium', 'High',
                    tostring(sku.name) contains 'Standard', 'Medium',
                    'Low'
                ),
            type == 'microsoft.compute/disks',
                case(
                    tostring(sku.name) == 'Premium_LRS', 'High',
                    tostring(sku.name) == 'StandardSSD_LRS', 'Medium',
                    'Low'
                ),
            type == 'microsoft.sql/servers/databases',
                case(
                    tostring(sku.tier) == 'Premium', 'High',
                    tostring(sku.tier) == 'Standard', 'Medium',
                    'Low'
                ),
            'Unknown'
        )
        | project
            Application,
            ResourceName = name,
            OptimizationType,
            CurrentConfiguration,
            UtilizationStatus,
            CostOptimizationPotential,
            OptimizationRecommendation,
            EstimatedMonthlyCost,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, CostOptimizationPotential desc, OptimizationType, ResourceName
        """

    @staticmethod
    def get_storage_compliance_summary_query() -> str:
        """
        Query for storage compliance summary by application

        Returns:
            KQL query string for storage compliance summary
        """
        return """
        Resources
        | where type in (
            'microsoft.storage/storageaccounts',
            'microsoft.compute/disks',
            'microsoft.documentdb/databaseaccounts',
            'microsoft.sql/servers/databases'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend IsEncrypted = case(
            type == 'microsoft.storage/storageaccounts', 
                (tobool(properties.encryption.services.blob.enabled) == true),
            type == 'microsoft.compute/disks', 
                (tostring(properties.encryption.type) contains 'Encryption'),
            type == 'microsoft.documentdb/databaseaccounts', 
                true, // Always encrypted
            type == 'microsoft.sql/servers/databases',
                true, // TDE enabled by default
            false
        )
        | extend IsSecureTransport = case(
            type == 'microsoft.storage/storageaccounts',
                (tobool(properties.supportsHttpsTrafficOnly) == true),
            type == 'microsoft.compute/disks',
                true, // Disks don't have transport layer
            type == 'microsoft.documentdb/databaseaccounts',
                true, // Always uses HTTPS
            type == 'microsoft.sql/servers/databases',
                true, // SQL connections use TLS
            false
        )
        | extend IsNetworkSecured = case(
            type == 'microsoft.storage/storageaccounts',
                (tobool(properties.allowBlobPublicAccess) == false or 
                 isnotempty(properties.networkAcls.ipRules) or 
                 isnotempty(properties.networkAcls.virtualNetworkRules)),
            type == 'microsoft.compute/disks',
                (tostring(properties.networkAccessPolicy) != 'AllowAll'),
            type == 'microsoft.documentdb/databaseaccounts',
                (tobool(properties.publicNetworkAccess) == false or 
                 isnotempty(properties.ipRules) or 
                 isnotempty(properties.virtualNetworkRules)),
            false
        )
        | extend HasSecurityIssue = not(IsEncrypted and IsSecureTransport and IsNetworkSecured)
        | summarize 
            TotalStorageResources = count(),
            StorageAccountCount = countif(type == 'microsoft.storage/storageaccounts'),
            ManagedDiskCount = countif(type == 'microsoft.compute/disks'),
            CosmosDBCount = countif(type == 'microsoft.documentdb/databaseaccounts'),
            SQLDatabaseCount = countif(type == 'microsoft.sql/servers/databases'),
            EncryptedResources = countif(IsEncrypted == true),
            SecureTransportResources = countif(IsSecureTransport == true),
            NetworkSecuredResources = countif(IsNetworkSecured == true),
            ResourcesWithIssues = countif(HasSecurityIssue == true),
            ComplianceScore = round((count() - countif(HasSecurityIssue == true)) * 100.0 / count(), 1)
        by Application
        | extend ComplianceStatus = case(
            ComplianceScore >= 95, 'Excellent',
            ComplianceScore >= 85, 'Good',
            ComplianceScore >= 70, 'Acceptable',
            ComplianceScore >= 50, 'Needs Improvement',
            'Critical Issues'
        )
        | project 
            Application,
            TotalStorageResources,
            StorageAccountCount,
            ManagedDiskCount,
            CosmosDBCount,
            SQLDatabaseCount,
            EncryptedResources,
            SecureTransportResources,
            NetworkSecuredResources,
            ResourcesWithIssues,
            ComplianceScore,
            ComplianceStatus
        | order by Application
        """
