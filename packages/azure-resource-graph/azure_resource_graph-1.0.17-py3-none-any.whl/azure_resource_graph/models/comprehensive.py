from pydantic import BaseModel, Field


class ComplianceSummary(BaseModel):
    """Legacy compliance summary model for backward compatibility"""

    application: str = Field(..., description="Application name")
    total_resources: int = Field(..., description="Total number of resources")
    compliant_resources: int = Field(..., description="Number of compliant resources")
    non_compliant_resources: int = Field(..., description="Number of non-compliant resources")
    compliance_percentage: float = Field(..., description="Compliance percentage")
    compliance_status: str = Field(..., description="Overall compliance status")

    @property
    def is_fully_compliant(self) -> bool:
        """Check if application is fully compliant"""
        return self.compliance_percentage == 100.0

    @property
    def compliance_grade(self) -> str:
        """Get compliance grade"""
        if self.compliance_percentage >= 95:
            return "A"
        elif self.compliance_percentage >= 90:
            return "B"
        elif self.compliance_percentage >= 80:
            return "C"
        elif self.compliance_percentage >= 70:
            return "D"
        else:
            return "F"

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_fully_compliant else "⚠️" if self.compliance_percentage >= 80 else "❌"
        return f"{status_emoji} {self.application}: {self.compliance_percentage}% compliant ({self.compliant_resources}/{self.total_resources}) - Grade {self.compliance_grade}"


class ComprehensiveSecuritySummary(BaseModel):
    """Comprehensive security summary combining storage and network analysis"""

    application: str = Field(..., description="Application name")
    storage_compliance_percentage: float = Field(..., description="Storage compliance percentage")
    network_security_score: float = Field(..., description="Network security score percentage")
    total_resources: int = Field(..., description="Total resources (storage + network)")
    critical_issues_count: int = Field(..., description="Number of critical security issues")
    optimization_opportunities: int = Field(..., description="Number of cost optimization opportunities")

    @property
    def overall_security_score(self) -> float:
        """Calculate weighted overall security score"""
        # Weight storage and network equally
        return (self.storage_compliance_percentage + self.network_security_score) / 2

    @property
    def security_posture(self) -> str:
        """Get overall security posture"""
        score = self.overall_security_score
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Fair"
        elif score >= 60:
            return "Poor"
        else:
            return "Critical"

    @property
    def requires_immediate_attention(self) -> bool:
        """Check if application requires immediate security attention"""
        return self.critical_issues_count > 0 or self.overall_security_score < 70

    @property
    def overall_grade(self) -> str:
        """Get overall security grade"""
        score = self.overall_security_score
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 65:
            return "D+"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def __str__(self) -> str:
        posture_emoji = {
            "Excellent": "🏆",
            "Good": "✅",
            "Fair": "⚠️",
            "Poor": "❌",
            "Critical": "🚨"
        }.get(self.security_posture, "❓")

        return f"{posture_emoji} {self.application}: {self.overall_security_score:.1f}% overall ({self.security_posture}) - Grade {self.overall_grade}"


