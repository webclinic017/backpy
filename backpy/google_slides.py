import googleapiclient.discovery as discovery
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/presentations',
          'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = './ridian-97524-daaeace7256c.json'
DOCUMENT_ID = '1HVAZIKtove6EhLkd_5snA3GHcCJbbCMfhAuPbi50pJI'


def main():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    requests = [
        {
            'replaceAllText': {
                "containsText": {
                    "text": "<<portfolio_name>>",
                },
                "replaceText": "This is a test name",
            }

        }]
    service = discovery.build('slides', 'v1', credentials=creds)
    result = service.presentations().batchUpdate(presentationId=DOCUMENT_ID,
                                             body={'requests': requests}).execute()
    print(result)


if __name__ == "__main__":
    main()
