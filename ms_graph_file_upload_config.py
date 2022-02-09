config = {
        "authority": "https://login.microsoftonline.com/SOME_UUID_VALUE", # this UUID is the Directory(tenant) ID, which you can grab from the app registration
        "client_id": "ANOTHER_UUID_VALUE",
        "secret": "CLIENT_SECRET",
        "endpoint": "https://graph.microsoft.com/v1.0/",
        "scope": "offline_access https://graph.microsoft.com/User.Read",
        "redirect_uri": "https://localhost:8443/test",
        "grant_type": "authorization_code",
        "drive_id": "DRIVE_ID", # in Sharepoint, go to ../_api/v2.0/drives to get the drive_id
        "folder": "/General/Folder/For/Uploads"
}