class RoleAssignmentResult(BaseModel):
    """Role assignment analysis result including privilege and guest user assessment"""

    application: str = Field(..., description="Application name from tags")
    assignment_name: str = Field(..., description="Name of the role assignment")
    principal_id: str = Field(..., description="Principal ID (user, service principal, or group)")
    principal_type: str = Field(..., description="Type of principal")
    role_name: str = Field(..., description="Name of the assigned role")
    role_type: str = Field(..., description="Type of role (Built-in or Custom)")
    scope_level: str = Field(..., description="Level of assignment scope")
    privilege_level: str = Field(..., description="Privilege level assessment")
    guest_user_risk: str = Field(..., description="Guest user risk assessment")
    security_risk: str = Field(..., description="Security risk level")
    assignment_details: str = Field(..., description="Additional assignment details")
    resource_group: str = Field(..., description="Azure resource group name")
    subscription_id: str = Field(..., description="Azure subscription ID")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_high_privilege(self) -> bool:
        """Check if this is a high privilege role assignment"""
        return "High Privilege" in self.privilege_level

    @property
    def is_guest_user(self) -> bool:
        """Check if this assignment is for a guest user"""
        return "Guest User" in self.guest_user_risk

    @property
    def is_custom_role(self) -> bool:
        """Check if this uses a custom role"""
        return self.role_type == "CustomRole" or "Custom" in self.privilege_level

    @property
    def is_high_risk(self) -> bool:
        """Check if this assignment is high security risk"""
        return self.security_risk.lower().startswith("high")

    @property
    def is_broad_scope(self) -> bool:
        """Check if assignment has broad scope"""
        return self.scope_level in ["Subscription", "Management Group"]

    @property
    def risk_level(self) -> str:
        """Extract risk level from security_risk field"""
        return self.security_risk.split(" - ")[0] if " - " in self.security_risk else self.security_risk

    def __str__(self) -> str:
        risk_emoji = "❌" if self.is_high_risk else "⚠️" if self.risk_level.lower() == "medium" else "✅"
        privilege_icon = "🔴" if self.is_high_privilege else "🟡" if self.is_custom_role else "🟢"
        guest_icon = "👤" if self.is_guest_user else ""
        return f"{risk_emoji} {privilege_icon} {guest_icon} {self.application}/{self.role_name} -> {self.principal_type} - {self.security_risk}"


class KeyVaultSecurityResult(BaseModel):
    """Key Vault security analysis result including certificates and access policies"""

    application: str = Field(..., description="Application name from tags")
    vault_name: str = Field(..., description="Name of the Key Vault")
    certificate_configuration: str = Field(..., description="Certificate configuration assessment")
    network_security: str = Field(..., description="Network security configuration")
    purge_protection_status: str = Field(..., description="Purge protection status")
    security_findings: str = Field(..., description="Security assessment findings")
    security_risk: str = Field(..., description="Security risk level")
    vault_details: str = Field(..., description="Additional vault configuration details")
    access_policies_count: int = Field(..., description="Number of access policies configured")
    network_rules_count: int = Field(..., description="Number of network rules configured")
    soft_delete_retention_days: int = Field(..., description="Soft delete retention in days")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def has_purge_protection(self) -> bool:
        """Check if purge protection is enabled"""
        return "Enabled" in self.purge_protection_status

    @property
    def has_network_restrictions(self) -> bool:
        """Check if network access restrictions are configured"""
        return "Restricted" in self.network_security

    @property
    def is_public_access(self) -> bool:
        """Check if vault allows public access"""
        return "Public Access" in self.network_security

    @property
    def is_high_risk(self) -> bool:
        """Check if Key Vault configuration is high risk"""
        return self.security_risk.lower().startswith("high")

    @property
    def has_many_access_policies(self) -> bool:
        """Check if vault has many access policies"""
        return self.access_policies_count > 10

    @property
    def is_compliant(self) -> bool:
        """Check if Key Vault meets security compliance standards"""
        return (self.has_purge_protection and
                self.has_network_restrictions and
                not self.is_high_risk)

    @property
    def risk_level(self) -> str:
        """Extract risk level from security_risk field"""
        return self.security_risk.split(" - ")[0] if " - " in self.security_risk else self.security_risk

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_compliant else "❌" if self.is_high_risk else "⚠️"
        protection_icon = "🛡️" if self.has_purge_protection else "⚠️"
        network_icon = "🔒" if self.has_network_restrictions else "🌐"
        return f"{status_emoji} {protection_icon} {network_icon} {self.application}/{self.vault_name} - {self.security_risk}"


