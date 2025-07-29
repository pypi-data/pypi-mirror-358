import contextvars
import logging
from collections import namedtuple
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, Optional, cast

from fabric.analytics.environment.base.context import (
    ArtifactContext,
    IContextProvider,
    IContextProviderPlugin,
    InternalContext,
)
from fabric.analytics.environment.plugin_provider import BaseProvider
from fabric.analytics.environment.utils.docstring import inherit_docs

logger = logging.getLogger(__name__)


class FabricContext(IContextProvider):
    """
    Initialize Fabric Context,
    **Priority:**
    **Value explicitly passed > Values set via SetFabricDefaultContext > Runtime default values provided by plugin you installed**

    with SetFabricDefaultContext(workspace_id='aaa'):

        FabricContext(workspace_id='bbb').workspace_id  ## bbb
        FabricContext().workspace_id                    ## aaa

        with SetFabricDefaultContext(workspace_id='ccc'):
            FabricContext().workspace_id                ## ccc

        FabricContext().workspace_id                    ## aaa

    FabricContext().workspace_id ## Plugin provides default context, throw failure is no plugin is registered
    """

    def __init__(
        self,
        capacity_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        onelake_endpoint: Optional[str] = None,
        pbi_shared_host: Optional[str] = None,
        mwc_workload_host: Optional[str] = None,
        artifact_context: Optional[ArtifactContext] = None,
        internal_context: Optional[InternalContext] = None,
    ):
        self._capacity_id = capacity_id
        self._workspace_id = workspace_id
        self._onelake_endpoint = onelake_endpoint
        self._pbi_shared_host = pbi_shared_host
        self._mwc_workload_host = mwc_workload_host
        self._artifact_context = artifact_context
        self._internal_context = internal_context
        self._default_fabric_context = DefaultFabricContext()

    def to_dict(self) -> Dict[str, Any]:
        """Convert an object into a named tuple, including only properties."""

        # Get all attributes, including @property methods
        attributes = {
            attr: str(getattr(self, attr))
            for attr in dir(self)
            if not attr.startswith("__")  # Ignore dunder methods
            and not callable(getattr(self, attr, None))  # Ignore methods
            and isinstance(getattr(type(self), attr, None), property)
        }

        return attributes

    def __str__(self):
        return f"{self.to_dict()}"

    @property
    def capacity_id(self) -> Optional[str]:
        return self._capacity_id or self._default_fabric_context.capacity_id

    @capacity_id.setter
    def capacity_id(self, value: Optional[str]) -> None:
        self._capacity_id = value

    @property
    def workspace_id(self) -> Optional[str]:
        return self._workspace_id or self._default_fabric_context.workspace_id

    @workspace_id.setter
    def workspace_id(self, value: Optional[str]) -> None:
        self._workspace_id = value

    @property
    def onelake_endpoint(self) -> Optional[str]:
        return self._check_url(
            self._onelake_endpoint or self._default_fabric_context.onelake_endpoint
        )

    @onelake_endpoint.setter
    def onelake_endpoint(self, value: Optional[str]) -> None:
        self._onelake_endpoint = value

    @property
    def pbi_shared_host(self) -> Optional[str]:
        return self._check_url(
            self._pbi_shared_host or self._default_fabric_context.pbi_shared_host
        )

    @pbi_shared_host.setter
    def pbi_shared_host(self, value: Optional[str]) -> None:
        self._pbi_shared_host = value

    @property
    def mwc_workload_host(self) -> Optional[str]:
        return self._check_url(
            self._mwc_workload_host or self._default_fabric_context.mwc_workload_host
        )

    @mwc_workload_host.setter
    def mwc_workload_host(self, value: Optional[str]) -> None:
        self._mwc_workload_host = value

    @property
    def artifact_context(self) -> ArtifactContext:
        return self._artifact_context or self._default_fabric_context.artifact_context

    @artifact_context.setter
    def artifact_context(self, value: ArtifactContext) -> None:
        self._artifact_context = value

    @property
    def internal_context(self) -> InternalContext:
        return self._internal_context or self._default_fabric_context.internal_context

    @internal_context.setter
    def internal_context(self, value: InternalContext) -> None:
        self._internal_context = value

    def _check_url(self, url: Optional[str]) -> Optional[str]:
        """
        Make sure url start with http:// or https://
        """
        if url is None:
            return url
        try:
            if not url.lower().startswith("http"):
                url = "https://" + url
            return url
        except AttributeError as exc:
            raise ValueError("URL must be a string.") from exc


