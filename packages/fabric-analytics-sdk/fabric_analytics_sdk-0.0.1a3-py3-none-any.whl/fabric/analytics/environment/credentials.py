import contextvars
from contextlib import contextmanager
from typing import Any

from azure.core.credentials import AccessToken, TokenCredential
from azure.identity import ChainedTokenCredential, DefaultAzureCredential
from azure.identity._exceptions import CredentialUnavailableError
from fabric.analytics.environment.base.credentials import (
    IFabricAnalyticsTokenCredentialProviderPlugin,
)
from fabric.analytics.environment.plugin_provider import (
    BaseProvider,
    NoAvailableProvider,
)


class FabricAnalyticsTokenCredentials(ChainedTokenCredential):
    """
    Get Fabric Token Credential,
    **Priority:**
    **Value explicitly passed to __init__ > Values set via SetFabricAnalyticsDefaultTokenCredentials > Runtime default credential provided by plugin you installed**

    For example:

    The ```FabricAnalyticsTokenCredentials(fabric_analytics_credential=MyCustomCredential())``` always use the custom credential you passed in.

    In below code:
    ```
    with SetFabricAnalyticsDefaultTokenCredentials(credential=MyCustomCredentialA()):

        FabricAnalyticsTokenCredentials(fabric_analytics_credential=MyCustomCredentialB()) ## MyCustomCredentialB is used
        FabricAnalyticsTokenCredentials() ## MyCustomCredentialA is used

        with SetFabricAnalyticsDefaultTokenCredentials(credential=MyCustomCredentialC()):
            FabricAnalyticsTokenCredentials() ## MyCustomCredentialC is used

        FabricAnalyticsTokenCredentials() ## MyCustomCredentialA is used

    FabricAnalyticsTokenCredentials() ## Plugin provides default credential, throw failure is no plugin is registered
    ```
    """

    def __init__(self, fabric_analytics_credential=None, **kwargs: Any) -> None:
        fabric_analytics_credential = (
            fabric_analytics_credential
            if fabric_analytics_credential
            else FabricAnalyticsTokenCredentialProvider().provider_plugin
        )
        super().__init__(fabric_analytics_credential, DefaultAzureCredential(**kwargs))


context_credential = contextvars.ContextVar("context_credential", default=None)


@contextmanager
def SetFabricAnalyticsDefaultTokenCredentials(credential: TokenCredential):
    previous_credential = context_credential.get()
    context_credential.set(credential)
    try:
        yield
    finally:
        context_credential.set(previous_credential)


class FabricAnalyticsTokenCredentialProvider(
    BaseProvider[IFabricAnalyticsTokenCredentialProviderPlugin]
):
    """
    Provide Fabric Credential by selecting appropriate credential provider plugins.
    Custom provider selection and initialization are both lazy.
    If you want initialization happen immediately, call load().

    We are not directly extending TokenCredential to avoid metaclass conflict,
    And TokenCredential is runtime checkable
    """

    plugin_entry_point_name = "fabric_analytics.token_credential_provider"

    def __init__(self):
        BaseProvider.__init__(self)
        self._register_entrypoints()

    @property
    def provider_plugin(self) -> IFabricAnalyticsTokenCredentialProviderPlugin:
        try:
            if context_credential.get() is not None:
                return context_credential.get()
            return super().provider_plugin
        except NoAvailableProvider as e:
            raise CredentialUnavailableError(str(e))
