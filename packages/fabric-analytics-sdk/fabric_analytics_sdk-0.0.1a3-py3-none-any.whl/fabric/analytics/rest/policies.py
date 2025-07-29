import logging
import os
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union

from azure.core.credentials import TokenCredential
from azure.core.pipeline import PipelineRequest, PipelineResponse, policies
from azure.core.pipeline.policies import (
    BearerTokenCredentialPolicy,
    HttpLoggingPolicy,
    SansIOHTTPPolicy,
)
from azure.core.pipeline.policies._universal import HTTPRequestType, HTTPResponseType
from fabric.analytics.environment.base.credentials import (
    IFabricAnalyticsMWCCredential,
    MWCTokenRequestPayload,
)
from fabric.analytics.environment.base.policies import MWCTokenCredentialPolicy

from ..version import VERSION


class IFabricAPIConfiguration(ABC):
    def __init__(
        self, credential: Optional[Any], audience: Optional[str], **kwargs: Any
    ) -> None:
        kwargs.setdefault("sdk_moniker", "fabric-analytics-sdk/{}".format(VERSION))
        self._configure_base(**kwargs)
        self._config_custom(credential, audience, **kwargs)

    @abstractmethod
    def get_default_policies(self, **kwargs: Any) -> List[SansIOHTTPPolicy]:
        pass

    @abstractmethod
    def _config_custom(
        self, credential: Any, audience: Optional[str], **kwargs: Any
    ) -> SansIOHTTPPolicy:
        pass

    def _configure_base(self, **kwargs: Any) -> None:
        self.user_agent_policy = kwargs.get(
            "user_agent_policy"
        ) or policies.UserAgentPolicy(**kwargs)
        self.headers_policy = kwargs.get("headers_policy") or policies.HeadersPolicy(
            **kwargs
        )
        self.proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)
        self.logging_policy = kwargs.get(
            "logging_policy"
        ) or policies.NetworkTraceLoggingPolicy(
            **kwargs
        )  # Basic request/response without body/headers
        self.http_logging_policy = kwargs.get("http_logging_policy")
        self.custom_hook_policy = kwargs.get(
            "custom_hook_policy"
        ) or policies.CustomHookPolicy(**kwargs)
        self.redirect_policy = kwargs.get("redirect_policy") or policies.RedirectPolicy(
            **kwargs
        )  # Handles 301/302

        retry_total = kwargs.pop("retry_total", 3)
        timeout: int = kwargs.pop("timeout", 10)

        self.retry_policy = kwargs.get("retry_policy") or policies.RetryPolicy(
            retry_tota=retry_total, timeout=timeout, **kwargs
        )
        self.authentication_policy = kwargs.get("authentication_policy")


class FabricAPIConfiguration(
    IFabricAPIConfiguration
):  # pylint: disable=too-many-instance-attributes,name-too-long
    """Configuration for Fabric PBI Rest APIs."""

    def __init__(
        self,
        credential: Optional[TokenCredential],
        audience: Optional[str],
        **kwargs: Any,
    ) -> None:
        super().__init__(credential=credential, audience=audience, **kwargs)

    def _config_custom(
        self, credential: Optional[TokenCredential], audience: Optional[str], **kwargs
    ):
        if not self.http_logging_policy:
            self.http_logging_policy = CustomHttpLoggingPolicy(
                **kwargs
            )  # Log all with sensitive data redacted.
            self.http_logging_policy.allowed_header_names.add("RequestId")
            self.http_logging_policy.allowed_header_names.add("Requestid")
            self.http_logging_policy.allowed_header_names.add("requestId")
        if not self.authentication_policy:
            self.authentication_policy = BearerTokenCredentialPolicy(
                credential, audience
            )
        return

    def get_default_policies(self, **kwargs: Any) -> List[SansIOHTTPPolicy]:
        return [
            policies.RequestIdPolicy(**kwargs),  # This insert x-ms-client-request-id
            self.headers_policy,
            self.user_agent_policy,
            self.proxy_policy,
            policies.ContentDecodePolicy(**kwargs),  # Decode according to content type
            self.redirect_policy,
            self.retry_policy,
            self.authentication_policy,
            self.custom_hook_policy,
            self.logging_policy,
            policies.DistributedTracingPolicy(**kwargs),  # create spans for Azure calls
            policies.SensitiveHeaderCleanupPolicy(
                **kwargs
            ),  # clean up sensitive headers when redirects
            self.http_logging_policy,
        ]


