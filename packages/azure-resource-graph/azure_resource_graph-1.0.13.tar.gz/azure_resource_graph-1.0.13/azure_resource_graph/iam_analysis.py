#!/usr/bin/env python3
"""
Identity & Access Management Analysis Module for Azure Resource Graph Client
Provides comprehensive IAM analysis including role assignments, Key Vault security, and managed identities
"""

from typing import List, Dict, Any, Optional


class IAMAnalysisQueries:
    """Identity & Access Management related queries for Azure Resource Graph"""

    @staticmethod
    def get_role_assignments_query() -> str:
        """
        Query for role assignments analysis including overprivileged accounts and guest users

        Returns:
            KQL query string for role assignments analysis
        """
        return """
        AuthorizationResources
        | where type == 'microsoft.authorization/roleassignments'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Global/Untagged'
        )
        | extend RoleDefinitionId = tostring(properties.roleDefinitionId)
        | extend PrincipalId = tostring(properties.principalId)
        | extend PrincipalType = tostring(properties.principalType)
        | extend Scope = tostring(properties.scope)
        | join kind=leftouter (
            AuthorizationResources
            | where type == 'microsoft.authorization/roledefinitions'
            | project RoleDefinitionId = id, RoleName = tostring(properties.roleName), 
                      RoleType = tostring(properties.type), IsCustomRole = (properties.type == 'CustomRole'),
                      BuiltInRole = (properties.type == 'BuiltInRole'),
                      RolePermissions = properties.permissions
        ) on RoleDefinitionId
        | extend ScopeLevel = case(
            Scope contains '/subscriptions/' and Scope contains '/resourceGroups/', 'Resource Group',
            Scope contains '/subscriptions/' and not(Scope contains '/resourceGroups/'), 'Subscription',
            Scope == '/', 'Management Group',
            'Resource'
        )
        | extend PrivilegeLevel = case(
            RoleName in ('Owner', 'Contributor', 'User Access Administrator'), 'High Privilege',
            RoleName in ('Reader', 'Monitoring Reader', 'Storage Blob Data Reader'), 'Low Privilege',
            IsCustomRole == true, 'Custom Role - Review Required',
            'Standard Privilege'
        )
        | extend GuestUserRisk = case(
            PrincipalType == 'User' and PrincipalId contains '#EXT#', 'Guest User Access',
            PrincipalType == 'User', 'Internal User',
            PrincipalType == 'ServicePrincipal', 'Service Principal',
            PrincipalType == 'Group', 'Group Assignment',
            'Unknown Principal Type'
        )
        | extend SecurityRisk = case(
            PrivilegeLevel == 'High Privilege' and ScopeLevel in ('Subscription', 'Management Group'), 'High - Elevated privileges at broad scope',
            PrivilegeLevel == 'High Privilege' and GuestUserRisk == 'Guest User Access', 'High - Guest user with elevated privileges',
            IsCustomRole == true and ScopeLevel in ('Subscription', 'Management Group'), 'Medium - Custom role at broad scope',
            GuestUserRisk == 'Guest User Access', 'Medium - Guest user access',
            PrivilegeLevel == 'High Privilege', 'Medium - Elevated privileges',
            'Low - Standard access'
        )
        | extend AssignmentDetails = strcat(
            'Principal: ', PrincipalType,
            ' | Scope: ', ScopeLevel,
            ' | Role Type: ', case(IsCustomRole == true, 'Custom', 'Built-in')
        )
        | project
            Application,
            AssignmentName = name,
            PrincipalId,
            PrincipalType,
            RoleName,
            RoleType,
            ScopeLevel,
            PrivilegeLevel,
            GuestUserRisk,
            SecurityRisk,
            AssignmentDetails,
            ResourceGroup = resourceGroup,
            SubscriptionId = subscriptionId,
            ResourceId = id
        | order by Application, SecurityRisk desc, PrivilegeLevel desc, RoleName
        """

    @staticmethod
    def get_key_vault_security_query() -> str:
        """
        Query for Key Vault security analysis including certificates, access policies, and protection settings

        Returns:
            KQL query string for Key Vault security analysis
        """
        return """
        Resources
        | where type == 'microsoft.keyvault/vaults'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend VaultUri = tostring(properties.vaultUri)
        | extend EnabledForDeployment = tobool(properties.enabledForDeployment)
        | extend EnabledForDiskEncryption = tobool(properties.enabledForDiskEncryption)
        | extend EnabledForTemplateDeployment = tobool(properties.enabledForTemplateDeployment)
        | extend EnableSoftDelete = tobool(properties.enableSoftDelete)
        | extend EnablePurgeProtection = tobool(properties.enablePurgeProtection)
        | extend SoftDeleteRetentionInDays = toint(properties.softDeleteRetentionInDays)
        | extend NetworkDefaultAction = tostring(properties.networkAcls.defaultAction)
        | extend AccessPoliciesCount = array_length(properties.accessPolicies)
        | extend NetworkRulesCount = array_length(properties.networkAcls.ipRules) + array_length(properties.networkAcls.virtualNetworkRules)
        | extend CertificateConfiguration = case(
            AccessPoliciesCount > 10, 'High Access Policy Count - Review Required',
            AccessPoliciesCount == 0, 'No Access Policies Configured',
            'Standard Access Configuration'
        )
        | extend NetworkSecurity = case(
            NetworkDefaultAction == 'Allow' and NetworkRulesCount == 0, 'Public Access - No Network Restrictions',
            NetworkDefaultAction == 'Allow' and NetworkRulesCount > 0, 'Public Access - Limited Network Rules',
            NetworkDefaultAction == 'Deny' and NetworkRulesCount > 0, 'Network Restricted Access',
            NetworkDefaultAction == 'Deny' and NetworkRulesCount == 0, 'Deny All - Verify Configuration',
            'Unknown Network Configuration'
        )
        | extend PurgeProtectionStatus = case(
            EnablePurgeProtection == true, 'Purge Protection Enabled',
            EnableSoftDelete == true and EnablePurgeProtection == false, 'Soft Delete Only - No Purge Protection',
            EnableSoftDelete == false, 'No Data Protection Configured',
            'Unknown Protection Status'
        )
        | extend SecurityFindings = case(
            EnablePurgeProtection == false and EnableSoftDelete == false, 'No data protection configured',
            EnablePurgeProtection == false, 'Purge protection disabled',
            NetworkDefaultAction == 'Allow' and NetworkRulesCount == 0, 'No network access restrictions',
            AccessPoliciesCount > 10, 'High number of access policies',
            'Standard security configuration'
        )
        | extend SecurityRisk = case(
            EnablePurgeProtection == false and EnableSoftDelete == false, 'High - No data protection',
            NetworkDefaultAction == 'Allow' and NetworkRulesCount == 0, 'High - Public access without restrictions',
            EnablePurgeProtection == false, 'Medium - No purge protection',
            AccessPoliciesCount > 10, 'Medium - High access policy count',
            NetworkDefaultAction == 'Allow', 'Medium - Public network access',
            'Low - Secure configuration'
        )
        | extend VaultDetails = strcat(
            'Soft Delete: ', case(EnableSoftDelete == true, 'Enabled', 'Disabled'),
            ' | Purge Protection: ', case(EnablePurgeProtection == true, 'Enabled', 'Disabled'),
            ' | Access Policies: ', tostring(AccessPoliciesCount),
            ' | Network: ', NetworkDefaultAction
        )
        | project
            Application,
            VaultName = name,
            CertificateConfiguration,
            NetworkSecurity,
            PurgeProtectionStatus,
            SecurityFindings,
            SecurityRisk,
            VaultDetails,
            AccessPoliciesCount,
            NetworkRulesCount,
            SoftDeleteRetentionInDays,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, SecurityRisk desc, VaultName
        """

    @staticmethod
    def get_managed_identities_query() -> str:
        """
        Query for managed identities analysis including usage patterns and orphaned identities

        Returns:
            KQL query string for managed identities analysis
        """
        return """
        Resources
        | where type == 'microsoft.managedidentity/userassignedidentities'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend CreatedTime = todatetime(properties.timeCreated)
        | extend DaysOld = datetime_diff('day', now(), CreatedTime)
        | extend ClientId = tostring(properties.clientId)
        | extend PrincipalId = tostring(properties.principalId)
        | extend TenantId = tostring(properties.tenantId)
        | join kind=leftouter (
            // Get role assignments for this managed identity
            AuthorizationResources
            | where type == 'microsoft.authorization/roleassignments'
            | where tostring(properties.principalType) == 'ServicePrincipal'
            | project PrincipalId = tostring(properties.principalId), 
                      RoleAssignmentId = id,
                      RoleDefinitionId = tostring(properties.roleDefinitionId),
                      AssignmentScope = tostring(properties.scope)
            | summarize RoleAssignmentsCount = count(), 
                       AssignmentScopes = make_set(AssignmentScope),
                       RoleDefinitions = make_set(RoleDefinitionId)
            by PrincipalId
        ) on PrincipalId
        | join kind=leftouter (
            // Get VM associations
            Resources
            | where type == 'microsoft.compute/virtualmachines'
            | where isnotempty(properties.instanceView) or isnotempty(identity.userAssignedIdentities)
            | extend UserAssignedIdentities = properties.instanceView.userAssignedIdentities
            | extend IdentityResourceIds = bag_keys(identity.userAssignedIdentities)
            | mv-expand IdentityResourceId = IdentityResourceIds
            | project VMName = name, VMResourceGroup = resourceGroup, IdentityResourceId = tostring(IdentityResourceId)
            | summarize AssociatedVMs = make_set(strcat(VMResourceGroup, '/', VMName)) by IdentityResourceId
        ) on $left.id == $right.IdentityResourceId
        | join kind=leftouter (
            // Get App Service associations
            Resources
            | where type == 'microsoft.web/sites'
            | where isnotempty(identity.userAssignedIdentities)
            | extend IdentityResourceIds = bag_keys(identity.userAssignedIdentities)
            | mv-expand IdentityResourceId = IdentityResourceIds
            | project AppServiceName = name, AppServiceResourceGroup = resourceGroup, IdentityResourceId = tostring(IdentityResourceId)
            | summarize AssociatedAppServices = make_set(strcat(AppServiceResourceGroup, '/', AppServiceName)) by IdentityResourceId
        ) on $left.id == $right.IdentityResourceId
        | extend UsagePattern = case(
            isnotempty(AssociatedVMs) and isnotempty(AssociatedAppServices), 'Multi-Resource Usage',
            isnotempty(AssociatedVMs), 'VM Identity',
            isnotempty(AssociatedAppServices), 'App Service Identity',
            RoleAssignmentsCount > 0, 'Has Role Assignments Only',
            'Potentially Orphaned'
        )
        | extend OrphanedStatus = case(
            isempty(AssociatedVMs) and isempty(AssociatedAppServices) and (RoleAssignmentsCount == 0 or isempty(RoleAssignmentsCount)), 'Orphaned - No Usage Detected',
            isempty(AssociatedVMs) and isempty(AssociatedAppServices) and RoleAssignmentsCount > 0, 'Unused - Has Role Assignments',
            DaysOld > 90 and UsagePattern == 'Potentially Orphaned', 'Stale - Created >90 days ago',
            'In Use'
        )
        | extend SecurityRisk = case(
            OrphanedStatus == 'Orphaned - No Usage Detected', 'High - Orphaned identity with no usage',
            RoleAssignmentsCount > 5, 'Medium - High number of role assignments',
            OrphanedStatus == 'Unused - Has Role Assignments', 'Medium - Unused but has permissions',
            OrphanedStatus == 'Stale - Created >90 days ago', 'Medium - Potentially stale identity',
            'Low - Active identity'
        )
        | extend IdentityDetails = strcat(
            'Age: ', tostring(DaysOld), ' days',
            ' | Role Assignments: ', case(isempty(RoleAssignmentsCount), '0', tostring(RoleAssignmentsCount)),
            ' | VMs: ', case(isempty(AssociatedVMs), '0', tostring(array_length(AssociatedVMs))),
            ' | App Services: ', case(isempty(AssociatedAppServices), '0', tostring(array_length(AssociatedAppServices)))
        )
        | project
            Application,
            IdentityName = name,
            UsagePattern,
            OrphanedStatus,
            SecurityRisk,
            IdentityDetails,
            RoleAssignmentsCount = case(isempty(RoleAssignmentsCount), 0, RoleAssignmentsCount),
            AssociatedVMsCount = case(isempty(AssociatedVMs), 0, array_length(AssociatedVMs)),
            AssociatedAppServicesCount = case(isempty(AssociatedAppServices), 0, array_length(AssociatedAppServices)),
            DaysOld,
            ClientId,
            PrincipalId,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = id
        | order by Application, SecurityRisk desc, OrphanedStatus desc, IdentityName
        """

    @staticmethod
    def get_custom_roles_query() -> str:
        """
        Query for custom roles analysis including unused roles and privilege assessment

        Returns:
            KQL query string for custom roles analysis
        """
        return """
        AuthorizationResources
        | where type == 'microsoft.authorization/roledefinitions'
        | where properties.type == 'CustomRole'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Global/System'
        )
        | extend RoleName = tostring(properties.roleName)
        | extend RoleDescription = tostring(properties.description)
        | extend CreatedDate = todatetime(properties.createdOn)
        | extend UpdatedDate = todatetime(properties.updatedOn)
        | extend DaysOld = datetime_diff('day', now(), CreatedDate)
        | extend DaysSinceUpdate = datetime_diff('day', now(), UpdatedDate)
        | extend AssignableScopes = properties.assignableScopes
        | extend Permissions = properties.permissions
        | extend Actions = properties.permissions[0].actions
        | extend NotActions = properties.permissions[0].notActions
        | extend DataActions = properties.permissions[0].dataActions
        | join kind=leftouter (
            // Get usage count from role assignments
            AuthorizationResources
            | where type == 'microsoft.authorization/roleassignments'
            | summarize AssignmentCount = count() by RoleDefinitionId = tostring(properties.roleDefinitionId)
        ) on $left.id == $right.RoleDefinitionId
        | extend UsageStatus = case(
            AssignmentCount == 0, 'Unused Custom Role',
            AssignmentCount == 1, 'Single Assignment',
            AssignmentCount <= 5, 'Limited Usage',
            'Active Usage'
        )
        | extend PrivilegeLevel = case(
            Actions has_any ('*', 'Microsoft.Authorization/*', 'Microsoft.Resources/*'), 'High Privilege - Broad Permissions',
            array_length(Actions) > 50, 'High Privilege - Many Actions',
            Actions has_any ('*/write', '*/delete'), 'Medium Privilege - Write/Delete Permissions',
            Actions has_any ('*/read'), 'Low Privilege - Read Only',
            'Unknown Privilege Level'
        )
        | extend ScopeRisk = case(
            AssignableScopes has '/' or AssignableScopes has '/subscriptions/', 'High - Broad Scope Assignment',
            array_length(AssignableScopes) > 5, 'Medium - Multiple Scopes',
            'Low - Limited Scope'
        )
        | extend SecurityRisk = case(
            UsageStatus == 'Unused Custom Role' and DaysOld > 90, 'High - Unused role >90 days old',
            PrivilegeLevel contains 'High Privilege' and ScopeRisk contains 'High', 'High - High privilege with broad scope',
            UsageStatus == 'Unused Custom Role', 'Medium - Unused custom role',
            PrivilegeLevel contains 'High Privilege', 'Medium - High privilege custom role',
            ScopeRisk contains 'High', 'Medium - Broad scope assignment',
            'Low - Standard custom role'
        )
        | extend RoleDetails = strcat(
            'Age: ', tostring(DaysOld), ' days',
            ' | Last Updated: ', tostring(DaysSinceUpdate), ' days ago',
            ' | Assignments: ', case(isempty(AssignmentCount), '0', tostring(AssignmentCount)),
            ' | Actions: ', tostring(array_length(Actions))
        )
        | project
            Application,
            RoleName,
            UsageStatus,
            PrivilegeLevel,
            ScopeRisk,
            SecurityRisk,
            RoleDetails,
            AssignmentCount = case(isempty(AssignmentCount), 0, AssignmentCount),
            ActionsCount = array_length(Actions),
            AssignableScopesCount = array_length(AssignableScopes),
            DaysOld,
            DaysSinceUpdate,
            RoleDescription,
            ResourceGroup = resourceGroup,
            SubscriptionId = subscriptionId,
            ResourceId = id
        | order by Application, SecurityRisk desc, UsageStatus desc, RoleName
        """

    @staticmethod
    def get_iam_compliance_summary_query() -> str:
        """
        Query for IAM compliance summary by application

        Returns:
            KQL query string for IAM compliance summary
        """
        return """
        // Role Assignments Analysis
        AuthorizationResources
        | where type == 'microsoft.authorization/roleassignments'
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Global/Untagged'
        )
        | extend IsHighPrivilege = (properties.roleDefinitionId contains 'Owner' or 
                                   properties.roleDefinitionId contains 'Contributor' or 
                                   properties.roleDefinitionId contains 'User Access Administrator')
        | extend IsGuestUser = (tostring(properties.principalType) == 'User' and tostring(properties.principalId) contains '#EXT#')
        | extend HasSecurityIssue = (IsHighPrivilege == true or IsGuestUser == true)
        | summarize 
            TotalRoleAssignments = count(),
            HighPrivilegeAssignments = countif(IsHighPrivilege == true),
            GuestUserAssignments = countif(IsGuestUser == true),
            RoleAssignmentsWithIssues = countif(HasSecurityIssue == true)
        by Application
        | join kind=fullouter (
            // Key Vault Analysis
            Resources
            | where type == 'microsoft.keyvault/vaults'
            | extend Application = case(
                isnotempty(tags.Application), tags.Application,
                isnotempty(tags.app), tags.app,
                'Untagged/Orphaned'
            )
            | extend HasPurgeProtection = tobool(properties.enablePurgeProtection)
            | extend HasSoftDelete = tobool(properties.enableSoftDelete)
            | extend HasNetworkRestrictions = (tostring(properties.networkAcls.defaultAction) == 'Deny')
            | extend HasSecurityIssue = not(HasPurgeProtection and HasSoftDelete and HasNetworkRestrictions)
            | summarize 
                TotalKeyVaults = count(),
                SecureKeyVaults = countif(HasSecurityIssue == false),
                KeyVaultsWithIssues = countif(HasSecurityIssue == true)
            by Application
        ) on Application
        | join kind=fullouter (
            // Managed Identities Analysis
            Resources
            | where type == 'microsoft.managedidentity/userassignedidentities'
            | extend Application = case(
                isnotempty(tags.Application), tags.Application,
                isnotempty(tags.app), tags.app,
                'Untagged/Orphaned'
            )
            | extend DaysOld = datetime_diff('day', now(), todatetime(properties.timeCreated))
            | extend IsOrphaned = (DaysOld > 90) // Simplified orphan detection
            | summarize 
                TotalManagedIdentities = count(),
                OrphanedIdentities = countif(IsOrphaned == true),
                IdentitiesWithIssues = countif(IsOrphaned == true)
            by Application
        ) on Application
        | extend Application = coalesce(Application, Application1, Application2)
        | extend TotalRoleAssignments = coalesce(TotalRoleAssignments, 0)
        | extend HighPrivilegeAssignments = coalesce(HighPrivilegeAssignments, 0)
        | extend GuestUserAssignments = coalesce(GuestUserAssignments, 0)
        | extend RoleAssignmentsWithIssues = coalesce(RoleAssignmentsWithIssues, 0)
        | extend TotalKeyVaults = coalesce(TotalKeyVaults, 0)
        | extend SecureKeyVaults = coalesce(SecureKeyVaults, 0)
        | extend KeyVaultsWithIssues = coalesce(KeyVaultsWithIssues, 0)
        | extend TotalManagedIdentities = coalesce(TotalManagedIdentities, 0)
        | extend OrphanedIdentities = coalesce(OrphanedIdentities, 0)
        | extend IdentitiesWithIssues = coalesce(IdentitiesWithIssues, 0)
        | extend TotalIAMResources = TotalRoleAssignments + TotalKeyVaults + TotalManagedIdentities
        | extend TotalIssues = RoleAssignmentsWithIssues + KeyVaultsWithIssues + IdentitiesWithIssues
        | extend IAMComplianceScore = case(
            TotalIAMResources == 0, 100.0,
            round((TotalIAMResources - TotalIssues) * 100.0 / TotalIAMResources, 1)
        )
        | extend IAMComplianceStatus = case(
            IAMComplianceScore >= 95, 'Excellent',
            IAMComplianceScore >= 85, 'Good',
            IAMComplianceScore >= 70, 'Acceptable',
            IAMComplianceScore >= 50, 'Needs Improvement',
            'Critical Issues'
        )
        | project 
            Application,
            TotalIAMResources,
            TotalRoleAssignments,
            HighPrivilegeAssignments,
            GuestUserAssignments,
            TotalKeyVaults,
            SecureKeyVaults,
            TotalManagedIdentities,
            OrphanedIdentities,
            TotalIssues,
            IAMComplianceScore,
            IAMComplianceStatus
        | where Application != ""
        | order by Application
        """