class ManagedIdentityResult(BaseModel):
    """Managed identity analysis result including usage patterns and orphan detection"""

    application: str = Field(..., description="Application name from tags")
    identity_name: str = Field(..., description="Name of the managed identity")
    usage_pattern: str = Field(..., description="Usage pattern assessment")
    orphaned_status: str = Field(..., description="Orphaned status assessment")
    security_risk: str = Field(..., description="Security risk level")
    identity_details: str = Field(..., description="Additional identity details")
    role_assignments_count: int = Field(..., description="Number of role assignments")
    associated_vms_count: int = Field(..., description="Number of associated VMs")
    associated_app_services_count: int = Field(..., description="Number of associated App Services")
    days_old: int = Field(..., description="Age of the identity in days")
    client_id: str = Field(..., description="Client ID of the managed identity")
    principal_id: str = Field(..., description="Principal ID of the managed identity")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_orphaned(self) -> bool:
        """Check if identity is orphaned"""
        return "Orphaned" in self.orphaned_status

    @property
    def is_in_use(self) -> bool:
        """Check if identity is actively in use"""
        return self.orphaned_status == "In Use"

    @property
    def is_high_risk(self) -> bool:
        """Check if identity is high security risk"""
        return self.security_risk.lower().startswith("high")

    @property
    def has_associations(self) -> bool:
        """Check if identity has resource associations"""
        return self.associated_vms_count > 0 or self.associated_app_services_count > 0

    @property
    def has_role_assignments(self) -> bool:
        """Check if identity has role assignments"""
        return self.role_assignments_count > 0

    @property
    def is_stale(self) -> bool:
        """Check if identity is potentially stale"""
        return self.days_old > 90 and not self.is_in_use

    @property
    def is_multi_resource(self) -> bool:
        """Check if identity is used by multiple resource types"""
        return "Multi-Resource" in self.usage_pattern

    @property
    def risk_level(self) -> str:
        """Extract risk level from security_risk field"""
        return self.security_risk.split(" - ")[0] if " - " in self.security_risk else self.security_risk

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_in_use else "❌" if self.is_orphaned else "⚠️"
        usage_icon = "🔗" if self.has_associations else "👤" if self.has_role_assignments else "❓"
        age_icon = "📅" if self.is_stale else ""
        return f"{status_emoji} {usage_icon} {age_icon} {self.application}/{self.identity_name} - {self.orphaned_status} ({self.days_old}d old)"


class CustomRoleResult(BaseModel):
    """Custom role analysis result including usage and privilege assessment"""

    application: str = Field(..., description="Application name from tags")
    role_name: str = Field(..., description="Name of the custom role")
    usage_status: str = Field(..., description="Usage status assessment")
    privilege_level: str = Field(..., description="Privilege level assessment")
    scope_risk: str = Field(..., description="Scope risk assessment")
    security_risk: str = Field(..., description="Security risk level")
    role_details: str = Field(..., description="Additional role details")
    assignment_count: int = Field(..., description="Number of role assignments")
    actions_count: int = Field(..., description="Number of actions in role")
    assignable_scopes_count: int = Field(..., description="Number of assignable scopes")
    days_old: int = Field(..., description="Age of the role in days")
    days_since_update: int = Field(..., description="Days since last update")
    role_description: str = Field(..., description="Description of the custom role")
    resource_group: str = Field(..., description="Azure resource group name")
    subscription_id: str = Field(..., description="Azure subscription ID")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_unused(self) -> bool:
        """Check if custom role is unused"""
        return "Unused" in self.usage_status

    @property
    def is_high_privilege(self) -> bool:
        """Check if role has high privileges"""
        return "High Privilege" in self.privilege_level

    @property
    def has_broad_scope(self) -> bool:
        """Check if role has broad scope"""
        return "High" in self.scope_risk

    @property
    def is_high_risk(self) -> bool:
        """Check if custom role is high security risk"""
        return self.security_risk.lower().startswith("high")

    @property
    def is_stale(self) -> bool:
        """Check if role is stale (old and unused)"""
        return self.is_unused and self.days_old > 90

    @property
    def has_many_actions(self) -> bool:
        """Check if role has many actions"""
        return self.actions_count > 20

    @property
    def is_actively_used(self) -> bool:
        """Check if role is actively used"""
        return self.assignment_count > 1

    @property
    def risk_level(self) -> str:
        """Extract risk level from security_risk field"""
        return self.security_risk.split(" - ")[0] if " - " in self.security_risk else self.security_risk

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_actively_used else "❌" if self.is_unused else "⚠️"
        privilege_icon = "🔴" if self.is_high_privilege else "🟡" if self.has_many_actions else "🟢"
        scope_icon = "🌐" if self.has_broad_scope else "🏠"
        return f"{status_emoji} {privilege_icon} {scope_icon} {self.application}/{self.role_name} - {self.usage_status} ({self.assignment_count} assignments)"


