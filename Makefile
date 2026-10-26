TESTS_DIR := ./tests/scenarios

.PHONY: test-unit
test-unit:
	$(PYTHON) -m pytest $(TESTS_DIR) --test-mode=unit

KIND_CLUSTER ?= visa-k8s-test-e2e
HELM_REPO_URL ?= https://alba-synchrotron.github.io/visa-k8s-controller-helm
HELM_CHART ?= alba-synchrotron/visa-k8s-controller
K8S_TEST_NAMESPACE ?= visa-k8s-test-e2e

.PHONY: test
test:
	$(MAKE) test-unit
	$(MAKE) test-e2e

.PHONY: setup-test-e2e
setup-test-e2e: ## Set up a Kind cluster for e2e tests if it does not exist.
	@command -v $(KIND) >/dev/null 2>&1 || { \
		echo "Kind is not installed. Please install Kind manually."; \
		exit 1; \
	}
	@command -v helm >/dev/null 2>&1 || { \
		echo "Helm is not installed. Please install Helm manually."; \
		exit 1; \
	}
	@case "$$($(KIND) get clusters)" in \
		*"$(KIND_CLUSTER)"*) \
			echo "Kind cluster '$(KIND_CLUSTER)' already exists. Skipping creation." ;; \
		*) \
			echo "Creating Kind cluster '$(KIND_CLUSTER)'..."; \
			$(KIND) create cluster --name $(KIND_CLUSTER) || exit $$? ;; \
	esac

.PHONY: install-controller-chart
install-controller-chart: ## Uninstall and reinstall the Helm chart for e2e tests.
	@$(KUBECTL) config use-context kind-$(KIND_CLUSTER)
	@$(HELM) repo add repo $(HELM_REPO_URL) --force-update
	@$(HELM) repo update
	@$(HELM) uninstall visa-k8s-controller \
		--namespace $(K8S_TEST_NAMESPACE) \
		--ignore-not-found
	@$(HELM) install visa-k8s-controller $(HELM_CHART) \
		--namespace $(K8S_TEST_NAMESPACE) \
		--create-namespace

.PHONY: install-k8s-fixtures
install-k8s-fixtures:
	@$(KUBECTL) apply -f ./tests/integration/k8s_fixtures/ -n $(K8S_TEST_NAMESPACE)

.PHONY: test-e2e
test-e2e: setup-test-e2e install-controller-chart install-k8s-fixtures ## Run the e2e tests. Expected an isolated environment using Kind.
	K8S_NAMESPACE=$(K8S_TEST_NAMESPACE) \
	$(PYTHON) -m pytest $(TESTS_DIR) --test-mode=integration
	$(MAKE) cleanup-test-e2e

.PHONY: test-e2e-only
test-e2e-only: ## Run the e2e tests. Expected an isolated environment using Kind.
	K8S_NAMESPACE=$(K8S_TEST_NAMESPACE) \
	$(PYTHON) -m pytest $(TESTS_DIR) --test-mode=integration
	$(MAKE) cleanup-test-e2e

.PHONY: cleanup-test-e2e
cleanup-test-e2e:
	@$(KIND) delete cluster --name $(KIND_CLUSTER)


KUBECTL ?= kubectl
KIND ?= kind
HELM ?= helm
PYTHON ?= python3