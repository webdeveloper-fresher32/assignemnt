from fastapi import HTTPException, status

class ClimateAnalyzerException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class ClimateDataFetchError(ClimateAnalyzerException):
    def __init__(self, detail: str = "Failed to fetch weather data from external climate source."):
        super().__init__(detail=detail, status_code=status.HTTP_502_BAD_GATEWAY)

class InvalidTimeRangeError(ClimateAnalyzerException):
    def __init__(self, detail: str = "Invalid time range specified. End year must be greater than or equal to start year."):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)

class InsufficientDataError(ClimateAnalyzerException):
    def __init__(self, detail: str = "Insufficient data points returned for statistical climate hazard evaluation."):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
