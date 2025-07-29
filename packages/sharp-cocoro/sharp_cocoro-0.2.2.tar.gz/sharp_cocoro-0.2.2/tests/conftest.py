import pytest
from pathlib import Path
import re

TESTS_DIR = Path(__file__).parent
CASSETTES_DIR = TESTS_DIR / "cassettes"

# Create cassettes directory if it doesn't exist
CASSETTES_DIR.mkdir(exist_ok=True)


def scrub_string(string, replacement='REDACTED'):
    """Helper to sanitize strings containing sensitive data."""
    # Replace appSecret values
    string = re.sub(r'appSecret=[^&\s]+', f'appSecret={replacement}', string)
    # Replace keys in cloudlabs URLs
    string = re.sub(r'/clpf/key/[^/\s"]+', f'/clpf/key/{replacement}', string)
    # Replace JSESSIONID
    string = re.sub(r'JSESSIONID=[^;]+', f'JSESSIONID={replacement}', string)
    # Replace boxId with full URL pattern
    string = re.sub(r'"boxId":\s*"https://[^"]+/clpf/key/[^"]+"', f'"boxId":"{replacement}"', string)
    return string


@pytest.fixture(scope="module") 
def vcr_config():
    return {
        "cassette_library_dir": str(CASSETTES_DIR),
        "record_mode": "once",
        "match_on": ["method", "path"],
        "filter_headers": ["authorization", "cookie"],
        "filter_query_parameters": [("appSecret", "REDACTED")],
        "decode_compressed_response": True,
        "filter_post_data_parameters": [("terminalAppId", "REDACTED")],
        "before_record_request": lambda request: scrub_request(request),
        "before_record_response": lambda response: scrub_response(response),
    }


def scrub_request(request):
    """Scrub sensitive data from requests."""
    # Scrub URI
    request.uri = scrub_string(request.uri)
    # Scrub body
    if hasattr(request, 'body') and request.body:
        if isinstance(request.body, str):
            request.body = scrub_string(request.body)
        elif isinstance(request.body, bytes):
            request.body = scrub_string(request.body.decode()).encode()
    return request


def scrub_response(response):
    """Scrub sensitive data from responses."""
    # Scrub response body
    if 'body' in response and 'string' in response['body']:
        body = response['body']['string']
        if isinstance(body, bytes):
            response['body']['string'] = scrub_string(body.decode()).encode()
        else:
            response['body']['string'] = scrub_string(body)
    
    # Scrub Set-Cookie header
    if 'headers' in response and 'Set-Cookie' in response['headers']:
        response['headers']['Set-Cookie'] = [
            scrub_string(cookie) for cookie in response['headers']['Set-Cookie']
        ]
    
    return response


@pytest.fixture
def vcr_cassette_name(request):
    """Generate cassette name based on test name."""
    return f"{request.node.name}.yaml"