class IAMComplianceSummary(BaseModel):
    """IAM compliance summary for an application"""

    application: str = Field(..., description="Application name")
    total_iam_resources: int = Field(..., description="Total IAM resources")
    total_role_assignments: int = Field(..., description="Total role assignments")
    high_privilege_assignments: int = Field(..., description="High privilege role assignments")
    guest_user_assignments: int = Field(..., description="Guest user assignments")
    total_key_vaults: int = Field(..., description="Total Key Vaults")
    secure_key_vaults: int = Field(..., description="Securely configured Key Vaults")
    total_managed_identities: int = Field(..., description="Total managed identities")
    orphaned_identities: int = Field(..., description="Orphaned managed identities")
    total_issues: int = Field(..., description="Total IAM security issues")
    iam_compliance_score: float = Field(..., description="IAM compliance score percentage")
    iam_compliance_status: str = Field(..., description="Overall IAM compliance status")

    @property
    def is_iam_compliant(self) -> bool:
        """Check if application IAM is compliant"""
        return self.iam_compliance_score >= 90.0

    @property
    def iam_compliance_grade(self) -> str:
        """Get IAM compliance grade"""
        if self.iam_compliance_score >= 95:
            return "A"
        elif self.iam_compliance_score >= 85:
            return "B"
        elif self.iam_compliance_score >= 70:
            return "C"
        elif self.iam_compliance_score >= 60:
            return "D"
        else:
            return "F"

    @property
    def has_critical_iam_issues(self) -> bool:
        """Check if there are critical IAM issues"""
        return self.total_issues > 0 and self.iam_compliance_score < 70

    @property
    def privilege_escalation_risk(self) -> bool:
        """Check if there's privilege escalation risk"""
        return self.high_privilege_assignments > (self.total_role_assignments * 0.2)  # More than 20% high privilege

    @property
    def guest_user_risk_ratio(self) -> float:
        """Get guest user risk ratio"""
        if self.total_role_assignments == 0:
            return 0.0
        return (self.guest_user_assignments / self.total_role_assignments) * 100

    @property
    def identity_hygiene_score(self) -> float:
        """Get identity hygiene score based on orphaned identities"""
        if self.total_managed_identities == 0:
            return 100.0
        return ((self.total_managed_identities - self.orphaned_identities) / self.total_managed_identities) * 100

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_iam_compliant else "⚠️" if self.iam_compliance_score >= 70 else "❌"
        privilege_warning = "🔴" if self.privilege_escalation_risk else ""
        guest_warning = "👤" if self.guest_user_assignments > 0 else ""
        return f"{status_emoji} {privilege_warning} {guest_warning} {self.application}: {self.iam_compliance_score:.1f}% IAM compliant ({self.total_issues} issues) - Grade {self.iam_compliance_grade}"


