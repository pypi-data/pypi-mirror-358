# Azure Resource Graph - Storage Encryption Analysis

A Python client for analyzing Azure storage encryption compliance across your applications using the Azure Resource Graph API.

## 🎯 What This Tool Does

This tool helps you **automatically discover and analyze storage encryption** across your Azure environment:

✅ **Discovers all storage resources** associated with your applications  
✅ **Analyzes encryption methods** (Platform Managed, Customer Managed Keys, etc.)  
✅ **Generates compliance reports** with pass/fail status  
✅ **Identifies security gaps** in your storage configuration  
✅ **Tracks encryption across** Storage Accounts, Managed Disks, Cosmos DB, SQL Databases  

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and install
git clone <your-repo-url>
cd azure-resource-graph
pip install -e .
```

### 2. Azure Setup

```bash
# Login to Azure
az login

# Get your Azure credentials (run this script)
./get_azure_env.sh
```

### 3. Configure Environment

Create `.env` file with your Azure credentials:
```bash
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_SUBSCRIPTION_IDS=your-subscription-id
```

### 4. Run Analysis

```python
from azure_resource_graph import AzureResourceGraphClient

# Initialize client
client = AzureResourceGraphClient()

# Analyze storage encryption across all applications
results = client.query_storage_encryption()

# Print summary
for item in results:
    status = "✅" if item['ComplianceStatus'] == "Compliant" else "❌"
    print(f"{status} {item['Application']} - {item['StorageResource']} - {item['EncryptionMethod']}")
```

## 📊 Core Use Cases

### Enterprise Storage Compliance

**Problem**: "I need to ensure all storage in my Azure environment is properly encrypted"

```python
from azure_resource_graph import AzureResourceGraphClient

client = AzureResourceGraphClient()

# Get comprehensive encryption analysis
storage_results = client.query_storage_encryption()
compliance_summary = client.get_compliance_summary()

# Generate compliance report
for app in compliance_summary:
    if app['CompliancePercentage'] < 100:
        print(f"⚠️  {app['Application']}: {app['CompliancePercentage']}% compliant")
        print(f"   {app['NonCompliantResources']} resources need attention")
```

### Application Security Audit

**Problem**: "I need to check encryption for a specific application"

```python
# Analyze specific application
app_storage = client.query_application_storage("ECommerceApp")

print(f"📊 Storage Analysis for ECommerceApp:")
for resource in app_storage:
    print(f"  - {resource['StorageResource']} ({resource['StorageType']})")
    print(f"    Encryption: {resource['EncryptionMethod']}")
    print(f"    Compliance: {resource['ComplianceStatus']}")
```

### Security Gap Detection

**Problem**: "Find all storage that's not properly encrypted"

```python
# Find non-compliant storage
storage_results = client.query_storage_encryption()

security_gaps = [
    item for item in storage_results 
    if item['ComplianceStatus'] in ['Non-Compliant', 'Partially Compliant']
]

print(f"🚨 Found {len(security_gaps)} security gaps:")
for gap in security_gaps:
    print(f"  ❌ {gap['Application']}: {gap['StorageResource']}")
    print(f"     Issue: {gap['EncryptionMethod']}")
    print(f"     Location: {gap['ResourceGroup']}")
```

### Cross-Subscription Analysis

**Problem**: "Analyze encryption across multiple Azure subscriptions"

```python
# Analyze multiple subscriptions
subscription_ids = ["sub-1", "sub-2", "sub-3"]
results = client.query_storage_encryption(subscription_ids)

# Group by subscription
from collections import defaultdict
by_subscription = defaultdict(list)

for item in results:
    # Extract subscription from resource ID
    sub_id = item['ResourceId'].split('/')[2]
    by_subscription[sub_id].append(item)

for sub_id, resources in by_subscription.items():
    compliant = sum(1 for r in resources if r['ComplianceStatus'] == 'Compliant')
    print(f"Subscription {sub_id}: {compliant}/{len(resources)} compliant")
