.DEFAULT_GOAL := help

PYTHON  ?= python3
KUBECTL ?= kubectl
KIND    ?= kind
HELM    ?= helm

TESTS_DIR ?= ./tests/scenarios
K8S_FIXTURES_DIR ?= ./tests/integration/k8s_fixtures

KIND_CLUSTER       ?= visa-k8s-test-e2e
K8S_TEST_NAMESPACE ?= visa-k8s-test-e2e

HELM_REPO_NAME ?= alba-synchrotron
HELM_REPO_URL  ?= https://alba-synchrotron.github.io/visa-k8s-controller-helm
HELM_CHART     ?= alba-synchrotron/visa-k8s-controller
HELM_RELEASE   ?= visa-k8s-controller

.PHONY: help
.PHONY: test test-unit test-e2e test-e2e-only
.PHONY: setup-test-cluster setup-test-e2e
.PHONY: install-controller-chart install-k8s-fixtures
.PHONY: run-test-e2e cleanup-test-e2e

##@ General

help: ## Show available targets
	@awk 'BEGIN { FS = ":.*## " } \
		/^##@/ { \
			printf "\n%s\n", substr($$0, 5); \
			next \
		} \
		/^[a-zA-Z0-9_-]+:.*## / { \
			printf "  %-26s %s\n", $$1, $$2 \
		}' $(MAKEFILE_LIST)

##@ Tests

test: ## Run unit and end-to-end tests
	$(MAKE) test-unit
	$(MAKE) test-e2e

test-unit: ## Run unit tests
	$(PYTHON) -m pytest "$(TESTS_DIR)" --test-mode=unit

test-e2e: ## Provision the environment, run integration tests, and clean up
	@set -eu; \
		trap '$(MAKE) cleanup-test-e2e' EXIT; \
		$(MAKE) setup-test-e2e; \
		$(MAKE) run-test-e2e

test-e2e-only: ## Run integration tests against an existing environment
	$(MAKE) run-test-e2e

run-test-e2e: ## Run integration tests without provisioning or cleanup
	K8S_NAMESPACE="$(K8S_TEST_NAMESPACE)" \
		$(PYTHON) -m pytest "$(TESTS_DIR)" --test-mode=integration

##@ Kubernetes environment

setup-test-cluster: ## Create the Kind cluster if it does not exist
	@set -eu; \
		for tool in "$(KIND)" "$(KUBECTL)" "$(HELM)"; do \
			command -v "$$tool" >/dev/null 2>&1 || { \
				echo "Error: '$$tool' is not installed or not in PATH." >&2; \
				exit 1; \
			}; \
		done; \
		if $(KIND) get clusters | grep -Fxq "$(KIND_CLUSTER)"; then \
			echo "Kind cluster '$(KIND_CLUSTER)' already exists."; \
		else \
			echo "Creating Kind cluster '$(KIND_CLUSTER)'..."; \
			$(KIND) create cluster --name "$(KIND_CLUSTER)"; \
		fi

setup-test-e2e: setup-test-cluster install-controller-chart install-k8s-fixtures ## Provision the E2E environment without running tests

install-controller-chart: ## Install or upgrade the controller Helm release
	@$(KUBECTL) config use-context "kind-$(KIND_CLUSTER)"
	@$(HELM) repo add "$(HELM_REPO_NAME)" "$(HELM_REPO_URL)" --force-update
	@$(HELM) repo update
	@$(HELM) upgrade --install "$(HELM_RELEASE)" "$(HELM_CHART)" \
		--namespace "$(K8S_TEST_NAMESPACE)" \
		--create-namespace \
		--wait \
		--timeout 5m

install-k8s-fixtures: ## Apply Kubernetes integration-test fixtures
	@$(KUBECTL) apply \
		-f "$(K8S_FIXTURES_DIR)" \
		-n "$(K8S_TEST_NAMESPACE)"

cleanup-test-e2e: ## Delete the Kind cluster if it exists
	@if ! command -v "$(KIND)" >/dev/null 2>&1; then \
		echo "Kind is not installed; skipping cleanup."; \
	elif $(KIND) get clusters | grep -Fxq "$(KIND_CLUSTER)"; then \
		$(KIND) delete cluster --name "$(KIND_CLUSTER)"; \
	else \
		echo "Kind cluster '$(KIND_CLUSTER)' does not exist."; \
	fi