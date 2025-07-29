"""Playground for Qlik Sense APIs exploration.

We connect to two APIs:
- Qlik Sense Repository Service (QRS) API
- Qlik Engine JSON API

We connect using the default Virtual Proxy Service (built into Qlik Sense Enterprise
default configuration, so no server-side configuration is required).

For auth, for the time being we use the Windows login method (NTLM), combined with the
"header" method of authenticating to these APIs.

In the case of the QRS API, we use the requests library to make HTTP requests, and use
the requests_ntlm library to handle NTLM authentication.

For the Qlik Engine JSON API, we use the websocket library to create a WebSocket
connection. To authenticate, we use a Qlik session ID that we get from calling a
QRS API endpoint (the endpoint doesn't matter, we only care that the server returns
a session ID in its response) using the method described above.
"""

from collections.abc import Generator
import json
import secrets
import ssl
import string
from typing import Any

import dlt
from dlt.extract.resource import DltResource
from dotenv import load_dotenv
from loguru import logger
import requests
from requests_ntlm import HttpNtlmAuth
import websocket


load_dotenv()

# # Disable SSL warnings (optional but recommended for self-signed certs)
requests.packages.urllib3.disable_warnings()


def get_qrs_session(ntlm_username: str, ntlm_password: str) -> requests.Session:
    session = requests.Session()
    # Probably a typo of xsrf; anyway, this is a random string of 16 alphanumeric chars.
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    xrfkey = "".join(secrets.choice(alphabet) for _ in range(16))
    headers = {
        "x-qlik-xrfkey": xrfkey,
        "User-Agent": "Windows",
    }
    session.auth = HttpNtlmAuth(ntlm_username, ntlm_password)
    session.headers = headers
    session.params = {"xrfkey": xrfkey}
    session.verify = False
    return session


def get_qlik_session_id(
    qrs_api_base_url: str, ntlm_username: str, ntlm_password: str
) -> str:
    """Retrieve Qlik session ID from the QRS API.

    Raises:
        ValueError: If session ID could not be retrieved.

    Returns:
        str: The Qlik session ID.
    """
    session = get_qrs_session(ntlm_username=ntlm_username, ntlm_password=ntlm_password)

    logger.debug("Retrieving Qlik session ID...")

    full_url = qrs_api_base_url + "/about"
    response = session.get(full_url)
    response.raise_for_status()
    session_id = session.cookies.get("X-Qlik-Session")

    if not session_id:
        msg = "Could not retrieve Qlik session ID. Perhaps Qlik API's logic changed?"
        raise ValueError(msg)

    logger.debug(f"Retrieved Qlik session ID: {session_id}.")
    return session_id


def get_socket(engine_api_url: str, session_id: str) -> websocket.WebSocket:
    """Create a WebSocket connection to the Qlik Engine JSON API.

    Args:
        session (requests.Session): An already configured requests Session object.

    Returns:
        websocket.WebSocket: An authenticated socket connection.
    """
    # Get a Qlik session ID from QRS API.
    # This way, we can (indirectly) use header auth in the Qlik Engine JSON API.
    headers = {"Cookie": f"X-Qlik-Session={session_id}"}

    # Connect to the Qlik Engine JSON API.
    logger.info("Creating a socket...")

    socket = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    socket.connect(engine_api_url, header=headers)
    on_authentication_msg = json.loads(socket.recv())
    logger.debug("On authentication message: ", on_authentication_msg)
    if on_authentication_msg["params"]["mustAuthenticate"]:
        msg = "Could not authenticate to Qlik Engine JSON API."
        msg += " Please ensure you're authenticated and provide a valid session ID."
        raise ValueError(msg)

    on_connected_msg = socket.recv()
    logger.debug("On connected message: ", on_connected_msg)

    return socket