```

## 🔍 Advanced Queries

### Custom KQL Queries

```python
# Custom query for specific storage types
query = """
Resources
| where type in ('microsoft.storage/storageaccounts', 'microsoft.compute/disks')
| where location == 'eastus'
| extend EncryptionEnabled = case(
    type == 'microsoft.storage/storageaccounts', 
    properties.encryption.services.blob.enabled,
    type == 'microsoft.compute/disks',
    properties.encryption.type contains 'Encryption',
    false
)
| project name, type, location, EncryptionEnabled, resourceGroup
| where EncryptionEnabled == false
"""

non_encrypted = client.query_resource_graph(query)
print(f"Found {len(non_encrypted)} unencrypted resources in East US")
```

### Storage Cost Analysis with Encryption

```python
# Analyze storage with cost implications
query = """
Resources
| where type == 'microsoft.storage/storageaccounts'
| extend EncryptionType = case(
    properties.encryption.keySource == 'Microsoft.Keyvault', 'Customer Managed (Premium)',
    properties.encryption.services.blob.enabled == true, 'Platform Managed (Standard)',
    'None (Risk)'
)
| extend AccountTier = properties.sku.tier
| project name, EncryptionType, AccountTier, location, resourceGroup
| summarize count() by EncryptionType, AccountTier
"""

cost_analysis = client.query_resource_graph(query)
for item in cost_analysis:
    print(f"{item['EncryptionType']} + {item['AccountTier']}: {item['count_']} accounts")
```

## 📈 Reporting and Monitoring

### Generate Compliance Dashboard

```python
import json
from datetime import datetime