class AKSClusterSecurityResult(BaseModel):
    """AKS cluster security analysis result including RBAC, networking, and compliance"""

    application: str = Field(..., description="Application name from tags")
    cluster_name: str = Field(..., description="Name of the AKS cluster")
    cluster_version: str = Field(..., description="Kubernetes version")
    network_configuration: str = Field(..., description="Network plugin and policy configuration")
    rbac_configuration: str = Field(..., description="RBAC and Azure AD configuration")
    api_server_access: str = Field(..., description="API server access configuration")
    security_findings: str = Field(..., description="Security assessment findings")
    security_risk: str = Field(..., description="Security risk level")
    cluster_compliance: str = Field(..., description="Overall compliance status")
    cluster_details: str = Field(..., description="Additional cluster configuration details")
    node_pool_count: int = Field(..., description="Number of node pools")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_private_cluster(self) -> bool:
        """Check if cluster uses private endpoint"""
        return "Private Endpoint" in self.api_server_access

    @property
    def has_rbac_enabled(self) -> bool:
        """Check if RBAC is properly configured"""
        return "RBAC" in self.rbac_configuration and "No RBAC" not in self.rbac_configuration

    @property
    def has_azure_ad_integration(self) -> bool:
        """Check if Azure AD integration is enabled"""
        return "Azure AD" in self.rbac_configuration

    @property
    def has_network_policy(self) -> bool:
        """Check if network policies are configured"""
        return "Policy: None" not in self.network_configuration

    @property
    def is_compliant(self) -> bool:
        """Check if cluster security configuration is compliant"""
        return self.cluster_compliance == "Compliant - Security Configured"

    @property
    def is_high_risk(self) -> bool:
        """Check if cluster has high security risk"""
        return self.security_risk.lower().startswith("high")

    @property
    def risk_level(self) -> str:
        """Extract risk level from security_risk field"""
        return self.security_risk.split(" - ")[0] if " - " in self.security_risk else self.security_risk

    @property
    def compliance_grade(self) -> str:
        """Get compliance grade based on configuration"""
        if self.is_compliant and self.has_azure_ad_integration and self.is_private_cluster:
            return "A"
        elif self.is_compliant:
            return "B"
        elif "Partially Compliant" in self.cluster_compliance:
            return "C"
        else:
            return "F"

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_compliant else "❌" if self.is_high_risk else "⚠️"
        rbac_icon = "🔐" if self.has_azure_ad_integration else "🔒" if self.has_rbac_enabled else "🔓"
        network_icon = "🔒" if self.is_private_cluster else "🌐"
        return f"{status_emoji} {rbac_icon} {network_icon} {self.application}/{self.cluster_name} (K8s {self.cluster_version}) - {self.security_risk}"


class AKSNodePoolResult(BaseModel):
    """AKS node pool analysis result including sizing, scaling, and optimization"""

    application: str = Field(..., description="Application name from tags")
    cluster_name: str = Field(..., description="Name of the AKS cluster")
    node_pool_name: str = Field(..., description="Name of the node pool")
    node_pool_type: str = Field(..., description="Type of node pool")
    vm_size: str = Field(..., description="VM size for nodes")
    vm_size_category: str = Field(..., description="VM size category")
    scaling_configuration: str = Field(..., description="Scaling configuration details")
    security_configuration: str = Field(..., description="Security configuration details")
    optimization_potential: str = Field(..., description="Cost optimization potential")
    node_pool_risk: str = Field(..., description="Node pool risk assessment")
    node_pool_details: str = Field(..., description="Additional node pool details")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_system_pool(self) -> bool:
        """Check if this is a system node pool"""
        return "System" in self.node_pool_details

    @property
    def is_auto_scaling_enabled(self) -> bool:
        """Check if auto-scaling is enabled"""
        return "Auto:" in self.scaling_configuration

    @property
    def is_legacy_vm_size(self) -> bool:
        """Check if using legacy VM sizes"""
        return self.vm_size_category == "Basic/Legacy"

    @property
    def has_host_encryption(self) -> bool:
        """Check if host encryption is enabled"""
        return "Encryption" in self.security_configuration

    @property
    def is_high_risk(self) -> bool:
        """Check if node pool has high risk"""
        return self.node_pool_risk.lower().startswith("high")

    @property
    def has_high_optimization_potential(self) -> bool:
        """Check if node pool has high optimization potential"""
        return "High" in self.optimization_potential

    @property
    def optimization_priority(self) -> str:
        """Get optimization priority level"""
        if self.has_high_optimization_potential:
            return "High"
        elif "Medium" in self.optimization_potential:
            return "Medium"
        else:
            return "Low"

    @property
    def risk_level(self) -> str:
        """Extract risk level from node_pool_risk field"""
        return self.node_pool_risk.split(" - ")[0] if " - " in self.node_pool_risk else self.node_pool_risk

    def __str__(self) -> str:
        risk_emoji = "❌" if self.is_high_risk else "⚠️" if self.risk_level.lower() == "medium" else "✅"
        pool_icon = "🖥️" if self.is_system_pool else "⚙️"
        scaling_icon = "📈" if self.is_auto_scaling_enabled else "📊"
        return f"{risk_emoji} {pool_icon} {scaling_icon} {self.application}/{self.cluster_name}/{self.node_pool_name} ({self.vm_size}) - {self.optimization_potential}"


