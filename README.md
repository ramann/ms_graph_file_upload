# Microsoft Graph API File Upload
Recently, I needed a way to upload files to Microsoft SharePoint on a regular/ongoing basis. Below are my notes of how I used Microsoft's OAuth 2.0 authorization code flow (https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow) and the Microsoft Graph API (https://docs.microsoft.com/en-us/graph/api/driveitem-createuploadsession?view=graph-rest-1.0) to do this. Ideally, I'd have a service account for this and use the client credentials grant flow, but sometimes its just easier to work with the access the Azure admin gave you than it is to go back-and-forth. In this case, I've delegated permission to the app to perform the uploads under my identity. Which means, since this isn't using a service account, this will stop working when my account is decommissioned. On the positive side, given that the refresh token's max inactive time is 90 days (https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-configurable-token-lifetimes), there shouldn't be a need to regularly get a new auth code.

First, register an application at portal.azure.com, and configure API permissions. I used Microsoft Graph->User.Read, and SharePoint->AllSites.Write and SharePoint->MyFiles.Write.

Then navigate to the below URL, sign in, and authorize the app.
https://login.microsoftonline.com/SOME_GUID_VALUE/oauth2/authorize?client_id=CLIENT_ID_GUID&redirect_uri=https%3A%2F%2Flocalhost:8443/test&response_type=code&response_mode=query&scope=offline_access%20https%3A%2F%2Fgraph.microsoft.com%2FUser.Read

Microsoft will redirect to localhost:8443/test (which does not exist). Take the "code" value from the URL and plug that into authcode. This auth code is what the code will use when requesting access/refresh tokens.

The code to create the upload session and upload the actual file is straightforward.
