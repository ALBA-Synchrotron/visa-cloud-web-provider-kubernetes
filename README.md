# VISA Cloud Web Provider Kubernetes


A REST API service implementing the cloud provider backend for the **VISA** (Virtual Infrastructure for Scientific Analysis) platform on top of **Kubernetes**.

This service acts as an abstraction bridge between the VISA Web application and a Kubernetes cluster. It translates standard VISA cloud management operations (Instances, Flavours, Images, Security Groups, Devices, and Metrics) into Custom Resources managed by the **VISA Kubernetes Controller** (`visa-k8s-controller`).

---

## Table of Contents

- [Architecture & Kubernetes Requirements](#architecture--kubernetes-requirements)
  - [VISA Kubernetes Controller](#visa-kubernetes-controller)
  - [Custom Resource Definitions (CRDs)](#custom-resource-definitions-crds)
  - [Cluster RBAC Requirements](#cluster-rbac-requirements)
- [Configuration & Environment Variables](#configuration--environment-variables)
  - [Environment Profiles](#environment-profiles)
  - [Configuration Reference](#configuration-reference)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Installation](#local-installation)
  - [Running the Application](#running-the-application)
  - [Running with Docker](#running-with-docker)
  - [Verifying Connectivity & Authentication](#verifying-connectivity--authentication)
- [Testing Guide](#testing-guide)
  - [Unit Tests (No Cluster Required)](#unit-tests-no-cluster-required)
  - [End-to-End (E2E) Integration Tests (Kind + Controller)](#end-to-end-e2e-integration-tests-kind--controller)
  - [Running All Tests](#running-all-tests)
- [API Reference](#api-reference)
  - [Authentication](#authentication)
  - [Healthcheck Endpoint](#healthcheck-endpoint)
  - [V1 API Endpoints](#v1-api-endpoints)
- [Makefile Targets](#makefile-targets)
- [Project Structure](#project-structure)
- [License](#license)

---

## Architecture & Kubernetes Requirements

### VISA Kubernetes Controller

This provider requires the [ALBA Synchrotron VISA Kubernetes Controller](https://github.com/ALBA-Synchrotron/visa-k8s-controller) deployed in your Kubernetes cluster. The controller watches custom resources and reconciles pods, storage, services, and sidecars corresponding to VISA virtual desktops.

- **API Group**: `cloudprovider.visa.k8s`
- **API Version**: `v1`
- **Helm Repository**: `https://alba-synchrotron.github.io/visa-k8s-controller-helm`
- **Helm Chart**: `alba-synchrotron/visa-k8s-controller`

To install the controller via Helm:

```bash
helm repo add alba-synchrotron https://alba-synchrotron.github.io/visa-k8s-controller-helm
helm repo update
helm install visa-k8s-controller alba-synchrotron/visa-k8s-controller \
  --namespace <target-namespace> \
  --create-namespace
```

### Custom Resource Definitions (CRDs)

The provider interacts with the following Custom Resources within the target namespace:

| CRD Kind | Plural Name | Purpose |
| :--- | :--- | :--- |
| `VISACloudInstance` | `visacloudinstances` | Represents a user virtual desktop instance, its desired/current state (`ACTIVE`, `STOPPED`), assigned flavour, image, security groups, owner, SSH/PAM public keys, and GUI settings. |
| `VISACloudFlavour` | `visacloudflavours` | Defines compute profiles (CPU cores/limits, RAM memory limits, disk size, and required sidecars such as Guacamole `guacd`). |
| `VISACloudImage` | `visacloudimages` | Defines available base container images (container registry reference, size, user shell, home templates). |
| `VISACloudSecurityGroup` | `visacloudsecuritygroups` | Defines security roles/groups attached to instances (e.g., `instance-admin`, `instance-sudoers`). |
| `VISACloudDevice` | `visaclouddevices` | Defines hardware/virtual accelerators and devices (`VIRTUAL_GPU`, `PCI_DEVICE`) assigned to instances or flavours. |
| `VISACloudSidecarConfig` | `visacloudsidecarconfigs` | Configures auxiliary containers (such as web streaming proxies or authentication agents) attached to instance pods. |

### Cluster RBAC Requirements

The provider needs a Kubernetes ServiceAccount or Kubeconfig context with permissions to manage custom resources in the target namespace (`K8S_NAMESPACE`):

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: visa-pods-test
  name: visa-cloud-web-provider-role
rules:
  - apiGroups: ["cloudprovider.visa.k8s"]
    resources:
      - visacloudinstances
      - visacloudinstances/status
      - visacloudflavours
      - visacloudimages
      - visacloudsecuritygroups
      - visaclouddevices
      - visacloudsidecarconfigs
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

---

## Configuration & Environment Variables

### Environment Profiles

The service supports three configuration modes controlled by `FLASK_ENV`:
- **`dev`** (Default): Uses local kubeconfig (`~/.kube/config`), `DEBUG` log level, development defaults.
- **`prod`**: Uses in-cluster ServiceAccount authentication (`/var/run/secrets/kubernetes.io/serviceaccount`), `INFO` log level.
- **`test`**: Used during test suite execution (mocked or integration cluster).

### Configuration Reference

All settings can be configured via environment variables (defined in `app/config.py`):

| Environment Variable | Description | Type / Options | Default (`dev`) | Default (`prod`) |
| :--- | :--- | :--- | :--- | :--- |
| `FLASK_ENV` | Application environment profile | `dev` \| `prod` \| `test` | `dev` | `prod` |
| `TESTING_MODE` | Test profile mode | `unit` \| `integration` | `unit` | `unit` |
| `AUTH_API_KEY` | Secret token used to authenticate incoming API requests | `string` | `rubber-duck` | `rubber-duck` |
| `AUTH_API_KEY_HEADER_NAME` | HTTP Header name inspected for the authentication token | `string` | `X-Auth-Token` | `X-Auth-Token` |
| `K8S_CONFIG_SOURCE` | Kubernetes configuration loader mechanism | `kubeconfig` \| `serviceaccount` | `kubeconfig` | `serviceaccount` |
| `K8S_CONFIG_FILE_PATH` | Path to kubeconfig file when using `kubeconfig` mode | `string` (path) | `~/.kube/config` | `~/.kube/config` |
| `K8S_NAMESPACE` | Kubernetes namespace where VISA CRD instances and resources reside | `string` | `visa-pods-test` | `visa-pods-test` |
| `LOG_LEVEL` | Python logging level | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` \| `CRITICAL` | `DEBUG` | `INFO` |
| `API_HOST` | Host address to bind the Flask HTTP server | `string` (IP/Host) | `0.0.0.0` | `0.0.0.0` |
| `API_PORT` | Port number to bind the Flask HTTP server | `integer` | `5000` | `5000` |
| `AUTO_START_INSTANCES_ON_CREATION` | Automatically set instance `desiredState: ACTIVE` when creating new instances | `boolean` (`True`/`False`) | `True` | `True` |
| `MAX_RAM_ALLOCATED` | Maximum aggregate RAM quota in Megabytes (MB) across all instances | `integer` | `51200` (50 GB) | `51200` |
| `MAX_INSTANCES_ALLOCATED` | Maximum number of simultaneously running instances quota | `integer` | `20` | `20` |
| `MAX_CORES_ALLOCATED` | Maximum aggregate CPU cores quota across all instances | `integer` | `15` | `15` |
| `IGNORE_SEC_GROUP_NOT_FOUND_ERRORS` | If `True`, ignoring non-existent security groups during instance creation instead of aborting | `boolean` (`True`/`False`) | `True` | `True` |
| `ENFORCE_MAX_QUOTAS` | Enforce instance/CPU/RAM quota validation during instance creation | `boolean` (`True`/`False`) | `True` | `True` |

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **pip** and **virtualenv**
- (Optional, for E2E tests) **Docker**, **Kind** (Kubernetes in Docker), **Helm 3**, and **kubectl**

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://git.cells.es/mis/visa/visa-cloud-web-provider-kubernetes.git
   cd visa-cloud-web-provider-kubernetes
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Ensure you have access to a Kubernetes cluster via `~/.kube/config` (or configure `K8S_CONFIG_FILE_PATH`), then launch the server:

```bash
# Option 1: Run entrypoint directly with Python
PYTHONPATH=. python app/run.py

# Option 2: Run using Flask CLI
FLASK_APP=app:create_app FLASK_ENV=dev flask run --host=0.0.0.0 --port=5000
```

### Running with Docker

Build the Docker image:
```bash
docker build -t visa-cloud-web-provider-kubernetes:latest .
```

Run container with custom environment variables:
```bash
docker run -d \
  --name visa-cloud-web-provider \
  -p 5000:5000 \
  -e FLASK_ENV=prod \
  -e AUTH_API_KEY="your-secure-token" \
  -e K8S_CONFIG_SOURCE=kubeconfig \
  -e K8S_NAMESPACE="visa-pods-prod" \
  -v ~/.kube/config:/root/.kube/config:ro \
  visa-cloud-web-provider-kubernetes:latest
```

### Verifying Connectivity & Authentication

Check service health (unauthenticated):
```bash
curl -i http://localhost:5000/healthz
```

Query the API (requires `X-Auth-Token` header):
```bash
curl -i -H "X-Auth-Token: rubber-duck" http://localhost:5000/v1/api/flavours
```

---

## Testing Guide

The project includes both fast **unit tests** (using mocked Kubernetes client responses) and **end-to-end integration tests** (using a local Kind cluster and the live `visa-k8s-controller`).

### Unit Tests (No Cluster Required)

Unit tests run entirely in-memory with mocked Kubernetes custom object responses. They execute in less than a second and require no Kubernetes cluster or external dependencies.

```bash
# Using Makefile
make test-unit

# Or directly with pytest
pytest ./tests/scenarios --test-mode=unit
```

### End-to-End (E2E) Integration Tests (Kind + Controller)

E2E tests spin up a local [Kind](https://kind.sigs.k8s.io/) Kubernetes cluster, deploy the `visa-k8s-controller` using Helm, apply test CRD manifests, execute the full API scenario test suite against live Kubernetes custom resources, and tear down the environment.

#### Automated All-in-One E2E Test

```bash
make test-e2e
```

#### Step-by-Step E2E Test Workflow

If you want to keep the test cluster running for iterative debugging:

1. **Create the Kind cluster**:
   ```bash
   make setup-test-cluster
   ```

2. **Deploy the controller & test fixtures**:
   ```bash
   make setup-test-e2e
   ```

3. **Run integration tests**:
   ```bash
   make test-e2e-only
   # Or directly:
   K8S_NAMESPACE=visa-k8s-test-e2e pytest ./tests/scenarios --test-mode=integration
   ```

4. **Clean up and delete Kind cluster**:
   ```bash
   make cleanup-test-e2e
   ```

### Running All Tests

```bash
make test
```

---

## API Reference

### Authentication

All endpoints under `/v1/api` require authentication using the API key specified in `AUTH_API_KEY`.

- **Header**: `X-Auth-Token: <AUTH_API_KEY>` (or customized via `AUTH_API_KEY_HEADER_NAME`)
- **Status on Failure**: `401 Unauthorized` (`{"error": "Invalid API key"}`)

### Healthcheck Endpoint

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/healthz` | No | Healthcheck probe returning `{"status": "ok"}` |

### V1 API Endpoints

All endpoints below are prefixed with `/v1/api`.

#### 1. Instances (`/v1/api/instances`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/v1/api/instances` | List all VISA cloud instances in the namespace |
| `GET` | `/v1/api/instances/identifiers` | List all instance ID numbers |
| `GET` | `/v1/api/instances/<instance_id>` | Get details for an instance by its ID or name |
| `GET` | `/v1/api/instances/<instance_id>/ip` | Get IP address for an instance |
| `POST` | `/v1/api/instances` | Create a new VISA cloud instance |
| `DELETE` | `/v1/api/instances/<instance_id>` | Delete an instance |
| `POST` | `/v1/api/instances/<instance_id>/start` | Start instance (sets `desiredState: ACTIVE`) |
| `POST` | `/v1/api/instances/<instance_id>/shutdown` | Stop instance (sets `desiredState: STOPPED`) |
| `POST` | `/v1/api/instances/<instance_id>/reboot` | Reboot instance (increments `rebootGeneration`) |
| `GET` | `/v1/api/instances/<instance_id>/security_groups` | Get security groups assigned to an instance |
| `POST` | `/v1/api/instances/<instance_id>/security_groups` | Add a security group to an instance |
| `POST` | `/v1/api/instances/<instance_id>/security_groups/remove` | Remove a security group from an instance |

##### Instance Creation Payload Example (`POST /v1/api/instances`)

```json
{
  "id": 101,
  "name": "analysis-desktop-101",
  "uid": "user-abc-123",
  "owner": "jdoe",
  "flavour": {
    "name": "flavour-standard-4core"
  },
  "image": {
    "name": "ubuntu-desktop-2204"
  },
  "securityGroups": [
    { "name": "instance-admin" }
  ],
  "associatedProposals": ["PROP-2026-001"],
  "instruments": ["BL01-BEAMLINE"],
  "keyboardLayout": "us",
  "screenHeight": "1080",
  "screenWidth": "1920",
  "bootCommand": "",
  "pamPublicKey": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
}
```

#### 2. Flavours (`/v1/api/flavours`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/v1/api/flavours` | List all available compute flavours |
| `GET` | `/v1/api/flavours/<id>` | Get details of a specific flavour |
| `GET` | `/v1/api/flavours/<id>/device_allocations` | Get device allocations for a flavour |

#### 3. Images (`/v1/api/images`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/v1/api/images` | List all available desktop images |
| `GET` | `/v1/api/images/<id>` | Get details of a specific image |

#### 4. Security Groups (`/v1/api/security_groups`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/v1/api/security_groups` | List all security groups |

#### 5. Devices (`/v1/api/devices`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/v1/api/devices` | List all devices |
| `GET` | `/v1/api/device/<device_type>/<device_identifier>` | Get a specific device by type and identifier |
| `GET` | `/v1/api/device_allocations` | List all device allocations |

#### 6. Metrics & Hypervisors (`/v1/api/metrics`, `/v1/api/hypervisor_*`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/v1/api/metrics` | Returns total cluster instance metrics and quota limits |
| `GET` | `/v1/api/hypervisor_inventories` | Hypervisor inventory metrics (CPU/RAM totals) |
| `GET` | `/v1/api/hypervisor_usages` | Hypervisor utilization metrics |
| `GET` | `/v1/api/hypervisor_allocations` | Hypervisor allocations |
| `GET` | `/v1/api/custom_resource_classes` | Custom resource classes supported |

---

## Makefile Targets

A `Makefile` is provided with targets for development and testing:

| Target | Description |
| :--- | :--- |
| `make test-unit` | Run all unit tests with mock Kubernetes provider |
| `make test-e2e` | Run complete end-to-end suite (Kind setup + Controller install + Tests + Teardown) |
| `make test-e2e-only` | Run integration tests against an already running test cluster |
| `make setup-test-cluster` | Create local Kind Kubernetes cluster named `visa-k8s-cluster` |
| `make setup-test-e2e` | Install `visa-k8s-controller` via Helm and load test CRD fixtures into Kind |
| `make cleanup-test-e2e` | Delete the local Kind cluster |
| `make test` | Run both unit tests and end-to-end tests |

---

## Project Structure

```
.
├── app/
│   ├── __init__.py                # Flask application factory
│   ├── auth.py                    # API key authentication middleware & decorators
│   ├── config.py                  # Environment-driven configuration (Dev/Prod/Test)
│   ├── run.py                     # Entry point script to start Flask server
│   ├── api/
│   │   ├── health.py              # /healthz endpoint
│   │   └── v1/                    # V1 REST API endpoints
│   │       ├── device.py          # /v1/api/devices endpoints
│   │       ├── flavour.py         # /v1/api/flavours endpoints
│   │       ├── hypervisor.py      # /v1/api/hypervisor_* endpoints
│   │       ├── image.py           # /v1/api/images endpoints
│   │       ├── instance.py        # /v1/api/instances endpoints & actions
│   │       ├── metrics.py         # /v1/api/metrics endpoints
│   │       ├── security_group.py  # /v1/api/security_groups endpoints
│   │       └── serializers/       # Request validation & JSON serialization schemas
│   ├── exceptions/                # Domain & Kubernetes error handling
│   ├── k8s/                       # Kubernetes client wrappers & CRD management logic
│   └── labels/                    # String constants, CRD names, and API group labels
├── tests/
│   ├── conftest.py                # Pytest configuration & fixture loader
│   ├── integration/               # Integration test fixtures & CRD YAML manifests
│   │   └── k8s_fixtures/          # Sample CRDs for flavours, images, instances, etc.
│   ├── scenarios/                 # Pytest scenarios (unit & integration tests)
│   └── unit/                      # Mocked fixtures for unit testing
├── Dockerfile                     # Production container image definition
├── Dockerfile-local-env           # Local test container environment
├── Makefile                       # Development & test automation targets
├── requirements.txt               # Python package dependencies
└── README.md                      # Project documentation
```

---

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0). See [LICENSE.md](LICENSE.md) for details.
