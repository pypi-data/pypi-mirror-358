import json
import logging
import os
from typing import Dict, Optional, Union
from urllib.parse import urlparse

from fabric.analytics.environment.base.context import (
    ArtifactContext,
    IContextProviderPlugin,
    InternalContext,
)

CONTEXT_FILE_PATH = "/home/trusted-service-user/.trident-context"
SPARK_CONF_PATH = "/opt/spark/conf/spark-defaults.conf"
CLUSTER_INFO_FILE_PATH = "/opt/health-agent/conf/cluster-info.json"

logger = logging.getLogger(__name__)

trident_context: Dict[str, str] = {}
trident_cluster_info: Dict[str, str] = {}


def get_spark_conf() -> Dict[str, str]:
    config = {}
    try:
        with open(SPARK_CONF_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    content = line.split(" ", 1)
                    if len(content) == 2:
                        config[content[0].strip()] = content[1].strip()
    except Exception:
        logger.exception("parse spark conf file fails")
    finally:
        return config


def reset_cached_context():
    global trident_context
    trident_context = {}


def safe_format(input_value: Union[str, bytes]) -> str:
    if isinstance(input_value, bytes):
        return input_value.decode("utf-8")  # or use the appropriate encoding
    return input_value


def get_fabric_context() -> Dict[str, str]:
    global trident_context
    if trident_context:
        return trident_context
    else:
        try:
            with open(CONTEXT_FILE_PATH, "r") as f:
                for line in f.readlines():
                    if len(line.split("=")) == 2:
                        k, v = line.split("=")
                        trident_context[k.strip()] = v.strip()
        except Exception:
            logger.warning("Error reading Fabric context file")

        try:
            spark_conf = get_spark_conf()
            trident_context.update(spark_conf)
        except Exception:
            logger.warning("Error reading token service config file")

        if "trident.onelake.endpoint" not in trident_context.keys():
            if "fs.defaultFS" in trident_context.keys():
                try:
                    url = trident_context.get("fs.defaultFS")
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc
                    domain = domain.split("@")[-1]  # type: ignore
                    trident_context["trident.onelake.endpoint"] = str(domain)
                except Exception:
                    logger.exception("malform fs.defaultFS")

        return trident_context


def get_cluster_info() -> Dict[str, str]:
    global trident_cluster_info
    if trident_cluster_info:
        return trident_cluster_info
    else:
        try:
            with open(CLUSTER_INFO_FILE_PATH, "r") as f:
                cluster_info = f.read()
                cluster_info_dict = json.loads(cluster_info)
                trident_cluster_info = cluster_info_dict.get('cluster_metadata', {})
                return trident_cluster_info
        except Exception:
            return {}


def workspace_pe_enabled() -> bool:
    return get_cluster_info().get("workspace-pe-enabled") == "true"


def get_mwc_workload_host() -> str:
    token_service_end_point = get_fabric_context().get(
        "trident.lakehouse.tokenservice.endpoint"
    )
    parsed_url = urlparse(token_service_end_point)
    return f"{safe_format(parsed_url.scheme)}://{safe_format(parsed_url.netloc)}/"


class NotebookContextProviderPlugin(IContextProviderPlugin):
    def __init__(self):
        self._mwc_workload_host = get_mwc_workload_host()
        return

    @classmethod
    def in_context(cls):
        return os.path.isfile("/home/trusted-service-user/.trident-context")

    @property
    def capacity_id(self) -> Optional[str]:
        return get_fabric_context().get("trident.capacity.id")

    @property
    def workspace_id(self) -> Optional[str]:
        return get_fabric_context().get("trident.artifact.workspace.id")

    @property
    def pbi_shared_host(self) -> Optional[str]:
        if not workspace_pe_enabled():
            return super().pbi_shared_host
        else:
            if self.workspace_id is None:
                return None
            ws_id = self.workspace_id.lower().replace('-', '')
            pbienv = self.internal_context.rollout_stage
            env_mark = pbienv if pbienv in ['daily', 'dxt', 'msit'] else ''
            host = f"https://{ws_id}.z{ws_id[:2]}.w.{env_mark}api.fabric.microsoft.com/"
            return host

    @property
    def onelake_endpoint(self) -> Optional[str]:
        return get_fabric_context().get("trident.onelake.endpoint")

    @property
    def mwc_workload_host(self) -> Optional[str]:
        if not workspace_pe_enabled():
            return self._mwc_workload_host
        else:
            if self.workspace_id is None:
                return None
            ws_id = self.workspace_id.lower().replace('-', '')
            pbienv = self.internal_context.rollout_stage
            env_mark = f'{pbienv}-' if pbienv in ['daily', 'dxt', 'msit'] else ''
            host = f"https://{ws_id}.z{ws_id[:2]}.{env_mark}c.fabric.microsoft.com/"
            return host

    @property
    def artifact_context(self) -> ArtifactContext:
        return ArtifactContext(
            artifact_id=get_fabric_context().get("trident.artifact.id"),
            attached_lakehouse_id=get_fabric_context().get("trident.lakehouse.id"),
            attached_lakehouse_workspace_id=get_fabric_context().get(
                "trident.workspace.id"
            ),
            artifact_type=get_fabric_context().get("trident.artifact.type"),
        )

    @property
    def internal_context(self) -> InternalContext:
        return InternalContext(get_fabric_context().get("spark.trident.pbienv"))
