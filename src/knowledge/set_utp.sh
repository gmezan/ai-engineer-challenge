az ad signed-in-user show --query id -o tsv

az role assignment create \
  --assignee $USER_OBJECT_ID \
  --role "Search Index Data Contributor" \
  --scope /subscriptions/"$SUBSCRIPTION_ID"/resourceGroups/"$RESOURCE_GROUP"/providers/Microsoft.Search/searchServices/$SEARCH_SERVICE_NAME
  