class ContainerRegistrySecurityResult(BaseModel):
    """Container Registry security analysis result including access controls and policies"""

    application: str = Field(..., description="Application name from tags")
    registry_name: str = Field(..., description="Name of the container registry")
    registry_sku: str = Field(..., description="Registry SKU tier")
    network_security: str = Field(..., description="Network security configuration")
    access_control: str = Field(..., description="Access control configuration")
    security_policies: str = Field(..., description="Security policies configuration")
    security_findings: str = Field(..., description="Security assessment findings")
    security_risk: str = Field(..., description="Security risk level")
    compliance_status: str = Field(..., description="Overall compliance status")
    registry_details: str = Field(..., description="Additional registry details")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_private_access_only(self) -> bool:
        """Check if registry uses private access only"""
        return "Private Access Only" in self.network_security

    @property
    def has_admin_user_enabled(self) -> bool:
        """Check if admin user is enabled"""
        return "Admin User" in self.access_control

    @property
    def has_content_trust(self) -> bool:
        """Check if content trust is enabled"""
        return "Trust" in self.security_policies

    @property
    def has_quarantine_policy(self) -> bool:
        """Check if quarantine policy is enabled"""
        return "Quarantine" in self.security_policies

    @property
    def is_premium_sku(self) -> bool:
        """Check if using Premium SKU"""
        return self.registry_sku == "Premium"

    @property
    def is_compliant(self) -> bool:
        """Check if registry configuration is compliant"""
        return self.compliance_status == "Compliant"

    @property
    def is_high_risk(self) -> bool:
        """Check if registry has high security risk"""
        return self.security_risk.lower().startswith("high")

    @property
    def is_publicly_accessible(self) -> bool:
        """Check if registry is publicly accessible"""
        return "Unrestricted Public Access" in self.network_security

    @property
    def risk_level(self) -> str:
        """Extract risk level from security_risk field"""
        return self.security_risk.split(" - ")[0] if " - " in self.security_risk else self.security_risk

    @property
    def compliance_grade(self) -> str:
        """Get compliance grade"""
        if self.is_compliant and self.is_private_access_only and self.has_content_trust:
            return "A"
        elif self.is_compliant:
            return "B"
        elif "Partially Compliant" in self.compliance_status:
            return "C"
        else:
            return "F"

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_compliant else "❌" if self.is_high_risk else "⚠️"
        access_icon = "🔒" if self.is_private_access_only else "🌐"
        trust_icon = "🛡️" if self.has_content_trust else "⚠️"
        return f"{status_emoji} {access_icon} {trust_icon} {self.application}/{self.registry_name} ({self.registry_sku}) - {self.security_risk}"


