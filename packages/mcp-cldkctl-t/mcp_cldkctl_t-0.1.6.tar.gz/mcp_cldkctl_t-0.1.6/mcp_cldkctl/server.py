#!/usr/bin/env python3
"""
MCP Server for Cloudeka CLI (cldkctl) functionality.
"""

import asyncio
import base64
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from importlib import metadata

import requests
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    Tool,
    TextContent,
    Content,
)
from mcp_cldkctl.tool_param_map import TOOL_PARAM_MAP


class SimpleNotificationOptions:
    """Simple notification options class for MCP server capabilities."""

    def __init__(self, prompts_changed=False, resources_changed=False, tools_changed=False):
        self.prompts_changed = prompts_changed
        self.resources_changed = resources_changed
        self.tools_changed = tools_changed


# Initialize the server
server = Server("cldkctl")

# Configuration
PRODUCTION_URL = "https://ai.cloudeka.id"
STAGING_URL = "https://staging.ai.cloudeka.id"
CACHE_FILE = os.path.expanduser("~/.cldkctl/mcp_cache.json")
CACHE_DIR = os.path.expanduser("~/.cldkctl")

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# Global state for authentication and environment
auth_cache = {
    "jwt_token": None,
    "login_payload": None,
    "expires_at": None,
    "user_info": None,
    "environment": "production",
    "base_url": PRODUCTION_URL,
}

# Environment configuration
current_base_url = PRODUCTION_URL  # Default to production
environment_name = "production"


def load_cache():
    """Load cached authentication data."""
    global auth_cache, current_base_url, environment_name
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cached_data = json.load(f)
                # Check if token is still valid
                if cached_data.get("expires_at"):
                    expires_at = datetime.fromisoformat(cached_data["expires_at"])
                    if datetime.now() < expires_at:
                        auth_cache.update(cached_data)
                        current_base_url = auth_cache["base_url"]
                        environment_name = auth_cache["environment"]
                        print(f"Loaded cached auth data, expires at {expires_at}", file=sys.stderr)
                        return True
                    else:
                        print("Cached token expired", file=sys.stderr)
                return False
    except Exception as e:
        print(f"Error loading cache: {e}", file=sys.stderr)
    return False


