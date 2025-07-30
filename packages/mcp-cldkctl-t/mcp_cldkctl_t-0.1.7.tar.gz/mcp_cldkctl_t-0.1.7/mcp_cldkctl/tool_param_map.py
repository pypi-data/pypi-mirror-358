TOOL_PARAM_MAP = {
    # --- Auth & Profile ---
    "mcp_cldkctl_cldkctl_login": {
        "endpoint": "/core/user/login",
        "method": "POST",
        "required_params": [
            {"name": "username", "type": "string", "desc": "User's login name"},
            {"name": "password", "type": "string", "desc": "User's password"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_profile_detail": {
        "endpoint": "/core/user/profile",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_update_profile": {
        "endpoint": "/core/user/organization/profile/member/:user_id",
        "method": "PUT",
        "required_params": [
            {"name": "user_id", "type": "string", "desc": "ID of the user to update"},
            {"name": "name", "type": "string", "desc": "Full name"},
            {"name": "email", "type": "string", "desc": "Email address"},
            {"name": "phone_number", "type": "string", "desc": "Phone number"},
            {"name": "address", "type": "string", "desc": "Address"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_change_password": {
        "endpoint": "/core/user/change-password",
        "method": "POST",
        "required_params": [
            {"name": "old_password", "type": "string", "desc": "Current password"},
            {"name": "new_password", "type": "string", "desc": "New password"},
        ],
        "optional_params": [],
    },
    # --- Project Management ---
    "mcp_cldkctl_cldkctl_project_list": {
        "endpoint": "/core/user/organization/projects/byOrg",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_project_detail": {
        "endpoint": "/core/user/project/detail/:project_id",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "ID of the project"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_update_project": {
        "endpoint": "/core/user/projects/:project_id",
        "method": "PUT",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "ID of the project"},
            {"name": "description", "type": "string", "desc": "New project description"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_check_before_delete_project": {
        "endpoint": "/core/user/checking/projects/:project_id",
        "method": "DELETE",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "ID of the project"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_delete_project": {
        "endpoint": "/core/user/projects/:project_id",
        "method": "DELETE",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "ID of the project"},
        ],
        "optional_params": [],
    },
    # --- Balance & Billing ---
    "mcp_cldkctl_cldkctl_balance_detail": {
        "endpoint": "/core/balance/accumulated/:project_id",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "ID of the project"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_payment_history": {
        "endpoint": "/core/payment/history",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_billing_daily_cost": {
        "endpoint": "/core/billing/v2/daily-cost/:project_id",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "ID of the project"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_billing_monthly_cost": {
        "endpoint": "/core/billing/monthly-cost/total-billed/:project_id",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "ID of the project"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_billing_history": {
        "endpoint": "/core/billing/monthly-cost/history",
        "method": "POST",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "ID of the project"},
            {"name": "start", "type": "string", "desc": "Start date (YYYY-MM-DD)"},
            {"name": "end", "type": "string", "desc": "End date (YYYY-MM-DD)"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_billing_invoice_sme": {
        "endpoint": "/core/balance/history/invoice",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_billing_invoice_sme_detail": {
        "endpoint": "/core/balance/history/invoice/detail/:invoice_id",
        "method": "GET",
        "required_params": [
            {"name": "invoice_id", "type": "string", "desc": "ID of the invoice"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_billing_invoice_enterprise": {
        "endpoint": "/core/billing/invoice/:project_id",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "ID of the project"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_billing_invoice_enterprise_detail": {
        "endpoint": "/core/billing/v2/invoice/detail/:invoice_id",
        "method": "GET",
        "required_params": [
            {"name": "invoice_id", "type": "string", "desc": "ID of the invoice"},
        ],
        "optional_params": [],
    },
    # --- Organization & Members ---
    "mcp_cldkctl_cldkctl_org_detail": {
        "endpoint": "/core/user/organization",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_org_members": {
        "endpoint": "/core/user/organization/member",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_org_member_add": {
        "endpoint": "/core/user/organization/member",
        "method": "POST",
        "required_params": [
            {"name": "user_id", "type": "string", "desc": "ID of the user to add"},
            {"name": "role_id", "type": "string", "desc": "Role ID to assign"},
            {"name": "project_id", "type": "string", "desc": "Project ID to assign"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_org_member_edit": {
        "endpoint": "/core/user/organization/member/:user_id",
        "method": "PUT",
        "required_params": [
            {"name": "user_id", "type": "string", "desc": "ID of the user to edit"},
            {"name": "role_id", "type": "string", "desc": "Role ID to assign"},
            {"name": "project_id", "type": "string", "desc": "Project ID to assign"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_org_member_delete": {
        "endpoint": "/core/user/organization/member/:user_id",
        "method": "DELETE",
        "required_params": [
            {"name": "user_id", "type": "string", "desc": "ID of the user to delete"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_org_role_list": {
        "endpoint": "/core/user/organization/role",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_org_role_add": {
        "endpoint": "/core/user/organization/role",
        "method": "POST",
        "required_params": [
            {"name": "name", "type": "string", "desc": "Role name"},
            {"name": "privileges", "type": "list", "desc": "List of privileges"},
        ],
        "optional_params": [],
    },
    # --- Kubernetes ---
    "mcp_cldkctl_cldkctl_k8s_pods": {
        "endpoint": "/core/pods",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_k8s_deployments": {
        "endpoint": "/core/deployment",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_k8s_services": {
        "endpoint": "/core/kubernetes/services",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_k8s_configmaps": {
        "endpoint": "/core/kubernetes/configmap",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_k8s_secrets": {
        "endpoint": "/core/kubernetes/secret",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
        ],
        "optional_params": [],
    },
    # --- VM Management ---
    "mcp_cldkctl_cldkctl_vm_list": {
        "endpoint": "/core/virtual-machine/list/all",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_vm_detail": {
        "endpoint": "/core/virtual-machine/detail-vm",
        "method": "POST",
        "required_params": [
            {"name": "vm_id", "type": "string", "desc": "ID of the VM"},
        ],
        "optional_params": [],
    },
    # --- Registry ---
    "mcp_cldkctl_cldkctl_registry_list": {
        "endpoint": "/core/dekaregistry/v2/registry",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_registry_repositories": {
        "endpoint": "/core/dekaregistry/v2/repository",
        "method": "GET",
        "required_params": [
            {"name": "registry_id", "type": "string", "desc": "Registry ID"},
        ],
        "optional_params": [],
    },
    # --- Notebook ---
    "mcp_cldkctl_cldkctl_notebook_list": {
        "endpoint": "/core/deka-notebook",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_notebook_create": {
        "endpoint": "/core/deka-notebook",
        "method": "POST",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "name", "type": "string", "desc": "Notebook name"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
            {"name": "image", "type": "string", "desc": "Image ID"},
            {"name": "cpu", "type": "string", "desc": "CPU amount"},
            {"name": "memory", "type": "string", "desc": "Memory size"},
            {"name": "storage", "type": "string", "desc": "Storage size"},
        ],
        "optional_params": [
            {"name": "gpu", "type": "string", "desc": "GPU amount (optional)"},
        ],
    },
    # --- Voucher ---
    "mcp_cldkctl_cldkctl_voucher_list": {
        "endpoint": "/core/user/voucher-credit/claimed",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_voucher_apply": {
        "endpoint": "/core/user/voucher-credit/claim",
        "method": "POST",
        "required_params": [
            {"name": "voucher_code", "type": "string", "desc": "Voucher code to apply"},
        ],
        "optional_params": [],
    },
    # --- Audit Log ---
    "mcp_cldkctl_cldkctl_audit_logs": {
        "endpoint": "/core/api/v1.1/user/activity/sp/get-auditlog",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    # --- Token Management ---
    "mcp_cldkctl_cldkctl_token_list": {
        "endpoint": "/core/cldkctl/token",
        "method": "GET",
        "required_params": [],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_token_create": {
        "endpoint": "/core/cldkctl/token",
        "method": "POST",
        "required_params": [
            {"name": "name", "type": "string", "desc": "Token name"},
            {"name": "expiration_days", "type": "integer", "desc": "Expiration in days"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_token_delete": {
        "endpoint": "/core/cldkctl/token/:token_id",
        "method": "DELETE",
        "required_params": [
            {"name": "token_id", "type": "string", "desc": "Token ID to delete"},
        ],
        "optional_params": [],
    },
    # --- More Kubernetes ---
    "mcp_cldkctl_cldkctl_k8s_pod_create": {
        "endpoint": "/core/pods",
        "method": "POST",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
            {"name": "spec", "type": "dict", "desc": "Pod spec (YAML/JSON)"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_k8s_pod_edit": {
        "endpoint": "/core/pods/:project_id/:namespace/:name",
        "method": "PUT",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
            {"name": "name", "type": "string", "desc": "Pod name"},
            {"name": "spec", "type": "dict", "desc": "Pod spec (YAML/JSON)"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_k8s_pod_delete": {
        "endpoint": "/core/pods/:project_id/:namespace/:name",
        "method": "DELETE",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
            {"name": "name", "type": "string", "desc": "Pod name"},
        ],
        "optional_params": [],
    },
    # --- More VM Management ---
    "mcp_cldkctl_cldkctl_vm_create": {
        "endpoint": "/core/virtual-machine",
        "method": "POST",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "name", "type": "string", "desc": "VM name"},
            {"name": "flavor", "type": "string", "desc": "Flavor ID"},
            {"name": "image", "type": "string", "desc": "Image ID"},
            {"name": "network", "type": "string", "desc": "Network ID"},
            {"name": "storage", "type": "string", "desc": "Storage size"},
        ],
        "optional_params": [
            {"name": "gpu", "type": "string", "desc": "GPU type (optional)"},
        ],
    },
    "mcp_cldkctl_cldkctl_vm_delete": {
        "endpoint": "/core/virtual-machine/delete",
        "method": "POST",
        "required_params": [
            {"name": "vm_id", "type": "string", "desc": "ID of the VM to delete"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_vm_reboot": {
        "endpoint": "/core/virtual-machine/reboot",
        "method": "POST",
        "required_params": [
            {"name": "vm_id", "type": "string", "desc": "ID of the VM to reboot"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_vm_turn_on": {
        "endpoint": "/core/virtual-machine/turn-on/vm",
        "method": "POST",
        "required_params": [
            {"name": "vm_id", "type": "string", "desc": "ID of the VM to turn on"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_vm_turn_off": {
        "endpoint": "/core/virtual-machine/turn-off/vm",
        "method": "POST",
        "required_params": [
            {"name": "vm_id", "type": "string", "desc": "ID of the VM to turn off"},
        ],
        "optional_params": [],
    },
    # --- More Registry ---
    "mcp_cldkctl_cldkctl_registry_detail": {
        "endpoint": "/core/dekaregistry/v2/registry/:registry_id",
        "method": "GET",
        "required_params": [
            {"name": "registry_id", "type": "string", "desc": "Registry ID"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_registry_overview": {
        "endpoint": "/core/dekaregistry/v2/registry/:registry_id/overview",
        "method": "GET",
        "required_params": [
            {"name": "registry_id", "type": "string", "desc": "Registry ID"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_registry_member_list": {
        "endpoint": "/core/dekaregistry/v2/member/:registry_id",
        "method": "GET",
        "required_params": [
            {"name": "registry_id", "type": "string", "desc": "Registry ID"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_registry_member_add": {
        "endpoint": "/core/dekaregistry/v2/member/:registry_id",
        "method": "POST",
        "required_params": [
            {"name": "registry_id", "type": "string", "desc": "Registry ID"},
            {"name": "user_id", "type": "string", "desc": "User ID to add"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_registry_member_delete": {
        "endpoint": "/core/dekaregistry/v2/member/:registry_id/detail/:member_id",
        "method": "DELETE",
        "required_params": [
            {"name": "registry_id", "type": "string", "desc": "Registry ID"},
            {"name": "member_id", "type": "string", "desc": "Member ID to delete"},
        ],
        "optional_params": [],
    },
    # --- More Notebook ---
    "mcp_cldkctl_cldkctl_notebook_delete": {
        "endpoint": "/core/deka-notebook/delete",
        "method": "POST",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "name", "type": "string", "desc": "Notebook name"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_notebook_update": {
        "endpoint": "/core/deka-notebook/yaml",
        "method": "PUT",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "name", "type": "string", "desc": "Notebook name"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
            {"name": "yaml", "type": "string", "desc": "Notebook YAML"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_notebook_start": {
        "endpoint": "/core/deka-notebook/start",
        "method": "POST",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "name", "type": "string", "desc": "Notebook name"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_notebook_stop": {
        "endpoint": "/core/deka-notebook/stop",
        "method": "POST",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
            {"name": "name", "type": "string", "desc": "Notebook name"},
            {"name": "namespace", "type": "string", "desc": "Namespace"},
        ],
        "optional_params": [],
    },
    # --- More Billing/Quota ---
    "mcp_cldkctl_cldkctl_project_r_quota_post": {
        "endpoint": "/mid/billing/projectdekagpu/quota/:project_id",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_project_r_quota_pre": {
        "endpoint": "/mid/billing/projectflavorgpu/project/:project_id",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
        ],
        "optional_params": [],
    },
    # --- More Token Management ---
    "mcp_cldkctl_cldkctl_token_update": {
        "endpoint": "/core/cldkctl/token/:token_id",
        "method": "PUT",
        "required_params": [
            {"name": "token_id", "type": "string", "desc": "Token ID to update"},
            {"name": "name", "type": "string", "desc": "New token name"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_token_regenerate": {
        "endpoint": "/core/cldkctl/token/regenerate/:token_id",
        "method": "POST",
        "required_params": [
            {"name": "token_id", "type": "string", "desc": "Token ID to regenerate"},
            {"name": "expiration_days", "type": "integer", "desc": "Expiration in days"},
        ],
        "optional_params": [],
    },
    # --- Miscellaneous ---
    "mcp_cldkctl_cldkctl_kube_dashboard": {
        "endpoint": "/core/user/projects/:project_id/vcluster/dashboard",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_kubeconfig": {
        "endpoint": "/core/user/projects/:project_id/vcluster/kubeconfig",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
        ],
        "optional_params": [],
    },
    "mcp_cldkctl_cldkctl_get_namespace": {
        "endpoint": "/core/user/projects/:project_id/vcluster/namespaces",
        "method": "GET",
        "required_params": [
            {"name": "project_id", "type": "string", "desc": "Project ID"},
        ],
        "optional_params": [],
    },
} 