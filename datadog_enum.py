#!/usr/bin/env python3
"""
Datadog API Key Enumeration Script
Enumerates what resources and data a Datadog API key has access to.

Author: l0lsec
GitHub: https://github.com/l0lsec
Version: 1.0.0

Usage:
    python3 datadog_enum.py <API_KEY> [APP_KEY] [--region REGION]
    
Examples:
    python3 datadog_enum.py abc123def456
    python3 datadog_enum.py abc123def456 xyz789app --region eu
"""

__author__ = "l0lsec"
__version__ = "1.0.0"
__github__ = "https://github.com/l0lsec"

import requests
import json
import sys
import argparse
import os
from datetime import datetime, timedelta

# Configuration - Can be set via args, env vars, or here directly
API_KEY = os.environ.get("DD_API_KEY", "")
APP_KEY = os.environ.get("DD_APP_KEY", "")

# Datadog API base URL (use .eu for EU, .us3, .us5 for other regions)
BASE_URL = "https://api.datadoghq.com"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}[✓] {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}[✗] {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}[i] {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}[!] {text}{Colors.END}")

def get_headers():
    headers = {
        "DD-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    if APP_KEY:
        headers["DD-APPLICATION-KEY"] = APP_KEY
    return headers

def test_endpoint(name, method, endpoint, data=None, description=""):
    """Test if an endpoint is accessible"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, headers=get_headers(), timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=get_headers(), json=data, timeout=10)
        
        if response.status_code == 200:
            print_success(f"{name}: ACCESSIBLE")
            if description:
                print_info(f"  → {description}")
            return True, response.json() if response.text else {}
        elif response.status_code == 403:
            print_error(f"{name}: FORBIDDEN (403)")
            return False, None
        elif response.status_code == 401:
            print_error(f"{name}: UNAUTHORIZED (401)")
            return False, None
        elif response.status_code == 404:
            print_warning(f"{name}: NOT FOUND (404)")
            return False, None
        else:
            print_warning(f"{name}: Status {response.status_code}")
            return False, None
    except Exception as e:
        print_error(f"{name}: Error - {str(e)}")
        return False, None

def validate_api_key():
    """Validate the API key"""
    print_header("VALIDATING API KEY")
    success, data = test_endpoint(
        "API Key Validation",
        "GET",
        "/api/v1/validate",
        description="Confirms the API key is valid"
    )
    if success and data:
        print_info(f"  Valid: {data.get('valid', 'Unknown')}")
    return success

def enumerate_organization():
    """Get organization information"""
    print_header("ORGANIZATION INFO")
    success, data = test_endpoint(
        "Organization Details",
        "GET",
        "/api/v1/org",
        description="Organization settings and info"
    )
    if success and data:
        org = data.get('org', {})
        print_info(f"  Name: {org.get('name', 'N/A')}")
        print_info(f"  Public ID: {org.get('public_id', 'N/A')}")
        print_info(f"  Created: {org.get('created', 'N/A')}")

def enumerate_users():
    """List users in the organization"""
    print_header("USERS")
    success, data = test_endpoint(
        "List Users",
        "GET",
        "/api/v2/users",
        description="All users in the organization"
    )
    if success and data:
        users = data.get('data', [])
        print_info(f"  Found {len(users)} users")
        for user in users[:10]:  # Show first 10
            attrs = user.get('attributes', {})
            print_info(f"    - {attrs.get('email', 'N/A')} ({attrs.get('status', 'N/A')})")
        if len(users) > 10:
            print_info(f"    ... and {len(users) - 10} more")

def enumerate_api_keys():
    """List API keys"""
    print_header("API KEYS")
    success, data = test_endpoint(
        "List API Keys",
        "GET",
        "/api/v2/api_keys",
        description="All API keys in the organization"
    )
    if success and data:
        keys = data.get('data', [])
        print_info(f"  Found {len(keys)} API keys")
        for key in keys[:5]:
            attrs = key.get('attributes', {})
            print_info(f"    - {attrs.get('name', 'N/A')} (Last 4: ...{attrs.get('last4', 'N/A')})")

def enumerate_app_keys():
    """List Application keys"""
    print_header("APPLICATION KEYS")
    success, data = test_endpoint(
        "List Application Keys",
        "GET",
        "/api/v2/application_keys",
        description="All application keys"
    )
    if success and data:
        keys = data.get('data', [])
        print_info(f"  Found {len(keys)} application keys")

def enumerate_dashboards():
    """List dashboards"""
    print_header("DASHBOARDS")
    success, data = test_endpoint(
        "List Dashboards",
        "GET",
        "/api/v1/dashboard",
        description="All dashboards"
    )
    if success and data:
        dashboards = data.get('dashboards', [])
        print_info(f"  Found {len(dashboards)} dashboards")
        for dash in dashboards[:5]:
            print_info(f"    - {dash.get('title', 'N/A')} (ID: {dash.get('id', 'N/A')})")
        if len(dashboards) > 5:
            print_info(f"    ... and {len(dashboards) - 5} more")

def enumerate_monitors():
    """List monitors"""
    print_header("MONITORS")
    success, data = test_endpoint(
        "List Monitors",
        "GET",
        "/api/v1/monitor",
        description="All configured monitors/alerts"
    )
    if success and data:
        if isinstance(data, list):
            print_info(f"  Found {len(data)} monitors")
            for mon in data[:5]:
                print_info(f"    - {mon.get('name', 'N/A')} (Type: {mon.get('type', 'N/A')})")
            if len(data) > 5:
                print_info(f"    ... and {len(data) - 5} more")

def enumerate_hosts():
    """List hosts"""
    print_header("HOSTS")
    success, data = test_endpoint(
        "List Hosts",
        "GET",
        "/api/v1/hosts",
        description="All monitored hosts"
    )
    if success and data:
        hosts = data.get('host_list', [])
        print_info(f"  Total hosts: {data.get('total_matching', len(hosts))}")
        for host in hosts[:5]:
            print_info(f"    - {host.get('name', 'N/A')} (Apps: {', '.join(host.get('apps', [])[:3])})")
        if len(hosts) > 5:
            print_info(f"    ... and more")

def enumerate_metrics():
    """List available metrics"""
    print_header("METRICS")
    success, data = test_endpoint(
        "List Metrics",
        "GET",
        "/api/v1/metrics?from=" + str(int((datetime.now() - timedelta(hours=1)).timestamp())),
        description="Active metrics in the last hour"
    )
    if success and data:
        metrics = data.get('metrics', [])
        print_info(f"  Found {len(metrics)} active metrics")
        for metric in metrics[:10]:
            print_info(f"    - {metric}")
        if len(metrics) > 10:
            print_info(f"    ... and {len(metrics) - 10} more")

def enumerate_integrations():
    """Check various integrations"""
    print_header("INTEGRATIONS")
    
    integrations = [
        ("AWS", "/api/v1/integration/aws"),
        ("Azure", "/api/v1/integration/azure"),
        ("GCP", "/api/v1/integration/gcp"),
        ("Slack", "/api/v1/integration/slack"),
        ("PagerDuty", "/api/v1/integration/pagerduty"),
        ("Webhooks", "/api/v1/integration/webhooks/configuration/webhooks"),
    ]
    
    for name, endpoint in integrations:
        test_endpoint(f"{name} Integration", "GET", endpoint)

def enumerate_logs():
    """Check logs access"""
    print_header("LOGS")
    
    # List log indexes
    test_endpoint(
        "Log Indexes",
        "GET",
        "/api/v1/logs/config/indexes",
        description="Log index configurations"
    )
    
    # List log pipelines
    test_endpoint(
        "Log Pipelines",
        "GET",
        "/api/v1/logs/config/pipelines",
        description="Log processing pipelines"
    )

def enumerate_apm():
    """Check APM access"""
    print_header("APM / TRACING")
    
    test_endpoint(
        "Services",
        "GET",
        "/api/v1/services",
        description="APM services"
    )

def enumerate_synthetics():
    """Check Synthetics access"""
    print_header("SYNTHETICS")
    
    success, data = test_endpoint(
        "Synthetic Tests",
        "GET",
        "/api/v1/synthetics/tests",
        description="Synthetic monitoring tests"
    )
    if success and data:
        tests = data.get('tests', [])
        print_info(f"  Found {len(tests)} synthetic tests")

def enumerate_notebooks():
    """List notebooks"""
    print_header("NOTEBOOKS")
    success, data = test_endpoint(
        "List Notebooks",
        "GET",
        "/api/v1/notebooks",
        description="All notebooks"
    )
    if success and data:
        notebooks = data.get('data', [])
        print_info(f"  Found {len(notebooks)} notebooks")

def enumerate_slos():
    """List SLOs"""
    print_header("SERVICE LEVEL OBJECTIVES (SLOs)")
    success, data = test_endpoint(
        "List SLOs",
        "GET",
        "/api/v1/slo",
        description="All SLOs"
    )
    if success and data:
        slos = data.get('data', [])
        print_info(f"  Found {len(slos)} SLOs")

def enumerate_downtimes():
    """List downtimes"""
    print_header("DOWNTIMES")
    success, data = test_endpoint(
        "List Downtimes",
        "GET",
        "/api/v1/downtime",
        description="Scheduled downtimes"
    )
    if success and data:
        if isinstance(data, list):
            print_info(f"  Found {len(data)} downtimes")

def enumerate_events():
    """Get recent events"""
    print_header("EVENTS")
    now = int(datetime.now().timestamp())
    start = now - 86400  # Last 24 hours
    success, data = test_endpoint(
        "Recent Events",
        "GET",
        f"/api/v1/events?start={start}&end={now}",
        description="Events from last 24 hours"
    )
    if success and data:
        events = data.get('events', [])
        print_info(f"  Found {len(events)} events in last 24h")

def enumerate_security():
    """Check security-related endpoints"""
    print_header("SECURITY")
    
    test_endpoint(
        "Security Monitoring Rules",
        "GET",
        "/api/v2/security_monitoring/rules",
        description="Security detection rules"
    )
    
    test_endpoint(
        "Security Signals",
        "GET",
        "/api/v2/security_monitoring/signals",
        description="Security signals/alerts"
    )

def enumerate_rum():
    """Check RUM access"""
    print_header("REAL USER MONITORING (RUM)")
    
    test_endpoint(
        "RUM Applications",
        "GET",
        "/api/v2/rum/applications",
        description="RUM application configurations"
    )

def enumerate_service_accounts():
    """List service accounts"""
    print_header("SERVICE ACCOUNTS")
    success, data = test_endpoint(
        "Service Accounts",
        "GET",
        "/api/v2/service_accounts",
        description="Service accounts"
    )

def enumerate_roles():
    """List roles"""
    print_header("ROLES & PERMISSIONS")
    success, data = test_endpoint(
        "List Roles",
        "GET",
        "/api/v2/roles",
        description="RBAC roles"
    )
    if success and data:
        roles = data.get('data', [])
        print_info(f"  Found {len(roles)} roles")
        for role in roles[:5]:
            attrs = role.get('attributes', {})
            print_info(f"    - {attrs.get('name', 'N/A')}")

def main():
    global API_KEY, APP_KEY, BASE_URL
    
    parser = argparse.ArgumentParser(
        description="Enumerate Datadog API key permissions and accessible resources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 datadog_enum.py YOUR_API_KEY
  python3 datadog_enum.py YOUR_API_KEY YOUR_APP_KEY
  python3 datadog_enum.py YOUR_API_KEY YOUR_APP_KEY --region eu
  python3 datadog_enum.py YOUR_API_KEY --region us3
  
Environment Variables:
  DD_API_KEY - Datadog API Key
  DD_APP_KEY - Datadog Application Key
        """
    )
    parser.add_argument("api_key", nargs="?", help="Datadog API Key")
    parser.add_argument("app_key", nargs="?", help="Datadog Application Key (optional)")
    parser.add_argument("--region", "-r", choices=["us1", "us3", "us5", "eu", "ap1"], 
                        default="us1", help="Datadog region (default: us1)")
    
    args = parser.parse_args()
    
    # Set keys from args or fall back to env vars
    if args.api_key:
        API_KEY = args.api_key
    if args.app_key:
        APP_KEY = args.app_key
    
    if not API_KEY:
        print(f"{Colors.RED}Error: API Key is required{Colors.END}")
        print(f"Usage: python3 datadog_enum.py <API_KEY> [APP_KEY] [--region REGION]")
        print(f"Or set DD_API_KEY environment variable")
        sys.exit(1)
    
    # Set region
    regions = {
        "us1": "https://api.datadoghq.com",
        "us3": "https://api.us3.datadoghq.com",
        "us5": "https://api.us5.datadoghq.com",
        "eu": "https://api.datadoghq.eu",
        "ap1": "https://api.ap1.datadoghq.com",
    }
    BASE_URL = regions.get(args.region, "https://api.datadoghq.com")
    
    print(f"""
{Colors.BOLD}{Colors.CYAN}
    ██████╗  █████╗ ████████╗ █████╗ ██████╗  ██████╗  ██████╗ 
    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔═══██╗██╔════╝ 
    ██║  ██║███████║   ██║   ███████║██║  ██║██║   ██║██║  ███╗
    ██║  ██║██╔══██║   ██║   ██╔══██║██║  ██║██║   ██║██║   ██║
    ██████╔╝██║  ██║   ██║   ██║  ██║██████╔╝╚██████╔╝╚██████╔╝
    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚═════╝ 
                                                               
    ███████╗███╗   ██╗██╗   ██╗███╗   ███╗███████╗██████╗      
    ██╔════╝████╗  ██║██║   ██║████╗ ████║██╔════╝██╔══██╗     
    █████╗  ██╔██╗ ██║██║   ██║██╔████╔██║█████╗  ██████╔╝     
    ██╔══╝  ██║╚██╗██║██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗     
    ███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║     
    ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝     
{Colors.END}
{Colors.YELLOW}    ╔══════════════════════════════════════════════════════════╗
    ║  Datadog API Key Enumeration Tool v{__version__}                  ║
    ║  Author: {__author__}                                         ║
    ║  GitHub: github.com/l0lsec                                 ║
    ╚══════════════════════════════════════════════════════════╝{Colors.END}
""")
    print_info(f"Using API endpoint: {BASE_URL}")
    
    if not APP_KEY:
        print_warning("No Application Key provided - some endpoints may be inaccessible")
        print_warning("API keys can only submit data, Application keys are needed to read data")
    
    # Run enumeration
    if not validate_api_key():
        print_error("API Key validation failed. Check your key and try again.")
        sys.exit(1)
    
    # Enumerate everything
    enumerate_organization()
    enumerate_users()
    enumerate_api_keys()
    enumerate_app_keys()
    enumerate_roles()
    enumerate_service_accounts()
    enumerate_hosts()
    enumerate_metrics()
    enumerate_dashboards()
    enumerate_monitors()
    enumerate_events()
    enumerate_downtimes()
    enumerate_slos()
    enumerate_notebooks()
    enumerate_logs()
    enumerate_apm()
    enumerate_synthetics()
    enumerate_rum()
    enumerate_integrations()
    enumerate_security()
    
    print_header("ENUMERATION COMPLETE")
    print_info("Review the results above to see what your API key can access")
    print_info("Green [✓] = Accessible, Red [✗] = Forbidden/Unauthorized")

if __name__ == "__main__":
    main()