class FabricMWCAPIConfiguration(
    IFabricAPIConfiguration
):  # pylint: disable=too-many-instance-attributes,name-too-long
    """Configuration for Fabric MWC Rest APIs."""

    def __init__(
        self,
        credential: Optional[Union[TokenCredential, IFabricAnalyticsMWCCredential]],
        audience: Optional[str],
        **kwargs: Any,
    ) -> None:
        super().__init__(credential=credential, audience=audience, **kwargs)

    def _config_custom(
        self,
        credential: Optional[Union[TokenCredential, IFabricAnalyticsMWCCredential]],
        audience: Optional[str],
        **kwargs,
    ):
        if not self.http_logging_policy:
            self.http_logging_policy = CustomHttpLoggingPolicy(**kwargs)
        if not self.authentication_policy:
            if hasattr(credential, "get_token"):
                self.authentication_policy = BearerTokenCredentialPolicy(
                    credential, audience
                )
            elif isinstance(credential, IFabricAnalyticsMWCCredential):
                if not kwargs.get("mwc_token_reqeust_payload") or not isinstance(
                    kwargs.get("mwc_token_reqeust_payload"), MWCTokenRequestPayload
                ):
                    raise Exception("Invalid mwc_token_request_payload")
                self.authentication_policy = MWCTokenCredentialPolicy(
                    credential=credential,
                    mwc_token_request_payload=kwargs.get("mwc_token_request_payload"),
                )
            elif credential is not None:
                raise Exception(f"{type(credential)} is not supported")
        return

    def get_default_policies(self, **kwargs: Any) -> List[SansIOHTTPPolicy]:
        return [
            policies.RequestIdPolicy(**kwargs),  # This insert x-ms-client-request-id
            self.headers_policy,
            self.user_agent_policy,
            self.proxy_policy,
            policies.ContentDecodePolicy(**kwargs),  # Decode according to content type
            self.redirect_policy,
            self.retry_policy,
            self.authentication_policy,
            self.custom_hook_policy,
            self.logging_policy,
            policies.DistributedTracingPolicy(**kwargs),  # create spans for Azure calls
            policies.SensitiveHeaderCleanupPolicy(
                **kwargs
            ),  # clean up sensitive headers when redirects
            self.http_logging_policy,
        ]


class CustomHttpLoggingPolicy(policies.HttpLoggingPolicy):
    DEFAULT_HEADERS_ALLOWLIST = policies.HttpLoggingPolicy.DEFAULT_HEADERS_ALLOWLIST | {
        "RequestId",
        "Requestid",
        "requestId",
        "x-ms-root-activity-id",
        "ActivityId",
    }

    def on_response(
        self,
        request: PipelineRequest[HTTPRequestType],
        response: PipelineResponse[HTTPRequestType, HTTPResponseType],
    ) -> None:
        http_response = response.http_response

        # Get logger in my context first (request has been retried)
        # then read from kwargs (pop if that's the case)
        # then use my instance logger
        # If on_request was called, should always read from context
        options = request.context.options
        logger = request.context.setdefault(
            "logger", options.pop("logger", self.logger)
        )

        try:
            if (
                response.http_response.status_code >= 400
                and response.http_response.status_code != 404
            ):
                logger.warning(
                    f"Error response returned, request: {request.http_request.url}, ClientActivityId {request.http_request.headers.get('ActivityId')}"
                )
                log_method = logger.warning
            else:
                log_method = logger.info

            if log_method == logger.info and not logger.isEnabledFor(logging.INFO):
                return

            multi_record = os.environ.get(HttpLoggingPolicy.MULTI_RECORD_LOG, False)
            if multi_record:
                log_method("Response status: %r", http_response.status_code)
                log_method("Response headers:")
                for res_header, value in http_response.headers.items():
                    value = self._redact_header(res_header, value)
                    log_method("    %r: %r", res_header, value)
                return
            log_string = "Response status: {}".format(http_response.status_code)
            log_string += "\nResponse headers:"
            for res_header, value in http_response.headers.items():
                value = self._redact_header(res_header, value)
                log_string += "\n    '{}': '{}'".format(res_header, value)
            log_method(log_string)
        except Exception as err:  # pylint: disable=broad-except
            logger.warning("Failed to log response: %s", repr(err))
