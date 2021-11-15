# pylint: skip-file
'Lambda function to load data from s3 to Redshift'
import os
import boto3
import json
from botocore.exceptions import ClientError

REDSHIFT_ID = os.environ['REDSHIFT_ID']
REDSHIFT_SECRET = os.environ['REDSHIFT_SECRET']
REDSHIFT_IAM_ROLE = os.environ['REDSHIFT_IAM_ROLE']
DATA_BUCKET_NAME = os.environ['DATA_BUCKET_NAME']
REGION = os.environ['REGION']

def run(event, context):
    '''
    Entry point of aws-lambda runtime
    To perform this lambda function with aws-lambda emulator in local:
      docker run -p 9000:8080 [IMAGE]
      curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
    '''
    
    print(f"event: {event}")
    print(f"REDSHIFT_ID: {REDSHIFT_ID}")
    print(f"REDSHIFT_SECRET: {REDSHIFT_SECRET}")
    print(f"REDSHIFT_IAM_ROLE: {REDSHIFT_IAM_ROLE}")
    print(f"DATA_BUCKET_NAME: {DATA_BUCKET_NAME}")
    
    session = boto3.session.Session()
    # client = session.client(service_name='secretsmanager', region_name=REGION)
    client = boto3.client('redshift-data')

    try:
        response = client.batch_execute_statement(
            ClusterIdentifier=REDSHIFT_ID,
            Database='default_db',
            SecretArn=REDSHIFT_SECRET,
            Sqls=[
                '''
                drop SCHEMA IF EXISTS demo cascade
                ''',
                '''
                create SCHEMA demo
                ''',
                '''
                set search_path to demo;
                ''',
                '''
                CREATE TABLE NATION  (
                    N_NATIONKEY  INTEGER NOT NULL,
                    N_NAME       CHAR(25) NOT NULL,
                    N_REGIONKEY  INTEGER NOT NULL,
                    N_COMMENT    VARCHAR(152))
                ''',
                f'''
                copy demo.nation from 's3://{DATA_BUCKET_NAME}/nation.tbl'
                iam_role '{REDSHIFT_IAM_ROLE}'
                ''',
                '''
                CREATE TABLE REGION  ( 
                    R_REGIONKEY  INTEGER NOT NULL,
                    R_NAME       CHAR(25) NOT NULL,
                    R_COMMENT    VARCHAR(152))
                ''',
                f'''
                copy demo.region from 's3://{DATA_BUCKET_NAME}/region.tbl'
                iam_role '{REDSHIFT_IAM_ROLE}'
                ''',
                '''
                CREATE TABLE PART  ( 
                    P_PARTKEY     INTEGER NOT NULL,
                    P_NAME        VARCHAR(55) NOT NULL,
                    P_MFGR        CHAR(25) NOT NULL,
                    P_BRAND       CHAR(10) NOT NULL,
                    P_TYPE        VARCHAR(25) NOT NULL,
                    P_SIZE        INTEGER NOT NULL,
                    P_CONTAINER   CHAR(10) NOT NULL,
                    P_RETAILPRICE DECIMAL(15,2) NOT NULL,
                    P_COMMENT     VARCHAR(23) NOT NULL )
                ''',
                f'''
                copy demo.part from 's3://{DATA_BUCKET_NAME}/part.tbl'
                iam_role '{REDSHIFT_IAM_ROLE}'
                ''',
                '''
                CREATE TABLE SUPPLIER (
                    S_SUPPKEY     INTEGER NOT NULL,
                    S_NAME        CHAR(25) NOT NULL,
                    S_ADDRESS     VARCHAR(40) NOT NULL,
                    S_NATIONKEY   INTEGER NOT NULL,
                    S_PHONE       CHAR(15) NOT NULL,
                    S_ACCTBAL     DECIMAL(15,2) NOT NULL,
                    S_COMMENT     VARCHAR(101) NOT NULL)
                ''',
                f'''
                copy demo.supplier from 's3://{DATA_BUCKET_NAME}/supplier.tbl'
                iam_role '{REDSHIFT_IAM_ROLE}'
                ''',
                '''
                CREATE TABLE PARTSUPP (
                    PS_PARTKEY     INTEGER NOT NULL,
                    PS_SUPPKEY     INTEGER NOT NULL,
                    PS_AVAILQTY    INTEGER NOT NULL,
                    PS_SUPPLYCOST  DECIMAL(15,2)  NOT NULL,
                    PS_COMMENT     VARCHAR(199) NOT NULL )
                ''',
                f'''
                copy demo.partsupp from 's3://{DATA_BUCKET_NAME}/partsupp.tbl'
                iam_role '{REDSHIFT_IAM_ROLE}'
                ''',
                '''
                CREATE TABLE CUSTOMER (
                    C_CUSTKEY     INTEGER NOT NULL,
                    C_NAME        VARCHAR(25) NOT NULL,
                    C_ADDRESS     VARCHAR(40) NOT NULL,
                    C_NATIONKEY   INTEGER NOT NULL,
                    C_PHONE       CHAR(15) NOT NULL,
                    C_ACCTBAL     DECIMAL(15,2)   NOT NULL,
                    C_MKTSEGMENT  CHAR(10) NOT NULL,
                    C_COMMENT     VARCHAR(117) NOT NULL)
                ''',
                f'''
                copy demo.customer from 's3://{DATA_BUCKET_NAME}/customer.tbl'
                iam_role '{REDSHIFT_IAM_ROLE}'
                ''',
                '''
                CREATE TABLE ORDERS  (
                    O_ORDERKEY       INTEGER NOT NULL,
                    O_CUSTKEY        INTEGER NOT NULL,
                    O_ORDERSTATUS    CHAR(1) NOT NULL,
                    O_TOTALPRICE     DECIMAL(15,2) NOT NULL,
                    O_ORDERDATE      DATE NOT NULL,
                    O_ORDERPRIORITY  CHAR(15) NOT NULL,  
                    O_CLERK          CHAR(15) NOT NULL, 
                    O_SHIPPRIORITY   INTEGER NOT NULL,
                    O_COMMENT        VARCHAR(79) NOT NULL)
                ''',
                f'''
                copy demo.orders from 's3://{DATA_BUCKET_NAME}/orders.tbl'
                iam_role '{REDSHIFT_IAM_ROLE}'
                ''',
                '''
                CREATE TABLE LINEITEM (
                    L_ORDERKEY    INTEGER NOT NULL,
                    L_PARTKEY     INTEGER NOT NULL,
                    L_SUPPKEY     INTEGER NOT NULL,
                    L_LINENUMBER  INTEGER NOT NULL,
                    L_QUANTITY    DECIMAL(15,2) NOT NULL,
                    L_EXTENDEDPRICE  DECIMAL(15,2) NOT NULL,
                    L_DISCOUNT    DECIMAL(15,2) NOT NULL,
                    L_TAX         DECIMAL(15,2) NOT NULL,
                    L_RETURNFLAG  CHAR(1) NOT NULL,
                    L_LINESTATUS  CHAR(1) NOT NULL,
                    L_SHIPDATE    DATE NOT NULL,
                    L_COMMITDATE  DATE NOT NULL,
                    L_RECEIPTDATE DATE NOT NULL,
                    L_SHIPINSTRUCT CHAR(25) NOT NULL,
                    L_SHIPMODE     CHAR(10) NOT NULL,
                    L_COMMENT      VARCHAR(44) NOT NULL)
                ''',
                f'''
                copy demo.lineitem from 's3://{DATA_BUCKET_NAME}/lineitem.tbl'
                iam_role '{REDSHIFT_IAM_ROLE}'
                ''',
            ],
            WithEvent=False,
        )
    except ClientError as client_error:
        print(client_error)
    else:
        print(response)
    
    return 'Data load from S3 has done.'
