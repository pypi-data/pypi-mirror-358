Django Azure AD Auth Redux
==========================

*Django Azure AD Auth* allows you to authenticate through Azure Active Directory.

  This fork has the following additional features:
  - Add the specification of the decode algorithm per newer PyJWT requirements.
  - Supports django > 3.2.18

Installation
------------

Run `pip install django-azure-ad-auth-redux`

Add the `AzureActiveDirectoryBackend` to your `AUTHENTICATION_BACKENDS` setting:

```python
AUTHENTICATION_BACKENDS = (
    ...
    "azure_ad_auth.backends.AzureActiveDirectoryBackend",
)
```

Settings
--------

### AAD_TENANT_ID

The Azure Tenant ID. It can be found in the URL of the Azure Management Portal.

### AAD_CLIENT_ID

The Azure Application Client ID.

### AAD_AUTHORITY

**default:** `"https://login.microsoftonline.com"`
The domain that is used for authorization, the federation metadata document, and logging out.

### AAD_SCOPE

**default:** `"openid"`
OAuth scope parameter.

### AAD_RESPONSE_TYPE

**default:** `"id_token"`
Tells OAuth to return a JWT token in its response.

### AAD_RESPONSE_MODE

**default:** `"form_post"`
Defines how the response parameters are returned. Valid choices are `fragment` or `form_post`.

### AAD_USER_CREATION

**default:** `True`
Allow creation of new users after successful authentication.

### AAD_USER_MAPPING

**default:** `{}`
Map fields from the token to the user, to be used on creation.

### AAD_USER_STATIC_MAPPING

**default:** `{}`
Map static values to user fields on creation.

### AAD_GROUP_MAPPING

**default:** `{}`
Map group ids to group names for user permissions.
