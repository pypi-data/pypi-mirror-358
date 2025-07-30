#!/usr/bin/env python3
"""
Enhanced Pytest tests for Azure Resource Graph Client with comprehensive analysis
Includes storage, network, VM governance, and IAM analysis testing with result display
"""

import json
import pytest
import time
import os
from typing import Dict, Any, List, Union
import pprint

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

from azure_resource_graph import AzureResourceGraphClient, AzureConfig
from azure_resource_graph.models import (
    NSGRule, NetworkResource, StorageResource, ComplianceSummary, NetworkComplianceSummary,
    StorageAccessControlResult, StorageBackupResult, StorageOptimizationResult, StorageComplianceSummary,
    VMSecurityResult, VMOptimizationResult, VMExtensionResult, VMPatchComplianceResult, VMGovernanceSummary,
    RoleAssignmentResult, KeyVaultSecurityResult, ManagedIdentityResult, CustomRoleResult, IAMComplianceSummary,
    CertificateAnalysisResult, NetworkTopologyResult, ResourceOptimizationResult, AKSClusterSecurityResult,
    AKSNodePoolResult, ContainerRegistrySecurityResult, AppServiceSecurityResult, ContainerWorkloadsComplianceSummary
)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def analyze_field_structure(results: List[Union[Dict, object]], title: str = "Results"):
    """
    Analyze and display the field structure of query results
    Works with both dictionaries and Pydantic objects
    """
    if not results:
        print(f"❌ No {title.lower()} to analyze")
        return

    print(f"\n🔍 FIELD ANALYSIS: {title}")
    print(f"{'=' * 40}")

    # Handle both Pydantic objects and dictionaries
    sample = results[0]
    if hasattr(sample, '__dict__'):
        # Pydantic object
        all_fields = set(sample.__dict__.keys())
        field_coverage = {field: len(results) for field in all_fields}  # All objects have all fields
        print(f"Total records: {len(results)} (Pydantic objects)")
        print(f"Fields per object: {len(all_fields)}")

        print(f"\nAvailable fields:")
        for field in sorted(all_fields):
            print(f"  ✅ {field:25}: 100.0% ({len(results)}/{len(results)} records)")

        # Show sample values
        print(f"\nSample field values:")
        for field in sorted(all_fields):
            value = getattr(sample, field)
            display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"  {field:25}: {display_value}")

    else:
        # Dictionary objects
        all_fields = set()
        field_coverage = {}

        for result in results:
            if isinstance(result, dict):
                for field in result.keys():
                    all_fields.add(field)
                    field_coverage[field] = field_coverage.get(field, 0) + 1

        print(f"Total records: {len(results)} (dictionaries)")
        print(f"Unique fields: {len(all_fields)}")
        print(f"\nField coverage:")

        for field in sorted(all_fields):
            coverage = field_coverage[field]
            percentage = (coverage / len(results)) * 100
            coverage_emoji = "✅" if percentage == 100 else "⚠️" if percentage >= 80 else "❌"
            print(f"  {coverage_emoji} {field:25}: {percentage:5.1f}% ({coverage}/{len(results)} records)")

        # Show sample values for each field
        if results:
            print(f"\nSample field values:")
            sample = results[0]
            for field in sorted(sample.keys()):
                value = sample[field]
                display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"  {field:25}: {display_value}")


def pretty_print_results(results: List[Union[Dict, object]], title: str, max_items: int = 3):
    """
    Pretty print test results for better visibility
    Works with both dictionaries and Pydantic objects
    """
    print(f"\n{'=' * 60}")
    print(f"📊 {title}")
    print(f"{'=' * 60}")
    print(f"Total items: {len(results)}")

    if not results:
        print("❌ No results returned")
        return

    print(f"\n📋 Sample results (showing first {min(max_items, len(results))} items):")
    for i, result in enumerate(results[:max_items]):
        print(f"\n--- Item {i + 1} ---")
        if hasattr(result, 'dict'):
            # Pydantic object
            pprint.pprint(result.dict(), indent=2, width=80)
        else:
            # Dictionary
            pprint.pprint(result, indent=2, width=80)

    if len(results) > max_items:
        print(f"\n... and {len(results) - max_items} more items")


# ============================================================================
# CONTAINER & MODERN WORKLOADS DISPLAY FUNCTIONS
# ============================================================================

