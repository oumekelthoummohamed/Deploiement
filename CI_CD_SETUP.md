# CI/CD Setup

Add these GitHub repository secrets:

- AZURE_CREDENTIALS: JSON from service principal
- ACR_NAME: acrmlopskelthoum
- RESOURCE_GROUP: rg-mlops
- CONTAINER_APP_NAME: acrmlopskelthoum

Create a service principal and assign roles:

1) az ad sp create-for-rbac --name "sp-bank-churn" --role contributor --scopes /subscriptions/39b7321b-cc7a-4f24-8a56-6634cb8c11c0 --sdk-auth
2) Assign AcrPush role to the SP on the ACR.

Paste the JSON output from step 1 into AZURE_CREDENTIALS.