class AppServiceSecurityResult(BaseModel):
    """App Service security analysis result including TLS, authentication, and network security"""

    application: str = Field(..., description="Application name from tags")
    app_service_name: str = Field(..., description="Name of the App Service")
    app_service_kind: str = Field(..., description="Kind of App Service")
    tls_configuration: str = Field(..., description="TLS/HTTPS configuration")
    network_security: str = Field(..., description="Network security configuration")
    authentication_method: str = Field(..., description="Authentication method configuration")
    security_findings: str = Field(..., description="Security assessment findings")
    security_risk: str = Field(..., description="Security risk level")
    compliance_status: str = Field(..., description="Overall compliance status")
    app_service_details: str = Field(..., description="Additional App Service details")
    custom_domain_count: int = Field(..., description="Number of custom domains")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_https_only(self) -> bool:
        """Check if HTTPS only is enabled"""
        return "HTTPS Only" in self.tls_configuration

    @property
    def has_modern_tls(self) -> bool:
        """Check if using modern TLS version"""
        return "TLS 1.2" in self.tls_configuration

    @property
    def has_legacy_tls(self) -> bool:
        """Check if using legacy TLS versions"""
        return "TLS 1.0" in self.tls_configuration or "TLS 1.1" in self.tls_configuration

    @property
    def has_authentication_configured(self) -> bool:
        """Check if authentication is configured"""
        return "No Centralized Auth" not in self.authentication_method

    @property
    def has_managed_identity(self) -> bool:
        """Check if managed identity is configured"""
        return "Managed Identity" in self.authentication_method

    @property
    def is_network_restricted(self) -> bool:
        """Check if network access is restricted"""
        return "IP Restricted" in self.network_security or "Private Access Only" in self.network_security

    @property
    def is_compliant(self) -> bool:
        """Check if App Service configuration is compliant"""
        return self.compliance_status == "Compliant"

    @property
    def is_high_risk(self) -> bool:
        """Check if App Service has high security risk"""
        return self.security_risk.lower().startswith("high")

    @property
    def has_custom_domains(self) -> bool:
        """Check if App Service has custom domains"""
        return self.custom_domain_count > 0

    @property
    def risk_level(self) -> str:
        """Extract risk level from security_risk field"""
        return self.security_risk.split(" - ")[0] if " - " in self.security_risk else self.security_risk

    @property
    def compliance_grade(self) -> str:
        """Get compliance grade"""
        if self.is_compliant and self.has_modern_tls and self.has_authentication_configured:
            return "A"
        elif self.is_compliant:
            return "B"
        elif "Partially Compliant" in self.compliance_status:
            return "C"
        else:
            return "F"

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_compliant else "❌" if self.is_high_risk else "⚠️"
        tls_icon = "🔒" if self.has_modern_tls else "⚠️" if self.has_legacy_tls else "🔓"
        auth_icon = "🔐" if self.has_authentication_configured else "👤"
        return f"{status_emoji} {tls_icon} {auth_icon} {self.application}/{self.app_service_name} ({self.app_service_kind}) - {self.security_risk}"


class AppServiceSlotResult(BaseModel):
    """App Service deployment slot analysis result"""

    application: str = Field(..., description="Application name from tags")
    app_service_name: str = Field(..., description="Name of the parent App Service")
    slot_name: str = Field(..., description="Name of the deployment slot")
    slot_state: str = Field(..., description="Current state of the slot")
    slot_configuration: str = Field(..., description="Security configuration of the slot")
    slot_risk: str = Field(..., description="Risk assessment of the slot")
    slot_details: str = Field(..., description="Additional slot details")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_secure_configuration(self) -> bool:
        """Check if slot has secure configuration"""
        return "Secure Configuration" in self.slot_configuration

    @property
    def is_running(self) -> bool:
        """Check if slot is running"""
        return "Running" in self.slot_state

    @property
    def is_high_risk(self) -> bool:
        """Check if slot has high risk"""
        return self.slot_risk.lower().startswith("high")

    @property
    def risk_level(self) -> str:
        """Extract risk level from slot_risk field"""
        return self.slot_risk.split(" - ")[0] if " - " in self.slot_risk else self.slot_risk

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_secure_configuration else "❌" if self.is_high_risk else "⚠️"
        state_icon = "🟢" if self.is_running else "🔴"
        return f"{status_emoji} {state_icon} {self.application}/{self.app_service_name}/{self.slot_name} - {self.slot_risk}"


