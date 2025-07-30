from .client import AzureResourceGraphClient, AzureConfig

from .models import (
    VMSecurityResult,
    VMOptimizationResult,
    VMExtensionResult,
    VMPatchComplianceResult,
    VMGovernanceSummary,
)

from .network_analysis import NetworkAnalysisQueries
from .storage_analysis import StorageAnalysisQueries
from .vm_governance import VMGovernanceQueries
from .container_workload_analysis import ContainerWorkloadsAnalysisQueries
from .iam_analysis import IAMAnalysisQueries  # or whatever the class name is

__version__ = "1.0.18"
__author__ = "Kenneth Stott"
__email__ = "ken@hasura.io"

# Make key classes available at package level
__all__ = [
    # Core client and configuration
    'AzureResourceGraphClient',
    'AzureConfig',

    # Query classes
    'StorageAnalysisQueries',
    'NetworkAnalysisQueries',
    'VMGovernanceQueries',
    'ContainerWorkloadsAnalysisQueries',
    'IAMAnalysisQueries',

    # Network Analysis Models
    # Storage Analysis Models
    # VM Governance Models
    'VMSecurityResult',
    'VMOptimizationResult',
    'VMExtensionResult',
    'VMPatchComplianceResult',
    'VMGovernanceSummary',

    # Legacy/Compatibility Models
]

__description__ = "Python client for Azure Resource Graph API with comprehensive storage, network, and VM governance analysis including security assessment, cost optimization, and compliance reporting"

# Version history
__version_info__ = {
    "1.0.12": "Initial storage encryption analysis",
    "1.1.0": "Enhanced with comprehensive network analysis, certificate management, topology mapping, and optimization",
    "1.2.0": "Major refactor: Comprehensive storage analysis with access control, backup assessment, cost optimization, and enhanced compliance reporting",
    "1.3.0": "Added comprehensive VM governance analysis: VM security, sizing optimization, extensions management, and patch compliance"
}

