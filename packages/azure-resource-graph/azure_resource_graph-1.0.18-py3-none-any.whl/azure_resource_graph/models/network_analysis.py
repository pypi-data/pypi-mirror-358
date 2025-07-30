from typing import Literal

from pydantic import BaseModel, Field


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
