# secrets:
SUBSCRIPTION_ID=
MGMT_RESOURCE_GROUP_NAME=
STORAGE_ACCOUNT_NAME=
STORAGE_ACCOUNT_SKU=Standard_LRS

# values:
REGION=eastus2
REPO_RESOURCE_GROUP_NAME=rg-ai-engineer-challenge
ID_GH_REPO=id-ai-engineer-challenge
OWNER=gmezan
REPO=ai-engineer-challenge


az group create --name $REPO_RESOURCE_GROUP_NAME \
    --location $REGION

az storage container create \
    --name $REPO \
    --account-name $STORAGE_ACCOUNT_NAME \
    --auth-mode login

export AZURE_CLIENT_ID=$(az identity show \
  --name $ID_GH_REPO \
  --resource-group $MGMT_RESOURCE_GROUP_NAME \
  --query clientId -o tsv)

export AZURE_TENANT_ID=$(az account show \
  --query tenantId -o tsv)

export AZURE_SUBSCRIPTION_ID=$(az account show \
  --query id -o tsv)

export ID_GH_REPO_SERVICE_PRINCIPAL=$(az identity show \
  --name $ID_GH_REPO \
  --resource-group $MGMT_RESOURCE_GROUP_NAME \
  --query principalId -o tsv)


az role assignment create \
    --assignee $ID_GH_REPO_SERVICE_PRINCIPAL \
    --role Contributor \
    --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$MGMT_RESOURCE_GROUP_NAME

az role assignment create \
    --assignee $ID_GH_REPO_SERVICE_PRINCIPAL \
    --role Owner \
    --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$REPO_RESOURCE_GROUP_NAME


az identity federated-credential create --identity-name $ID_GH_REPO \
                                    --name onPullRequest \
                                    --resource-group $MGMT_RESOURCE_GROUP_NAME \
                                    --audiences api://AzureADTokenExchange \
                                    --issuer https://token.actions.githubusercontent.com \
                                    --subject repo:"$OWNER"/"$REPO":pull_request

az identity federated-credential create --identity-name $ID_GH_REPO \
                                    --name onBranch \
                                    --resource-group $MGMT_RESOURCE_GROUP_NAME \
                                    --audiences api://AzureADTokenExchange \
                                    --issuer https://token.actions.githubusercontent.com \
                                    --subject repo:"$OWNER"/"$REPO":ref:refs/heads/main

az identity federated-credential create --identity-name $ID_GH_REPO  \
                                    --name onEnvironment \
                                    --resource-group $MGMT_RESOURCE_GROUP_NAME \
                                    --audiences api://AzureADTokenExchange \
                                    --issuer https://token.actions.githubusercontent.com \
                                    --subject repo:"$OWNER"/"$REPO":environment:azure


gh auth login

gh secret set AZURE_CLIENT_ID \
    --repo $OWNER/$REPO \
    --body "$AZURE_CLIENT_ID"

gh secret set AZURE_SUBSCRIPTION_ID \
    --repo $OWNER/$REPO \
    --body "$SUBSCRIPTION_ID"

gh secret set AZURE_TENANT_ID \
    --repo $OWNER/$REPO \
    --body "$AZURE_TENANT_ID"

gh secret set AZ_TF_RG \
    --repo $OWNER/$REPO \
    --body "$MGMT_RESOURCE_GROUP_NAME"

gh secret set AZ_TF_SA \
    --repo $OWNER/$REPO \
    --body "$STORAGE_ACCOUNT_NAME"

export ENCRYPTION_KEY=$(openssl rand -base64 32)
gh secret set ENCRYPTION_KEY \
  --repo $OWNER/$REPO \
  --body "$ENCRYPTION_KEY"