from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from fabric.analytics.environment.base.plugin import IPlugin
from fabric.analytics.environment.utils.docstring import inherit_docs

ARTIFACT_TYPE_NOTEBOOK = "SynapseNotebook"
ARTIFACT_TYPE_LAKEHOUSE = "Lakehouse"
ARTIFACT_TYPE_EXPERIMENT = "MLExperiment"
ARTIFACT_TYPE_REGISTERED_MODEL = "MLModel"
ARTIFACT_TYPE_SJD = "SparkJobDefinition"
ARTIFACT_TYPE_GENRIC = "Item"

# https://dev.azure.com/powerbi/Trident/_wiki/wikis/Trident.wiki/46148/Environments
SUPPORTED_FABRIC_REST_ENVIRONMENTS = {
    "onebox": "analysis.windows-int.net/powerbi/api/",
    "daily": "dailyapi.fabric.microsoft.com/",
    "edog": "powerbiapi.analysis-df.windows.net/",
    "dxt": "dxtapi.fabric.microsoft.com/",
    "msit": "msitapi.fabric.microsoft.com/",
    "msitbcdr": "msitapi.fabric.microsoft.com/",
    "prod": "api.fabric.microsoft.com/",
}


class ArtifactContext:
    def __init__(
        self,
        artifact_id: str,
        attached_lakehouse_id: Optional[str] = None,
        attached_lakehouse_workspace_id: Optional[str] = None,
        artifact_type: str = ARTIFACT_TYPE_NOTEBOOK,
    ):
        self.artifact_id = artifact_id
        self.attached_lakehouse_id = attached_lakehouse_id
        self.attached_lakehouse_workspace_id = attached_lakehouse_workspace_id
        self.artifact_type = artifact_type

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return f"{self.to_dict()}"


class InternalContext:
    def __init__(self, rollout_stage: str = "prod"):
        self.rollout_stage = rollout_stage

    def is_ppe(self) -> bool:
        return self.rollout_stage in ["cst", "edog", "int3"]

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return f"{self.to_dict()}"

    @property
    def rollout_stage(self) -> str:
        return self._rollout_stage

    @rollout_stage.setter
    def rollout_stage(self, rollout_stage: str):
        self._rollout_stage = rollout_stage.lower()


class IContextProvider(ABC):
    @property
    @abstractmethod
    def capacity_id(self) -> Optional[str]:
        """
        The id of capacity you operate on.
        """
        pass

    @property
    @abstractmethod
    def workspace_id(self) -> Optional[str]:
        """
        The id of workspace you operate on.
        """
        pass

    @property
    @abstractmethod
    def onelake_endpoint(self) -> Optional[str]:
        """
        The URL of the Onelake endpoint, start with https://
        """
        pass

    @property
    def pbi_shared_host(self) -> str:
        """
        The URL of the PowerBI shared host, start with https://
        """
        return "https://" + SUPPORTED_FABRIC_REST_ENVIRONMENTS.get(
            self.internal_context.rollout_stage, "api.fabric.microsoft.com/"
        )

    @property
    def mwc_workload_host(self) -> Optional[str]:
        """
        The URL of the MWC workload host, start with https://
        This is optional since connect to private api (mwc workload) is not a must
        """
        raise Exception("mwc endpoint unknown")

    @property
    def artifact_context(self) -> ArtifactContext:
        raise Exception("Notebook context unavailable")

    @property
    def internal_context(self) -> InternalContext:
        """
        Additional Internal Context
        """
        return InternalContext()


@inherit_docs
class IContextProviderPlugin(IContextProvider, IPlugin):
    pass
