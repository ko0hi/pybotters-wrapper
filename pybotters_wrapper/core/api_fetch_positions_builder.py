from .api_fetch_positions import (
    PositionsFetchAPI,
    PositionsFetchAPIResponse,
    PositionsFetchAPIGenerateEndpointParameters,
    PositionsFetchAPITranslateParametersParameters,
    PositionsFetchAPIWrapResponseParameters,
)

from .api_fetch_builder import FetchAPIBuilder


class PositionsFetchAPIBuilder(
    FetchAPIBuilder[
        PositionsFetchAPI,
        PositionsFetchAPIGenerateEndpointParameters,
        PositionsFetchAPITranslateParametersParameters,
        PositionsFetchAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(PositionsFetchAPIBuilder, self).__init__(
            PositionsFetchAPI, PositionsFetchAPIResponse
        )
