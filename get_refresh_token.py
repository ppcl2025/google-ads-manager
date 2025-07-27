from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json',
    scopes=["https://www.googleapis.com/auth/adwords"]
)
credentials = flow.run_local_server(port=56230, prompt='consent')
print("Refresh Token:", credentials.refresh_token)