def display_aks_cluster_security_analysis(aks_security_results: List[Union[Dict, AKSClusterSecurityResult]]):
    """
    Display AKS cluster security analysis summary
    """
    if not aks_security_results:
        print("❌ No AKS cluster security data available")
        return

    print(f"\n🚀 AKS CLUSTER SECURITY ANALYSIS SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'is_private_cluster':
                return "Private Endpoint" in obj.get('APIServerAccess', '')
            elif prop_name == 'has_rbac_enabled':
                return "RBAC" in obj.get('RBACConfiguration', '') and "No RBAC" not in obj.get('RBACConfiguration', '')
            elif prop_name == 'has_azure_ad_integration':
                return "Azure AD" in obj.get('RBACConfiguration', '')
            elif prop_name == 'has_network_policy':
                return "Policy: None" not in obj.get('NetworkConfiguration', '')
            elif prop_name == 'is_compliant':
                return obj.get('ClusterCompliance', '') == "Compliant - Security Configured"
            elif prop_name == 'is_high_risk':
                return obj.get('SecurityRisk', '').lower().startswith('high')
            return False

    total_clusters = len(aks_security_results)
    private_clusters = [r for r in aks_security_results if has_property(r, 'is_private_cluster')]
    rbac_enabled = [r for r in aks_security_results if has_property(r, 'has_rbac_enabled')]
    azure_ad_integrated = [r for r in aks_security_results if has_property(r, 'has_azure_ad_integration')]
    network_policies = [r for r in aks_security_results if has_property(r, 'has_network_policy')]
    compliant_clusters = [r for r in aks_security_results if has_property(r, 'is_compliant')]
    high_risk_clusters = [r for r in aks_security_results if has_property(r, 'is_high_risk')]

    print(f"Total AKS clusters: {total_clusters}")
    print(
        f"Private clusters: {len(private_clusters)} ({len(private_clusters) / total_clusters * 100:.1f}%)" if total_clusters > 0 else "Private clusters: 0")
    print(
        f"RBAC enabled: {len(rbac_enabled)} ({len(rbac_enabled) / total_clusters * 100:.1f}%)" if total_clusters > 0 else "RBAC enabled: 0")
    print(
        f"Azure AD integrated: {len(azure_ad_integrated)} ({len(azure_ad_integrated) / total_clusters * 100:.1f}%)" if total_clusters > 0 else "Azure AD integrated: 0")
    print(
        f"Network policies configured: {len(network_policies)} ({len(network_policies) / total_clusters * 100:.1f}%)" if total_clusters > 0 else "Network policies: 0")
    print(
        f"Compliant clusters: {len(compliant_clusters)} ({len(compliant_clusters) / total_clusters * 100:.1f}%)" if total_clusters > 0 else "Compliant clusters: 0")
    print(f"High-risk clusters: {len(high_risk_clusters)}")

    if high_risk_clusters:
        print(f"\n🚨 HIGH-RISK AKS CLUSTERS:")
        for cluster in high_risk_clusters[:5]:  # Show first 5
            app = get_field(cluster, "application", "Application")
            cluster_name = get_field(cluster, "cluster_name", "ClusterName")
            security_risk = get_field(cluster, "security_risk", "SecurityRisk")
            security_findings = get_field(cluster, "security_findings", "SecurityFindings")
            print(f"  ❌ {app}/{cluster_name}: {security_risk}")
            print(f"      💡 {security_findings}")

    # Show cluster versions
    cluster_versions = {}
    for cluster in aks_security_results:
        version = get_field(cluster, "cluster_version", "ClusterVersion")
        cluster_versions[version] = cluster_versions.get(version, 0) + 1

    if cluster_versions:
        print(f"\n📊 Kubernetes Versions:")
        for version, count in sorted(cluster_versions.items(), reverse=True):
            version_icon = "✅" if version >= "1.28" else "⚠️" if version >= "1.26" else "❌"
            print(f"  {version_icon} {version}: {count} clusters")


def display_aks_node_pool_analysis(node_pool_results: List[Union[Dict, AKSNodePoolResult]]):
    """
    Display AKS node pool analysis summary
    """
    if not node_pool_results:
        print("❌ No AKS node pool data available")
        return

    print(f"\n🖥️ AKS NODE POOL ANALYSIS SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'is_auto_scaling_enabled':
                return "Auto:" in obj.get('ScalingConfiguration', '')
            elif prop_name == 'is_legacy_vm_size':
                return obj.get('VMSizeCategory', '') == "Basic/Legacy"
            elif prop_name == 'has_host_encryption':
                return "Encryption" in obj.get('SecurityConfiguration', '')
            elif prop_name == 'is_high_risk':
                return obj.get('NodePoolRisk', '').lower().startswith('high')
            elif prop_name == 'has_high_optimization_potential':
                return "High" in obj.get('OptimizationPotential', '')
            return False

    total_pools = len(node_pool_results)
    auto_scaling_pools = [r for r in node_pool_results if has_property(r, 'is_auto_scaling_enabled')]
    legacy_vm_pools = [r for r in node_pool_results if has_property(r, 'is_legacy_vm_size')]
    encrypted_pools = [r for r in node_pool_results if has_property(r, 'has_host_encryption')]
    high_risk_pools = [r for r in node_pool_results if has_property(r, 'is_high_risk')]
    optimization_pools = [r for r in node_pool_results if has_property(r, 'has_high_optimization_potential')]

    print(f"Total node pools: {total_pools}")
    print(
        f"Auto-scaling enabled: {len(auto_scaling_pools)} ({len(auto_scaling_pools) / total_pools * 100:.1f}%)" if total_pools > 0 else "Auto-scaling enabled: 0")
    print(f"Legacy VM sizes: {len(legacy_vm_pools)}")
    print(
        f"Host encryption enabled: {len(encrypted_pools)} ({len(encrypted_pools) / total_pools * 100:.1f}%)" if total_pools > 0 else "Host encryption: 0")
    print(f"High-risk pools: {len(high_risk_pools)}")
    print(f"High optimization potential: {len(optimization_pools)}")

    if optimization_pools:
        print(f"\n💡 NODE POOLS WITH HIGH OPTIMIZATION POTENTIAL:")
        for pool in optimization_pools[:5]:  # Show first 5
            app = get_field(pool, "application", "Application")
            cluster_name = get_field(pool, "cluster_name", "ClusterName")
            pool_name = get_field(pool, "node_pool_name", "NodePoolName")
            vm_size = get_field(pool, "vm_size", "VMSize")
            optimization = get_field(pool, "optimization_potential", "OptimizationPotential")
            print(f"  🔴 {app}/{cluster_name}/{pool_name} ({vm_size}): {optimization}")


def display_container_registry_security_analysis(registry_results: List[Union[Dict, ContainerRegistrySecurityResult]]):
    """
    Display Container Registry security analysis summary
    """
    if not registry_results:
        print("❌ No Container Registry security data available")
        return

    print(f"\n📦 CONTAINER REGISTRY SECURITY ANALYSIS SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'is_private_access_only':
                return "Private Access Only" in obj.get('NetworkSecurity', '')
            elif prop_name == 'has_admin_user_enabled':
                return "Admin User" in obj.get('AccessControl', '')
            elif prop_name == 'has_content_trust':
                return "Trust" in obj.get('SecurityPolicies', '')
            elif prop_name == 'is_premium_sku':
                return obj.get('RegistrySKU', '') == "Premium"
            elif prop_name == 'is_compliant':
                return obj.get('ComplianceStatus', '') == "Compliant"
            elif prop_name == 'is_high_risk':
                return obj.get('SecurityRisk', '').lower().startswith('high')
            elif prop_name == 'is_publicly_accessible':
                return "Unrestricted Public Access" in obj.get('NetworkSecurity', '')
            return False

    total_registries = len(registry_results)
    private_registries = [r for r in registry_results if has_property(r, 'is_private_access_only')]
    admin_enabled = [r for r in registry_results if has_property(r, 'has_admin_user_enabled')]
    content_trust = [r for r in registry_results if has_property(r, 'has_content_trust')]
    premium_sku = [r for r in registry_results if has_property(r, 'is_premium_sku')]
    compliant_registries = [r for r in registry_results if has_property(r, 'is_compliant')]
    high_risk_registries = [r for r in registry_results if has_property(r, 'is_high_risk')]
    public_registries = [r for r in registry_results if has_property(r, 'is_publicly_accessible')]

    print(f"Total container registries: {total_registries}")
    print(
        f"Private access only: {len(private_registries)} ({len(private_registries) / total_registries * 100:.1f}%)" if total_registries > 0 else "Private access: 0")
    print(f"Admin user enabled: {len(admin_enabled)}")
    print(
        f"Content trust enabled: {len(content_trust)} ({len(content_trust) / total_registries * 100:.1f}%)" if total_registries > 0 else "Content trust: 0")
    print(
        f"Premium SKU: {len(premium_sku)} ({len(premium_sku) / total_registries * 100:.1f}%)" if total_registries > 0 else "Premium SKU: 0")
    print(f"Compliant registries: {len(compliant_registries)}")
    print(f"High-risk registries: {len(high_risk_registries)}")

    if public_registries:
        print(f"\n🌐 PUBLICLY ACCESSIBLE REGISTRIES:")
        for registry in public_registries[:5]:  # Show first 5
            app = get_field(registry, "application", "Application")
            registry_name = get_field(registry, "registry_name", "RegistryName")
            security_risk = get_field(registry, "security_risk", "SecurityRisk")
            print(f"  ⚠️ {app}/{registry_name}: {security_risk}")

    if admin_enabled:
        print(f"\n👤 REGISTRIES WITH ADMIN USER ENABLED:")
        for registry in admin_enabled[:3]:  # Show first 3
            app = get_field(registry, "application", "Application")
            registry_name = get_field(registry, "registry_name", "RegistryName")
            print(f"  ❌ {app}/{registry_name}: Admin user access enabled")


def display_app_service_security_analysis(app_service_results: List[Union[Dict, AppServiceSecurityResult]]):
    """
    Display App Service security analysis summary
    """
    if not app_service_results:
        print("❌ No App Service security data available")
        return

    print(f"\n🌐 APP SERVICE SECURITY ANALYSIS SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'is_https_only':
                return "HTTPS Only" in obj.get('TLSConfiguration', '')
            elif prop_name == 'has_modern_tls':
                return "TLS 1.2" in obj.get('TLSConfiguration', '')
            elif prop_name == 'has_legacy_tls':
                return "TLS 1.0" in obj.get('TLSConfiguration', '') or "TLS 1.1" in obj.get('TLSConfiguration', '')
            elif prop_name == 'has_authentication_configured':
                return "No Centralized Auth" not in obj.get('AuthenticationMethod', '')
            elif prop_name == 'has_managed_identity':
                return "Managed Identity" in obj.get('AuthenticationMethod', '')
            elif prop_name == 'is_compliant':
                return obj.get('ComplianceStatus', '') == "Compliant"
            elif prop_name == 'is_high_risk':
                return obj.get('SecurityRisk', '').lower().startswith('high')
            elif prop_name == 'has_custom_domains':
                return int(obj.get('CustomDomainCount', 0)) > 0
            return False

    total_apps = len(app_service_results)
    https_only = [r for r in app_service_results if has_property(r, 'is_https_only')]
    modern_tls = [r for r in app_service_results if has_property(r, 'has_modern_tls')]
    legacy_tls = [r for r in app_service_results if has_property(r, 'has_legacy_tls')]
    with_auth = [r for r in app_service_results if has_property(r, 'has_authentication_configured')]
    managed_identity = [r for r in app_service_results if has_property(r, 'has_managed_identity')]
    compliant_apps = [r for r in app_service_results if has_property(r, 'is_compliant')]
    high_risk_apps = [r for r in app_service_results if has_property(r, 'is_high_risk')]
    custom_domains = [r for r in app_service_results if has_property(r, 'has_custom_domains')]

    print(f"Total App Services: {total_apps}")
    print(
        f"HTTPS only: {len(https_only)} ({len(https_only) / total_apps * 100:.1f}%)" if total_apps > 0 else "HTTPS only: 0")
    print(
        f"Modern TLS (1.2): {len(modern_tls)} ({len(modern_tls) / total_apps * 100:.1f}%)" if total_apps > 0 else "Modern TLS: 0")
    print(f"Legacy TLS: {len(legacy_tls)}")
    print(
        f"Authentication configured: {len(with_auth)} ({len(with_auth) / total_apps * 100:.1f}%)" if total_apps > 0 else "Authentication: 0")
    print(
        f"Managed identity: {len(managed_identity)} ({len(managed_identity) / total_apps * 100:.1f}%)" if total_apps > 0 else "Managed identity: 0")
    print(f"Custom domains: {len(custom_domains)}")
    print(f"Compliant App Services: {len(compliant_apps)}")
    print(f"High-risk App Services: {len(high_risk_apps)}")

    if legacy_tls:
        print(f"\n⚠️ APP SERVICES WITH LEGACY TLS:")
        for app in legacy_tls[:5]:  # Show first 5
            app_name = get_field(app, "application", "Application")
            service_name = get_field(app, "app_service_name", "AppServiceName")
            tls_config = get_field(app, "tls_configuration", "TLSConfiguration")
            print(f"  ❌ {app_name}/{service_name}: {tls_config}")

    if high_risk_apps:
        print(f"\n🚨 HIGH-RISK APP SERVICES:")
        for app in high_risk_apps[:5]:  # Show first 5
            app_name = get_field(app, "application", "Application")
            service_name = get_field(app, "app_service_name", "AppServiceName")
            security_risk = get_field(app, "security_risk", "SecurityRisk")
            security_findings = get_field(app, "security_findings", "SecurityFindings")
            print(f"  ❌ {app_name}/{service_name}: {security_risk}")
            print(f"      💡 {security_findings}")


def display_container_workloads_compliance_summary(
        container_compliance_results: List[Union[Dict, ContainerWorkloadsComplianceSummary]]):
    """
    Display Container & Modern Workloads compliance metrics in a readable format
    """
    if not container_compliance_results:
        print("❌ No container workloads compliance data available")
        return

    print(f"\n📈 CONTAINER & MODERN WORKLOADS COMPLIANCE SUMMARY")
    print(f"{'=' * 55}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, 0)

    total_apps = len(container_compliance_results)
    total_workloads = sum(
        get_field(r, "total_container_workloads", "TotalContainerWorkloads") for r in container_compliance_results)
    total_aks = sum(get_field(r, "total_aks_clusters", "TotalAKSClusters") for r in container_compliance_results)
    total_registries = sum(
        get_field(r, "total_container_registries", "TotalContainerRegistries") for r in container_compliance_results)
    total_app_services = sum(
        get_field(r, "total_app_services", "TotalAppServices") for r in container_compliance_results)

    overall_compliance = sum(
        get_field(r, "container_workloads_compliance_score", "ContainerWorkloadsComplianceScore") for r in
        container_compliance_results) / total_apps if total_apps > 0 else 0

    print(f"Applications analyzed: {total_apps}")
    print(f"Total container workloads: {total_workloads}")
    print(f"AKS clusters: {total_aks}")
    print(f"Container registries: {total_registries}")
    print(f"App Services: {total_app_services}")
    print(f"Average compliance score: {overall_compliance:.1f}%")

    print(f"\n📊 Per-Application Container Workloads Compliance:")
    for app in container_compliance_results:
        app_name = get_field(app, "application", "Application")
        compliance_score = get_field(app, "container_workloads_compliance_score", "ContainerWorkloadsComplianceScore")
        issues = get_field(app, "container_workloads_with_issues", "ContainerWorkloadsWithIssues")
        total_app_workloads = get_field(app, "total_container_workloads", "TotalContainerWorkloads")

        aks_count = get_field(app, "total_aks_clusters", "TotalAKSClusters")
        registry_count = get_field(app, "total_container_registries", "TotalContainerRegistries")
        app_service_count = get_field(app, "total_app_services", "TotalAppServices")

        status_emoji = "✅" if compliance_score >= 95 else "⚠️" if compliance_score >= 80 else "❌"

        # Show grade if available
        grade = ""
        if hasattr(app, "container_workloads_compliance_grade"):
            grade = f" (Grade {app.container_workloads_compliance_grade})"

        # Show maturity if available
        maturity = ""
        if hasattr(app, "container_orchestration_maturity"):
            maturity_icon = {"Advanced": "🚀", "Intermediate": "⚙️", "Basic": "🔧", "Traditional": "🌐", "None": "❓"}.get(
                app.container_orchestration_maturity, "❓")
            maturity = f" {maturity_icon} {app.container_orchestration_maturity}"

        workload_breakdown = f"AKS:{aks_count} Registry:{registry_count} App:{app_service_count}"

        print(
            f"{status_emoji} {app_name}: {compliance_score:.1f}% compliant ({issues} issues, {total_app_workloads} workloads: {workload_breakdown}){grade}{maturity}")

# ============================================================================
# STORAGE ANALYSIS DISPLAY FUNCTIONS
# ============================================================================

def display_storage_analysis_summary(storage_results: List[Union[Dict, StorageResource]]):
    """
    Display comprehensive storage analysis summary
    """
    if not storage_results:
        print("❌ No storage analysis data available")
        return

    print(f"\n🗄️ COMPREHENSIVE STORAGE ANALYSIS SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'is_high_risk':
                risk = obj.get('ComplianceRisk', '')
                return 'High' in risk
            elif prop_name == 'uses_customer_managed_keys':
                encryption = obj.get('EncryptionMethod', '')
                return 'Customer Managed Key' in encryption
            elif prop_name == 'is_compliant':
                risk = obj.get('ComplianceRisk', '')
                return not risk.startswith('High')
            return False

    total_resources = len(storage_results)
    high_risk = [r for r in storage_results if has_property(r, 'is_high_risk')]
    cmk_encrypted = [r for r in storage_results if has_property(r, 'uses_customer_managed_keys')]
    compliant = [r for r in storage_results if has_property(r, 'is_compliant')]

    print(f"Total storage resources: {total_resources}")
    print(f"High-risk resources: {len(high_risk)}")
    print(f"Customer-managed key encryption: {len(cmk_encrypted)}")
    print(f"Compliant resources: {len(compliant)}")

    # Storage type breakdown
    storage_types = {}
    encryption_methods = {}
    compliance_risks = {}

    for resource in storage_results:
        storage_type = get_field(resource, 'storage_type', 'StorageType')
        encryption = get_field(resource, 'encryption_method', 'EncryptionMethod')
        risk = get_field(resource, 'compliance_risk', 'ComplianceRisk')

        storage_types[storage_type] = storage_types.get(storage_type, 0) + 1
        encryption_methods[encryption] = encryption_methods.get(encryption, 0) + 1
        compliance_risks[risk] = compliance_risks.get(risk, 0) + 1

    print(f"\n📊 Storage Types:")
    for storage_type, count in sorted(storage_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {storage_type}: {count}")

    print(f"\n🔒 Encryption Methods:")
    for method, count in sorted(encryption_methods.items(), key=lambda x: x[1], reverse=True):
        emoji = "🔐" if "Customer Managed" in method else "🔑" if "Platform Managed" in method else "⚠️"
        print(f"  {emoji} {method}: {count}")

    print(f"\n⚠️ Compliance Risks:")
    for risk, count in sorted(compliance_risks.items(), key=lambda x: x[1], reverse=True):
        emoji = "❌" if "High" in risk else "⚠️" if "Medium" in risk else "✅"
        print(f"  {emoji} {risk}: {count}")


def display_storage_compliance_metrics(compliance_results: List[Union[Dict, StorageComplianceSummary]]):
    """
    Display comprehensive storage compliance metrics in a readable format
    """
    if not compliance_results:
        print("❌ No storage compliance data available")
        return

    print(f"\n📈 COMPREHENSIVE STORAGE COMPLIANCE SUMMARY")
    print(f"{'=' * 50}")

    # Handle both dictionary and Pydantic object formats
    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, 0)

    total_apps = len(compliance_results)
    total_resources = sum(get_field(r, "total_storage_resources", "TotalStorageResources") for r in compliance_results)
    total_encrypted = sum(get_field(r, "encrypted_resources", "EncryptedResources") for r in compliance_results)
    total_secure_transport = sum(
        get_field(r, "secure_transport_resources", "SecureTransportResources") for r in compliance_results)
    total_network_secured = sum(
        get_field(r, "network_secured_resources", "NetworkSecuredResources") for r in compliance_results)

    overall_compliance = sum(get_field(r, "compliance_score", "ComplianceScore") for r in
                             compliance_results) / total_apps if total_apps > 0 else 0

    print(f"Applications analyzed: {total_apps}")
    print(f"Total storage resources: {total_resources}")
    print(
        f"Encrypted resources: {total_encrypted} ({total_encrypted / total_resources * 100:.1f}%)" if total_resources > 0 else "Encrypted resources: 0")
    print(
        f"Secure transport: {total_secure_transport} ({total_secure_transport / total_resources * 100:.1f}%)" if total_resources > 0 else "Secure transport: 0")
    print(
        f"Network secured: {total_network_secured} ({total_network_secured / total_resources * 100:.1f}%)" if total_resources > 0 else "Network secured: 0")
    print(f"Average compliance score: {overall_compliance:.1f}%")

    print(f"\n📊 Per-Application Storage Compliance:")
    for app in compliance_results:
        app_name = get_field(app, "application", "Application")
        compliance_score = get_field(app, "compliance_score", "ComplianceScore")
        issues = get_field(app, "resources_with_issues", "ResourcesWithIssues")
        total_app_resources = get_field(app, "total_storage_resources", "TotalStorageResources")

        status_emoji = "✅" if compliance_score >= 95 else "⚠️" if compliance_score >= 80 else "❌"

        # Show grade if available
        grade = ""
        if hasattr(app, "compliance_grade"):
            grade = f" (Grade {app.compliance_grade})"

        print(
            f"{status_emoji} {app_name}: {compliance_score:.1f}% compliant ({issues} issues, {total_app_resources} resources){grade}")


def display_storage_optimization_analysis(optimization_results: List[Union[Dict, StorageOptimizationResult]]):
    """
    Display storage optimization analysis results
    """
    if not optimization_results:
        print("❌ No storage optimization data available")
        return

    print(f"\n💰 STORAGE OPTIMIZATION SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'is_unused':
                status = obj.get('UtilizationStatus', '')
                return 'Unused' in status
            elif prop_name == 'has_high_optimization_potential':
                potential = obj.get('CostOptimizationPotential', '')
                return 'High' in potential
            return False

    total_resources = len(optimization_results)
    unused_resources = [r for r in optimization_results if has_property(r, 'is_unused')]
    high_potential = [r for r in optimization_results if has_property(r, 'has_high_optimization_potential')]

    print(f"Total storage resources analyzed: {total_resources}")
    print(f"Unused storage resources: {len(unused_resources)}")
    print(f"High optimization potential: {len(high_potential)}")

    if high_potential:
        print(f"\n💡 High storage optimization opportunities:")
        for resource in high_potential[:5]:  # Show first 5
            app = get_field(resource, "application", "Application")
            name = get_field(resource, "resource_name", "ResourceName")
            optimization_type = get_field(resource, "optimization_type", "OptimizationType")
            potential = get_field(resource, "cost_optimization_potential", "CostOptimizationPotential")
            recommendation = get_field(resource, "optimization_recommendation", "OptimizationRecommendation")
            print(f"  🔴 {app}/{name} ({optimization_type}): {potential}")
            print(f"      💡 {recommendation}")


def display_legacy_compliance_metrics(compliance_results: List[Union[Dict, ComplianceSummary]]):
    """
    Display legacy compliance metrics in a readable format (backward compatibility)
    """
    if not compliance_results:
        print("❌ No compliance data available")
        return

    print(f"\n📈 LEGACY COMPLIANCE SUMMARY")
    print(f"{'=' * 50}")

    # Handle both dictionary and Pydantic object formats
    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, 0)

    total_apps = len(compliance_results)
    total_resources = sum(get_field(r, "total_resources", "TotalResources") for r in compliance_results)
    total_compliant = sum(get_field(r, "compliant_resources", "CompliantResources") for r in compliance_results)

    overall_compliance = (total_compliant / total_resources * 100) if total_resources > 0 else 0

    print(f"Applications analyzed: {total_apps}")
    print(f"Total resources: {total_resources}")
    print(f"Overall compliance: {overall_compliance:.1f}%")

    print(f"\n📊 Per-Application Breakdown:")
    for app in compliance_results:
        app_name = get_field(app, "application", "Application")
        compliance_pct = get_field(app, "compliance_percentage", "CompliancePercentage")
        compliant = get_field(app, "compliant_resources", "CompliantResources")
        total = get_field(app, "total_resources", "TotalResources")

        status_emoji = "✅" if compliance_pct >= 90 else "⚠️" if compliance_pct >= 70 else "❌"

        # Show grade if available
        grade = ""
        if hasattr(app, "compliance_grade"):
            grade = f" (Grade {app.compliance_grade})"

        print(f"{status_emoji} {app_name}: {compliance_pct:.1f}% ({compliant}/{total} compliant){grade}")


# ============================================================================
# NETWORK ANALYSIS DISPLAY FUNCTIONS
# ============================================================================

def display_network_security_metrics(network_results: List[Union[Dict, NetworkComplianceSummary]]):
    """
    Display network security metrics in a readable format
    """
    if not network_results:
        print("❌ No network security data available")
        return

    print(f"\n🛡️ NETWORK SECURITY SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, 0)

    total_apps = len(network_results)
    total_resources = sum(get_field(r, "total_network_resources", "TotalNetworkResources") for r in network_results)
    total_issues = sum(get_field(r, "resources_with_issues", "ResourcesWithIssues") for r in network_results)

    overall_security_score = sum(
        get_field(r, "security_score", "SecurityScore") for r in network_results) / total_apps if total_apps > 0 else 0

    print(f"Applications analyzed: {total_apps}")
    print(f"Total network resources: {total_resources}")
    print(f"Resources with issues: {total_issues}")
    print(f"Average security score: {overall_security_score:.1f}%")

    print(f"\n🌐 Per-Application Network Security:")
    for app in network_results:
        app_name = get_field(app, "application", "Application")
        security_score = get_field(app, "security_score", "SecurityScore")
        issues = get_field(app, "resources_with_issues", "ResourcesWithIssues")
        nsg_count = get_field(app, "nsg_count", "NSGCount")

        status_emoji = "✅" if security_score >= 90 else "⚠️" if security_score >= 75 else "❌"

        # Show grade if available
        grade = ""
        if hasattr(app, "security_grade"):
            grade = f" (Grade {app.security_grade})"

        print(f"{status_emoji} {app_name}: {security_score:.1f}% secure ({issues} issues, {nsg_count} NSGs){grade}")


def display_nsg_rule_analysis(nsg_rules: List[Union[Dict, NSGRule]]):
    """
    Display detailed NSG rule analysis
    """
    if not nsg_rules:
        print("❌ No NSG rules to analyze")
        return

    print(f"\n🛡️ NSG RULES ANALYSIS")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            risk_level = obj.get('RiskLevel', '')
            if prop_name == 'is_high_risk':
                return 'High' in risk_level
            elif prop_name == 'is_internet_facing':
                source = obj.get('SourceAddressPrefix', '')
                return source in ['*', '0.0.0.0/0', 'Internet']
            elif prop_name == 'allows_admin_ports':
                dest_ports = obj.get('DestinationPortRange', '')
                return '22' in dest_ports or '3389' in dest_ports
            return False

    total_rules = len(nsg_rules)
    high_risk_rules = [rule for rule in nsg_rules if has_property(rule, 'is_high_risk')]
    internet_facing = [rule for rule in nsg_rules if has_property(rule, 'is_internet_facing')]
    admin_exposed = [rule for rule in nsg_rules if
                     has_property(rule, 'is_internet_facing') and has_property(rule, 'allows_admin_ports')]

    print(f"Total NSG rules: {total_rules}")
    print(f"High-risk rules: {len(high_risk_rules)}")
    print(f"Internet-facing rules: {len(internet_facing)}")
    print(f"Admin ports exposed to internet: {len(admin_exposed)}")

    if admin_exposed:
        print(f"\n🚨 CRITICAL: Admin ports exposed to internet:")
        for rule in admin_exposed[:5]:  # Show first 5
            app = get_field(rule, "application", "Application")
            nsg_name = get_field(rule, "nsg_name", "NSGName")
            rule_name = get_field(rule, "rule_name", "RuleName")
            dest_ports = get_field(rule, "destination_port_range", "DestinationPortRange")
            print(f"  ❌ {app}/{nsg_name}: {rule_name} allows {dest_ports}")

    if high_risk_rules:
        print(f"\n⚠️ High-risk rules by application:")
        risk_by_app = {}
        for rule in high_risk_rules:
            app = get_field(rule, "application", "Application")
            risk_by_app[app] = risk_by_app.get(app, 0) + 1

        for app, count in sorted(risk_by_app.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {app}: {count} high-risk rules")


def display_certificate_analysis(cert_results: List[Dict[str, Any]]):
    """
    Display certificate analysis results
    """
    if not cert_results:
        print("❌ No certificate data available")
        return

    print(f"\n🔐 CERTIFICATE ANALYSIS SUMMARY")
    print(f"{'=' * 50}")

    total_resources = len(cert_results)
    non_compliant = [r for r in cert_results if "Non-Compliant" in r.get("ComplianceStatus", "")]
    high_risk = [r for r in cert_results if r.get("SecurityRisk", "") == "High"]
    modern_tls = [r for r in cert_results if "Modern TLS" in r.get("ComplianceStatus", "")]

    print(f"Total certificate configurations: {total_resources}")
    print(f"Non-compliant configurations: {len(non_compliant)}")
    print(f"High-risk configurations: {len(high_risk)}")
    print(f"Modern TLS configurations: {len(modern_tls)}")

    if high_risk:
        print(f"\n⚠️ High-risk certificate configurations:")
        for cert in high_risk[:5]:  # Show first 5
            app = cert.get("Application", "Unknown")
            resource = cert.get("ResourceName", "Unknown")
            status = cert.get("ComplianceStatus", "Unknown")
            print(f"  ❌ {app}/{resource}: {status}")


def display_optimization_analysis(optimization_results: List[Dict[str, Any]]):
    """
    Display resource optimization analysis results
    """
    if not optimization_results:
        print("❌ No optimization data available")
        return

    print(f"\n💰 RESOURCE OPTIMIZATION SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'is_unused':
                status = obj.get('UtilizationStatus', '')
                return 'Unused' in status
            elif prop_name == 'has_high_optimization_potential':
                potential = obj.get('CostOptimizationPotential', '')
                return 'High' in potential
            elif prop_name == 'is_misconfigured':
                status = obj.get('UtilizationStatus', '')
                return 'Misconfigured' in status
            return False

    total_resources = len(optimization_results)
    unused_resources = [r for r in optimization_results if has_property(r, 'is_unused')]
    high_potential = [r for r in optimization_results if has_property(r, 'has_high_optimization_potential')]
    misconfigured = [r for r in optimization_results if has_property(r, 'is_misconfigured')]

    print(f"Total resources analyzed: {total_resources}")
    print(f"Unused resources: {len(unused_resources)}")
    print(f"High optimization potential: {len(high_potential)}")
    print(f"Misconfigured resources: {len(misconfigured)}")

    if high_potential:
        print(f"\n💡 High optimization potential resources:")
        for resource in high_potential[:5]:  # Show first 5
            app = get_field(resource, "application", "Application")
            name = get_field(resource, "resource_name", "ResourceName")
            resource_type = get_field(resource, "optimization_type", "OptimizationType")
            potential = get_field(resource, "cost_optimization_potential", "CostOptimizationPotential")
            print(f"  🔴 {app}/{name} ({resource_type}): {potential}")


# ============================================================================
# VM GOVERNANCE DISPLAY FUNCTIONS
# ============================================================================

def display_vm_governance_summary(vm_summary_results: List[Union[Dict, VMGovernanceSummary]]):
    """
    Display VM governance metrics in a readable format
    """
    if not vm_summary_results:
        print("❌ No VM governance data available")
        return

    print(f"\n🖥️ VM GOVERNANCE SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, 0)

    total_apps = len(vm_summary_results)
    total_vms = sum(get_field(r, "total_vms", "TotalVMs") for r in vm_summary_results)
    total_encrypted = sum(get_field(r, "encrypted_vms", "EncryptedVMs") for r in vm_summary_results)
    total_optimized = sum(get_field(r, "optimized_vms", "OptimizedVMs") for r in vm_summary_results)
    total_stopped = sum(get_field(r, "stopped_vms", "StoppedVMs") for r in vm_summary_results)

    overall_governance = sum(get_field(r, "governance_score", "GovernanceScore") for r in
                             vm_summary_results) / total_apps if total_apps > 0 else 0

    print(f"Applications analyzed: {total_apps}")
    print(f"Total VMs: {total_vms}")
    print(
        f"Encrypted VMs: {total_encrypted} ({total_encrypted / total_vms * 100:.1f}%)" if total_vms > 0 else "Encrypted VMs: 0")
    print(
        f"Optimized VMs: {total_optimized} ({total_optimized / total_vms * 100:.1f}%)" if total_vms > 0 else "Optimized VMs: 0")
    print(f"Stopped VMs (cost waste): {total_stopped}")
    print(f"Average governance score: {overall_governance:.1f}%")

    print(f"\n🖥️ Per-Application VM Governance:")
    for app in vm_summary_results:
        app_name = get_field(app, "application", "Application")
        governance_score = get_field(app, "governance_score", "GovernanceScore")
        issues = get_field(app, "vms_with_issues", "VMsWithIssues")
        total_app_vms = get_field(app, "total_vms", "TotalVMs")
        windows_vms = get_field(app, "windows_vms", "WindowsVMs")
        linux_vms = get_field(app, "linux_vms", "LinuxVMs")

        status_emoji = "✅" if governance_score >= 80 else "⚠️" if governance_score >= 60 else "❌"

        # Show grade if available
        grade = ""
        if hasattr(app, "governance_grade"):
            grade = f" (Grade {app.governance_grade})"

        print(
            f"{status_emoji} {app_name}: {governance_score:.1f}% governed ({issues} issues, {total_app_vms} VMs: {windows_vms}W/{linux_vms}L){grade}")


# ============================================================================
# IAM ANALYSIS DISPLAY FUNCTIONS
# ============================================================================

def display_iam_compliance_summary(iam_summary_results: List[Union[Dict, IAMComplianceSummary]]):
    """
    Display IAM compliance metrics in a readable format
    """
    if not iam_summary_results:
        print("❌ No IAM compliance data available")
        return

    print(f"\n🔐 IAM COMPLIANCE SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, 0)

    total_apps = len(iam_summary_results)
    total_iam_resources = sum(get_field(r, "total_iam_resources", "TotalIAMResources") for r in iam_summary_results)
    total_high_privilege = sum(get_field(r, "high_privilege_assignments", "HighPrivilegeAssignments") for r in iam_summary_results)
    total_guest_users = sum(get_field(r, "guest_user_assignments", "GuestUserAssignments") for r in iam_summary_results)
    total_orphaned_identities = sum(get_field(r, "orphaned_identities", "OrphanedIdentities") for r in iam_summary_results)

    overall_iam_compliance = sum(get_field(r, "iam_compliance_score", "IAMComplianceScore") for r in
                                 iam_summary_results) / total_apps if total_apps > 0 else 0

    print(f"Applications analyzed: {total_apps}")
    print(f"Total IAM resources: {total_iam_resources}")
    print(f"High-privilege assignments: {total_high_privilege}")
    print(f"Guest user assignments: {total_guest_users}")
    print(f"Orphaned identities: {total_orphaned_identities}")
    print(f"Average IAM compliance score: {overall_iam_compliance:.1f}%")

    print(f"\n🔐 Per-Application IAM Compliance:")
    for app in iam_summary_results:
        app_name = get_field(app, "application", "Application")
        iam_compliance_score = get_field(app, "iam_compliance_score", "IAMComplianceScore")
        issues = get_field(app, "total_issues", "TotalIssues")
        total_app_resources = get_field(app, "total_iam_resources", "TotalIAMResources")

        status_emoji = "✅" if iam_compliance_score >= 90 else "⚠️" if iam_compliance_score >= 70 else "❌"

        # Show grade if available
        grade = ""
        if hasattr(app, "iam_compliance_grade"):
            grade = f" (Grade {app.iam_compliance_grade})"

        print(f"{status_emoji} {app_name}: {iam_compliance_score:.1f}% IAM compliant ({issues} issues, {total_app_resources} resources){grade}")


def display_role_assignment_analysis(role_assignment_results: List[Union[Dict, RoleAssignmentResult]]):
    """
    Display role assignment analysis summary
    """
    if not role_assignment_results:
        print("❌ No role assignment data available")
        return

    print(f"\n🎭 ROLE ASSIGNMENT ANALYSIS SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'is_high_privilege':
                return "High Privilege" in obj.get('PrivilegeLevel', '')
            elif prop_name == 'is_guest_user':
                return "Guest User" in obj.get('GuestUserRisk', '')
            elif prop_name == 'is_custom_role':
                return obj.get('RoleType', '') == 'CustomRole'
            elif prop_name == 'is_high_risk':
                return obj.get('SecurityRisk', '').lower().startswith('high')
            elif prop_name == 'is_broad_scope':
                return obj.get('ScopeLevel', '') in ['Subscription', 'Management Group']
            return False

    total_assignments = len(role_assignment_results)
    high_privilege = [r for r in role_assignment_results if has_property(r, 'is_high_privilege')]
    guest_users = [r for r in role_assignment_results if has_property(r, 'is_guest_user')]
    custom_roles = [r for r in role_assignment_results if has_property(r, 'is_custom_role')]
    high_risk = [r for r in role_assignment_results if has_property(r, 'is_high_risk')]
    broad_scope = [r for r in role_assignment_results if has_property(r, 'is_broad_scope')]

    print(f"Total role assignments: {total_assignments}")
    print(f"High-privilege assignments: {len(high_privilege)}")
    print(f"Guest user assignments: {len(guest_users)}")
    print(f"Custom role assignments: {len(custom_roles)}")
    print(f"High-risk assignments: {len(high_risk)}")
    print(f"Broad scope assignments: {len(broad_scope)}")

    # Show critical combinations
    privilege_escalation_risk = [r for r in role_assignment_results if
                                has_property(r, 'is_high_privilege') and has_property(r, 'is_broad_scope')]
    guest_admin_access = [r for r in role_assignment_results if
                         has_property(r, 'is_guest_user') and has_property(r, 'is_high_privilege')]

    if privilege_escalation_risk:
        print(f"\n🚨 CRITICAL: {len(privilege_escalation_risk)} privilege escalation risks (high privilege + broad scope):")
        for ra in privilege_escalation_risk[:5]:  # Show first 5
            app = get_field(ra, "application", "Application")
            role_name = get_field(ra, "role_name", "RoleName")
            scope_level = get_field(ra, "scope_level", "ScopeLevel")
            print(f"  ❌ {app}: {role_name} at {scope_level} level")

    if guest_admin_access:
        print(f"\n👤 ALERT: {len(guest_admin_access)} guest users with admin access:")
        for ra in guest_admin_access[:3]:  # Show first 3
            app = get_field(ra, "application", "Application")
            role_name = get_field(ra, "role_name", "RoleName")
            print(f"  ⚠️ {app}: Guest user with {role_name}")


def display_key_vault_security_analysis(key_vault_results: List[Union[Dict, KeyVaultSecurityResult]]):
    """
    Display Key Vault security analysis summary
    """
    if not key_vault_results:
        print("❌ No Key Vault security data available")
        return

    print(f"\n🔐 KEY VAULT SECURITY ANALYSIS SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'has_purge_protection':
                return "Enabled" in obj.get('PurgeProtectionStatus', '')
            elif prop_name == 'is_public_access':
                return "Public Access" in obj.get('NetworkSecurity', '')
            elif prop_name == 'is_high_risk':
                return obj.get('SecurityRisk', '').lower().startswith('high')
            elif prop_name == 'is_compliant':
                return not obj.get('SecurityRisk', '').lower().startswith('high')
            return False

    total_vaults = len(key_vault_results)
    purge_protected = [r for r in key_vault_results if has_property(r, 'has_purge_protection')]
    public_access = [r for r in key_vault_results if has_property(r, 'is_public_access')]
    high_risk = [r for r in key_vault_results if has_property(r, 'is_high_risk')]
    compliant = [r for r in key_vault_results if has_property(r, 'is_compliant')]

    print(f"Total Key Vaults: {total_vaults}")
    print(f"With purge protection: {len(purge_protected)}")
    print(f"With public access: {len(public_access)}")
    print(f"High-risk vaults: {len(high_risk)}")
    print(f"Compliant vaults: {len(compliant)}")

    if public_access:
        print(f"\n🌐 Key Vaults with public access:")
        for kv in public_access[:5]:  # Show first 5
            app = get_field(kv, "application", "Application")
            vault_name = get_field(kv, "vault_name", "VaultName")
            security_risk = get_field(kv, "security_risk", "SecurityRisk")
            print(f"  ⚠️ {app}/{vault_name}: {security_risk}")

    if high_risk:
        print(f"\n❌ High-risk Key Vault configurations:")
        for kv in high_risk[:5]:  # Show first 5
            app = get_field(kv, "application", "Application")
            vault_name = get_field(kv, "vault_name", "VaultName")
            security_findings = get_field(kv, "security_findings", "SecurityFindings")
            print(f"  ❌ {app}/{vault_name}: {security_findings}")


def display_managed_identity_analysis(managed_identity_results: List[Union[Dict, ManagedIdentityResult]]):
    """
    Display managed identity analysis summary
    """
    if not managed_identity_results:
        print("❌ No managed identity data available")
        return

    print(f"\n🆔 MANAGED IDENTITY ANALYSIS SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'is_orphaned':
                return "Orphaned" in obj.get('OrphanedStatus', '')
            elif prop_name == 'is_in_use':
                return obj.get('OrphanedStatus', '') == 'In Use'
            elif prop_name == 'is_high_risk':
                return obj.get('SecurityRisk', '').lower().startswith('high')
            elif prop_name == 'is_stale':
                return int(obj.get('DaysOld', 0)) > 90 and not has_property(obj, 'is_in_use')
            return False

    total_identities = len(managed_identity_results)
    orphaned = [r for r in managed_identity_results if has_property(r, 'is_orphaned')]
    in_use = [r for r in managed_identity_results if has_property(r, 'is_in_use')]
    high_risk = [r for r in managed_identity_results if has_property(r, 'is_high_risk')]
    stale = [r for r in managed_identity_results if has_property(r, 'is_stale')]

    print(f"Total managed identities: {total_identities}")
    print(f"Orphaned identities: {len(orphaned)}")
    print(f"In use identities: {len(in_use)}")
    print(f"High-risk identities: {len(high_risk)}")
    print(f"Stale identities: {len(stale)}")

    if orphaned:
        print(f"\n❌ Orphaned managed identities (cleanup recommended):")
        for mi in orphaned[:5]:  # Show first 5
            app = get_field(mi, "application", "Application")
            identity_name = get_field(mi, "identity_name", "IdentityName")
            days_old = get_field(mi, "days_old", "DaysOld")
            orphaned_status = get_field(mi, "orphaned_status", "OrphanedStatus")
            print(f"  🗑️ {app}/{identity_name}: {orphaned_status} ({days_old} days old)")

    if stale:
        print(f"\n📅 Stale managed identities:")
        for mi in stale[:3]:  # Show first 3
            app = get_field(mi, "application", "Application")
            identity_name = get_field(mi, "identity_name", "IdentityName")
            days_old = get_field(mi, "days_old", "DaysOld")
            print(f"  ⏰ {app}/{identity_name}: {days_old} days old")


def display_custom_role_analysis(custom_role_results: List[Union[Dict, CustomRoleResult]]):
    """
    Display custom role analysis summary
    """
    if not custom_role_results:
        print("❌ No custom role data available")
        return

    print(f"\n📋 CUSTOM ROLE ANALYSIS SUMMARY")
    print(f"{'=' * 50}")

    def get_field(obj, field_name, dict_key=None):
        if hasattr(obj, field_name):
            return getattr(obj, field_name)
        else:
            return obj.get(dict_key or field_name, '')

    def has_property(obj, prop_name):
        if hasattr(obj, prop_name):
            return getattr(obj, prop_name)
        else:
            # Fallback logic for dictionary objects
            if prop_name == 'is_unused':
                return "Unused" in obj.get('UsageStatus', '')
            elif prop_name == 'is_high_privilege':
                return "High Privilege" in obj.get('PrivilegeLevel', '')
            elif prop_name == 'is_high_risk':
                return obj.get('SecurityRisk', '').lower().startswith('high')
            elif prop_name == 'is_stale':
                return has_property(obj, 'is_unused') and int(obj.get('DaysOld', 0)) > 90
            elif prop_name == 'is_actively_used':
                return int(obj.get('AssignmentCount', 0)) > 1
            return False

    total_roles = len(custom_role_results)
    unused = [r for r in custom_role_results if has_property(r, 'is_unused')]
    high_privilege = [r for r in custom_role_results if has_property(r, 'is_high_privilege')]
    high_risk = [r for r in custom_role_results if has_property(r, 'is_high_risk')]
    stale = [r for r in custom_role_results if has_property(r, 'is_stale')]
    actively_used = [r for r in custom_role_results if has_property(r, 'is_actively_used')]

    print(f"Total custom roles: {total_roles}")
    print(f"Unused roles: {len(unused)}")
    print(f"High-privilege roles: {len(high_privilege)}")
    print(f"High-risk roles: {len(high_risk)}")
    print(f"Stale roles: {len(stale)}")
    print(f"Actively used roles: {len(actively_used)}")

    if unused:
        print(f"\n🗑️ Unused custom roles (consider cleanup):")
        for cr in unused[:5]:  # Show first 5
            app = get_field(cr, "application", "Application")
            role_name = get_field(cr, "role_name", "RoleName")
            days_old = get_field(cr, "days_old", "DaysOld")
            assignment_count = get_field(cr, "assignment_count", "AssignmentCount")
            print(f"  ❌ {app}/{role_name}: {assignment_count} assignments, {days_old} days old")

    if high_privilege:
        print(f"\n🔴 High-privilege custom roles:")
        for cr in high_privilege[:3]:  # Show first 3
            app = get_field(cr, "application", "Application")
            role_name = get_field(cr, "role_name", "RoleName")
            privilege_level = get_field(cr, "privilege_level", "PrivilegeLevel")
            print(f"  ⚠️ {app}/{role_name}: {privilege_level}")


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

# ============================================================================
# CONTAINER & MODERN WORKLOADS FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def aks_cluster_security_results(client):
    """Fixture to get AKS cluster security analysis results once per test session"""
    try:
        return client.query_aks_cluster_security()
    except Exception as e:
        pytest.skip(f"AKS cluster security query failed: {e}")


@pytest.fixture(scope="session")
def aks_node_pool_results(client):
    """Fixture to get AKS node pool analysis results once per test session"""
    try:
        return client.query_aks_node_pools()
    except Exception as e:
        pytest.skip(f"AKS node pool query failed: {e}")


@pytest.fixture(scope="session")
def container_registry_security_results(client):
    """Fixture to get Container Registry security analysis results once per test session"""
    try:
        return client.query_container_registry_security()
    except Exception as e:
        pytest.skip(f"Container Registry security query failed: {e}")


@pytest.fixture(scope="session")
def app_service_security_results(client):
    """Fixture to get App Service security analysis results once per test session"""
    try:
        return client.query_app_service_security()
    except Exception as e:
        pytest.skip(f"App Service security query failed: {e}")


@pytest.fixture(scope="session")
def app_service_slot_results(client):
    """Fixture to get App Service deployment slot results once per test session"""
    try:
        return client.query_app_service_deployment_slots()
    except Exception as e:
        pytest.skip(f"App Service deployment slots query failed: {e}")


@pytest.fixture(scope="session")
def container_workloads_compliance_summary_results(client):
    """Fixture to get Container & Modern Workloads compliance summary results once per test session"""
    try:
        return client.get_container_workloads_compliance_summary()
    except Exception as e:
        pytest.skip(f"Container workloads compliance summary query failed: {e}")

@pytest.fixture(scope="session")
def client():
    """Create an Azure Resource Graph client for testing"""
    try:
        return AzureResourceGraphClient()
    except Exception as e:
        pytest.skip(f"Failed to create Azure client: {e}")


@pytest.fixture(scope="session")
def sample_basic_query():
    """Sample basic query for testing Resource Graph functionality"""
    return """
    Resources
    | where type == 'microsoft.storage/storageaccounts' or type == 'microsoft.compute/virtualmachines'
    | project name, type, location, resourceGroup, tags
    | limit 10
    """


# ============================================================================
# STORAGE ANALYSIS FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def storage_analysis_results(client):
    """Fixture to get comprehensive storage analysis results once per test session"""
    try:
        return client.query_storage_analysis()
    except Exception as e:
        pytest.skip(f"Storage analysis query failed: {e}")


@pytest.fixture(scope="session")
def storage_access_control_results(client):
    """Fixture to get storage access control results once per test session"""
    try:
        return client.query_storage_access_control()
    except Exception as e:
        pytest.skip(f"Storage access control query failed: {e}")


@pytest.fixture(scope="session")
def storage_backup_results(client):
    """Fixture to get storage backup analysis results once per test session"""
    try:
        return client.query_storage_backup_analysis()
    except Exception as e:
        pytest.skip(f"Storage backup analysis query failed: {e}")


@pytest.fixture(scope="session")
def storage_optimization_results(client):
    """Fixture to get storage optimization results once per test session"""
    try:
        return client.query_storage_optimization()
    except Exception as e:
        pytest.skip(f"Storage optimization query failed: {e}")


@pytest.fixture(scope="session")
def storage_compliance_summary_results(client):
    """Fixture to get comprehensive storage compliance summary results once per test session"""
    try:
        return client.get_storage_compliance_summary()
    except Exception as e:
        pytest.skip(f"Storage compliance summary query failed: {e}")


# Legacy storage fixtures for backward compatibility
@pytest.fixture(scope="session")
def storage_encryption_results(client):
    """Fixture to get storage encryption results once per test session (backward compatibility)"""
    try:
        return client.query_storage_encryption()
    except Exception as e:
        pytest.skip(f"Storage encryption query failed: {e}")


@pytest.fixture(scope="session")
def compliance_summary_results(client):
    """Fixture to get compliance summary results once per test session (backward compatibility)"""
    try:
        return client.get_compliance_summary()
    except Exception as e:
        pytest.skip(f"Compliance summary query failed: {e}")


# ============================================================================
# NETWORK ANALYSIS FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def network_analysis_results(client):
    """Fixture to get network analysis results once per test session"""
    try:
        return client.query_network_analysis()
    except Exception as e:
        pytest.skip(f"Network analysis query failed: {e}")


@pytest.fixture(scope="session")
def nsg_detailed_results(client):
    """Fixture to get detailed NSG rule results once per test session"""
    try:
        return client.query_nsg_detailed()
    except Exception as e:
        pytest.skip(f"NSG detailed query failed: {e}")


@pytest.fixture(scope="session")
def network_compliance_summary_results(client):
    """Fixture to get network compliance summary results once per test session"""
    try:
        return client.get_network_compliance_summary()
    except Exception as e:
        pytest.skip(f"Network compliance summary query failed: {e}")


@pytest.fixture(scope="session")
def certificate_analysis_results(client):
    """Fixture to get certificate analysis results once per test session"""
    try:
        return client.query_certificate_analysis()
    except Exception as e:
        pytest.skip(f"Certificate analysis query failed: {e}")


@pytest.fixture(scope="session")
def network_topology_results(client):
    """Fixture to get network topology results once per test session"""
    try:
        return client.query_network_topology()
    except Exception as e:
        pytest.skip(f"Network topology query failed: {e}")


@pytest.fixture(scope="session")
def network_optimization_results(client):
    """Fixture to get network resource optimization results once per test session"""
    try:
        return client.query_resource_optimization()
    except Exception as e:
        pytest.skip(f"Network resource optimization query failed: {e}")


# ============================================================================
# VM GOVERNANCE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def vm_security_results(client):
    """Fixture to get VM security analysis results once per test session"""
    try:
        return client.query_vm_security()
    except Exception as e:
        pytest.skip(f"VM security query failed: {e}")


@pytest.fixture(scope="session")
def vm_optimization_results(client):
    """Fixture to get VM optimization results once per test session"""
    try:
        return client.query_vm_optimization()
    except Exception as e:
        pytest.skip(f"VM optimization query failed: {e}")


@pytest.fixture(scope="session")
def vm_extensions_results(client):
    """Fixture to get VM extensions results once per test session"""
    try:
        return client.query_vm_extensions()
    except Exception as e:
        pytest.skip(f"VM extensions query failed: {e}")


@pytest.fixture(scope="session")
def vm_patch_compliance_results(client):
    """Fixture to get VM patch compliance results once per test session"""
    try:
        return client.query_vm_patch_compliance()
    except Exception as e:
        pytest.skip(f"VM patch compliance query failed: {e}")


@pytest.fixture(scope="session")
def vm_governance_summary_results(client):
    """Fixture to get VM governance summary results once per test session"""
    try:
        return client.get_vm_governance_summary()
    except Exception as e:
        pytest.skip(f"VM governance summary query failed: {e}")


# ============================================================================
# IDENTITY & ACCESS MANAGEMENT FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def role_assignment_results(client):
    """Fixture to get role assignment analysis results once per test session"""
    try:
        return client.query_role_assignments()
    except Exception as e:
        pytest.skip(f"Role assignment query failed: {e}")


@pytest.fixture(scope="session")
def key_vault_security_results(client):
    """Fixture to get Key Vault security analysis results once per test session"""
    try:
        return client.query_key_vault_security()
    except Exception as e:
        pytest.skip(f"Key Vault security query failed: {e}")


@pytest.fixture(scope="session")
def managed_identity_results(client):
    """Fixture to get managed identity analysis results once per test session"""
    try:
        return client.query_managed_identities()
    except Exception as e:
        pytest.skip(f"Managed identity query failed: {e}")


@pytest.fixture(scope="session")
def custom_role_results(client):
    """Fixture to get custom role analysis results once per test session"""
    try:
        return client.query_custom_roles()
    except Exception as e:
        pytest.skip(f"Custom role query failed: {e}")


@pytest.fixture(scope="session")
def iam_compliance_summary_results(client):
    """Fixture to get IAM compliance summary results once per test session"""
    try:
        return client.get_iam_compliance_summary()
    except Exception as e:
        pytest.skip(f"IAM compliance summary query failed: {e}")

# ============================================================================
# CONTAINER & MODERN WORKLOADS ANALYSIS TESTS
# ============================================================================

@pytest.mark.container
class TestContainerWorkloadsAnalysisWithDisplay:
    """Test comprehensive Container & Modern Workloads analysis with result display"""

    @pytest.mark.integration
    def test_aks_cluster_security_analysis_with_display(self, aks_cluster_security_results):
        """Test AKS cluster security analysis and display results"""
        assert isinstance(aks_cluster_security_results, list)

        # Display the results
        pretty_print_results(
            aks_cluster_security_results,
            "AKS CLUSTER SECURITY ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(aks_cluster_security_results, "AKS Cluster Security Analysis")

        # Display AKS cluster security analysis
        display_aks_cluster_security_analysis(aks_cluster_security_results)

    # !/usr/bin/env python3
    """
    Fixed AKS Node Pool Analysis Query - Safe for environments with no AKS clusters
    Replace the get_aks_node_pool_analysis_query() method in container_workload_analysis.py
    """

    @staticmethod
    def get_aks_node_pool_analysis_query() -> str:
        """
        Safe AKS node pool analysis query that handles empty result sets properly

        Returns:
            KQL query string for AKS node pool analysis
        """
        return """
        Resources
        | where type == 'microsoft.containerservice/managedclusters'
        | extend Application = coalesce(tags.Application, tags.app, 'Untagged/Orphaned')
        | extend HasAgentPools = array_length(properties.agentPoolProfiles) > 0
        | where HasAgentPools == true
        | mv-expand nodePool = properties.agentPoolProfiles
        | extend NodePoolName = tostring(nodePool.name)
        | extend NodePoolType = coalesce(tostring(nodePool.type), 'User')
        | extend VMSize = tostring(nodePool.vmSize)
        | extend NodeCount = toint(nodePool.count)
        | extend EnableAutoScaling = coalesce(tobool(nodePool.enableAutoScaling), false)
        | extend NodePoolMode = coalesce(tostring(nodePool.mode), 'User')
        | extend OSType = coalesce(tostring(nodePool.osType), 'Linux')
        | extend VMSizeCategory = case(
            VMSize startswith 'Standard_A', 'Basic/Legacy',
            VMSize startswith 'Standard_B', 'Burstable',
            VMSize startswith 'Standard_D', 'General Purpose',
            VMSize startswith 'Standard_E', 'Memory Optimized',
            VMSize startswith 'Standard_F', 'Compute Optimized',
            'Standard'
        )
        | extend ScalingConfiguration = case(
            EnableAutoScaling == true, 'Auto-scaling Enabled',
            'Manual Scaling'
        )
        | extend NodePoolRisk = case(
            VMSizeCategory == 'Basic/Legacy', 'Medium - Legacy VM sizes',
            NodeCount == 1 and NodePoolMode == 'System', 'High - Single node system pool',
            'Low - Standard configuration'
        )
        | extend OptimizationPotential = case(
            VMSizeCategory == 'Basic/Legacy', 'High - Upgrade to modern VM sizes',
            EnableAutoScaling != true and NodePoolMode == 'User', 'Medium - Enable auto-scaling',
            'Low - Configuration appears optimal'
        )
        | extend NodePoolDetails = strcat(
            'VM: ', VMSize,
            ' | Count: ', tostring(NodeCount),
            ' | Mode: ', NodePoolMode,
            ' | OS: ', OSType
        )
        | project
            Application,
            ClusterName = name,
            NodePoolName,
            NodePoolType,
            VMSize,
            VMSizeCategory,
            ScalingConfiguration,
            OptimizationPotential,
            NodePoolRisk,
            NodePoolDetails,
            ResourceGroup = resourceGroup,
            Location = location,
            ResourceId = strcat(id, '/agentPools/', NodePoolName)
        | order by Application, ClusterName, NodePoolRisk desc, NodePoolName
        """

    @pytest.mark.integration
    def test_container_registry_security_with_display(self, container_registry_security_results):
        """Test Container Registry security analysis and display results"""
        assert isinstance(container_registry_security_results, list)

        # Display the results
        pretty_print_results(
            container_registry_security_results,
            "CONTAINER REGISTRY SECURITY ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(container_registry_security_results, "Container Registry Security Analysis")

        # Display Container Registry security analysis
        display_container_registry_security_analysis(container_registry_security_results)

    @pytest.mark.integration
    def test_app_service_security_with_display(self, app_service_security_results):
        """Test App Service security analysis and display results"""
        assert isinstance(app_service_security_results, list)

        # Display the results
        pretty_print_results(
            app_service_security_results,
            "APP SERVICE SECURITY ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(app_service_security_results, "App Service Security Analysis")

        # Display App Service security analysis
        display_app_service_security_analysis(app_service_security_results)

    @pytest.mark.integration
    def test_app_service_deployment_slots_with_display(self, app_service_slot_results):
        """Test App Service deployment slots analysis and display results"""
        assert isinstance(app_service_slot_results, list)

        # Display the results
        pretty_print_results(
            app_service_slot_results,
            "APP SERVICE DEPLOYMENT SLOTS ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(app_service_slot_results, "App Service Deployment Slots Analysis")

        if app_service_slot_results:
            def has_property(obj, prop_name):
                if hasattr(obj, prop_name):
                    return getattr(obj, prop_name)
                else:
                    # Fallback logic for dictionary objects
                    if prop_name == 'is_secure_configuration':
                        return "Secure Configuration" in obj.get('SlotConfiguration', '')
                    elif prop_name == 'is_high_risk':
                        return obj.get('SlotRisk', '').lower().startswith('high')
                    return False

            secure_slots = [r for r in app_service_slot_results if has_property(r, 'is_secure_configuration')]
            high_risk_slots = [r for r in app_service_slot_results if has_property(r, 'is_high_risk')]

            print(f"\n📊 DEPLOYMENT SLOTS SUMMARY")
            print(f"{'=' * 40}")
            print(f"Total deployment slots: {len(app_service_slot_results)}")
            print(f"Secure configurations: {len(secure_slots)}")
            print(f"High-risk slots: {len(high_risk_slots)}")

    @pytest.mark.integration
    def test_container_workloads_compliance_summary_with_display(self, container_workloads_compliance_summary_results):
        """Test Container & Modern Workloads compliance summary and display results"""
        assert isinstance(container_workloads_compliance_summary_results, list)

        # Display the results
        pretty_print_results(
            container_workloads_compliance_summary_results,
            "CONTAINER & MODERN WORKLOADS COMPLIANCE SUMMARY RESULTS",
            max_items=5
        )

        # Display container workloads compliance metrics
        display_container_workloads_compliance_summary(container_workloads_compliance_summary_results)

    @pytest.mark.integration
    def test_comprehensive_container_workloads_analysis(self, client):
        """Test comprehensive container workloads analysis method"""
        print(f"\n🚀 TESTING COMPREHENSIVE CONTAINER WORKLOADS ANALYSIS")
        print(f"{'=' * 60}")

        try:
            results = client.query_comprehensive_container_workloads_analysis()

            assert isinstance(results, dict)
            assert 'aks_cluster_security' in results
            assert 'aks_node_pools' in results
            assert 'container_registry_security' in results
            assert 'app_service_security' in results
            assert 'app_service_slots' in results
            assert 'compliance_summary' in results

            print(f"\n✅ Comprehensive analysis completed successfully")
            print(f"   🚀 AKS clusters: {len(results['aks_cluster_security'])}")
            print(f"   🖥️ Node pools: {len(results['aks_node_pools'])}")
            print(f"   📦 Container registries: {len(results['container_registry_security'])}")
            print(f"   🌐 App Services: {len(results['app_service_security'])}")
            print(f"   🔄 Deployment slots: {len(results['app_service_slots'])}")
            print(f"   📊 Applications: {len(results['compliance_summary'])}")

            return results

        except Exception as e:
            print(f"⚠️ Comprehensive container workloads analysis failed: {e}")
            pytest.skip(f"Comprehensive container workloads analysis failed: {e}")

# ============================================================================
# COMPREHENSIVE STORAGE ANALYSIS TESTS
# ============================================================================

@pytest.mark.storage
class TestComprehensiveStorageAnalysisWithDisplay:
    """Test comprehensive storage analysis with result display"""

    @pytest.mark.integration
    def test_storage_analysis_query_with_display(self, storage_analysis_results):
        """Test comprehensive storage analysis query execution and display results"""
        assert isinstance(storage_analysis_results, list)

        # Display the results
        pretty_print_results(
            storage_analysis_results,
            "COMPREHENSIVE STORAGE ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(storage_analysis_results, "Storage Analysis Resources")

        # Display comprehensive storage analysis summary
        display_storage_analysis_summary(storage_analysis_results)

    @pytest.mark.integration
    def test_storage_access_control_with_display(self, storage_access_control_results):
        """Test storage access control analysis and display results"""
        assert isinstance(storage_access_control_results, list)

        # Display the results
        pretty_print_results(
            storage_access_control_results,
            "STORAGE ACCESS CONTROL ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(storage_access_control_results, "Storage Access Control")

        if storage_access_control_results:
            def has_property(obj, prop_name):
                if hasattr(obj, prop_name):
                    return getattr(obj, prop_name)
                else:
                    # Fallback logic for dictionary objects
                    if prop_name == 'is_high_risk':
                        return obj.get('SecurityRisk', '').lower() == 'high'
                    elif prop_name == 'allows_public_access':
                        return 'Enabled' in obj.get('PublicAccess', '')
                    return False

            high_risk_access = [r for r in storage_access_control_results if has_property(r, 'is_high_risk')]
            public_access = [r for r in storage_access_control_results if has_property(r, 'allows_public_access')]

            print(f"\n📊 STORAGE ACCESS CONTROL SUMMARY")
            print(f"{'=' * 40}")
            print(f"Total access configurations: {len(storage_access_control_results)}")
            print(f"High-risk configurations: {len(high_risk_access)}")
            print(f"Public access enabled: {len(public_access)}")

    @pytest.mark.integration
    def test_storage_backup_analysis_with_display(self, storage_backup_results):
        """Test storage backup analysis and display results"""
        assert isinstance(storage_backup_results, list)

        # Display the results
        pretty_print_results(
            storage_backup_results,
            "STORAGE BACKUP ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(storage_backup_results, "Storage Backup Analysis")

        if storage_backup_results:
            def has_property(obj, prop_name):
                if hasattr(obj, prop_name):
                    return getattr(obj, prop_name)
                else:
                    # Fallback logic for dictionary objects
                    if prop_name == 'has_backup_configured':
                        return "No backup" not in obj.get('BackupConfiguration', '').lower()
                    elif prop_name == 'is_high_risk':
                        return obj.get('DisasterRecoveryRisk', '').lower().startswith('high')
                    return False

            no_backup = [r for r in storage_backup_results if not has_property(r, 'has_backup_configured')]
            high_risk_dr = [r for r in storage_backup_results if has_property(r, 'is_high_risk')]

            print(f"\n📊 STORAGE BACKUP SUMMARY")
            print(f"{'=' * 40}")
            print(f"Total backup configurations: {len(storage_backup_results)}")
            print(f"Resources without backup: {len(no_backup)}")
            print(f"High disaster recovery risk: {len(high_risk_dr)}")

    @pytest.mark.integration
    def test_storage_optimization_with_display(self, storage_optimization_results):
        """Test storage optimization analysis and display results"""
        assert isinstance(storage_optimization_results, list)

        # Display the results
        pretty_print_results(
            storage_optimization_results,
            "STORAGE OPTIMIZATION ANALYSIS RESULTS",
            max_items=5
        )

        # Display storage optimization analysis
        display_storage_optimization_analysis(storage_optimization_results)

    @pytest.mark.integration
    def test_storage_compliance_summary_with_display(self, storage_compliance_summary_results):
        """Test comprehensive storage compliance summary and display results"""
        assert isinstance(storage_compliance_summary_results, list)

        # Display the results
        pretty_print_results(
            storage_compliance_summary_results,
            "COMPREHENSIVE STORAGE COMPLIANCE SUMMARY",
            max_items=5
        )

        # Display compliance metrics
        display_storage_compliance_metrics(storage_compliance_summary_results)


# ============================================================================
# NETWORK ANALYSIS TESTS
# ============================================================================

@pytest.mark.network
class TestNetworkAnalysisWithDisplay:
    """Test comprehensive network analysis with result display"""

    @pytest.mark.integration
    def test_network_analysis_query_with_display(self, network_analysis_results):
        """Test network analysis query execution and display results"""
        assert isinstance(network_analysis_results, list)

        # Display the results
        pretty_print_results(
            network_analysis_results,
            "NETWORK ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(network_analysis_results, "Network Analysis Resources")

    @pytest.mark.integration
    def test_nsg_detailed_analysis_with_display(self, nsg_detailed_results):
        """Test detailed NSG rule analysis and display results"""
        assert isinstance(nsg_detailed_results, list)

        # Display the results
        pretty_print_results(
            nsg_detailed_results,
            "DETAILED NSG RULES ANALYSIS",
            max_items=5
        )

        # Display detailed NSG analysis
        display_nsg_rule_analysis(nsg_detailed_results)

    @pytest.mark.integration
    def test_certificate_analysis_with_display(self, certificate_analysis_results):
        """Test certificate analysis and display results"""
        assert isinstance(certificate_analysis_results, list)

        # Display the results
        pretty_print_results(
            certificate_analysis_results,
            "CERTIFICATE ANALYSIS RESULTS",
            max_items=5
        )

        # Display certificate analysis
        display_certificate_analysis(certificate_analysis_results)

    @pytest.mark.integration
    def test_network_topology_with_display(self, network_topology_results):
        """Test network topology analysis and display results"""
        assert isinstance(network_topology_results, list)

        # Display the results
        pretty_print_results(
            network_topology_results,
            "NETWORK TOPOLOGY ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(network_topology_results, "Network Topology")

    @pytest.mark.integration
    def test_network_optimization_with_display(self, network_optimization_results):
        """Test network resource optimization analysis and display results"""
        assert isinstance(network_optimization_results, list)

        # Display the results
        pretty_print_results(
            network_optimization_results,
            "NETWORK RESOURCE OPTIMIZATION ANALYSIS RESULTS",
            max_items=5
        )

        # Display optimization analysis
        display_optimization_analysis(network_optimization_results)

    @pytest.mark.integration
    def test_network_compliance_summary_with_display(self, network_compliance_summary_results):
        """Test network compliance summary and display results"""
        assert isinstance(network_compliance_summary_results, list)

        # Display the results
        pretty_print_results(
            network_compliance_summary_results,
            "NETWORK COMPLIANCE SUMMARY RESULTS",
            max_items=5
        )

        # Display network security metrics
        display_network_security_metrics(network_compliance_summary_results)


# ============================================================================
# VM GOVERNANCE ANALYSIS TESTS
# ============================================================================

@pytest.mark.vm
class TestVMGovernanceAnalysisWithDisplay:
    """Test comprehensive VM governance analysis with result display"""

    @pytest.mark.integration
    def test_vm_security_analysis_with_display(self, vm_security_results):
        """Test VM security analysis and display results"""
        assert isinstance(vm_security_results, list)

        # Display the results
        pretty_print_results(
            vm_security_results,
            "VM SECURITY ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(vm_security_results, "VM Security Analysis")

    @pytest.mark.integration
    def test_vm_optimization_analysis_with_display(self, vm_optimization_results):
        """Test VM optimization analysis and display results"""
        assert isinstance(vm_optimization_results, list)

        # Display the results
        pretty_print_results(
            vm_optimization_results,
            "VM OPTIMIZATION ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(vm_optimization_results, "VM Optimization Analysis")

    @pytest.mark.integration
    def test_vm_extensions_analysis_with_display(self, vm_extensions_results):
        """Test VM extensions analysis and display results"""
        assert isinstance(vm_extensions_results, list)

        # Display the results
        pretty_print_results(
            vm_extensions_results,
            "VM EXTENSIONS ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(vm_extensions_results, "VM Extensions Analysis")

    @pytest.mark.integration
    def test_vm_patch_compliance_with_display(self, vm_patch_compliance_results):
        """Test VM patch compliance analysis and display results"""
        assert isinstance(vm_patch_compliance_results, list)

        # Display the results
        pretty_print_results(
            vm_patch_compliance_results,
            "VM PATCH COMPLIANCE ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(vm_patch_compliance_results, "VM Patch Compliance Analysis")

    @pytest.mark.integration
    def test_vm_governance_summary_with_display(self, vm_governance_summary_results):
        """Test VM governance summary and display results"""
        assert isinstance(vm_governance_summary_results, list)

        # Display the results
        pretty_print_results(
            vm_governance_summary_results,
            "VM GOVERNANCE SUMMARY RESULTS",
            max_items=5
        )

        # Display VM governance metrics
        display_vm_governance_summary(vm_governance_summary_results)


# ============================================================================
# IDENTITY & ACCESS MANAGEMENT ANALYSIS TESTS
# ============================================================================

@pytest.mark.iam
class TestIAMAnalysisWithDisplay:
    """Test comprehensive IAM analysis with result display"""

    @pytest.mark.integration
    def test_role_assignment_analysis_with_display(self, role_assignment_results):
        """Test role assignment analysis and display results"""
        assert isinstance(role_assignment_results, list)

        # Display the results
        pretty_print_results(
            role_assignment_results,
            "ROLE ASSIGNMENT ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(role_assignment_results, "Role Assignment Analysis")

        # Display role assignment analysis
        display_role_assignment_analysis(role_assignment_results)

    @pytest.mark.integration
    def test_key_vault_security_with_display(self, key_vault_security_results):
        """Test Key Vault security analysis and display results"""
        assert isinstance(key_vault_security_results, list)

        # Display the results
        pretty_print_results(
            key_vault_security_results,
            "KEY VAULT SECURITY ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(key_vault_security_results, "Key Vault Security Analysis")

        # Display Key Vault security analysis
        display_key_vault_security_analysis(key_vault_security_results)

    @pytest.mark.integration
    def test_managed_identity_analysis_with_display(self, managed_identity_results):
        """Test managed identity analysis and display results"""
        assert isinstance(managed_identity_results, list)

        # Display the results
        pretty_print_results(
            managed_identity_results,
            "MANAGED IDENTITY ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(managed_identity_results, "Managed Identity Analysis")

        # Display managed identity analysis
        display_managed_identity_analysis(managed_identity_results)

    @pytest.mark.integration
    def test_custom_role_analysis_with_display(self, custom_role_results):
        """Test custom role analysis and display results"""
        assert isinstance(custom_role_results, list)

        # Display the results
        pretty_print_results(
            custom_role_results,
            "CUSTOM ROLE ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(custom_role_results, "Custom Role Analysis")

        # Display custom role analysis
        display_custom_role_analysis(custom_role_results)

    @pytest.mark.integration
    def test_iam_compliance_summary_with_display(self, iam_compliance_summary_results):
        """Test IAM compliance summary and display results"""
        assert isinstance(iam_compliance_summary_results, list)

        # Display the results
        pretty_print_results(
            iam_compliance_summary_results,
            "IAM COMPLIANCE SUMMARY RESULTS",
            max_items=5
        )

        # Display IAM compliance metrics
        display_iam_compliance_summary(iam_compliance_summary_results)


# ============================================================================
# BACKWARD COMPATIBILITY TESTS
# ============================================================================

@pytest.mark.compatibility
class TestBackwardCompatibilityWithDisplay:
    """Test backward compatibility with legacy methods"""

    @pytest.mark.integration
    def test_legacy_storage_encryption_with_display(self, storage_encryption_results):
        """Test legacy storage encryption query execution and display results"""
        assert isinstance(storage_encryption_results, list)

        # Display the results
        pretty_print_results(
            storage_encryption_results,
            "LEGACY STORAGE ENCRYPTION ANALYSIS RESULTS",
            max_items=5
        )

        # Analyze field structure
        analyze_field_structure(storage_encryption_results, "Legacy Storage Encryption Resources")

    @pytest.mark.integration
    def test_legacy_compliance_summary_with_display(self, compliance_summary_results):
        """Test legacy compliance summary and display results"""
        assert isinstance(compliance_summary_results, list)

        # Display the results
        pretty_print_results(
            compliance_summary_results,
            "LEGACY COMPLIANCE SUMMARY RESULTS",
            max_items=5
        )

        # Display legacy compliance metrics
        display_legacy_compliance_metrics(compliance_summary_results)

    @pytest.mark.integration
    def test_backward_compatibility_methods(self, client):
        """Test backward compatibility methods"""
        print(f"\n🔄 TESTING BACKWARD COMPATIBILITY")
        print(f"{'=' * 40}")

        # Test old method names still work
        try:
            old_storage_results = client.query_storage_encryption()
            new_storage_results = client.query_storage_analysis()

            print(f"✅ query_storage_encryption() works: {len(old_storage_results)} results")
            print(f"✅ query_storage_analysis() works: {len(new_storage_results)} results")

            # Results should be the same
            assert len(old_storage_results) == len(new_storage_results)
            print(f"✅ Both methods return same number of results")

        except Exception as e:
            print(f"⚠️ Storage backward compatibility test failed: {e}")

        try:
            old_network_results = client.query_network_security()
            new_network_results = client.query_network_analysis()

            print(f"✅ query_network_security() works: {len(old_network_results)} results")
            print(f"✅ query_network_analysis() works: {len(new_network_results)} results")

            # Results should be the same
            assert len(old_network_results) == len(new_network_results)
            print(f"✅ Both methods return same number of results")

        except Exception as e:
            print(f"⚠️ Network backward compatibility test failed: {e}")

        try:
            old_compliance = client.get_compliance_summary()
            new_compliance = client.get_storage_compliance_summary()

            print(f"✅ get_compliance_summary() works: {len(old_compliance)} results")
            print(f"✅ get_storage_compliance_summary() works: {len(new_compliance)} results")

        except Exception as e:
            print(f"⚠️ Compliance backward compatibility test failed: {e}")


# ============================================================================
# COMPREHENSIVE WORKFLOW TESTS
# ============================================================================

@pytest.mark.integration
class TestComprehensiveWorkflowWithDisplay:
    """Test complete end-to-end workflows with comprehensive analysis"""

    def test_complete_comprehensive_analysis_workflow(self, client):
        """Test complete comprehensive analysis workflow including all storage, network, VM, and IAM features"""

        print(f"\n🚀 STARTING COMPREHENSIVE ANALYSIS WORKFLOW")
        print(f"{'=' * 60}")

        # ====================================================================
        # STORAGE ANALYSIS WORKFLOW
        # ====================================================================

        print(f"\n📋 STORAGE ANALYSIS WORKFLOW")
        print(f"{'=' * 40}")

        # Step 1: Comprehensive Storage Analysis
        print(f"\n🗄️ Step 1: Comprehensive storage analysis...")
        storage_results = client.query_storage_analysis()
        display_storage_analysis_summary(storage_results)

        # Step 2: Storage Access Control Analysis
        print(f"\n🔐 Step 2: Storage access control analysis...")
        access_control_results = client.query_storage_access_control()
        high_risk_access = [r for r in access_control_results if hasattr(r, 'is_high_risk') and r.is_high_risk]
        print(f"Found {len(high_risk_access)} high-risk access configurations")

        # Step 3: Storage Backup Analysis
        print(f"\n💾 Step 3: Storage backup analysis...")
        backup_results = client.query_storage_backup_analysis()
        no_backup = [r for r in backup_results if hasattr(r, 'has_backup_configured') and not r.has_backup_configured]
        print(f"Found {len(no_backup)} resources without proper backup")

        # Step 4: Storage Optimization Analysis
        print(f"\n💰 Step 4: Storage optimization analysis...")
        storage_optimization = client.query_storage_optimization()
        display_storage_optimization_analysis(storage_optimization)

        # Step 5: Storage Compliance Summary
        print(f"\n📈 Step 5: Storage compliance summary...")
        storage_summary = client.get_storage_compliance_summary()
        display_storage_compliance_metrics(storage_summary)

        # ====================================================================
        # VM GOVERNANCE ANALYSIS WORKFLOW
        # ====================================================================

        print(f"\n🖥️ VM GOVERNANCE ANALYSIS WORKFLOW")
        print(f"{'=' * 45}")

        # Step 6: VM Security Analysis
        print(f"\n🔒 Step 6: VM security analysis...")
        vm_security = client.query_vm_security()
        high_risk_vms = [vm for vm in vm_security if hasattr(vm, 'is_high_risk') and vm.is_high_risk]
        print(f"Found {len(high_risk_vms)} high-risk VMs")

        # Step 7: VM Optimization Analysis
        print(f"\n💰 Step 7: VM optimization analysis...")
        vm_optimization = client.query_vm_optimization()
        stopped_vms = [vm for vm in vm_optimization if
                       hasattr(vm, 'is_stopped_but_allocated') and vm.is_stopped_but_allocated]
        print(f"Found {len(stopped_vms)} stopped VMs still incurring costs")

        # Step 8: VM Extensions Analysis
        print(f"\n🔧 Step 8: VM extensions analysis...")
        vm_extensions = client.query_vm_extensions()
        failed_extensions = [ext for ext in vm_extensions if hasattr(ext, 'is_healthy') and not ext.is_healthy]
        print(f"Found {len(failed_extensions)} failed extensions")

        # Step 9: VM Patch Compliance
        print(f"\n🩹 Step 9: VM patch compliance analysis...")
        vm_patches = client.query_vm_patch_compliance()
        manual_patching = [vm for vm in vm_patches if
                           hasattr(vm, 'requires_manual_patching') and vm.requires_manual_patching]
        print(f"Found {len(manual_patching)} VMs requiring manual patching")

        # Step 10: VM Governance Summary
        print(f"\n📊 Step 10: VM governance summary...")
        vm_summary = client.get_vm_governance_summary()
        display_vm_governance_summary(vm_summary)

        # ====================================================================
        # NETWORK ANALYSIS WORKFLOW
        # ====================================================================

        print(f"\n🌐 NETWORK ANALYSIS WORKFLOW")
        print(f"{'=' * 40}")

        # Step 11: Network Analysis
        print(f"\n🔒 Step 11: Network analysis...")
        network_results = client.query_network_analysis()
        nsg_results = client.query_nsg_detailed()
        network_summary = client.get_network_compliance_summary()

        display_network_security_metrics(network_summary)
        display_nsg_rule_analysis(nsg_results)

        # Step 12: Certificate Analysis
        print(f"\n🔐 Step 12: Certificate analysis...")
        cert_results = client.query_certificate_analysis()
        display_certificate_analysis(cert_results)

        # Step 13: Network Topology Analysis
        print(f"\n🗺️ Step 13: Network topology analysis...")
        topology_results = client.query_network_topology()
        print(f"Found {len(topology_results)} topology components")

        # Step 14: Network Resource Optimization Analysis
        print(f"\n💰 Step 14: Network resource optimization analysis...")
        network_optimization = client.query_resource_optimization()
        display_optimization_analysis(network_optimization)

        # ====================================================================
        # IDENTITY & ACCESS MANAGEMENT ANALYSIS WORKFLOW
        # ====================================================================

        print(f"\n🔐 IDENTITY & ACCESS MANAGEMENT ANALYSIS WORKFLOW")
        print(f"{'=' * 50}")

        # Step 15: Role Assignment Analysis
        print(f"\n🎭 Step 15: Role assignment analysis...")
        role_assignments = client.query_role_assignments()
        display_role_assignment_analysis(role_assignments)

        # Step 16: Key Vault Security Analysis
        print(f"\n🔐 Step 16: Key Vault security analysis...")
        key_vault_security = client.query_key_vault_security()
        display_key_vault_security_analysis(key_vault_security)

        # Step 17: Managed Identity Analysis
        print(f"\n🆔 Step 17: Managed identity analysis...")
        managed_identities = client.query_managed_identities()
        display_managed_identity_analysis(managed_identities)

        # Step 18: Custom Role Analysis
        print(f"\n📋 Step 18: Custom role analysis...")
        custom_roles = client.query_custom_roles()
        display_custom_role_analysis(custom_roles)

        # Step 19: IAM Compliance Summary
        print(f"\n🏛️ Step 19: IAM compliance summary...")
        iam_summary = client.get_iam_compliance_summary()
        display_iam_compliance_summary(iam_summary)

        # Step 20: AKS Cluster Security Analysis
        print(f"\n🔐 Step 20: AKS cluster security analysis...")
        aks_security = client.query_aks_cluster_security()
        display_aks_cluster_security_analysis(aks_security)

        # Step 21: AKS Node Pool Analysis - FIXED VERSION
        print(f"\n🖥️ Step 21: AKS node pool analysis...")
        try:
            # Check if we found any AKS clusters in Step 20
            if len(aks_security) == 0:
                print("   ✅ No AKS clusters found - skipping node pool analysis")
                node_pools = []
            else:
                print(f"   🔍 Found {len(aks_security)} AKS clusters, analyzing node pools...")
                node_pools = client.query_aks_node_pools()

            display_aks_node_pool_analysis(node_pools)

        except Exception as e:
            print(f"   ⚠️ AKS node pool analysis failed: {str(e)[:100]}")
            print(f"   ℹ️ This is expected in environments without AKS clusters")
            node_pools = []

        # Step 22: Container Registry Security Analysis
        print(f"\n📦 Step 22: Container Registry security analysis...")
        registry_security = client.query_container_registry_security()
        display_container_registry_security_analysis(registry_security)

        # Step 23: App Service Security Analysis
        print(f"\n🌐 Step 23: App Service security analysis...")
        app_service_security = client.query_app_service_security()
        display_app_service_security_analysis(app_service_security)

        # Step 24: App Service Deployment Slots Analysis
        print(f"\n🔄 Step 24: App Service deployment slots analysis...")
        app_service_slots = client.query_app_service_deployment_slots()
        print(f"Found {len(app_service_slots)} deployment slots")

        # Step 25: Container Workloads Compliance Summary
        print(f"\n📊 Step 25: Container workloads compliance summary...")
        container_summary = client.get_container_workloads_compliance_summary()
        display_container_workloads_compliance_summary(container_summary)

        # ====================================================================
        # CROSS-ANALYSIS AND INSIGHTS
        # ====================================================================

        print(f"\n🎯 CROSS-ANALYSIS AND INSIGHTS")
        print(f"{'=' * 40}")

        # Get applications from different analyses
        storage_apps = set()
        network_apps = set()
        vm_apps = set()
        iam_apps = set()

        if storage_results:
            storage_apps = set(
                r.application if hasattr(r, 'application') else r.get('Application', '') for r in storage_results)
        if network_results:
            network_apps = set(
                r.application if hasattr(r, 'application') else r.get('Application', '') for r in network_results)
        if vm_security:
            vm_apps = set(
                r.application if hasattr(r, 'application') else r.get('Application', '') for r in vm_security)
        if role_assignments:
            iam_apps = set(
                r.application if hasattr(r, 'application') else r.get('Application', '') for r in role_assignments)

        common_apps = storage_apps & network_apps & vm_apps & iam_apps
        print(f"Applications with comprehensive coverage: {len(common_apps)}")

        # Identify high-priority applications
        high_priority_apps = set()

        # Apps with storage compliance issues
        for summary in storage_summary:
            if hasattr(summary, 'has_critical_issues') and summary.has_critical_issues:
                high_priority_apps.add(summary.application)
            elif hasattr(summary, 'compliance_score') and summary.compliance_score < 80:
                high_priority_apps.add(summary.application)
            elif not hasattr(summary, 'compliance_score') and summary.get('ComplianceScore', 100) < 80:
                high_priority_apps.add(summary.get('Application', ''))

        # Apps with network security issues
        for summary in network_summary:
            if hasattr(summary, 'has_critical_issues') and summary.has_critical_issues:
                high_priority_apps.add(summary.application)
            elif hasattr(summary, 'security_score') and summary.security_score < 80:
                high_priority_apps.add(summary.application)
            elif not hasattr(summary, 'security_score') and summary.get('SecurityScore', 100) < 80:
                high_priority_apps.add(summary.get('Application', ''))

        print(f"\n🚨 HIGH PRIORITY APPLICATIONS ({len(high_priority_apps)} total):")
        for app in sorted(high_priority_apps)[:10]:  # Show first 10
            print(f"    ❌ {app}")

        # Final comprehensive summary
        print(f"\n✅ COMPREHENSIVE ANALYSIS SUMMARY")
        print(f"{'=' * 50}")
        print(f"✅ Storage resources: {len(storage_results)}")
        print(f"✅ VM security analysis: {len(vm_security)}")
        print(f"✅ Network resources: {len(network_results)}")
        print(f"✅ NSG rules: {len(nsg_results)}")
        print(f"✅ Key Vault configurations: {len(key_vault_security)}")
        print(f"✅ High-priority applications: {len(high_priority_apps)}")

        # Calculate overall scores
        if storage_summary and network_summary and vm_summary and iam_summary:
            avg_storage_compliance = sum(
                s.compliance_score if hasattr(s, 'compliance_score') else s.get('ComplianceScore', 0)
                for s in storage_summary
            ) / len(storage_summary)

            avg_network_security = sum(
                s.security_score if hasattr(s, 'security_score') else s.get('SecurityScore', 0)
                for s in network_summary
            ) / len(network_summary)

            avg_vm_governance = sum(
                s.governance_score if hasattr(s, 'governance_score') else s.get('GovernanceScore', 0)
                for s in vm_summary
            ) / len(vm_summary)

            avg_iam_compliance = sum(
                s.iam_compliance_score if hasattr(s, 'iam_compliance_score') else s.get('IAMComplianceScore', 0)
                for s in iam_summary
            ) / len(iam_summary)

            overall_score = (avg_storage_compliance + avg_network_security + avg_vm_governance + avg_iam_compliance) / 4

            print(f"✅ Average storage compliance: {avg_storage_compliance:.1f}%")
            print(f"✅ Average network security: {avg_network_security:.1f}%")
            print(f"✅ Average VM governance: {avg_vm_governance:.1f}%")
            print(f"✅ Average IAM compliance: {avg_iam_compliance:.1f}%")
            print(f"✅ Overall security score: {overall_score:.1f}%")

        return {
            'storage_analysis': storage_results,
            'vm_security': vm_security,
            'network_analysis': network_results,
            'nsg_detailed': nsg_results,
            'aks_security': aks_security,
            'node_pools': node_pools,
            'high_priority_apps': high_priority_apps
        }


# ============================================================================
# DEBUG AND UTILITY TESTS
# ============================================================================

class TestDebugUtilities:
    """Utility tests for debugging and comprehensive data exploration"""

    @pytest.mark.integration
    def test_export_comprehensive_data(self, storage_analysis_results, storage_access_control_results,
                                       storage_backup_results, storage_optimization_results,
                                       network_analysis_results, nsg_detailed_results,
                                       certificate_analysis_results, network_topology_results,
                                       network_optimization_results, role_assignment_results,
                                       key_vault_security_results, managed_identity_results,
                                       custom_role_results, tmp_path):
        """Export comprehensive sample data for analysis"""

        # Convert Pydantic objects to dictionaries for JSON serialization
        def serialize_results(results):
            if not results:
                return []
            if hasattr(results[0], 'dict'):
                return [r.dict() for r in results]
            else:
                return results

        # Create comprehensive data export
        export_data = {
            "export_timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
            "metadata": {
                "version": "1.4.0",
                "analysis_type": "comprehensive_storage_network_vm_iam",
                "capabilities": [
                    "storage_analysis", "storage_access_control", "storage_backup", "storage_optimization",
                    "network_analysis", "nsg_detailed", "certificate_analysis", "network_topology",
                    "network_optimization", "role_assignments", "key_vault_security",
                    "managed_identities", "custom_roles"
                ]
            },
            "samples": {
                "storage_analysis": serialize_results(storage_analysis_results[:5]),
                "storage_access_control": serialize_results(storage_access_control_results[:5]),
                "storage_backup": serialize_results(storage_backup_results[:5]),
                "storage_optimization": serialize_results(storage_optimization_results[:5]),
                "network_analysis": serialize_results(network_analysis_results[:5]),
                "nsg_detailed": serialize_results(nsg_detailed_results[:5]),
                "certificate_analysis": serialize_results(certificate_analysis_results[:5]),  # Fixed
                "network_topology": serialize_results(network_topology_results[:5]),  # Fixed
                "network_optimization": serialize_results(network_optimization_results[:5]),  # Fixed
                "role_assignments": serialize_results(role_assignment_results[:5]),
                "key_vault_security": serialize_results(key_vault_security_results[:5]),
                "managed_identities": serialize_results(managed_identity_results[:5]),
                "custom_roles": serialize_results(custom_role_results[:5])
            },
            "statistics": {
                "total_storage_resources": len(storage_analysis_results) if storage_analysis_results else 0,
                "total_storage_access_configs": len(
                    storage_access_control_results) if storage_access_control_results else 0,
                "total_storage_backup_configs": len(storage_backup_results) if storage_backup_results else 0,
                "total_storage_optimization_opportunities": len(
                    storage_optimization_results) if storage_optimization_results else 0,
                "total_network_resources": len(network_analysis_results) if network_analysis_results else 0,
                "total_nsg_rules": len(nsg_detailed_results) if nsg_detailed_results else 0,
                "total_certificate_configs": len(certificate_analysis_results) if certificate_analysis_results else 0,
                "total_topology_components": len(network_topology_results) if network_topology_results else 0,
                "total_network_optimization_opportunities": len(
                    network_optimization_results) if network_optimization_results else 0,
                "total_role_assignments": len(role_assignment_results) if role_assignment_results else 0,
                "total_key_vaults": len(key_vault_security_results) if key_vault_security_results else 0,
                "total_managed_identities": len(managed_identity_results) if managed_identity_results else 0,
                "total_custom_roles": len(custom_role_results) if custom_role_results else 0
            }
        }

        # Save to temporary file
        export_file = tmp_path / "comprehensive_analysis_export.json"
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\n💾 Comprehensive data exported to: {export_file}")
        print(f"📁 File size: {export_file.stat().st_size} bytes")

        # Display what was exported
        print(f"\n📋 Export contents:")
        for category, data in export_data["samples"].items():
            print(f"   - {category}: {len(data)} samples")

        print(f"\n📊 Statistics:")
        for stat, value in export_data["statistics"].items():
            print(f"   - {stat}: {value}")

        assert export_file.exists()
        return export_file


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_addoption(parser):
    """Add custom pytest command line options"""
    parser.addoption(
        "--show-results", action="store_true", default=False,
        help="Show detailed query results during test execution"
    )
    parser.addoption(
        "--comprehensive", action="store_true", default=False,
        help="Run comprehensive analysis tests including all features"
    )


def pytest_configure(config):
    """Configure pytest with custom settings"""
    if config.getoption("--show-results"):
        import logging
        logging.basicConfig(level=logging.INFO)
        print("\n🔍 Detailed result display enabled!")

    if config.getoption("--comprehensive"):
        print("\n🎯 Comprehensive analysis mode enabled!")

    # Register custom markers
    config.addinivalue_line("markers", "storage: mark test as storage analysis related")
    config.addinivalue_line("markers", "network: mark test as network analysis related")
    config.addinivalue_line("markers", "vm: mark test as VM governance related")
    config.addinivalue_line("markers", "iam: mark test as Identity & Access Management related")
    config.addinivalue_line("markers", "container: mark test as Container & Modern Workloads related")  # NEW
    config.addinivalue_line("markers", "certificates: mark test as certificate analysis related")
    config.addinivalue_line("markers", "topology: mark test as network topology related")
    config.addinivalue_line("markers", "optimization: mark test as resource optimization related")
    config.addinivalue_line("markers", "compliance: mark test as compliance related")
    config.addinivalue_line("markers", "compatibility: mark test as backward compatibility related")
    config.addinivalue_line("markers", "integration: mark test as integration test")


# ============================================================================
# PYTEST MARKERS REFERENCE
# ============================================================================
"""
Available pytest markers for running specific test groups:

Container & Modern Workloads Tests:
pytest -m container            # Container workloads analysis tests

Storage Tests:
pytest -m storage              # All storage analysis tests
pytest -m "storage and not compatibility"  # New storage tests only

Network Tests:
pytest -m network              # Network analysis tests
pytest -m certificates         # Certificate analysis tests
pytest -m topology             # Network topology tests
pytest -m optimization         # Resource optimization tests

VM Governance Tests:
pytest -m vm                   # VM governance tests

Identity & Access Management Tests:
pytest -m iam                  # IAM analysis tests

Compatibility Tests:
pytest -m compatibility        # Backward compatibility tests

Combined Tests:
pytest -m "storage or network" # Storage and network tests
pytest -m "network and not optimization" # Network but not optimization
pytest -m "iam or vm"          # IAM and VM governance tests

Special Modes:
pytest --show-results          # Show detailed output
pytest --comprehensive         # Full comprehensive analysis

Example Commands:
pytest test_client.py -m "storage" --show-results -v
pytest test_client.py -m "storage or certificates" --comprehensive
pytest test_client.py -m "iam" --show-results -v
pytest test_client.py::TestIAMAnalysisWithDisplay::test_role_assignment_analysis_with_display -s --show-results
pytest test_client.py::TestComprehensiveWorkflowWithDisplay::test_complete_comprehensive_analysis_workflow -s --show-results
pytest test_client.py -m "compatibility" --show-results -v
pytest test_client.py -m "iam and integration" --show-results -v
pytest test_client.py -m "container" --show-results -v
pytest test_client.py::TestContainerWorkloadsAnalysisWithDisplay::test_aks_cluster_security_analysis_with_display -s --show-results
pytest test_client.py::TestContainerWorkloadsAnalysisWithDisplay::test_comprehensive_container_workloads_analysis -s --show-results
"""
