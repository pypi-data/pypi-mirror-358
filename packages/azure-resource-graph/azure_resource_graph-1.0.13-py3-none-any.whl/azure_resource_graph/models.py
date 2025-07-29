#!/usr/bin/env python3
"""
Enhanced Pydantic models for Azure Resource Graph responses
Includes comprehensive storage and network analysis models
All field names use snake_case convention
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# VM GOVERNANCE MODELS
# ============================================================================

class VMSecurityResult(BaseModel):
    """VM security analysis result including encryption, extensions, and compliance"""

    application: str = Field(..., description="Application name from tags")
    vm_name: str = Field(..., description="Name of the virtual machine")
    os_type: str = Field(..., description="Operating system type (Windows/Linux)")
    vm_size: str = Field(..., description="VM size/SKU")
    power_state: str = Field(..., description="Current power state of the VM")
    disk_encryption: str = Field(..., description="Disk encryption status")
    security_extensions: str = Field(..., description="Security extensions installed")
    security_findings: str = Field(..., description="Security assessment findings")
    security_risk: str = Field(..., description="Security risk level")
    compliance_status: str = Field(..., description="Overall compliance status")
    vm_details: str = Field(..., description="Additional VM configuration details")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_compliant(self) -> bool:
        """Check if VM security configuration is compliant"""
        return self.compliance_status == "Compliant"

    @property
    def is_encrypted(self) -> bool:
        """Check if VM disk encryption is enabled"""
        return "Encrypted" in self.disk_encryption

    @property
    def is_high_risk(self) -> bool:
        """Check if VM has high security risk"""
        return self.security_risk.lower().startswith("high")

    @property
    def has_security_extensions(self) -> bool:
        """Check if VM has security extensions installed"""
        return "Extensions:" in self.security_extensions

    @property
    def is_running(self) -> bool:
        """Check if VM is currently running"""
        return self.power_state == "Running"

    @property
    def risk_level(self) -> str:
        """Extract risk level from security_risk field"""
        return self.security_risk.split(" - ")[0] if " - " in self.security_risk else self.security_risk

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_compliant else "❌" if self.is_high_risk else "⚠️"
        return f"{status_emoji} {self.application}/{self.vm_name} ({self.os_type}, {self.vm_size}) - {self.security_risk}"


class VMOptimizationResult(BaseModel):
    """VM sizing and optimization analysis result"""

    application: str = Field(..., description="Application name from tags")
    vm_name: str = Field(..., description="Name of the virtual machine")
    vm_size: str = Field(..., description="Current VM size/SKU")
    vm_size_category: str = Field(..., description="VM size category (e.g., General Purpose, Memory Optimized)")
    power_state: str = Field(..., description="Current power state of the VM")
    os_type: str = Field(..., description="Operating system type")
    utilization_status: str = Field(..., description="Resource utilization assessment")
    optimization_potential: str = Field(..., description="Cost optimization potential")
    optimization_recommendation: str = Field(..., description="Specific optimization recommendation")
    estimated_monthly_cost: str = Field(..., description="Estimated monthly cost category")
    days_running: int = Field(..., description="Number of days the VM has been running")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_stopped_but_allocated(self) -> bool:
        """Check if VM is stopped but still incurring costs"""
        return self.power_state == "Stopped"

    @property
    def is_legacy_size(self) -> bool:
        """Check if VM is using legacy/deprecated sizes"""
        return "Legacy" in self.vm_size_category

    @property
    def has_high_optimization_potential(self) -> bool:
        """Check if VM has high cost optimization potential"""
        return "High" in self.optimization_potential

    @property
    def is_recently_created(self) -> bool:
        """Check if VM was created recently"""
        return self.days_running < 7

    @property
    def is_expensive(self) -> bool:
        """Check if VM is in expensive cost category"""
        return self.estimated_monthly_cost in ["High", "Very High"]

    @property
    def optimization_priority(self) -> str:
        """Get optimization priority level"""
        if self.has_high_optimization_potential:
            return "High"
        elif "Medium" in self.optimization_potential:
            return "Medium"
        else:
            return "Low"

    def __str__(self) -> str:
        priority_emoji = "🔴" if self.optimization_priority == "High" else "🟡" if self.optimization_priority == "Medium" else "🟢"
        return f"{priority_emoji} {self.application}/{self.vm_name} ({self.vm_size}) - {self.optimization_potential}"


class VMExtensionResult(BaseModel):
    """VM extension analysis result"""

    application: str = Field(..., description="Application name from tags")
    vm_name: str = Field(..., description="Name of the virtual machine")
    extension_name: str = Field(..., description="Name of the VM extension")
    extension_type: str = Field(..., description="Type of the extension")
    extension_category: str = Field(..., description="Category of the extension (Security, Monitoring, etc.)")
    extension_publisher: str = Field(..., description="Publisher of the extension")
    extension_version: str = Field(..., description="Version of the extension")
    provisioning_state: str = Field(..., description="Provisioning state of the extension")
    extension_status: str = Field(..., description="Current status of the extension")
    security_importance: str = Field(..., description="Security importance level")
    compliance_impact: str = Field(..., description="Impact on compliance if extension fails")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_security_extension(self) -> bool:
        """Check if this is a security-related extension"""
        return "Security" in self.extension_category

    @property
    def is_monitoring_extension(self) -> bool:
        """Check if this is a monitoring-related extension"""
        return "Monitoring" in self.extension_category

    @property
    def is_backup_extension(self) -> bool:
        """Check if this is a backup-related extension"""
        return "Backup" in self.extension_category

    @property
    def is_healthy(self) -> bool:
        """Check if extension is in healthy state"""
        return self.extension_status == "Healthy"

    @property
    def is_critical(self) -> bool:
        """Check if extension is critical for security"""
        return self.security_importance == "Critical"

    @property
    def has_compliance_impact(self) -> bool:
        """Check if extension failure impacts compliance"""
        return not self.compliance_impact.lower().startswith("low")

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_healthy else "❌" if self.extension_status == "Failed" else "⚠️"
        importance_icon = "🔒" if self.is_security_extension else "📊" if self.is_monitoring_extension else "💾" if self.is_backup_extension else "⚙️"
        return f"{status_emoji} {importance_icon} {self.application}/{self.vm_name}: {self.extension_type} - {self.extension_status}"


class VMPatchComplianceResult(BaseModel):
    """VM patch compliance analysis result"""

    application: str = Field(..., description="Application name from tags")
    vm_name: str = Field(..., description="Name of the virtual machine")
    os_type: str = Field(..., description="Operating system type")
    power_state: str = Field(..., description="Current power state of the VM")
    automatic_updates_enabled: str = Field(..., description="Automatic updates configuration")
    patch_mode: str = Field(..., description="Patch management mode")
    patch_compliance_status: str = Field(..., description="Patch compliance status")
    patch_risk: str = Field(..., description="Patch management risk level")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_automated_patching(self) -> bool:
        """Check if VM has automated patching configured"""
        return "Automated" in self.patch_compliance_status

    @property
    def requires_manual_patching(self) -> bool:
        """Check if VM requires manual patch management"""
        return "Manual" in self.patch_compliance_status

    @property
    def is_high_risk(self) -> bool:
        """Check if VM has high patch management risk"""
        return self.patch_risk.lower().startswith("high")

    @property
    def is_platform_managed(self) -> bool:
        """Check if VM patching is platform managed"""
        return "Platform Managed" in self.patch_compliance_status

    @property
    def risk_level(self) -> str:
        """Extract risk level from patch_risk field"""
        return self.patch_risk.split(" - ")[0] if " - " in self.patch_risk else self.patch_risk

    def __str__(self) -> str:
        risk_emoji = "❌" if self.is_high_risk else "⚠️" if self.risk_level.lower() == "medium" else "✅"
        patch_icon = "🤖" if self.is_automated_patching else "👤"
        return f"{risk_emoji} {patch_icon} {self.application}/{self.vm_name} ({self.os_type}) - {self.patch_compliance_status}"


class VMGovernanceSummary(BaseModel):
    """VM governance compliance summary for an application"""

    application: str = Field(..., description="Application name")
    total_vms: int = Field(..., description="Total number of VMs")
    windows_vms: int = Field(..., description="Number of Windows VMs")
    linux_vms: int = Field(..., description="Number of Linux VMs")
    running_vms: int = Field(..., description="Number of running VMs")
    stopped_vms: int = Field(..., description="Number of stopped VMs")
    deallocated_vms: int = Field(..., description="Number of deallocated VMs")
    encrypted_vms: int = Field(..., description="Number of encrypted VMs")
    legacy_size_vms: int = Field(..., description="Number of VMs with legacy sizes")
    optimized_vms: int = Field(..., description="Number of optimized VMs")
    vms_with_issues: int = Field(..., description="Number of VMs with governance issues")
    governance_score: float = Field(..., description="Governance score percentage")
    governance_status: str = Field(..., description="Overall governance status")

    @property
    def encryption_coverage(self) -> float:
        """Get encryption coverage percentage"""
        if self.total_vms == 0:
            return 0.0
        return (self.encrypted_vms / self.total_vms) * 100

    @property
    def optimization_ratio(self) -> float:
        """Get optimization ratio percentage"""
        if self.total_vms == 0:
            return 0.0
        return (self.optimized_vms / self.total_vms) * 100

    @property
    def cost_waste_ratio(self) -> float:
        """Get percentage of VMs potentially wasting costs"""
        if self.total_vms == 0:
            return 0.0
        return ((self.stopped_vms + self.legacy_size_vms) / self.total_vms) * 100

    @property
    def is_well_governed(self) -> bool:
        """Check if VMs are well governed"""
        return self.governance_score >= 80.0

    @property
    def has_critical_issues(self) -> bool:
        """Check if there are critical governance issues"""
        return self.vms_with_issues > 0 and self.governance_score < 60

    @property
    def governance_grade(self) -> str:
        """Get governance grade"""
        if self.governance_score >= 95:
            return "A"
        elif self.governance_score >= 85:
            return "B"
        elif self.governance_score >= 70:
            return "C"
        elif self.governance_score >= 60:
            return "D"
        else:
            return "F"

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_well_governed else "⚠️" if self.governance_score >= 60 else "❌"
        return f"{status_emoji} {self.application}: {self.governance_score:.1f}% governed ({self.vms_with_issues} issues, {self.total_vms} VMs) - Grade {self.governance_grade}"


# ============================================================================
# NETWORK ANALYSIS MODELS
# ============================================================================

class NSGRule(BaseModel):
    """Network Security Group rule with risk assessment"""

    application: str = Field(..., description="Application name from tags")
    nsg_name: str = Field(..., description="Name of the Network Security Group")
    rule_name: str = Field(..., description="Name of the security rule")
    access: Literal["Allow", "Deny"] = Field(..., description="Rule access type")
    direction: Literal["Inbound", "Outbound"] = Field(..., description="Traffic direction")
    priority: int = Field(..., description="Rule priority (lower numbers have higher priority)")
    protocol: str = Field(..., description="Network protocol (TCP, UDP, *, etc.)")
    source_address_prefix: str = Field(..., description="Source address prefix or range")
    destination_address_prefix: str = Field(..., description="Destination address prefix or range")
    source_port_range: str = Field(..., description="Source port range")
    destination_port_range: str = Field(..., description="Destination port range")
    risk_level: str = Field(..., description="Risk assessment of the rule")
    resource_group: str = Field(..., description="Azure resource group name")
    resource_id: str = Field(..., description="Full Azure resource ID")

    class Config:
        allow_population_by_field_name = True

    @property
    def is_high_risk(self) -> bool:
        """Check if this rule is considered high risk"""
        return "High" in self.risk_level

    @property
    def is_internet_facing(self) -> bool:
        """Check if this rule allows traffic from the internet"""
        return self.source_address_prefix in ["*", "0.0.0.0/0", "Internet"]

    @property
    def allows_admin_ports(self) -> bool:
        """Check if this rule allows common admin ports (SSH, RDP)"""
        admin_ports = ["22", "3389"]
        return any(port in self.destination_port_range for port in admin_ports)

    def __str__(self) -> str:
        risk_emoji = "❌" if self.is_high_risk else "⚠️" if "Medium" in self.risk_level else "✅"
        return f"{risk_emoji} {self.application}/{self.nsg_name}/{self.rule_name} - {self.risk_level}"


class NetworkResource(BaseModel):
    """General network resource with security assessment"""

    application: str = Field(..., description="Application name from tags")
    network_resource: str = Field(..., description="Name of the network resource")
    network_resource_type: str = Field(..., description="Type of network resource")
    security_findings: str = Field(..., description="Security assessment findings")
    compliance_risk: str = Field(..., description="Compliance risk level")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    additional_details: str = Field(..., description="Additional configuration details")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def risk_level(self) -> str:
        """Extract risk level from compliance_risk field"""
        return self.compliance_risk.split(" - ")[0] if " - " in self.compliance_risk else self.compliance_risk

    @property
    def is_high_risk(self) -> bool:
        """Check if this resource is high risk"""
        return self.risk_level.lower() == "high"

    def __str__(self) -> str:
        risk_emoji = "❌" if self.is_high_risk else "⚠️" if self.risk_level.lower() == "medium" else "✅"
        return f"{risk_emoji} {self.application}/{self.network_resource} ({self.network_resource_type}) - {self.compliance_risk}"


class CertificateAnalysisResult(BaseModel):
    """SSL/TLS certificate analysis result"""

    application: str = Field(..., description="Application name from tags")
    resource_name: str = Field(..., description="Name of the resource (App Gateway/Load Balancer)")
    resource_type: str = Field(..., description="Type of resource")
    certificate_count: int = Field(..., description="Number of SSL certificates configured")
    ssl_policy_details: str = Field(..., description="SSL/TLS policy configuration details")
    compliance_status: str = Field(..., description="Certificate compliance status")
    security_risk: str = Field(..., description="Security risk level")
    listener_details: str = Field(..., description="Listener configuration details")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_compliant(self) -> bool:
        """Check if certificate configuration is compliant"""
        return "Compliant" in self.compliance_status

    @property
    def is_high_risk(self) -> bool:
        """Check if certificate configuration is high risk"""
        return self.security_risk.lower() == "high"

    @property
    def has_modern_tls(self) -> bool:
        """Check if using modern TLS versions"""
        return "Modern TLS" in self.compliance_status

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_compliant else "❌" if self.is_high_risk else "⚠️"
        return f"{status_emoji} {self.application}/{self.resource_name} ({self.resource_type}) - {self.compliance_status}"


class NetworkTopologyResult(BaseModel):
    """Network topology analysis result"""

    application: str = Field(..., description="Application name from tags")
    network_resource: str = Field(..., description="Name of the network resource")
    topology_type: str = Field(..., description="Type of topology component")
    network_configuration: str = Field(..., description="Network configuration details")
    configuration_risk: str = Field(..., description="Configuration risk level")
    security_implications: str = Field(..., description="Security implications")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def risk_level(self) -> str:
        """Extract risk level from configuration_risk field"""
        return self.configuration_risk.split(" - ")[0] if " - " in self.configuration_risk else self.configuration_risk

    @property
    def is_high_risk(self) -> bool:
        """Check if topology configuration is high risk"""
        return self.risk_level.lower() == "high"

    @property
    def has_ddos_protection(self) -> bool:
        """Check if DDoS protection is enabled"""
        return "DDoS" in self.network_configuration and "Enabled" in self.network_configuration

    def __str__(self) -> str:
        risk_emoji = "❌" if self.is_high_risk else "⚠️" if self.risk_level.lower() == "medium" else "✅"
        return f"{risk_emoji} {self.application}/{self.network_resource} ({self.topology_type}) - {self.configuration_risk}"


class ResourceOptimizationResult(BaseModel):
    """Network resource optimization analysis result"""

    application: str = Field(..., description="Application name from tags")
    resource_name: str = Field(..., description="Name of the resource")
    optimization_type: str = Field(..., description="Type of resource for optimization")
    utilization_status: str = Field(..., description="Resource utilization status")
    cost_optimization_potential: str = Field(..., description="Cost optimization potential")
    resource_details: str = Field(..., description="Resource configuration details")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_unused(self) -> bool:
        """Check if resource is unused"""
        return "Unused" in self.utilization_status

    @property
    def is_misconfigured(self) -> bool:
        """Check if resource is misconfigured"""
        return "Misconfigured" in self.utilization_status

    @property
    def has_high_optimization_potential(self) -> bool:
        """Check if resource has high cost optimization potential"""
        return "High" in self.cost_optimization_potential

    @property
    def optimization_priority(self) -> str:
        """Get optimization priority level"""
        if self.has_high_optimization_potential:
            return "High"
        elif "Medium" in self.cost_optimization_potential:
            return "Medium"
        else:
            return "Low"

    def __str__(self) -> str:
        priority_emoji = "🔴" if self.optimization_priority == "High" else "🟡" if self.optimization_priority == "Medium" else "🟢"
        return f"{priority_emoji} {self.application}/{self.resource_name} ({self.optimization_type}) - {self.cost_optimization_potential}"


class NetworkComplianceSummary(BaseModel):
    """Network security compliance summary for an application"""

    application: str = Field(..., description="Application name")
    total_network_resources: int = Field(..., description="Total network resources")
    nsg_count: int = Field(..., description="Number of NSGs")
    public_ip_count: int = Field(..., description="Number of Public IPs")
    app_gateway_count: int = Field(..., description="Number of Application Gateways")
    resources_with_issues: int = Field(..., description="Resources with security issues")
    security_score: float = Field(..., description="Security score percentage")
    security_status: str = Field(..., description="Overall security status")

    @property
    def is_secure(self) -> bool:
        """Check if application network is secure"""
        return self.security_score >= 90.0

    @property
    def security_grade(self) -> str:
        """Get security grade"""
        if self.security_score >= 95:
            return "A"
        elif self.security_score >= 90:
            return "B"
        elif self.security_score >= 80:
            return "C"
        elif self.security_score >= 70:
            return "D"
        else:
            return "F"

    @property
    def has_critical_issues(self) -> bool:
        """Check if there are critical security issues"""
        return self.resources_with_issues > 0 and self.security_score < 70

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_secure else "⚠️" if self.security_score >= 75 else "❌"
        return f"{status_emoji} {self.application}: {self.security_score}% secure ({self.resources_with_issues} issues) - Grade {self.security_grade}"


# ============================================================================
# STORAGE ANALYSIS MODELS
# ============================================================================

class StorageResource(BaseModel):
    """Storage resource with comprehensive security analysis"""

    application: str = Field(..., description="Application name from tags")
    storage_resource: str = Field(..., description="Name of the storage resource")
    storage_type: str = Field(..., description="Type of storage resource")
    encryption_method: str = Field(..., description="Encryption method used")
    security_findings: str = Field(..., description="Security assessment findings")
    compliance_risk: str = Field(..., description="Compliance risk level")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    additional_details: str = Field(..., description="Additional configuration details")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_compliant(self) -> bool:
        """Check if storage resource is compliant"""
        return not self.compliance_risk.startswith("High")

    @property
    def uses_customer_managed_keys(self) -> bool:
        """Check if using customer managed keys"""
        return "Customer Managed Key" in self.encryption_method

    @property
    def encryption_strength(self) -> str:
        """Get encryption strength level"""
        if self.uses_customer_managed_keys:
            return "Strong"
        elif "Platform Managed" in self.encryption_method:
            return "Standard"
        else:
            return "Weak"

    @property
    def risk_level(self) -> str:
        """Extract risk level from compliance_risk field"""
        return self.compliance_risk.split(" - ")[0] if " - " in self.compliance_risk else self.compliance_risk

    @property
    def is_high_risk(self) -> bool:
        """Check if this resource is high risk"""
        return self.risk_level.lower() == "high"

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_compliant else "❌" if self.is_high_risk else "⚠️"
        return f"{status_emoji} {self.application}/{self.storage_resource} ({self.storage_type}) - {self.compliance_risk}"


class StorageAccessControlResult(BaseModel):
    """Storage access control and network security analysis result"""

    application: str = Field(..., description="Application name from tags")
    resource_name: str = Field(..., description="Name of the storage resource")
    resource_type: str = Field(..., description="Type of storage resource")
    public_access: str = Field(..., description="Public access configuration")
    network_restrictions: str = Field(..., description="Network access restrictions")
    authentication_method: str = Field(..., description="Authentication method configured")
    security_risk: str = Field(..., description="Security risk level")
    access_details: str = Field(..., description="Additional access configuration details")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def allows_public_access(self) -> bool:
        """Check if resource allows public access"""
        return "Enabled" in self.public_access

    @property
    def has_network_restrictions(self) -> bool:
        """Check if network restrictions are configured"""
        return "No Network" not in self.network_restrictions

    @property
    def is_high_risk(self) -> bool:
        """Check if access configuration is high risk"""
        return self.security_risk.lower() == "high"

    @property
    def uses_modern_auth(self) -> bool:
        """Check if using modern authentication methods"""
        return "Azure AD" in self.authentication_method or "Identity-based" in self.authentication_method

    def __str__(self) -> str:
        risk_emoji = "❌" if self.is_high_risk else "⚠️" if self.security_risk.lower() == "medium" else "✅"
        return f"{risk_emoji} {self.application}/{self.resource_name} ({self.resource_type}) - {self.security_risk}"


class StorageBackupResult(BaseModel):
    """Storage backup and disaster recovery analysis result"""

    application: str = Field(..., description="Application name from tags")
    resource_name: str = Field(..., description="Name of the storage resource")
    resource_type: str = Field(..., description="Type of storage resource")
    backup_configuration: str = Field(..., description="Backup configuration details")
    retention_policy: str = Field(..., description="Data retention policy")
    compliance_status: str = Field(..., description="Backup compliance status")
    disaster_recovery_risk: str = Field(..., description="Disaster recovery risk level")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def has_backup_configured(self) -> bool:
        """Check if backup is configured"""
        return "No backup" not in self.backup_configuration.lower()

    @property
    def has_advanced_backup(self) -> bool:
        """Check if advanced backup features are enabled"""
        return "Point-in-time" in self.backup_configuration or "Continuous" in self.backup_configuration

    @property
    def is_compliant(self) -> bool:
        """Check if backup configuration is compliant"""
        return "Compliant" in self.compliance_status

    @property
    def is_high_risk(self) -> bool:
        """Check if disaster recovery risk is high"""
        return self.disaster_recovery_risk.lower().startswith("high")

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_compliant else "❌" if self.is_high_risk else "⚠️"
        return f"{status_emoji} {self.application}/{self.resource_name} ({self.resource_type}) - {self.compliance_status}"


class StorageOptimizationResult(BaseModel):
    """Storage cost optimization analysis result"""

    application: str = Field(..., description="Application name from tags")
    resource_name: str = Field(..., description="Name of the storage resource")
    optimization_type: str = Field(..., description="Type of storage resource")
    current_configuration: str = Field(..., description="Current resource configuration")
    utilization_status: str = Field(..., description="Resource utilization status")
    cost_optimization_potential: str = Field(..., description="Cost optimization potential")
    optimization_recommendation: str = Field(..., description="Specific optimization recommendation")
    estimated_monthly_cost: str = Field(..., description="Estimated monthly cost category")
    resource_group: str = Field(..., description="Azure resource group name")
    location: str = Field(..., description="Azure region/location")
    resource_id: str = Field(..., description="Full Azure resource ID")

    @property
    def is_unused(self) -> bool:
        """Check if resource is unused"""
        return "Unused" in self.utilization_status

    @property
    def is_over_provisioned(self) -> bool:
        """Check if resource is over-provisioned"""
        return "Over-provisioned" in self.utilization_status

    @property
    def has_high_optimization_potential(self) -> bool:
        """Check if resource has high cost optimization potential"""
        return "High" in self.cost_optimization_potential

    @property
    def optimization_priority(self) -> str:
        """Get optimization priority level"""
        if self.has_high_optimization_potential:
            return "High"
        elif "Medium" in self.cost_optimization_potential:
            return "Medium"
        else:
            return "Low"

    def __str__(self) -> str:
        priority_emoji = "🔴" if self.optimization_priority == "High" else "🟡" if self.optimization_priority == "Medium" else "🟢"
        return f"{priority_emoji} {self.application}/{self.resource_name} ({self.optimization_type}) - {self.cost_optimization_potential}"


class StorageComplianceSummary(BaseModel):
    """Storage compliance summary for an application"""

    application: str = Field(..., description="Application name")
    total_storage_resources: int = Field(..., description="Total storage resources")
    storage_account_count: int = Field(..., description="Number of Storage Accounts")
    managed_disk_count: int = Field(..., description="Number of Managed Disks")
    cosmos_db_count: int = Field(..., description="Number of Cosmos DB accounts")
    sql_database_count: int = Field(..., description="Number of SQL databases")
    encrypted_resources: int = Field(..., description="Number of encrypted resources")
    secure_transport_resources: int = Field(..., description="Number of resources with secure transport")
    network_secured_resources: int = Field(..., description="Number of network-secured resources")
    resources_with_issues: int = Field(..., description="Resources with security issues")
    compliance_score: float = Field(..., description="Compliance score percentage")
    compliance_status: str = Field(..., description="Overall compliance status")

    @property
    def is_fully_compliant(self) -> bool:
        """Check if application is fully compliant"""
        return self.compliance_score >= 95.0

    @property
    def compliance_grade(self) -> str:
        """Get compliance grade"""
        if self.compliance_score >= 95:
            return "A"
        elif self.compliance_score >= 85:
            return "B"
        elif self.compliance_score >= 70:
            return "C"
        elif self.compliance_score >= 60:
            return "D"
        else:
            return "F"

    @property
    def has_critical_issues(self) -> bool:
        """Check if there are critical compliance issues"""
        return self.resources_with_issues > 0 and self.compliance_score < 70

    @property
    def encryption_coverage(self) -> float:
        """Get encryption coverage percentage"""
        if self.total_storage_resources == 0:
            return 0.0
        return (self.encrypted_resources / self.total_storage_resources) * 100

    def __str__(self) -> str:
        status_emoji = "✅" if self.is_fully_compliant else "⚠️" if self.compliance_score >= 80 else "❌"
        return f"{status_emoji} {self.application}: {self.compliance_score}% compliant ({self.resources_with_issues} issues) - Grade {self.compliance_grade}"


# ============================================================================
# COMPREHENSIVE SUMMARY MODELS
# ============================================================================

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

# ============================================================================
# IDENTITY & ACCESS MANAGEMENT MODELS
# ============================================================================

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


# ============================================================================
# COMPREHENSIVE SUMMARY MODELS
# ============================================================================

# ============================================================================
# CONTAINER & MODERN WORKLOADS MODELS
# ============================================================================

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

