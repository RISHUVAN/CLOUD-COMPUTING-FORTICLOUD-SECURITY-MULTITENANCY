#####Ensure Dependencies #####
google-cloud-compute==1.1.0
google-cloud-pubsub==2.8.0
flask==2.1.2
werkzeug==2.1.2

#####Deploying to Google Cloud Functions#####
gcloud functions deploy fortigate_function --runtime python39 --trigger-http --entry-point main --allow-unauthenticated

####Debugging and Logging#####
gcloud functions logs read fortigate_function

#####Check Deployment and Logs####
gcloud functions deploy fortigate_function --runtime python39 --trigger-http --entry-point main --allow-unauthenticated

gcloud functions logs read fortigate_function