def get(
    request: dict[str, Any],
    engine_api_url: str,
    session_id: str | None = None,
    socket: websocket.WebSocket | None = None,
) -> dict[str, Any]:
    """Retrieve a response from the Qlik Engine JSON API using WebSocket.

    Args:
        request (dict[str, Any]): The request body.
        engine_api_url (str): The URL of the Qlik Engine JSON API.
        session_id (str | None, optional): The ID of the Qlik session to use. Defaults
            to None.
        socket (websocket.WebSocket | None, optional): The socket to use. Defaults to
            None.

    Raises:
        ValueError: If neither a session nor a socket is provided, or if the socket is
            specified, but without its session.

    Returns:
        dict[str, Any] | None: The response from Qlik Engine JSON API.
    """
    if not session_id and not socket:
        msg = "Either `socket` or `session_id` must be provided."
        raise ValueError(msg)

    is_socket_externally_managed = bool(socket)
    if not is_socket_externally_managed:
        socket = get_socket(engine_api_url, session_id=session_id)

    logger.info(f"Calling '{request['method']}' method...")
    socket.send(json.dumps(request))
    response = json.loads(socket.recv())

    if not is_socket_externally_managed:
        socket.close()

    if machine_readable_error := response.get("error"):
        error_code = machine_readable_error["code"]
        error_message_short = machine_readable_error["message"]
        error_message_long = machine_readable_error["parameter"]
        human_readable_error = (
            f"Error {error_code} ('{error_message_short}'). " + error_message_long + "."
        )
        raise ValueError(human_readable_error)

    return response["result"]


@dlt.source
def qlik_sense(
    qrs_api_base_url: str = dlt.secrets.value,
    engine_api_url: str = dlt.secrets.value,
    ntlm_username: str = dlt.secrets.value,
    ntlm_password: str = dlt.secrets.value,
):
    # We use a single Qlik session for all requests.
    qlik_session_id = get_qlik_session_id(
        qrs_api_base_url, ntlm_username=ntlm_username, ntlm_password=ntlm_password
    )

    @dlt.resource(primary_key="qDocId", write_disposition="merge")
    def apps_engine(
        modified_at=dlt.sources.incremental(
            "modifiedDate", initial_value="2024-01-01T00:00:00Z"
        ),
    ) -> DltResource:
        """Get metadata about all apps in Qlik Sense from the Engine JSON API."""
        query = {
            "jsonrpc": "2.0",
            # "id": 1,
            "method": "GetDocList",
            "handle": -1,
            "params": [],
        }
        apps_info_nested = get(
            query, session_id=qlik_session_id, engine_api_url=engine_api_url
        )
        # Unnest and return only the modified apps.
        yield from [
            {
                "qDocId": app["qDocId"],
                "qDocName": app["qDocName"],
                "description": app["qMeta"]["description"],
                "createdDate": app["qMeta"]["createdDate"],
                "modifiedDate": app["qMeta"]["modifiedDate"],
                "stream": {
                    "id": app["qMeta"]["stream"]["id"]
                    if app["qMeta"].get("stream")
                    else None,
                    "name": app["qMeta"]["stream"]["name"]
                    if app["qMeta"].get("stream")
                    else None,
                },
            }
            for app in apps_info_nested["qDocList"]
            if app["qMeta"]["modifiedDate"] > modified_at.start_value
        ]

    @dlt.transformer(data_from=apps_engine, primary_key="id", write_disposition="merge")
    def app_details_qrs(apps: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
        app_id = apps["qDocId"]
        logger.debug(f"Retrieving app {app_id} details...")

        session = get_qrs_session(
            ntlm_username=ntlm_username, ntlm_password=ntlm_password
        )
        full_url = qrs_api_base_url + f"/app/{app_id}"
        response = session.get(full_url)
        response.raise_for_status()
        yield response.json()

    @dlt.transformer(data_from=apps_engine, primary_key="id", write_disposition="merge")
    def app_details_engine(
        apps: dict[str, Any],
    ) -> Generator[dict[str, Any], None, None]:
        app_id = apps["qDocId"]
        # These two requests are connected, so we need to perform them on the same
        # socket.
        socket = get_socket(engine_api_url, session_id=qlik_session_id)
        open_app_query = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "OpenDoc",
            "handle": -1,
            "params": {"qDocName": app_id},
        }
        lineage_query = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "GetLineage",
            "handle": 1,
            "params": {},
        }
        try:
            _ = get(open_app_query, socket=socket, engine_api_url=engine_api_url)
            lineage = get(lineage_query, socket=socket, engine_api_url=engine_api_url)[
                "qLineage"
            ]
        except Exception as e:
            msg = f"Failed retrieving lineage for app: {app_id}."
            raise ValueError(msg) from e
        finally:
            socket.close()

        # Add app ID to the table since it's not in the response.
        for row in lineage:
            row["id"] = app_id
            # row["models"] = extract_models(row)  # TODO
        yield lineage

    return [apps_engine, app_details_qrs, app_details_engine]


if __name__ == "__main__":
    for app in qlik_sense().add_limit(1):
        print(json.dumps(app, indent=4))