class ContainerWorkloadsComplianceSummary(BaseModel):
    """Container & Modern Workloads compliance summary for an application"""

    application: str = Field(..., description="Application name")
    total_container_workloads: int = Field(..., description="Total container workload resources")
    total_aks_clusters: int = Field(..., description="Total AKS clusters")
    secure_aks_clusters: int = Field(..., description="Securely configured AKS clusters")
    total_container_registries: int = Field(..., description="Total container registries")
    secure_container_registries: int = Field(..., description="Securely configured container registries")
    total_app_services: int = Field(..., description="Total App Services")
    secure_app_services: int = Field(..., description="Securely configured App Services")
    container_workloads_with_issues: int = Field(..., description="Container workloads with security issues")
    container_workloads_compliance_score: float = Field(..., description="Container workloads compliance score percentage")
    container_workloads_compliance_status: str = Field(..., description="Overall container workloads compliance status")

    @property
    def is_container_workloads_compliant(self) -> bool:
        """Check if container workloads are compliant"""
        return self.container_workloads_compliance_score >= 90.0

    @property
    def container_workloads_compliance_grade(self) -> str:
        """Get container workloads compliance grade"""
        if self.container_workloads_compliance_score >= 95:
            return "A"
        elif self.container_workloads_compliance_score >= 85:
            return "B"
        elif self.container_workloads_compliance_score >= 70:
            return "C"
        elif self.container_workloads_compliance_score >= 60:
            return "D"
        else:
            return "F"

    @property
    def has_critical_container_issues(self) -> bool:
        """Check if there are critical container workloads issues"""
        return self.container_workloads_with_issues > 0 and self.container_workloads_compliance_score < 70

    @property
    def aks_security_ratio(self) -> float:
        """Get AKS security ratio"""
        if self.total_aks_clusters == 0:
            return 100.0
        return (self.secure_aks_clusters / self.total_aks_clusters) * 100

    @property
    def registry_security_ratio(self) -> float:
        """Get container registry security ratio"""
        if self.total_container_registries == 0:
            return 100.0
        return (self.secure_container_registries / self.total_container_registries) * 100

    @property
    def app_service_security_ratio(self) -> float:
        """Get App Service security ratio"""
        if self.total_app_services == 0:
            return 100.0
        return (self.secure_app_services / self.total_app_services) * 100

    @property
    def container_orchestration_maturity(self) -> str:
        """Assess container orchestration maturity"""
        if self.total_aks_clusters > 0 and self.total_container_registries > 0:
            if self.aks_security_ratio >= 90 and self.registry_security_ratio >= 90:
                return "Advanced"
            elif self.aks_security_ratio >= 70 or self.registry_security_ratio >= 70:
                return "Intermediate"
            else:
                return "Basic"
        elif self.total_app_services > 0:
            return "Traditional"
        else:
            return "None"

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_container_workloads_compliant else "⚠️" if self.container_workloads_compliance_score >= 70 else "❌"
        maturity_icon = {"Advanced": "🚀", "Intermediate": "⚙️", "Basic": "🔧", "Traditional": "🌐", "None": "❓"}.get(self.container_orchestration_maturity, "❓")
        return f"{status_emoji} {maturity_icon} {self.application}: {self.container_workloads_compliance_score:.1f}% container compliant ({self.container_workloads_with_issues} issues) - Grade {self.container_workloads_compliance_grade} ({self.container_orchestration_maturity})"
