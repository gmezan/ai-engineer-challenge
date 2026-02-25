# Initial set up for repository

First we provision the resources and configure the repo with managed identity and federated credentials to establish a secure connection between the repo and azure

Prerequisites:

1. Create a _management_ Resource Group
    ```sh
    az group create --name $MGMT_RESOURCE_GROUP_NAME \
        --location $REGION
    ```

1. Create the _repo_ Resource Group
    ```sh
    az group create --name $REPO_RESOURCE_GROUP_NAME \
        --location $REGION
    ```

1. Create a storage account in the resource group
    ```sh
    az storage account create \
        --name $STORAGE_ACCOUNT_NAME \
        --resource-group $MGMT_RESOURCE_GROUP_NAME \
        --location $REGION \
        --sku $STORAGE_ACCOUNT_SKU
    ```

1. Create a container in the storage account (This container will be used to store the project _tfstate_.)
    ```sh
    az storage container create \
        --name $REPO \
        --account-name $STORAGE_ACCOUNT_NAME \
        --auth-mode login
    ```

1. Create Managed Identity to login to Azure from GitHub
    ```sh
    az identity create --name $ID_GH_REPO \
        --resource-group $MGMT_RESOURCE_GROUP_NAME \
        --location $REGION
    ```

1. Grant the following permissions:

    _Contributor_ Role over the _management_ resource group to the managed identity. 

    ```sh
    az role assignment create \
        --assignee $ID_GH_REPO_SERVICE_PRINCIPAL \
        --role Contributor \
        --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$MGMT_RESOURCE_GROUP_NAME
    ```

    _Owner_ Role over the _repo_ resource group to the managed identity.
    ```sh
    az role assignment create \
        --assignee $ID_GH_REPO_SERVICE_PRINCIPAL \
        --role Owner \
        --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$REPO_RESOURCE_GROUP_NAME
    ```

1. Create the following federated credentials

    ```sh
    az identity federated-credential create --identity-name $ID_GH_REPO \
                                        --name onPullRequest \
                                        --resource-group $MGMT_RESOURCE_GROUP_NAME \
                                        --audiences api://AzureADTokenExchange \
                                        --issuer https://token.actions.githubusercontent.com \
                                        --subject repo:$OWNER/$REPO:pull_request

    az identity federated-credential create --identity-name $ID_GH_REPO \
                                        --name onBranch \
                                        --resource-group $MGMT_RESOURCE_GROUP_NAME \
                                        --audiences api://AzureADTokenExchange \
                                        --issuer https://token.actions.githubusercontent.com \
                                        --subject repo:$OWNER/$REPO:ref:refs/heads/main-azure

    az identity federated-credential create --identity-name $ID_GH_REPO  \
                                        --name onEnvironment \
                                        --resource-group $MGMT_RESOURCE_GROUP_NAME \
                                        --audiences api://AzureADTokenExchange \
                                        --issuer https://token.actions.githubusercontent.com \
                                        --subject repo:$OWNER/$REPO:environment:azure
    ```

1. Configure credentials in GH. Go to the correspondent GH repo. In _Settings_ > _Secrets and variables_ > _Actions_, create the following secrets with the values corresponding to the created managed identity.
   - `AZURE_CLIENT_ID`
   - `AZURE_SUBSCRIPTION_ID`
   - `AZURE_TENANT_ID`


    ```sh
    gh auth login

    gh secret set AZURE_CLIENT_ID \
    --repo $OWNER/$REPO \
    --body "$AZURE_CLIENT_ID"

    gh secret set AZURE_SUBSCRIPTION_ID \
    --repo $OWNER/$REPO \
    --body "$SUBSCRIPTION_ID"

    gh secret set AZURE_TENANT_ID \
    --repo $OWNER/$REPO \
    --body "$TENANT_ID"
    ```