# Quick start example
__example_usage__ = '''
from azure_resource_graph import AzureResourceGraphClient

# Initialize client
client = AzureResourceGraphClient()

# === STORAGE ANALYSIS ===

# Comprehensive storage security analysis
storage_results = client.query_storage_analysis()
print(f"Found {len(storage_results)} storage resources")

# Storage access control analysis
access_results = client.query_storage_access_control()
high_risk_access = [result for result in access_results if result.is_high_risk]
print(f"Found {len(high_risk_access)} high-risk access configurations")

# Storage backup analysis
backup_results = client.query_storage_backup_analysis()
no_backup = [result for result in backup_results if not result.has_backup_configured]
print(f"Found {len(no_backup)} resources without proper backup")

# Storage cost optimization
storage_optimization = client.query_storage_optimization()
high_savings = [result for result in storage_optimization if result.has_high_optimization_potential]
print(f"Found {len(high_savings)} high-cost optimization opportunities")

# Storage compliance summary
storage_summary = client.get_storage_compliance_summary()
critical_apps = [s for s in storage_summary if s.has_critical_issues]
print(f"Found {len(critical_apps)} applications with critical storage issues")

# === VM GOVERNANCE ANALYSIS ===

# VM security analysis
vm_security = client.query_vm_security()
high_risk_vms = [vm for vm in vm_security if vm.is_high_risk]
unencrypted_vms = [vm for vm in vm_security if not vm.is_encrypted]
print(f"Found {len(high_risk_vms)} high-risk VMs, {len(unencrypted_vms)} unencrypted VMs")

# VM optimization analysis
vm_optimization = client.query_vm_optimization()
stopped_vms = [vm for vm in vm_optimization if vm.is_stopped_but_allocated]
legacy_vms = [vm for vm in vm_optimization if vm.is_legacy_size]
high_cost_savings = [vm for vm in vm_optimization if vm.has_high_optimization_potential]
print(f"Found {len(stopped_vms)} stopped VMs, {len(legacy_vms)} legacy sizes, {len(high_cost_savings)} high optimization potential")

# VM extensions analysis
vm_extensions = client.query_vm_extensions()
security_extensions = [ext for ext in vm_extensions if ext.is_security_extension]
failed_extensions = [ext for ext in vm_extensions if not ext.is_healthy]
print(f"Found {len(security_extensions)} security extensions, {len(failed_extensions)} failed extensions")

# VM patch compliance
vm_patches = client.query_vm_patch_compliance()
manual_patching = [vm for vm in vm_patches if vm.requires_manual_patching]
high_patch_risk = [vm for vm in vm_patches if vm.is_high_risk]
print(f"Found {len(manual_patching)} VMs requiring manual patching, {len(high_patch_risk)} high patch risk")

# VM governance summary
vm_summary = client.get_vm_governance_summary()
critical_vm_apps = [s for s in vm_summary if s.has_critical_issues]
print(f"Found {len(critical_vm_apps)} applications with critical VM governance issues")

# === NETWORK ANALYSIS ===

# Network security analysis  
network_results = client.query_network_analysis()
print(f"Found {len(network_results)} network resources")

# NSG detailed analysis
nsg_rules = client.query_nsg_detailed()
high_risk = [rule for rule in nsg_rules if rule.is_high_risk]
admin_exposed = [rule for rule in nsg_rules if rule.is_internet_facing and rule.allows_admin_ports]
print(f"Found {len(high_risk)} high-risk NSG rules, {len(admin_exposed)} expose admin ports")

# Certificate analysis
cert_results = client.query_certificate_analysis()
non_compliant_certs = [cert for cert in cert_results if "Non-Compliant" in cert.get("ComplianceStatus", "")]
print(f"Found {len(non_compliant_certs)} non-compliant certificate configurations")

# Network topology analysis
topology_results = client.query_network_topology()
high_risk_topology = [topo for topo in topology_results if "High" in topo.get("ConfigurationRisk", "")]
print(f"Found {len(high_risk_topology)} high-risk network topology configurations")

# Network resource optimization
network_optimization = client.query_resource_optimization()
unused_network = [res for res in network_optimization if "Unused" in res.get("UtilizationStatus", "")]
print(f"Found {len(unused_network)} unused network resources for cost savings")

# Network compliance summary
network_summary = client.get_network_compliance_summary()
critical_network = [s for s in network_summary if s.has_critical_issues]
print(f"Found {len(critical_network)} applications with critical network issues")

# === EXAMPLES USING PYDANTIC PROPERTIES ===

# Filter storage resources by encryption strength
strong_encryption = [r for r in storage_results if r.encryption_strength == "Strong"]
weak_encryption = [r for r in storage_results if r.encryption_strength == "Weak"]

# Filter VMs by governance criteria
production_vms = [vm for vm in vm_security if vm.is_running and vm.is_encrypted]
cost_waste_vms = [vm for vm in vm_optimization if vm.is_stopped_but_allocated or vm.is_legacy_size]
security_gaps = [vm for vm in vm_security if not vm.has_security_extensions]

# Filter VM extensions by criticality
critical_failed = [ext for ext in vm_extensions if ext.is_critical and not ext.is_healthy]
monitoring_gaps = [ext for ext in vm_extensions if ext.is_monitoring_extension and not ext.is_healthy]

# Filter network rules by specific risks
internet_admin = [rule for rule in nsg_rules if rule.is_internet_facing and rule.allows_admin_ports]
high_priority_issues = [rule for rule in nsg_rules if rule.is_high_risk and rule.priority < 1000]

print(f"""
📊 COMPREHENSIVE ANALYSIS SUMMARY:
Storage: {len(strong_encryption)} strong encryption, {len(weak_encryption)} weak encryption
VMs: {len(production_vms)} production-ready, {len(cost_waste_vms)} cost waste, {len(security_gaps)} security gaps  
Extensions: {len(critical_failed)} critical failures, {len(monitoring_gaps)} monitoring gaps
Network: {len(internet_admin)} critical admin exposure, {len(high_priority_issues)} high-priority issues
""")
'''
