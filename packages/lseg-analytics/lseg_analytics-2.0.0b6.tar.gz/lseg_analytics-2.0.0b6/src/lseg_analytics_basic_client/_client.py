# coding=utf-8


from copy import deepcopy
from typing import Any

from corehttp.rest import HttpRequest, HttpResponse
from corehttp.runtime import PipelineClient, policies
from typing_extensions import Self

from ._configuration import AnalyticsAPIClientConfiguration
from ._serialization import Deserializer, Serializer
from .operations import (
    YieldBookRestOperations,
    calendarResourceOperations,
    calendarsResourceOperations,
    floatingRateIndexResourceOperations,
    floatingRateIndicesResourceOperations,
    fxForwardCurveResourceOperations,
    fxForwardCurvesResourceOperations,
    fxForwardResourceOperations,
    fxForwardsResourceOperations,
    fxSpotResourceOperations,
    fxSpotsResourceOperations,
    instrumentTemplateResourceOperations,
    instrumentTemplatesResourceOperations,
    irSwapResourceOperations,
    irSwapsResourceOperations,
)


class AnalyticsAPIClient:  # pylint: disable=client-accepts-api-version-keyword,too-many-instance-attributes
    """Analytic API to support channels workflows.

    :ivar calendars_resource: calendarsResourceOperations operations
    :vartype calendars_resource: analyticsapi.operations.calendarsResourceOperations
    :ivar calendar_resource: calendarResourceOperations operations
    :vartype calendar_resource: analyticsapi.operations.calendarResourceOperations
    :ivar fx_forward_curves_resource: fxForwardCurvesResourceOperations operations
    :vartype fx_forward_curves_resource: analyticsapi.operations.fxForwardCurvesResourceOperations
    :ivar fx_forward_curve_resource: fxForwardCurveResourceOperations operations
    :vartype fx_forward_curve_resource: analyticsapi.operations.fxForwardCurveResourceOperations
    :ivar fx_forwards_resource: fxForwardsResourceOperations operations
    :vartype fx_forwards_resource: analyticsapi.operations.fxForwardsResourceOperations
    :ivar fx_forward_resource: fxForwardResourceOperations operations
    :vartype fx_forward_resource: analyticsapi.operations.fxForwardResourceOperations
    :ivar fx_spots_resource: fxSpotsResourceOperations operations
    :vartype fx_spots_resource: analyticsapi.operations.fxSpotsResourceOperations
    :ivar fx_spot_resource: fxSpotResourceOperations operations
    :vartype fx_spot_resource: analyticsapi.operations.fxSpotResourceOperations
    :ivar yield_book_rest: YieldBookRestOperations operations
    :vartype yield_book_rest: analyticsapi.operations.YieldBookRestOperations
    :ivar instrument_templates_resource: instrumentTemplatesResourceOperations operations
    :vartype instrument_templates_resource:
     analyticsapi.operations.instrumentTemplatesResourceOperations
    :ivar instrument_template_resource: instrumentTemplateResourceOperations operations
    :vartype instrument_template_resource:
     analyticsapi.operations.instrumentTemplateResourceOperations
    :ivar ir_swaps_resource: irSwapsResourceOperations operations
    :vartype ir_swaps_resource: analyticsapi.operations.irSwapsResourceOperations
    :ivar ir_swap_resource: irSwapResourceOperations operations
    :vartype ir_swap_resource: analyticsapi.operations.irSwapResourceOperations
    :ivar floating_rate_indices_resource: floatingRateIndicesResourceOperations operations
    :vartype floating_rate_indices_resource:
     analyticsapi.operations.floatingRateIndicesResourceOperations
    :ivar floating_rate_index_resource: floatingRateIndexResourceOperations operations
    :vartype floating_rate_index_resource:
     analyticsapi.operations.floatingRateIndexResourceOperations
    :param endpoint: Service host. Default value is "https://api.analytics.lseg.com".
    :type endpoint: str
    """

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential
        self, endpoint: str = "https://api.analytics.lseg.com", **kwargs: Any
    ) -> None:
        _endpoint = "{endpoint}"
        self._config = AnalyticsAPIClientConfiguration(endpoint=endpoint, **kwargs)
        _policies = kwargs.pop("policies", None)
        if _policies is None:
            _policies = [
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                policies.ContentDecodePolicy(**kwargs),
                self._config.retry_policy,
                self._config.authentication_policy,
                self._config.logging_policy,
            ]
        self._client: PipelineClient = PipelineClient(endpoint=_endpoint, policies=_policies, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False
        self.calendars_resource = calendarsResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.calendar_resource = calendarResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_forward_curves_resource = fxForwardCurvesResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_forward_curve_resource = fxForwardCurveResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_forwards_resource = fxForwardsResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_forward_resource = fxForwardResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_spots_resource = fxSpotsResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.fx_spot_resource = fxSpotResourceOperations(self._client, self._config, self._serialize, self._deserialize)
        self.yield_book_rest = YieldBookRestOperations(self._client, self._config, self._serialize, self._deserialize)
        self.instrument_templates_resource = instrumentTemplatesResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.instrument_template_resource = instrumentTemplateResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.ir_swaps_resource = irSwapsResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.ir_swap_resource = irSwapResourceOperations(self._client, self._config, self._serialize, self._deserialize)
        self.floating_rate_indices_resource = floatingRateIndicesResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.floating_rate_index_resource = floatingRateIndexResourceOperations(
            self._client, self._config, self._serialize, self._deserialize
        )

    def send_request(self, request: HttpRequest, *, stream: bool = False, **kwargs: Any) -> HttpResponse:
        """Runs the network request through the client's chained policies.

        >>> from corehttp.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/dpcodegen/python/send_request

        :param request: The network request you want to make. Required.
        :type request: ~corehttp.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~corehttp.rest.HttpResponse
        """

        request_copy = deepcopy(request)
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        request_copy.url = self._client.format_url(request_copy.url, **path_format_arguments)
        return self._client.send_request(request_copy, stream=stream, **kwargs)  # type: ignore

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client.__exit__(*exc_details)
