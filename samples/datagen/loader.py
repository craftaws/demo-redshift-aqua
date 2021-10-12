# pylint: skip-file
'Lambda function to generate data'
import os
import subprocess
import boto3

DATA_BUCKET_NAME = os.environ['data_bucket_name']
LAMBDA_RUNTIME_DATA_DIR='/var/runtime/dbgen'

boto_client_s3 = boto3.client('s3')
boto_resource_s3 = boto3.resource('s3')

def load(event, context):
    '''
    Entry point of aws-lambda runtime
    To perform this lambda function with aws-lambda emulator in local:
      docker run -p 9000:8080 [IMAGE]
      curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
    '''

    print(f"Make BUCKET[{DATA_BUCKET_NAME}] empty...")
    boto_bucket = boto_resource_s3.Bucket(DATA_BUCKET_NAME)
    boto_bucket.objects.all().delete()

    print(f"Working data bucket is: {DATA_BUCKET_NAME}")

    for (root, dirs, files) in os.walk(LAMBDA_RUNTIME_DATA_DIR):
      if len(files) > 0:
        for file_name in files:
          print(
            boto_client_s3.upload_file(f"{LAMBDA_RUNTIME_DATA_DIR}/{file_name}",DATA_BUCKET_NAME,file_name)
          )
    return "Complete generate data & copy to s3"