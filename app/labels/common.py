ALL_COOLIO: str = "Service is up and running"

# Initialization
INIT_APP: str = "Initializing application"
INIT_K8S: str = "Initializing Kubernetes"

# Authentication errors
ERR_API_AUTH_NOT_CONFIGURED: str = "API authentication is not configured"
ERR_INVALID_API_KEY: str = "Invalid or missing API key"

# Kubernetes errors
ERR_K8S_CONF_LOAD: str = "Error loading Kubernetes config"
ERR_K8S_CRD_NOT_FOUND: str = "VISA-k8s CRDs not found in current cluster configuration, check cluster and k8s client config"

# General errors
ERR_FETCHING_K8S_CRDS: str = "Error getting Kubernetes VISA-k8s API resources"
INVALID_PAYLOAD: str = "Request's payload is invalid"
CP_CREATION_QUOTA_EXCEEDED: str = "VISACloudInstance cannot be created as it will exceed max resource quota configured"

# General error suffixes and prefixes
NOT_FOUND_SFX: str = "not found"
NOT_FOUND_IN_SFX: str = "not found in"
ERR_LISTING_PFX: str = "Error listing"
ERR_STARTING_PFX: str = "Error starting"
ERR_STOPPING_PFX: str = "Error stopping"
ERR_CREATING_PFX: str = "Error creating"
ERR_UPDATING_PFX: str = "Error updating"
ERR_DELETING_PFX: str = "Error deleting"
ERR_RESTARTING_PFX: str = "Error restarting"

# Instances actions
MSG_START_INSTANCE: str = "Starting instance"
MSG_STOP_INSTANCE: str = "Stopping instance"
MSG_REBOOT_INSTANCE: str = "Rebooting instance"
MSG_SEC_GROUP_ADDED: str = "Security group added to instance"
MSG_SEC_GROUP_REMOVED: str = "Security group removed from instance"
MSG_INSTANCE_DELETED: str = "Instance deleted"
