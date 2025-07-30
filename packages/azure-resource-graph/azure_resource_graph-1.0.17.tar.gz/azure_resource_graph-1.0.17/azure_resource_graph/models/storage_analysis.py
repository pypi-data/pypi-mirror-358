from pydantic import BaseModel, Field


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
