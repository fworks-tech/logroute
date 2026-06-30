from trips.application.dto import GeocodeSearchRequest, GeocodeSearchResponse


class GeocodeSearchUseCase:
    def __init__(self, geocoder, cache):
        self._geocoder = geocoder
        self._cache = cache

    def execute(self, request: GeocodeSearchRequest) -> GeocodeSearchResponse:
        cache_key = f"geocode_search_{request.query}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return GeocodeSearchResponse(results=cached)

        results = self._geocoder.search(request.query)
        self._cache.set(cache_key, results, 86400)
        return GeocodeSearchResponse(results=results)
