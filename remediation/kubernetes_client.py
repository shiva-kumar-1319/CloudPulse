from typing import Optional, List
from shared.logging import get_logger

logger = get_logger("remediation-k8s-client")

try:
    from kubernetes import client as k8s_client, config as k8s_config
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False


class KubernetesRemediationClient:
    """
    RBAC-scoped Kubernetes API client for automated self-healing operations.
    Handles pod deletion (restarts) and deployment scaling.
    """
    def __init__(self, namespace: str = "cloudpulse"):
        self.namespace = namespace
        self.apps_api = None
        self.core_api = None
        self.in_cluster = False
        self.init_k8s_client()

    def init_k8s_client(self):
        if not K8S_AVAILABLE:
            logger.warning("Kubernetes Python library not installed. Running in mock fallback mode.")
            return

        try:
            # Attempt loading in-cluster config (Pod ServiceAccount)
            k8s_config.load_incluster_config()
            self.in_cluster = True
            logger.info("Loaded in-cluster Kubernetes configuration.")
        except Exception:
            try:
                # Attempt loading local kubeconfig (~/.kube/config)
                k8s_config.load_kube_config()
                self.in_cluster = True
                logger.info("Loaded local kubeconfig configuration.")
            except Exception as exc:
                logger.warning(f"Could not load Kubernetes cluster context ({exc}). Running in mock execution mode.")
                self.in_cluster = False
                return

        self.apps_api = k8s_client.AppsV1Api()
        self.core_api = k8s_client.CoreV1Api()

    def restart_pod(self, service_name: str) -> bool:
        """
        Restart service pod by deleting a targeted pod instance under the deployment.
        """
        logger.info(f"Initiating pod restart remediation for service: '{service_name}' in namespace: '{self.namespace}'")

        if not self.in_cluster or not self.core_api:
            logger.info(f"[MOCK EXECUTION] Successfully executed restart_pod for '{service_name}'. Target pod recycled.")
            return True

        try:
            label_selector = f"app={service_name}"
            pods = self.core_api.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=label_selector
            )

            if not pods.items:
                logger.warning(f"No active pods found matching selector '{label_selector}'")
                return False

            target_pod = pods.items[0].metadata.name
            logger.info(f"Deleting target pod '{target_pod}' to trigger replica replacement...")

            self.core_api.delete_namespaced_pod(
                name=target_pod,
                namespace=self.namespace
            )
            logger.info(f"Successfully deleted pod '{target_pod}'. K8s controller recreating fresh instance.")
            return True
        except Exception as err:
            logger.error(f"Failed to execute Kubernetes pod deletion for '{service_name}': {err}")
            return False

    def scale_deployment(self, service_name: str, target_replicas: int) -> bool:
        """
        Scale deployment replicas up or down.
        """
        logger.info(f"Initiating scale remediation for service '{service_name}' to {target_replicas} replicas")

        if not self.in_cluster or not self.apps_api:
            logger.info(f"[MOCK EXECUTION] Successfully scaled deployment '{service_name}' to {target_replicas} replicas.")
            return True

        try:
            body = {"spec": {"replicas": target_replicas}}
            self.apps_api.patch_namespaced_deployment_scale(
                name=service_name,
                namespace=self.namespace,
                body=body
            )
            logger.info(f"Successfully patched scale subresource for deployment '{service_name}' -> {target_replicas} replicas")
            return True
        except Exception as err:
            logger.error(f"Failed to scale deployment '{service_name}': {err}")
            return False
