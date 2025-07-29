import logging
import uuid
from typing import Any, Optional

from azure.core.credentials import TokenCredential
from azure.core.rest import HttpRequest, HttpResponse
from fabric.analytics.environment.context import FabricContext
from fabric.analytics.environment.credentials import FabricAnalyticsTokenCredentials
from fabric.analytics.rest._generated._client import BaseFabricRestClient
from fabric.analytics.rest.client_extension import _FabricRestAPIExtension
from fabric.analytics.rest.policies import CustomHttpLoggingPolicy

logger = logging.getLogger(__name__)


class FabricRestClient(BaseFabricRestClient, _FabricRestAPIExtension):
    def __init__(
        self,
        credential: Optional[TokenCredential] = None,
        context: FabricContext = None,
        **kwargs: Any,
    ):
        if not credential:
            credential = FabricAnalyticsTokenCredentials()

        if not context:
            context = FabricContext()

        if "http_logging_policy" not in kwargs:
            kwargs["http_logging_policy"] = CustomHttpLoggingPolicy(**kwargs)

        super().__init__(
            endpoint=context.pbi_shared_host,
            credential=credential,
            **kwargs,
        )

    def send_request(
        self, request: HttpRequest, *, stream: bool = False, **kwargs: Any
    ) -> HttpResponse:
        if "ActivityId" not in request.headers:
            request.headers["ActivityId"] = str(uuid.uuid4())

        try:
            return super().send_request(request=request, stream=stream, **kwargs)
        except Exception as e:
            logger.error(
                f"Exception {e} sending request {request.url}, ClientActivityId: {request.headers.get('ActivityId')}"
            )
            raise e
