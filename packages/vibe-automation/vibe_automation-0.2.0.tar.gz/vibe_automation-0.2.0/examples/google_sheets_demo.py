import logging
from typing import List, Any, Dict

from va import step, workflow

from va.clients.auth_connection_client import get_connection


from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from va.store.orby.orby_client import get_orby_client

CONNECTION_ID = "684b0d98620c471e89305924"


@workflow("Google Sheets Demo")
def main():
    orby_client = get_orby_client()
    oauth_token = None
    with step("Orby login"):
        orby_client.login()

    with step("Get connection to Google Sheets"):
        connection = get_connection(CONNECTION_ID)
        oauth_token = connection.token.access_token
        # if no oauth token, raise an error
        if not oauth_token:
            raise Exception("No OAuth token available")

    # Create google sheets and drive services
    credentials = Credentials(token=oauth_token)
    sheets_service = build("sheets", "v4", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)

    with step("List existing spreadsheets"):
        spreadsheets = list_spreadsheets(drive_service)
        if len(spreadsheets) > 0:
            logging.info(f"Found {len(spreadsheets)} spreadsheets")
            for spreadsheet in spreadsheets:
                logging.info(f"  - {spreadsheet['name']} (ID: {spreadsheet['id']})")
        else:
            logging.info("No spreadsheets found")

    with step("Create new spreadsheet"):
        spreadsheet = create_spreadsheet(sheets_service, "VA Demo Spreadsheet")
        spreadsheet_id = spreadsheet["spreadsheetId"]
        logging.info(f"Created spreadsheet: {spreadsheet}")

    with step("Write data to spreadsheet"):
        sample_data = [
            ["Name", "Age", "City"],
            ["Alice", 25, "New York"],
            ["Bob", 30, "San Francisco"],
            ["Charlie", 35, "Chicago"],
            ["Diana", 28, "Boston"],
        ]
        write_2d_array(sheets_service, spreadsheet_id, "Sheet1!A1", sample_data)

    with step("Read data from created spreadsheet"):
        data = read_range(sheets_service, spreadsheet_id, "Sheet1!A1:C5")
        logging.info(f"Read data: {data}")


def list_spreadsheets(drive_service) -> List[Dict[str, Any]]:
    try:
        results = drive_service.files().list().execute()

        files = results.get("files", [])
        logging.info(f"Found {len(files)} spreadsheets")
        for file in files[:5]:  # Log first 5
            logging.info(f"  - {file['name']} (ID: {file['id']})")
        return files

    except HttpError as error:
        logging.error(f"An error occurred listing spreadsheets: {error}")
        return []


def create_spreadsheet(service: build, title: str) -> Dict[str, Any]:
    payload = {
        "properties": {"title": title},
        "sheets": [{"properties": {"title": "Sheet1"}}],
    }
    response = service.spreadsheets().create(body=payload).execute()
    return response


def write_2d_array(
    service: build, spreadsheet_id: str, range_name: str, data: List[List[Any]]
) -> Dict[str, Any]:
    payload = {"values": data, "majorDimension": "ROWS"}
    params = {"valueInputOption": "RAW"}
    response = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=params["valueInputOption"],
            body=payload,
        )
        .execute()
    )
    return response


def read_range(service: build, spreadsheet_id: str, range_name: str) -> List[List[str]]:
    response = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    return response.get("values", [])


def share_spreadsheet(
    service: build, spreadsheet_id: str, email: str, role: str = "writer"
) -> Dict[str, Any]:
    payload = {"type": "user", "role": role, "emailAddress": email}
    response = (
        service.permissions().create(fileId=spreadsheet_id, body=payload).execute()
    )
    return response


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