class DefaultFabricContext(IContextProvider):
    def __init__(self):
        self._context_provider = ContextProvider()

    @property
    def capacity_id(self) -> Optional[str]:
        if fabric_default_context_override.get():
            ctx = cast(StaticFabricContext, fabric_default_context_override.get())
            if ctx.capacity_id is not None:
                return ctx.capacity_id
        return self._context_provider.provider_plugin.capacity_id

    @property
    def workspace_id(self) -> Optional[str]:
        if fabric_default_context_override.get():
            ctx = cast(StaticFabricContext, fabric_default_context_override.get())
            if ctx.workspace_id is not None:
                return ctx.workspace_id
        return self._context_provider.provider_plugin.workspace_id

    @property
    def onelake_endpoint(self) -> Optional[str]:
        if fabric_default_context_override.get():
            ctx = cast(StaticFabricContext, fabric_default_context_override.get())
            if ctx.onelake_endpoint is not None:
                return ctx.onelake_endpoint
        return self._context_provider.provider_plugin.onelake_endpoint

    @property
    def pbi_shared_host(self) -> Optional[str]:
        if fabric_default_context_override.get():
            ctx = cast(StaticFabricContext, fabric_default_context_override.get())
            if ctx.pbi_shared_host is not None:
                return ctx.pbi_shared_host
        return self._context_provider.provider_plugin.pbi_shared_host

    @property
    def mwc_workload_host(self) -> Optional[str]:
        if fabric_default_context_override.get():
            ctx = cast(StaticFabricContext, fabric_default_context_override.get())
            if ctx.mwc_workload_host is not None:
                return ctx.mwc_workload_host
        return self._context_provider.provider_plugin.mwc_workload_host

    @property
    def artifact_context(self) -> ArtifactContext:
        if fabric_default_context_override.get():
            ctx = cast(StaticFabricContext, fabric_default_context_override.get())
            if ctx.artifact_context is not None:
                return ctx.artifact_context
        return self._context_provider.provider_plugin.artifact_context

    @property
    def internal_context(self) -> InternalContext:
        if fabric_default_context_override.get():
            ctx = cast(StaticFabricContext, fabric_default_context_override.get())
            if ctx.internal_context is not None:
                return ctx.internal_context
        return self._context_provider.provider_plugin.internal_context


@inherit_docs
class ContextProvider(BaseProvider[IContextProviderPlugin]):
    """
    Provide Fabric Context by selecting appropriate context provider plugins.
    Custom provider selection and initialization are both lazy.
    If you want initialization happen immediately, call load().
    """

    plugin_entry_point_name = "fabric_analytics.context_provider"

    def __init__(self):
        BaseProvider.__init__(self)

    @property
    def provider_plugin(self) -> IContextProvider:
        return super().provider_plugin


# This is overrideable
fabric_default_context_override: ContextVar["Optional[StaticFabricContext]"] = (
    contextvars.ContextVar("fabric_default_context_override", default=None)
)


class StaticFabricContext:
    def __init__(
        self,
        capacity_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        onelake_endpoint: Optional[str] = None,
        pbi_shared_host: Optional[str] = None,
        mwc_workload_host: Optional[str] = None,
        artifact_context: Optional[ArtifactContext] = None,
        internal_context: Optional[InternalContext] = None,
    ):
        self.capacity_id = capacity_id
        self.workspace_id = workspace_id
        self.onelake_endpoint = onelake_endpoint
        self.pbi_shared_host = pbi_shared_host
        self.mwc_workload_host = mwc_workload_host
        self.artifact_context = artifact_context
        self.internal_context = internal_context
        pass


@contextmanager
def SetFabricDefaultContext(
    capacity_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    onelake_endpoint: Optional[str] = None,
    pbi_shared_host: Optional[str] = None,
    mwc_workload_host: Optional[str] = None,
    artifact_context: Optional[ArtifactContext] = None,
    internal_context: Optional[InternalContext] = None,
):
    """
    This override context-local default fabirc context returned by DefaultFabricContext()
    """
    previous_context = fabric_default_context_override.get()
    fabric_default_context_override.set(
        StaticFabricContext(
            capacity_id=capacity_id,
            workspace_id=workspace_id,
            onelake_endpoint=onelake_endpoint,
            pbi_shared_host=pbi_shared_host,
            mwc_workload_host=mwc_workload_host,
            artifact_context=artifact_context,
            internal_context=internal_context,
        )
    )
    try:
        yield
    finally:
        fabric_default_context_override.set(previous_context)
