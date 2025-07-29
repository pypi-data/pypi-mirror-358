#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Azure Resource Graph Client tests
"""

import os
import pytest
import json
import time
from typing import Dict, Any, List, Optional

from azure_resource_graph import AzureResourceGraphClient, AzureConfig


@pytest.fixture(scope="session")
def client() -> Optional[AzureResourceGraphClient]:
    """
    Session-scoped client fixture that initializes once for all tests
    """
    try:
        client = AzureResourceGraphClient()

        # Verify we have basic config
        config = client.config
        if not all([config.tenant_id, config.client_id, config.client_secret]):
            pytest.skip("Azure credentials not configured. Set up .env file or environment variables.")

        return client
    except Exception as e:
        pytest.skip(f"Failed to initialize Azure client: {e}")


@pytest.fixture(scope="session")
def client_config(client: AzureResourceGraphClient) -> AzureConfig:
    """
    Get the client configuration for testing
    """
    return client.config


@pytest.fixture(scope="session")
def access_token(client: AzureResourceGraphClient) -> str:
    """
    Get access token for authentication tests
    """
    try:
        token = client._get_access_token()
        if not token:
            pytest.fail("Failed to get access token")
        return token
    except Exception as e:
        pytest.fail(f"Authentication failed: {e}")


@pytest.fixture(scope="session")
def storage_encryption_results(client: AzureResourceGraphClient) -> List[Dict[str, Any]]:
    """
    Get storage encryption results for multiple tests
    """
    try:
        results = client.query_storage_encryption()
        return results
    except Exception as e:
        pytest.fail(f"Failed to get storage encryption results: {e}")


@pytest.fixture(scope="session")
def compliance_summary_results(client: AzureResourceGraphClient) -> List[Dict[str, Any]]:
    """
    Get compliance summary results for multiple tests
    """
    try:
        results = client.get_compliance_summary()
        return results
    except Exception as e:
        pytest.fail(f"Failed to get compliance summary: {e}")


@pytest.fixture(scope="function")
def sample_basic_query() -> str:
    """
    Simple query for basic testing
    """
    return """
    Resources
    | where type == 'microsoft.resources/resourcegroups'
    | project name, location, resourceGroup
    | limit 5
    """


@pytest.fixture(scope="function")
def invalid_query() -> str:
    """
    Invalid query for error handling tests
    """
    return "INVALID KQL SYNTAX HERE"


@pytest.fixture(scope="session", autouse=True)
def test_session_info(request):
    """
    Print test session information
    """
    print("\n" + "=" * 80)
    print(" Azure Resource Graph Client - Pytest Test Suite")
    print("=" * 80)

    def finalizer():
        print("\n" + "=" * 80)
        print(" Test Session Complete")
        print("=" * 80)

    request.addfinalizer(finalizer)


@pytest.fixture(scope="function")
def temp_results_file(tmp_path):
    """
    Temporary file for saving test results
    """
    return tmp_path / "test_results.json"


# Pytest markers for test categorization
def pytest_configure(config):
    """
    Configure custom pytest markers
    """
    config.addinivalue_line(
        "markers", "auth: mark test as authentication-related"
    )
    config.addinivalue_line(
        "markers", "query: mark test as query-related"
    )
    config.addinivalue_line(
        "markers", "storage: mark test as storage encryption-related"
    )
    config.addinivalue_line(
        "markers", "compliance: mark test as compliance-related"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


# Test data generators
@pytest.fixture
def mock_storage_resource():
    """
    Mock storage resource data for unit tests
    """
    return {
        "Application": "TestApp",
        "StorageResource": "teststorage123",
        "StorageType": "Storage Account",
        "EncryptionMethod": "Platform Managed + HTTPS",
        "ComplianceStatus": "Compliant",
        "ResourceGroup": "rg-test-123",
        "Location": "eastus",
        "AdditionalDetails": "HTTPS: Required | Public: Blocked",
        "ResourceId": "/subscriptions/test/resourceGroups/rg-test-123/providers/Microsoft.Storage/storageAccounts/teststorage123"
    }


@pytest.fixture
def mock_compliance_summary():
    """
    Mock compliance summary data for unit tests
    """
    return {
        "Application": "TestApp",
        "TotalResources": 5,
        "CompliantResources": 4,
        "NonCompliantResources": 1,
        "CompliancePercentage": 80.0,
        "ComplianceStatus": "Mostly Compliant"
    }


# Performance measurement fixture
@pytest.fixture
def performance_timer():
    """
    Simple performance timer for test benchmarking
    """
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()
            return self.duration

        @property
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

    return Timer()


# Test environment checks
def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add environment-based skips
    """
    # Check if we have Azure credentials
    has_azure_creds = all([
        os.getenv('AZURE_TENANT_ID'),
        os.getenv('AZURE_CLIENT_ID'),
        os.getenv('AZURE_CLIENT_SECRET')
    ])

    if not has_azure_creds:
        # Add skip marker to integration tests if no credentials
        skip_integration = pytest.mark.skip(reason="Azure credentials not configured")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