def generate_compliance_report():
    client = AzureResourceGraphClient()
    
    # Get all data
    storage_results = client.query_storage_encryption()
    compliance_summary = client.get_compliance_summary()
    
    # Create dashboard data
    dashboard = {
        'timestamp': datetime.now().isoformat(),
        'overall_stats': {
            'total_storage_resources': len(storage_results),
            'total_applications': len(compliance_summary),
            'overall_compliance': sum(app['CompliancePercentage'] for app in compliance_summary) / len(compliance_summary) if compliance_summary else 0
        },
        'by_application': compliance_summary,
        'security_gaps': [
            item for item in storage_results 
            if item['ComplianceStatus'] != 'Compliant'
        ],
        'by_storage_type': {}
    }
    
    # Group by storage type
    from collections import Counter
    storage_types = Counter(item['StorageType'] for item in storage_results)
    compliant_by_type = Counter(
        item['StorageType'] for item in storage_results 
        if item['ComplianceStatus'] == 'Compliant'
    )
    
    for storage_type, total in storage_types.items():
        compliant = compliant_by_type.get(storage_type, 0)
        dashboard['by_storage_type'][storage_type] = {
            'total': total,
            'compliant': compliant,
            'compliance_rate': (compliant / total) * 100
        }
    
    # Save report
    with open(f'compliance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    return dashboard

# Generate report
report = generate_compliance_report()
print(f"📊 Overall compliance: {report['overall_stats']['overall_compliance']:.1f}%")
```

### Automated Monitoring Script

```python
#!/usr/bin/env python3
"""
Daily storage encryption monitoring script
"""

def daily_compliance_check():
    client = AzureResourceGraphClient()
    
    # Check for new non-compliant resources
    results = client.query_storage_encryption()
    
    critical_issues = [
        item for item in results 
        if item['ComplianceStatus'] == 'Non-Compliant'
    ]
    
    if critical_issues:
        print(f"🚨 ALERT: {len(critical_issues)} non-compliant storage resources found!")
        
        for issue in critical_issues:
            print(f"❌ {issue['Application']}: {issue['StorageResource']}")
            print(f"   Issue: {issue['EncryptionMethod']}")
            print(f"   Resource Group: {issue['ResourceGroup']}")
        
        # You could send alerts here (email, Slack, etc.)
        return False
    else:
        print("✅ All storage resources are compliant")
        return True

if __name__ == "__main__":
    daily_compliance_check()
```

## 🏢 Enterprise Integration

### CI/CD Pipeline Integration

```yaml
# Azure DevOps Pipeline
name: Storage Encryption Compliance Check

trigger:
  - main

jobs:
- job: ComplianceCheck
  steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.9'
  
  - script: |
      pip install -e .
    displayName: 'Install dependencies'
  
  - script: |
      python scripts/compliance_check.py
    env:
      AZURE_TENANT_ID: $(AZURE_TENANT_ID)
      AZURE_CLIENT_ID: $(AZURE_CLIENT_ID)
      AZURE_CLIENT_SECRET: $(AZURE_CLIENT_SECRET)
      AZURE_SUBSCRIPTION_IDS: $(AZURE_SUBSCRIPTION_IDS)
    displayName: 'Run storage encryption compliance check'
```

### PowerBI Integration

```python
def export_for_powerbi():
    """Export data in PowerBI-friendly format"""
    client = AzureResourceGraphClient()
    results = client.query_storage_encryption()
    
    # Flatten for PowerBI
    powerbi_data = []
    for item in results:
        powerbi_data.append({
            'Application': item['Application'],
            'StorageResource': item['StorageResource'],
            'StorageType': item['StorageType'],
            'EncryptionMethod': item['EncryptionMethod'],
            'IsCompliant': 1 if item['ComplianceStatus'] == 'Compliant' else 0,
            'ComplianceStatus': item['ComplianceStatus'],
            'ResourceGroup': item['ResourceGroup'],
            'Location': item['Location'],
            'AnalysisDate': datetime.now().isoformat()
        })
    
    # Export to CSV for PowerBI
    import pandas as pd
    df = pd.DataFrame(powerbi_data)
    df.to_csv('azure_storage_compliance.csv', index=False)
    print(f"📊 Exported {len(powerbi_data)} records to PowerBI CSV")
```

## 🔧 Testing

```bash
# Run all tests
pytest

# Run only integration tests (requires Azure credentials)
pytest -m integration

# Run only unit tests (no Azure required)
pytest -m unit

# Run specific storage tests
pytest -m storage -v
```

## 🛡️ Security Best Practices

### Least Privilege Access

Your service principal only needs **Reader** permissions:

```bash
# Create minimal-privilege service principal
az ad sp create-for-rbac \
  --name "StorageComplianceReader" \
  --role "Reader" \
  --scopes "/subscriptions/$SUBSCRIPTION_ID"
```

### Secure Credential Management

```bash
# Use Azure Key Vault for production
az keyvault secret set \
  --vault-name "your-keyvault" \
  --name "azure-client-secret" \
  --value "$AZURE_CLIENT_SECRET"

# Or use managed identity when running on Azure
# No credentials needed!
```

## 📚 API Reference

### Main Methods

**`client.query_storage_encryption(subscription_ids=None)`**
- Returns: List of storage resources with encryption analysis
- Use: Primary method for compliance checking

**`client.get_compliance_summary(subscription_ids=None)`**  
- Returns: Application-level compliance summary
- Use: Executive dashboards and reporting

**`client.query_application_storage(app_name, subscription_ids=None)`**
- Returns: All storage for a specific application
- Use: Application-specific security audits

**`client.query_resource_graph(query, subscription_ids=None)`**
- Returns: Custom KQL query results
- Use: Advanced analysis and custom reports

## 🚨 Common Issues

### No Results Returned
```python
# Check if your resources are tagged
results = client.query_resource_graph("Resources | where isnotempty(tags.Application) | limit 10")
if not results:
    print("❌ No tagged resources found. Make sure your resources have Application tags.")
```

### Authentication Errors
```python
# Test authentication
try:
    token = client._get_access_token()
    print("✅ Authentication successful")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
```

### Subscription Access
```python
# Check subscription access
subs = client.query_resource_graph("Resources | distinct subscriptionId")
print(f"✅ Access to {len(subs)} subscriptions")
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🎯 Ready to secure your Azure storage?** Start with the Quick Start guide above and begin analyzing your storage encryption compliance today!