def save_cache():
    """Save authentication data to cache."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(auth_cache, f, default=str)
    except Exception as e:
        print(f"Error saving cache: {e}", file=sys.stderr)


def authenticate_with_token(token: str, force_staging: bool = False) -> bool:
    """Authenticate using a cldkctl token and get JWT."""
    global auth_cache, current_base_url, environment_name

    # Determine which URL to use
    if force_staging:
        base_url = STAGING_URL
        env_name = "staging"
    else:
        base_url = PRODUCTION_URL
        env_name = "production"

    print(f"Authenticating with {env_name} environment: {base_url}", file=sys.stderr)
    url = f"{base_url}/core/cldkctl/auth"
    payload = {"token": token}

    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        print(f"Auth response status: {response.status_code}", file=sys.stderr)

        if response.status_code == 200:
            data = response.json()
            jwt_token = data.get("data", {}).get("token")
            if jwt_token:
                # Update global state
                current_base_url = base_url
                environment_name = env_name
                # Cache the authentication data
                auth_cache["jwt_token"] = jwt_token
                auth_cache["login_payload"] = base64.b64encode(json.dumps(payload).encode()).decode()
                auth_cache["expires_at"] = (datetime.now() + timedelta(hours=24)).isoformat()
                auth_cache["user_info"] = data.get("data", {})
                auth_cache["environment"] = env_name
                auth_cache["base_url"] = base_url
                save_cache()
                print(f"Authentication successful with {env_name}", file=sys.stderr)
                return True
            else:
                print("No JWT token in response", file=sys.stderr)
                return False
        elif response.status_code == 400 and "pq: relation \"cldkctl_tokens\" does not exist" in response.text:
            print("Production backend has database issue, trying staging...", file=sys.stderr)
            if not force_staging:
                return authenticate_with_token(token, force_staging=True)
            else:
                print("Staging also failed with the same issue.", file=sys.stderr)
                return False
        else:
            print(f"Authentication failed: {response.status_code} - {response.text}", file=sys.stderr)
            return False
    except requests.RequestException as e:
        print(f"Authentication request error: {e}", file=sys.stderr)
        if not force_staging:
            print("Trying staging as fallback...", file=sys.stderr)
            return authenticate_with_token(token, force_staging=True)
        return False


def get_auth_headers() -> Dict[str, str]:
    """Get headers with authentication token."""
    if not auth_cache.get("jwt_token"):
        raise Exception("Not authenticated. Please authenticate first.")

    # Check for token expiration
    expires_at_str = auth_cache.get("expires_at")
    if expires_at_str:
        if datetime.now() >= datetime.fromisoformat(expires_at_str):
            print("Token expired, attempting re-authentication", file=sys.stderr)
            if auth_cache.get("login_payload"):
                login_data = json.loads(base64.b64decode(auth_cache["login_payload"]).decode())
                if not authenticate_with_token(login_data["token"], force_staging=(environment_name == "staging")):
                    raise Exception("Re-authentication failed")
            else:
                raise Exception("Token expired and no login payload to re-authenticate.")

    return {
        "Authorization": f"Bearer {auth_cache['jwt_token']}",
        "Content-Type": "application/json",
    }


def make_authenticated_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
    """Make an authenticated request to the API."""
    url = f"{current_base_url}{endpoint}"
    try:
        headers = get_auth_headers()
        response = requests.request(method, url, headers=headers, json=data, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Authenticated request failed: {e}", file=sys.stderr)
        # In case of an error, return a structured error message
        return {"error": True, "message": str(e), "status_code": getattr(e.response, "status_code", None)}


# Load cached auth on startup
load_cache()


def get_tool_definitions():
    """Dynamically generate the list of available tools from TOOL_PARAM_MAP."""
    from mcp_cldkctl.tool_param_map import TOOL_PARAM_MAP
    tools = []
    for tool_name, info in TOOL_PARAM_MAP.items():
        properties = {}
        required = []
        for param in info.get("required_params", []):
            properties[param["name"]] = {"type": param["type"], "description": param.get("desc", "")}
            required.append(param["name"])
        for param in info.get("optional_params", []):
            properties[param["name"]] = {"type": param["type"], "description": param.get("desc", "")}
        tools.append(Tool(
            name=tool_name.replace("mcp_cldkctl_", ""),
            description=f"{info.get('method', '').upper()} {info.get('endpoint', '')}",
            inputSchema={"type": "object", "properties": properties, "required": required}
        ))
    return tools


def get_endpoint_map():
    """Get the mapping of tool names to API endpoints."""
    return {
        # Authentication endpoints
        "cldkctl_auth": ("/core/cldkctl/auth", "POST"),
        "cldkctl_switch_environment": ("/core/cldkctl/environment", "POST"),
        "cldkctl_status": "/core/cldkctl/status",
        
        # Profile Management endpoints
        "cldkctl_profile_detail": ("/core/user/profile", "GET"),
        "cldkctl_update_profile": ("/core/user/organization/profile/member/:user_id", "PUT"),
        "cldkctl_change_password": ("/core/user/change-password", "POST"),

        # Project Management endpoints
        "cldkctl_project_list": ("/core/user/organization/projects/byOrg", "GET"),
        "cldkctl_project_detail": ("/core/user/project/detail/:project_id", "GET"),
        "cldkctl_update_project": ("/core/user/projects/:project_id", "PUT"),
        "cldkctl_check_before_delete_project": ("/core/user/checking/projects/:project_id", "DELETE"),
        "cldkctl_delete_project": ("/core/user/projects/:project_id", "DELETE"),
        "cldkctl_project_r_quota_post": ("/mid/billing/projectdekagpu/quota/:project_id", "GET"),
        "cldkctl_project_r_quota_pre": ("/mid/billing/projectflavorgpu/project/:project_id", "GET"),

        # Organization Management endpoints
        "cldkctl_org_detail": ("/core/user/organization", "GET"),
        "cldkctl_org_edit": ("/core/user/organization/edit/:organization_id", "PUT"),
        "cldkctl_org_members": ("/core/user/organization/member", "GET"),
        "cldkctl_org_member_add": ("/core/user/organization/member", "POST"),
        "cldkctl_org_member_edit": ("/core/user/organization/member/:user_id", "PUT"),
        "cldkctl_org_member_delete": ("/core/user/organization/member/:user_id", "DELETE"),
        "cldkctl_org_member_activate": ("/core/user/manageuser/active/:user_id", "PUT"),
        "cldkctl_org_member_deactivate": ("/core/user/manageuser/deactive/:user_id", "PUT"),
        "cldkctl_org_member_resend_invitation": ("/core/superadmin/manageuser/resend-verified/:user_id", "POST"),
        # Balance & Billing endpoints
        "cldkctl_billing_daily_cost": ("/core/billing/v2/daily-cost/:project_id", "GET"),
        "cldkctl_billing_monthly_cost": ("/core/billing/monthly-cost/total-billed/:project_id", "GET"),
        "cldkctl_billing_history": ("/core/billing/v2/history", "POST"),
        "cldkctl_billing_invoice_sme": ("/core/balance/history/invoice", "GET"),
        "cldkctl_billing_invoice_sme_detail": ("/core/balance/history/invoice/detail/:invoice_id", "GET"),
        "cldkctl_billing_invoice_enterprise": ("/core/billing/invoice/:project_id", "GET"),
        "cldkctl_billing_invoice_enterprise_detail": ("/core/billing/v2/invoice/detail/:invoice_id", "GET"),
        "cldkctl_payment_history": ("/core/payment/history", "GET"),
        # Kubernetes Core Tools
        "cldkctl_k8s_pods": ("/core/k8s/pods", "GET"),
        "cldkctl_k8s_pod_create": ("/core/k8s/pods", "POST"),
        "cldkctl_k8s_pod_edit": ("/core/k8s/pods/:project_id/:name", "PUT"),
        "cldkctl_k8s_pod_delete": ("/core/k8s/pods/:project_id/:name", "DELETE"),
        "cldkctl_k8s_pod_console": ("/core/k8s/pods/:project_id/:name/console", "GET"),
        "cldkctl_k8s_pod_console_token": ("/core/k8s/pods/:project_id/:name/console-token", "GET"),
        "cldkctl_k8s_deployments": ("/core/k8s/deployments", "GET"),
        "cldkctl_k8s_deployment_create": ("/core/k8s/deployments", "POST"),
        "cldkctl_k8s_deployment_edit": ("/core/k8s/deployments/:project_id/:name", "PUT"),
        "cldkctl_k8s_deployment_delete": ("/core/k8s/deployments/:project_id/:name", "DELETE"),
        "cldkctl_k8s_services": ("/core/k8s/services", "GET"),
        "cldkctl_k8s_service_create": ("/core/k8s/services", "POST"),
        "cldkctl_k8s_service_edit": ("/core/k8s/services/:project_id/:name", "PUT"),
        "cldkctl_k8s_service_delete": ("/core/k8s/services/:project_id/:name", "DELETE"),
        "cldkctl_k8s_configmaps": ("/core/k8s/configmaps", "GET"),
        "cldkctl_k8s_secrets": ("/core/k8s/secrets", "GET"),
        # Virtual Machines Tools
        "cldkctl_vm_list": ("/core/vm/list", "GET"),
        "cldkctl_vm_detail": ("/core/vm/:vm_id", "GET"),
        # Registry Tools
        "cldkctl_registry_list": ("/core/registry/list", "GET"),
        "cldkctl_registry_repositories": ("/core/registry/:registry_id/repositories", "GET"),
        # Notebooks Tools
        "cldkctl_notebook_list": ("/core/notebook/list", "GET"),
        "cldkctl_notebook_create": ("/core/notebook", "POST"),
        # Vouchers Tools
        "cldkctl_voucher_list": ("/core/voucher/list", "GET"),
        "cldkctl_voucher_apply": ("/core/voucher/apply", "POST"),
        # Tokens Tools
        "cldkctl_token_list": ("/core/token/list", "GET"),
        "cldkctl_token_create": ("/core/token", "POST"),
        "cldkctl_token_delete": ("/core/token/:token_id", "DELETE"),
        # Audit Tools
        "cldkctl_audit_logs": ("/core/audit/logs", "GET"),
        # Registry Artifacts Tools
        "cldkctl_registry_artifact_list": ("/core/registry/artifact/list", "GET"),
        # Login tool
        "cldkctl_login": ("/core/user/login", "POST"),
        # Organization Management endpoints
        "cldkctl_org_role_list": ("/core/user/organization/role", "GET"),
        "cldkctl_org_role_detail": ("/core/user/organization/role/:role_id", "GET"),
        "cldkctl_org_role_edit": ("/core/user/organization/role/:role_id", "PUT"),
        "cldkctl_org_role_delete": ("/core/user/organization/role/:role_id", "DELETE"),
        "cldkctl_org_role_add": ("/core/user/organization/role", "POST"),
        "cldkctl_voucher_claim": ("/core/user/voucher-credit/claim", "POST"),
        "cldkctl_voucher_claimed_list": ("/core/user/voucher-credit/claimed", "GET"),
        "cldkctl_voucher_trial_claimed_list": ("/core/user/voucher/claimed", "GET"),
        "cldkctl_audit_log": ("/core/api/v1.1/user/activity/sp/get-auditlog", "GET"),
        # --- END CONTINUATION OF FULL AUTO-GENERATED TOOL STUBS ---
        "cldkctl_kube_dashboard": ("/core/user/projects/:project_id/vcluster/dashboard", "GET"),
        "cldkctl_kubeconfig": ("/core/user/projects/:project_id/vcluster/kubeconfig", "GET"),
        "cldkctl_get_pod": ("/core/pods", "GET"),
        "cldkctl_create_pod": ("/core/pods", "POST"),
        "cldkctl_edit_pod": ("/core/pods/:project_id/:namespace/:name", "PUT"),
        "cldkctl_delete_pod": ("/core/pods/:project_id/:namespace/:name", "DELETE"),
        "cldkctl_console_pod": ("/core/pods/console/:token", "GET"),
        "cldkctl_console_token_pod": ("/core/pods/console", "POST"),
        "cldkctl_get_deployment": ("/core/deployment", "GET"),
        "cldkctl_create_deployment": ("/core/deployment", "POST"),
        "cldkctl_edit_deployment": ("/core/deployment/:project_id/:namespace/:name", "PUT"),
        "cldkctl_delete_deployment": ("/core/deployment/:project_id/:namespace/:name", "DELETE"),
        "cldkctl_get_daemonset": ("/core/daemonset", "GET"),
        "cldkctl_create_daemonset": ("/core/daemonset", "POST"),
        "cldkctl_edit_daemonset": ("/core/daemonset/:project_id/:namespace/:name", "PUT"),
        "cldkctl_delete_daemonset": ("/core/daemonset/:project_id/:namespace/:name", "DELETE"),
        "cldkctl_get_statefulset": ("/core/statefulsets", "GET"),
        "cldkctl_create_statefulset": ("/core/statefulsets", "POST"),
        "cldkctl_edit_statefulset": ("/core/statefulsets/:project_id/:namespace/:name", "PUT"),
        "cldkctl_delete_statefulset": ("/core/statefulsets/:project_id/:namespace/:name", "DELETE"),
        # --- CONTINUATION OF FULL AUTO-GENERATED TOOL STUBS ---
        "cldkctl_get_service": ("/core/kubernetes/services", "GET"),
        "cldkctl_create_service": ("/core/kubernetes/services", "POST"),
        "cldkctl_edit_service": ("/core/kubernetes/services/:project_id/:namespace/:name", "PUT"),
        "cldkctl_delete_service": ("/core/kubernetes/services/:project_id/:namespace/:name", "DELETE"),
        "cldkctl_get_persistent_volume": ("/core/kubernetes/pv", "GET"),
        "cldkctl_create_persistent_volume": ("/core/kubernetes/pv", "POST"),
        "cldkctl_edit_persistent_volume": ("/core/kubernetes/pv/:project_id/:name", "PUT"),
        "cldkctl_delete_persistent_volume": ("/core/kubernetes/pv/:project_id/:name", "DELETE"),
        "cldkctl_get_pvc": ("/core/kubernetes/pvc", "GET"),
        "cldkctl_create_pvc": ("/core/kubernetes/pvc", "POST"),
        "cldkctl_edit_pvc": ("/core/kubernetes/pvc/:project_id/:namespace/:name", "PUT"),
        "cldkctl_delete_pvc": ("/core/kubernetes/pvc/:project_id/:namespace/:name", "DELETE"),
        "cldkctl_get_data_volume": ("/core/datavolume", "GET"),
        "cldkctl_create_data_volume": ("/core/datavolume", "POST"),
        "cldkctl_edit_data_volume": ("/core/datavolume/:project_id/:namespace/:name", "PUT"),
        "cldkctl_delete_data_volume": ("/core/datavolume/:project_id/:namespace/:name", "DELETE"),
        "cldkctl_get_resource_v1": ("/core/kubernetes/:resource", "GET"),
        "cldkctl_create_resource_v1": ("/core/kubernetes/:resource", "POST"),
        "cldkctl_edit_resource_v1": ("/core/kubernetes/:resource/:project_id/:namespace/:name", "PATCH"),
        "cldkctl_delete_resource_v1": ("/core/kubernetes/:resource/:project_id/:namespace/:name", "DELETE"),
        "cldkctl_get_custom_resources": ("/core/kubernetes/apiresources/:project_id", "GET"),
        "cldkctl_get_crd": ("/core/kubernetes/resource/:project_id", "GET"),
        "cldkctl_create_crd": ("/core/kubernetes/resource", "POST"),
        "cldkctl_edit_crd": ("/core/kubernetes/resource/:project_id/:name", "PATCH"),
        "cldkctl_delete_crd": ("/core/kubernetes/resource/:project_id/:name", "DELETE"),
        "cldkctl_get_namespace": ("/core/user/projects/:project_id/vcluster/namespaces", "GET"),
        "cldkctl_get_image_os": ("/core/cluster-image-os", "GET"),
        "cldkctl_get_vm_flavor_type": ("/core/virtual-machine/flavor_type", "GET"),
        "cldkctl_get_vm_gpu": ("/core/virtual-machine/gpu/:project_id", "GET"),
        "cldkctl_get_vm_storage_class": ("/core/virtual-machine/storage-class/:project_id", "GET"),
        "cldkctl_get_vm_flavor": ("/core/virtual-machine/flavor/:flavorType_id", "GET"),
        "cldkctl_create_vm": ("/core/virtual-machine", "POST"),
        "cldkctl_create_vm_yaml": ("/core/virtual-machine/yaml", "POST"),
        "cldkctl_get_vm": ("/core/virtual-machine/list/all", "GET"),
        "cldkctl_vm_detail": ("/core/virtual-machine/detail-vm", "POST"),
        "cldkctl_edit_vm_yaml": ("/core/virtual-machine/yaml/:project_id/:namespace/:name", "PUT"),
        "cldkctl_delete_vm": ("/core/virtual-machine/delete", "POST"),
        "cldkctl_reboot_vm": ("/core/virtual-machine/reboot", "POST"),
        "cldkctl_turn_off_vm": ("/core/virtual-machine/turn-off/vm", "POST"),
        "cldkctl_turn_on_vm": ("/core/virtual-machine/turn-on/vm", "POST"),
        "cldkctl_registry_quota": ("/core/dekaregistry/v2/project/quota/:project_id", "GET"),
        "cldkctl_registry_list": ("/core/dekaregistry/v2/registry", "GET"),
        "cldkctl_registry_overview": ("/core/dekaregistry/v2/registry/:registry_id/overview", "GET"),
        "cldkctl_registry_cert": ("/core/dekaregistry/v1/registry/downloadcrt", "GET"),
        "cldkctl_registry_create": ("/core/dekaregistry/v2/registry", "POST"),
        "cldkctl_registry_update": ("/core/dekaregistry/v2/registry/:registry_id", "PUT"),
        "cldkctl_registry_detail": ("/core/dekaregistry/v2/registry/:registry_id", "GET"),
        "cldkctl_registry_logs": ("/core/dekaregistry/v2/registry/:registry_id/logs", "GET"),
        "cldkctl_registry_labels": ("/core/dekaregistry/v1/registry/lislabels/:organization_id/:user_id/:project_id/:registry_id", "GET"),
        "cldkctl_registry_labels_update": ("/core/dekaregistry/v1/registry/updatelabels/:organization_id/:user_id/:project_id/:registry_id", "PUT"),
        "cldkctl_registry_labels_create": ("/core/dekaregistry/v1/registry/createlabels/:organization_id/:user_id/:project_id/:registry_id", "POST"),
        "cldkctl_registry_labels_delete": ("/core/dekaregistry/v1/registry/deletelabels/:organization_id/:user_id/:project_id/:labels_id/:registry_id", "DELETE"),
        "cldkctl_registry_tag_list": ("/core/dekaregistry/v2/tag/:registry_id", "GET"),
        "cldkctl_registry_tag_create": ("/core/dekaregistry/v2/tag/:registry_id", "POST"),
        "cldkctl_registry_tag_update": ("/core/dekaregistry/v2/tag/detail/:tag_id", "PUT"),
        "cldkctl_registry_tag_delete": ("/core/dekaregistry/v2/tag/detail/:tag_id", "DELETE"),
        "cldkctl_registry_tag_disable": ("/core/dekaregistry/v2/tag/detail/:tag_id/disable", "POST"),
        "cldkctl_registry_tag_enable": ("/core/dekaregistry/v2/tag/detail/:tag_id/enable", "POST"),
        "cldkctl_registry_member_list": ("/core/dekaregistry/v2/member/:registry_id", "GET"),
        "cldkctl_registry_available_member": ("/core/dekaregistry/v2/project/member/:project_id", "GET"),
        "cldkctl_registry_show_password": ("/core/dekaregistry/v2/user/password/show", "POST"),
        "cldkctl_registry_member_add": ("/core/dekaregistry/v2/member/:registry_id", "POST"),
        "cldkctl_registry_member_delete": ("/core/dekaregistry/v2/member/:registry_id/detail/:member_id", "DELETE"),
        "cldkctl_registry_repository_list": ("/core/dekaregistry/v2/repository", "GET"),
        "cldkctl_registry_artifact_list": ("/core/dekaregistry/v2/artifact", "GET"),
        "cldkctl_registry_artifact_detail": ("/core/dekaregistry/v2/artifact/:artifact_id", "GET"),
        "cldkctl_registry_artifact_add_label": ("/core/dekaregistry/v2/artifact/:artifact_id/assign-label/:label_id", "PATCH"),
        "cldkctl_registry_artifact_remove_label": ("/core/dekaregistry/v2/artifact/:artifact_id/unassign-label/:label_id", "PATCH"),
        "cldkctl_registry_artifact_scan": ("/core/dekaregistry/v2/artifact/:artifact_id/scan", "POST"),
        "cldkctl_registry_artifact_stop_scan": ("/core/dekaregistry/v2/artifact/:artifact_id/stop-scan", "POST"),
        "cldkctl_registry_artifact_tags": ("/core/dekaregistry/v2/artifact/:artifact_id/tag", "GET"),
        "cldkctl_registry_artifact_delete_tag": ("/core/dekaregistry/v2/artifact/:artifact_id/tag/:tag", "DELETE"),
        "cldkctl_registry_artifact_add_tag": ("/core/dekaregistry/v2/artifact/:artifact_id/tag/:tag", "POST"),
        "cldkctl_notebook_list": ("/core/deka-notebook", "GET"),
        "cldkctl_notebook_create": ("/core/deka-notebook", "POST"),
        "cldkctl_notebook_delete": ("/core/deka-notebook/delete", "POST"),
        "cldkctl_notebook_update": ("/core/deka-notebook/yaml", "PUT"),
        "cldkctl_notebook_start": ("/core/deka-notebook/start", "POST"),
        "cldkctl_notebook_stop": ("/core/deka-notebook/stop", "POST"),
        "cldkctl_notebook_images": ("/core/deka-notebook/images", "GET"),
        "cldkctl_superadmin_project_list": ("/core/superadmin/list/manageorgproject", "GET"),
        "cldkctl_superadmin_org_detail": ("/core/superadmin/manageorg/:organization_id", "GET"),
        "cldkctl_superadmin_balance_detail": ("/core/superadmin/balance/accumulated/:organization_id/:project_id", "GET"),
        "cldkctl_superadmin_billing_invoice_sme": ("/core/superadmin/balance/history/invoice/:organization_id", "GET"),
        "cldkctl_superadmin_billing_invoice_enterprise": ("/core/superadmin/invoice/:organization_id/:project_id", "GET"),
    }


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available tools."""
    try:
        tools = get_tool_definitions()
        print(f"Successfully loaded {len(tools)} tools.", file=sys.stderr)
        return tools
    except Exception as e:
        print(f"!!!!!!!! ERROR GETTING TOOL DEFINITIONS !!!!!!!!", file=sys.stderr)
        print(f"Exception: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return []


def format_response(data: Any) -> str:
    """Formats API response data for display."""
    if isinstance(data, dict) and data.get("error"):
        return f"❌ API Error: {data.get('message', 'Unknown error')}"
    return f"```json\n{json.dumps(data, indent=2)}\n```"


def validate_tool_params(tool_name, arguments):
    from mcp_cldkctl.tool_param_map import TOOL_PARAM_MAP
    tool_info = TOOL_PARAM_MAP.get(f"mcp_cldkctl_{tool_name}")
    if not tool_info:
        return False, f"Unknown tool: {tool_name}"
    missing = []
    for param in tool_info["required_params"]:
        if param["name"] not in arguments or arguments[param["name"]] in (None, ""):
            missing.append(param["name"])
    if missing:
        return False, f"Missing required parameters: {', '.join(missing)}"
    return True, None


# Optional: tool schema discovery
def describe_tool(tool_name):
    tool_info = TOOL_PARAM_MAP.get(tool_name)
    if not tool_info:
        return {"error": "Unknown tool"}
    return tool_info


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[Content]:
    valid, error = validate_tool_params(name, arguments)
    if not valid:
        return [Content(type="text", text=error)]
    """Handle tool calls."""
    global current_base_url, environment_name
    
    try:
        # Handle authentication tools
        if name == "cldkctl_auth":
            token = arguments["token"]
            force_staging = arguments.get("force_staging", False)
            if authenticate_with_token(token, force_staging):
                env_info = f" ({environment_name})" if environment_name != "production" else ""
                user_info = auth_cache.get('user_info', {})
                text = (
                    f"✅ Authentication successful{env_info}!\n\n"
                    f"User: {user_info.get('name', 'Unknown')}\n"
                    f"Role: {user_info.get('role', 'Unknown')}\n"
                    f"Organization: {user_info.get('organization_id', 'None')}\n"
                    f"Environment: {environment_name}\n"
                    f"Base URL: {current_base_url}"
                )
                return [TextContent(type="text", text=text)]
            else:
                return [TextContent(type="text", text="❌ Authentication failed.")]

        elif name == "cldkctl_switch_environment":
            env = arguments["environment"]
            if env in ["production", "staging"]:
                current_base_url = PRODUCTION_URL if env == "production" else STAGING_URL
                environment_name = env
                auth_cache.update({"jwt_token": None, "expires_at": None, "environment": env, "base_url": current_base_url})
                save_cache()
                text = f"✅ Switched to {environment_name} environment. You may need to re-authenticate."
            else:
                text = "❌ Invalid environment. Use 'production' or 'staging'."
            return [TextContent(type="text", text=text)]

        elif name == "cldkctl_status":
            status_text = f"**Environment Status**\n- **Environment:** {environment_name}\n- **Base URL:** {current_base_url}\n\n"
            if auth_cache.get("jwt_token"):
                expires_at = datetime.fromisoformat(auth_cache["expires_at"]) if auth_cache["expires_at"] else None
                status_text += f"**Authentication Status**\n- **Status:** ✅ Authenticated\n"
                status_text += f"- **User:** {auth_cache.get('user_info', {}).get('name', 'Unknown')}\n"
                if expires_at:
                    status_text += f"- **Token Expires:** {expires_at.strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                status_text += f"**Authentication Status**\n- **Status:** ❌ Not authenticated"
            return [TextContent(type="text", text=status_text)]

        # Handle profile management tools
        elif name == "cldkctl_profile_detail":
            response = make_authenticated_request("GET", "/core/user/profile")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_update_profile":
            user_id = arguments["user_id"]
            profile_data = arguments["profile_data"]
            response = make_authenticated_request("PUT", f"/core/user/organization/profile/member/{user_id}", data=profile_data)
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_change_password":
            response = make_authenticated_request("POST", "/core/user/change-password", data={"old_password": arguments["old_password"], "new_password": arguments["new_password"]})
            return [TextContent(type="text", text=format_response(response))]

        # Handle project management tools
        elif name == "cldkctl_project_list":
            response = make_authenticated_request("GET", "/core/user/organization/projects/byOrg")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_project_detail":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/core/user/project/detail/{project_id}")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_update_project":
            project_id = arguments["project_id"]
            project_data = arguments["project_data"]
            response = make_authenticated_request("PUT", f"/core/user/projects/{project_id}", data=project_data)
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_check_before_delete_project":
            project_id = arguments["project_id"]
            response = make_authenticated_request("DELETE", f"/core/user/checking/projects/{project_id}")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_delete_project":
            project_id = arguments["project_id"]
            response = make_authenticated_request("DELETE", f"/core/user/projects/{project_id}")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_project_r_quota_post":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/mid/billing/projectdekagpu/quota/{project_id}")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_project_r_quota_pre":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/mid/billing/projectflavorgpu/project/{project_id}")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_balance_detail":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/core/balance/accumulated/{project_id}")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_payment_history":
            response = make_authenticated_request("GET", "/core/payment/history")
            return [TextContent(type="text", text=format_response(response))]

        # Handle organization management tools
        elif name == "cldkctl_org_detail":
            response = make_authenticated_request("GET", "/core/user/organization")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_org_edit":
            organization_id = arguments["organization_id"]
            org_data = arguments["org_data"]
            response = make_authenticated_request("PUT", f"/core/user/organization/edit/{organization_id}", data=org_data)
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_org_members":
            response = make_authenticated_request("GET", "/core/user/organization/member")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_org_member_add":
            member_data = arguments["member_data"]
            response = make_authenticated_request("POST", "/core/user/organization/member", data=member_data)
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_org_member_edit":
            user_id = arguments["user_id"]
            member_data = arguments["member_data"]
            response = make_authenticated_request("PUT", f"/core/user/organization/member/{user_id}", data=member_data)
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_org_member_delete":
            user_id = arguments["user_id"]
            response = make_authenticated_request("DELETE", f"/core/user/organization/member/{user_id}")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_org_member_activate":
            user_id = arguments["user_id"]
            response = make_authenticated_request("PUT", f"/core/user/manageuser/active/{user_id}")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_org_member_deactivate":
            user_id = arguments["user_id"]
            response = make_authenticated_request("PUT", f"/core/user/manageuser/deactive/{user_id}")
            return [TextContent(type="text", text=format_response(response))]

        elif name == "cldkctl_org_member_resend_invitation":
            user_id = arguments["user_id"]
            response = make_authenticated_request("POST", f"/core/superadmin/manageuser/resend-verified/{user_id}")
            return [TextContent(type="text", text=format_response(response))]

        # Balance & Billing tools
        elif name == "cldkctl_billing_daily_cost":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/core/billing/v2/daily-cost/{project_id}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_billing_monthly_cost":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/core/billing/monthly-cost/total-billed/{project_id}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_billing_history":
            data = {}
            if "project_id" in arguments:
                data["project_id"] = arguments["project_id"]
            if "start_date" in arguments:
                data["start_date"] = arguments["start_date"]
            if "end_date" in arguments:
                data["end_date"] = arguments["end_date"]
            response = make_authenticated_request("POST", "/core/billing/v2/history", data=data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_billing_invoice_sme":
            response = make_authenticated_request("GET", "/core/balance/history/invoice")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_billing_invoice_sme_detail":
            invoice_id = arguments["invoice_id"]
            response = make_authenticated_request("GET", f"/core/balance/history/invoice/detail/{invoice_id}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_billing_invoice_enterprise":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/core/billing/invoice/{project_id}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_billing_invoice_enterprise_detail":
            invoice_id = arguments["invoice_id"]
            response = make_authenticated_request("GET", f"/core/billing/v2/invoice/detail/{invoice_id}")
            return [TextContent(type="text", text=format_response(response))]

        # Kubernetes Core Tools
        elif name == "cldkctl_k8s_pods":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            response = make_authenticated_request("GET", f"/core/k8s/pods?project_id={project_id}&namespace={namespace}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_pod_create":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            pod_data = arguments["pod_data"]
            response = make_authenticated_request("POST", f"/core/k8s/pods?project_id={project_id}&namespace={namespace}", data=pod_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_pod_edit":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            pod_data = arguments["pod_data"]
            response = make_authenticated_request("PUT", f"/core/k8s/pods/{project_id}/{namespace}/{name}", data=pod_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_pod_delete":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            response = make_authenticated_request("DELETE", f"/core/k8s/pods/{project_id}/{namespace}/{name}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_pod_console":
            project_id = arguments["project_id"]
            name = arguments["name"]
            response = make_authenticated_request("GET", f"/core/k8s/pods/{project_id}/{name}/console")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_pod_console_token":
            pod_name = arguments["pod_name"]
            namespace = arguments["namespace"]
            response = make_authenticated_request("GET", f"/core/k8s/pods/{pod_name}/{namespace}/console-token")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_deployments":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            response = make_authenticated_request("GET", f"/core/k8s/deployments?project_id={project_id}&namespace={namespace}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_deployment_create":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            deployment_data = arguments["deployment_data"]
            response = make_authenticated_request("POST", f"/core/k8s/deployments?project_id={project_id}&namespace={namespace}", data=deployment_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_deployment_edit":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            deployment_data = arguments["deployment_data"]
            response = make_authenticated_request("PUT", f"/core/k8s/deployments/{project_id}/{namespace}/{name}", data=deployment_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_deployment_delete":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            response = make_authenticated_request("DELETE", f"/core/k8s/deployments/{project_id}/{namespace}/{name}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_services":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            response = make_authenticated_request("GET", f"/core/k8s/services?project_id={project_id}&namespace={namespace}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_service_create":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            service_data = arguments["service_data"]
            response = make_authenticated_request("POST", f"/core/k8s/services?project_id={project_id}&namespace={namespace}", data=service_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_service_edit":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            service_data = arguments["service_data"]
            response = make_authenticated_request("PUT", f"/core/k8s/services/{project_id}/{namespace}/{name}", data=service_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_service_delete":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            response = make_authenticated_request("DELETE", f"/core/k8s/services/{project_id}/{namespace}/{name}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_configmaps":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            response = make_authenticated_request("GET", f"/core/k8s/configmaps?project_id={project_id}&namespace={namespace}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_k8s_secrets":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            response = make_authenticated_request("GET", f"/core/k8s/secrets?project_id={project_id}&namespace={namespace}")
            return [TextContent(type="text", text=format_response(response))]

        # Virtual Machines Tools
        elif name == "cldkctl_vm_list":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/core/vm/list?project_id={project_id}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_vm_detail":
            vm_id = arguments["vm_id"]
            response = make_authenticated_request("GET", f"/core/vm/{vm_id}")
            return [TextContent(type="text", text=format_response(response))]

        # Registry Tools
        elif name == "cldkctl_registry_list":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/core/registry/list?project_id={project_id}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_registry_repositories":
            registry_id = arguments["registry_id"]
            response = make_authenticated_request("GET", f"/core/registry/{registry_id}/repositories")
            return [TextContent(type="text", text=format_response(response))]

        # Notebooks Tools
        elif name == "cldkctl_notebook_list":
            random_string = arguments["random_string"]
            response = make_authenticated_request("GET", f"/core/notebook/list?random_string={random_string}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_notebook_create":
            name = arguments["name"]
            project_id = arguments["project_id"]
            image = arguments["image"]
            cpu = arguments["cpu"]
            memory = arguments["memory"]
            response = make_authenticated_request("POST", "/core/notebook", data={
                "name": name,
                "project_id": project_id,
                "image": image,
                "cpu": cpu,
                "memory": memory
            })
            return [TextContent(type="text", text=format_response(response))]

        # Vouchers Tools
        elif name == "cldkctl_voucher_list":
            random_string = arguments["random_string"]
            response = make_authenticated_request("GET", f"/core/voucher/list?random_string={random_string}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_voucher_apply":
            voucher_code = arguments["voucher_code"]
            response = make_authenticated_request("POST", "/core/voucher/apply", data={"voucher_code": voucher_code})
            return [TextContent(type="text", text=format_response(response))]

        # Tokens Tools
        elif name == "cldkctl_token_list":
            random_string = arguments["random_string"]
            response = make_authenticated_request("GET", f"/core/token/list?random_string={random_string}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_token_create":
            name = arguments["name"]
            expiration_days = arguments["expiration_days"]
            response = make_authenticated_request("POST", "/core/token", data={
                "name": name,
                "expiration_days": expiration_days
            })
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_token_delete":
            token_id = arguments["token_id"]
            response = make_authenticated_request("DELETE", f"/core/token/{token_id}")
            return [TextContent(type="text", text=format_response(response))]

        # Audit Tools
        elif name == "cldkctl_audit_logs":
            random_string = arguments["random_string"]
            response = make_authenticated_request("GET", f"/core/audit/logs?random_string={random_string}")
            return [TextContent(type="text", text=format_response(response))]

        # Registry Artifacts Tools
        elif name == "cldkctl_registry_artifact_list":
            random_string = arguments["random_string"]
            response = make_authenticated_request("GET", f"/core/registry/artifact/list?random_string={random_string}")
            return [TextContent(type="text", text=format_response(response))]

        # Login tool
        elif name == "cldkctl_login":
            payload = arguments["payload"]
            response = make_authenticated_request("POST", "/core/user/login", data=payload)
            return [TextContent(type="text", text=format_response(response))]

        # Organization Management endpoints
        elif name == "cldkctl_org_role_list":
            response = make_authenticated_request("GET", "/core/user/organization/role")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_org_role_detail":
            role_id = arguments["role_id"]
            response = make_authenticated_request("GET", f"/core/user/organization/role/{role_id}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_org_role_edit":
            role_id = arguments["role_id"]
            role_data = arguments["role_data"]
            response = make_authenticated_request("PUT", f"/core/user/organization/role/{role_id}", data=role_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_org_role_delete":
            role_id = arguments["role_id"]
            response = make_authenticated_request("DELETE", f"/core/user/organization/role/{role_id}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_org_role_add":
            role_data = arguments["role_data"]
            response = make_authenticated_request("POST", "/core/user/organization/role", data=role_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_voucher_claim":
            claim_data = arguments["claim_data"]
            response = make_authenticated_request("POST", "/core/user/voucher-credit/claim", data=claim_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_voucher_claimed_list":
            response = make_authenticated_request("GET", "/core/user/voucher-credit/claimed")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_voucher_trial_claimed_list":
            response = make_authenticated_request("GET", "/core/user/voucher/claimed")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_audit_log":
            response = make_authenticated_request("GET", "/core/api/v1.1/user/activity/sp/get-auditlog")
            return [TextContent(type="text", text=format_response(response))]

        # --- END CONTINUATION OF FULL AUTO-GENERATED TOOL STUBS ---
        elif name == "cldkctl_kube_dashboard":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/core/user/projects/{project_id}/vcluster/dashboard")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_kubeconfig":
            project_id = arguments["project_id"]
            response = make_authenticated_request("GET", f"/core/user/projects/{project_id}/vcluster/kubeconfig")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_get_pod":
            response = make_authenticated_request("GET", "/core/pods")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_create_pod":
            pod_data = arguments["pod_data"]
            response = make_authenticated_request("POST", "/core/pods", data=pod_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_edit_pod":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            pod_data = arguments["pod_data"]
            response = make_authenticated_request("PUT", f"/core/pods/{project_id}/{namespace}/{name}", data=pod_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_delete_pod":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            response = make_authenticated_request("DELETE", f"/core/pods/{project_id}/{namespace}/{name}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_console_pod":
            token = arguments["token"]
            response = make_authenticated_request("GET", f"/core/pods/console/{token}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_console_token_pod":
            console_data = arguments["console_data"]
            response = make_authenticated_request("POST", "/core/pods/console", data=console_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_get_deployment":
            response = make_authenticated_request("GET", "/core/deployment")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_create_deployment":
            deployment_data = arguments["deployment_data"]
            response = make_authenticated_request("POST", "/core/deployment", data=deployment_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_edit_deployment":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            deployment_data = arguments["deployment_data"]
            response = make_authenticated_request("PUT", f"/core/deployment/{project_id}/{namespace}/{name}", data=deployment_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_delete_deployment":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            response = make_authenticated_request("DELETE", f"/core/deployment/{project_id}/{namespace}/{name}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_get_daemonset":
            response = make_authenticated_request("GET", "/core/daemonset")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_create_daemonset":
            daemonset_data = arguments["daemonset_data"]
            response = make_authenticated_request("POST", "/core/daemonset", data=daemonset_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_edit_daemonset":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            daemonset_data = arguments["daemonset_data"]
            response = make_authenticated_request("PUT", f"/core/daemonset/{project_id}/{namespace}/{name}", data=daemonset_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_delete_daemonset":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            response = make_authenticated_request("DELETE", f"/core/daemonset/{project_id}/{namespace}/{name}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_get_statefulset":
            response = make_authenticated_request("GET", "/core/statefulsets")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_create_statefulset":
            statefulset_data = arguments["statefulset_data"]
            response = make_authenticated_request("POST", "/core/statefulsets", data=statefulset_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_edit_statefulset":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            statefulset_data = arguments["statefulset_data"]
            response = make_authenticated_request("PUT", f"/core/statefulsets/{project_id}/{namespace}/{name}", data=statefulset_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_delete_statefulset":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            response = make_authenticated_request("DELETE", f"/core/statefulsets/{project_id}/{namespace}/{name}")
            return [TextContent(type="text", text=format_response(response))]
        # --- CONTINUATION OF FULL AUTO-GENERATED TOOL STUBS ---
        elif name == "cldkctl_get_service":
            response = make_authenticated_request("GET", "/core/kubernetes/services")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_create_service":
            service_data = arguments["service_data"]
            response = make_authenticated_request("POST", "/core/kubernetes/services", data=service_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_edit_service":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            service_data = arguments["service_data"]
            response = make_authenticated_request("PUT", f"/core/kubernetes/services/{project_id}/{namespace}/{name}", data=service_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_delete_service":
            project_id = arguments["project_id"]
            namespace = arguments["namespace"]
            name = arguments["name"]
            response = make_authenticated_request("DELETE", f"/core/kubernetes/services/{project_id}/{namespace}/{name}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_get_persistent_volume":
            response = make_authenticated_request("GET", "/core/kubernetes/pv")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_create_persistent_volume":
            pv_data = arguments["pv_data"]
            response = make_authenticated_request("POST", "/core/kubernetes/pv", data=pv_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_edit_persistent_volume":
            project_id = arguments["project_id"]
            name = arguments["name"]
            pv_data = arguments["pv_data"]
            response = make_authenticated_request("PUT", f"/core/kubernetes/pv/{project_id}/{name}", data=pv_data)
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_delete_persistent_volume":
            project_id = arguments["project_id"]
            name = arguments["name"]
            response = make_authenticated_request("DELETE", f"/core/kubernetes/pv/{project_id}/{name}")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_get_pvc":
            response = make_authenticated_request("GET", "/core/kubernetes/pvc")
            return [TextContent(type="text", text=format_response(response))]
        elif name == "cldkctl_create_pvc":
            pvc_data = arguments["pvc_data"]
            response = make_authenticated_request("POST", "/core/kubernetes/pvc", data=pvc_data)

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        print(f"Error calling tool {name}: {e}", file=sys.stderr)
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def main():
    """Main function."""
    print("Initializing server...", file=sys.stderr)
    try:
        __version__ = metadata.version("mcp-cldkctl")
    except metadata.PackageNotFoundError:
        __version__ = "0.0.0-dev"

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="cldkctl",
                server_version=__version__,
                capabilities=server.get_capabilities(
                    notification_options=SimpleNotificationOptions(
                        prompts_changed=False,
                        resources_changed=False,
                        tools_changed=False,
                    ),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server shutting down.", file=sys.stderr)