#!/usr/bin/env python3
"""
Render Service Configuration Verification Script for TTPROv4
Service ID: srv-d29srkqdbo4c73antk40

This script verifies the Render service configuration and can trigger deployments.
Set RENDER_API_KEY environment variable before running.
"""

import os
import sys
import requests
import time
import json
from typing import Dict, List, Optional

# Render API Configuration
RENDER_API_BASE = "https://api.render.com/v1"
SERVICE_ID = "srv-d29srkqdbo4c73antk40"  # TTPROv4 service ID

# Required environment variables to check
REQUIRED_ENV_VARS = [
    "ENVIRONMENT",
    "DATABASE_URL", 
    "REDIS_URL",
    "FIREBASE_PROJECT_ID",
    "FIREBASE_CLIENT_EMAIL",
    "FIREBASE_PRIVATE_KEY",
    "OPENAI_API_KEY",  # if used
    "YOUTUBE_API_KEY",  # if used
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "API_BASE_URL"
]

# Expected configuration
EXPECTED_CONFIG = {
    "branch": "bootstrap/v5",
    "healthCheckPath": "/",
    "preDeployCommand": "alembic upgrade head",
    "environment_production": "production"
}

class RenderAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_service(self, service_id: str) -> Optional[Dict]:
        """Get service configuration"""
        try:
            response = requests.get(
                f"{RENDER_API_BASE}/services/{service_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting service: {e}")
            return None
    
    def get_service_env_vars(self, service_id: str) -> Optional[List[Dict]]:
        """Get service environment variables"""
        try:
            response = requests.get(
                f"{RENDER_API_BASE}/services/{service_id}/env-vars",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting environment variables: {e}")
            return None
    
    def list_services(self) -> Optional[List[Dict]]:
        """List all services to find worker services"""
        try:
            response = requests.get(
                f"{RENDER_API_BASE}/services",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error listing services: {e}")
            return None
    
    def create_deploy(self, service_id: str) -> Optional[Dict]:
        """Trigger a manual deploy"""
        try:
            response = requests.post(
                f"{RENDER_API_BASE}/services/{service_id}/deploys",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating deploy: {e}")
            return None
    
    def get_deploy_status(self, service_id: str, deploy_id: str) -> Optional[Dict]:
        """Get deploy status"""
        try:
            response = requests.get(
                f"{RENDER_API_BASE}/services/{service_id}/deploys/{deploy_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting deploy status: {e}")
            return None

def verify_service_configuration(client: RenderAPIClient) -> bool:
    """Verify the main service configuration"""
    print("🔍 Verifying TTPROv4 service configuration...")
    
    service = client.get_service(SERVICE_ID)
    if not service:
        print("❌ Failed to get service information")
        return False
    
    print(f"✅ Service found: {service.get('name', 'N/A')}")
    print(f"   - Service ID: {service.get('id', 'N/A')}")
    print(f"   - Type: {service.get('type', 'N/A')}")
    print(f"   - Status: {service.get('serviceDetails', {}).get('status', 'N/A')}")
    
    # Check branch
    repo_branch = service.get('serviceDetails', {}).get('buildFilter', {}).get('branches', [])
    if EXPECTED_CONFIG["branch"] in repo_branch:
        print(f"✅ Branch correctly set to: {EXPECTED_CONFIG['branch']}")
    else:
        print(f"❌ Branch mismatch. Expected: {EXPECTED_CONFIG['branch']}, Got: {repo_branch}")
        return False
    
    # Check health check path
    health_check = service.get('serviceDetails', {}).get('healthCheckPath')
    if health_check == EXPECTED_CONFIG["healthCheckPath"]:
        print(f"✅ Health check path correctly set to: {EXPECTED_CONFIG['healthCheckPath']}")
    else:
        print(f"❌ Health check path mismatch. Expected: {EXPECTED_CONFIG['healthCheckPath']}, Got: {health_check}")
        return False
    
    # Check pre-deploy command
    pre_deploy = service.get('serviceDetails', {}).get('preDeployCommand')
    if pre_deploy == EXPECTED_CONFIG["preDeployCommand"]:
        print(f"✅ Pre-deploy command correctly set to: {EXPECTED_CONFIG['preDeployCommand']}")
    else:
        print(f"❌ Pre-deploy command mismatch. Expected: {EXPECTED_CONFIG['preDeployCommand']}, Got: {pre_deploy}")
        return False
    
    return True

def verify_environment_variables(client: RenderAPIClient) -> bool:
    """Verify all required environment variables are present"""
    print("\n🔍 Verifying environment variables...")
    
    env_vars = client.get_service_env_vars(SERVICE_ID)
    if not env_vars:
        print("❌ Failed to get environment variables")
        return False
    
    # Create a set of existing env var keys
    existing_vars = {var['key'] for var in env_vars}
    missing_vars = []
    empty_vars = []
    
    for var_name in REQUIRED_ENV_VARS:
        if var_name not in existing_vars:
            missing_vars.append(var_name)
        else:
            # Check if variable has a value (not empty)
            var_data = next(var for var in env_vars if var['key'] == var_name)
            if not var_data.get('value', '').strip():
                empty_vars.append(var_name)
            else:
                print(f"✅ {var_name}: Present and non-empty")
    
    # Check ENVIRONMENT=production specifically
    env_var = next((var for var in env_vars if var['key'] == 'ENVIRONMENT'), None)
    if env_var and env_var.get('value') == 'production':
        print("✅ ENVIRONMENT correctly set to 'production'")
    else:
        print(f"❌ ENVIRONMENT variable issue. Expected: 'production'")
        return False
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    if empty_vars:
        print(f"\n❌ Empty environment variables: {', '.join(empty_vars)}")
        return False
    
    print("\n✅ All required environment variables are present and non-empty")
    return True

def verify_worker_services(client: RenderAPIClient) -> bool:
    """Verify worker services exist with proper REDIS_URL"""
    print("\n🔍 Verifying worker services...")
    
    services = client.list_services()
    if not services:
        print("❌ Failed to list services")
        return False
    
    # Look for celery worker services
    celery_service = None
    celery_beat_service = None
    
    for service in services:
        name = service.get('name', '').lower()
        if 'ttpro-celery' in name and 'beat' not in name:
            celery_service = service
        elif 'ttpro-celery-beat' in name:
            celery_beat_service = service
    
    if not celery_service:
        print("❌ ttpro-celery worker service not found")
        return False
    
    if not celery_beat_service:
        print("❌ ttpro-celery-beat worker service not found")
        return False
    
    print(f"✅ Found ttpro-celery service: {celery_service.get('id')}")
    print(f"✅ Found ttpro-celery-beat service: {celery_beat_service.get('id')}")
    
    # Check REDIS_URL for both worker services
    for worker_name, worker_service in [("ttpro-celery", celery_service), ("ttpro-celery-beat", celery_beat_service)]:
        worker_env_vars = client.get_service_env_vars(worker_service.get('id'))
        if not worker_env_vars:
            print(f"❌ Failed to get environment variables for {worker_name}")
            return False
        
        redis_var = next((var for var in worker_env_vars if var['key'] == 'REDIS_URL'), None)
        if redis_var and redis_var.get('value', '').strip():
            print(f"✅ {worker_name}: REDIS_URL is present and non-empty")
        else:
            print(f"❌ {worker_name}: REDIS_URL is missing or empty")
            return False
    
    return True

def trigger_deploy_and_wait(client: RenderAPIClient) -> bool:
    """Trigger manual deploy and wait for healthy status"""
    print("\n🚀 Triggering manual deployment...")
    
    deploy = client.create_deploy(SERVICE_ID)
    if not deploy:
        print("❌ Failed to trigger deployment")
        return False
    
    deploy_id = deploy.get('id')
    print(f"✅ Deployment triggered: {deploy_id}")
    
    # Wait for deployment to complete
    print("⏳ Waiting for deployment to complete...")
    max_wait = 600  # 10 minutes
    wait_time = 0
    check_interval = 30  # Check every 30 seconds
    
    while wait_time < max_wait:
        time.sleep(check_interval)
        wait_time += check_interval
        
        deploy_status = client.get_deploy_status(SERVICE_ID, deploy_id)
        if not deploy_status:
            print("❌ Failed to get deployment status")
            return False
        
        status = deploy_status.get('status', 'unknown')
        print(f"📊 Deploy status: {status} ({wait_time}s elapsed)")
        
        if status == 'live':
            print("✅ Deployment completed successfully and service is healthy!")
            return True
        elif status in ['failed', 'canceled']:
            print(f"❌ Deployment failed with status: {status}")
            return False
    
    print("⏰ Deployment timeout - please check manually")
    return False

def main():
    """Main verification function"""
    print("🔧 TTPROv4 Render Service Verification")
    print("=" * 50)
    
    # Get API key
    api_key = os.environ.get('RENDER_API_KEY')
    if not api_key:
        print("❌ RENDER_API_KEY environment variable not set")
        print("Please set your Render API key: export RENDER_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    client = RenderAPIClient(api_key)
    
    # Run all verification steps
    config_ok = verify_service_configuration(client)
    env_vars_ok = verify_environment_variables(client)
    workers_ok = verify_worker_services(client)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 50)
    
    all_good = config_ok and env_vars_ok and workers_ok
    
    if all_good:
        print("✅ All verifications passed!")
        
        # Ask about deployment
        deploy_choice = input("\n🚀 All configurations are correct. Trigger manual deployment? (y/N): ")
        if deploy_choice.lower().startswith('y'):
            deploy_ok = trigger_deploy_and_wait(client)
            if deploy_ok:
                print("\n🎉 TTPROv4 service is fully configured and deployed successfully!")
            else:
                print("\n⚠️  Service configuration is correct but deployment encountered issues")
                sys.exit(1)
        else:
            print("\n✅ Service configuration verified. No deployment triggered.")
    else:
        print("\n❌ Some verifications failed. Please fix the issues above.")
        
        if not config_ok:
            print("   - Service configuration issues detected")
        if not env_vars_ok:
            print("   - Environment variable issues detected")
        if not workers_ok:
            print("   - Worker service issues detected")
        
        sys.exit(1)

if __name__ == "__main__":
    main()