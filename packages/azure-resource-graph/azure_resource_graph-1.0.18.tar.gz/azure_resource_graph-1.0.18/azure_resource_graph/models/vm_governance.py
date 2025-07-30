from pydantic import BaseModel, Field


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
