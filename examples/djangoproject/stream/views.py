from django.http import HttpRequest, StreamingHttpResponse

from .components import streaming_table_page
from .items import generate_items


def stream(request: HttpRequest) -> StreamingHttpResponse:
    return StreamingHttpResponse(streaming_table_page(generate_items()))
