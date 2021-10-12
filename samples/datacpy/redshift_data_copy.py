# pylint: skip-file
'Lambda function to load data from s3 to Redshift'
import os
import boto3
import json
from botocore.exceptions import ClientError
import redshift_connector

REDSHIFT_SECRET = os.environ['REDSHIFT_SECRET']
REGION = os.environ['REGION']

def run(event, context):
    '''
    Entry point of aws-lambda runtime
    To perform this lambda function with aws-lambda emulator in local:
      docker run -p 9000:8080 [IMAGE]
      curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
    '''
    
    print(f"event: {event}")
    
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=REGION)
    
    try:
        response = client.get_secret_value(SecretId=REDSHIFT_SECRET)
    except ClientError as e:
        print(e.response['Error']['Code'])
    else:
        cluster_prop = json.loads(response['SecretString'])
        print(cluster_prop)
        
        conn = redshift_connector.connect(
            host=cluster_prop['host'],
            port=cluster_prop['port'],
            database=cluster_prop['dbname'],
            user=cluster_prop['username'],
            password=cluster_prop['password'],
        )
        
        RED_CLUSTER=cluster_prop['dbClusterIdentifier']
        cursor: redshift_connector.Cursor = conn.cursor()
        cursor.execute(f"select 'It has done with query execution on Redshift:{RED_CLUSTER}.'")
        result: tuple = cursor.fetchall()
        print(result)
    
    return 'Done!'
