# Airflow Integration

This document provides information regarding the integration between UltiHash and Apache Airflow

## Airflow Configuration

1. Make sure Apache Airflow has the following Python packages installed:
```
pip3 install 'apache-airflow[amazon]'
pip3 install apache-airflow-providers-amazon
```

2. Create a connection object pointing to the UltiHash cluster. The example below shows how to provision a connection named `ultihash` by using Airflow CLI. Replace <endpoint-url> with the HTTP URL of the provisioned UltiHash cluster.
```
airflow connections add 'ultihash' --conn-json '{  
        "conn_type": "aws",
        "login": "ACCESS_KEY_ID",
        "password": "AWS_SECRET_KEY",
        "extra": {
            "endpoint_url": "<endpoint-url>",  
            "verify": "False",
            "service_config": {
              "s3": {
                "endpoint_url": "<endpoint-url>"
              }
            }
        }
    }'
    
# The output should be:
# Successfully added `conn_id`=ultihash : aws://ACCESS_KEY_ID:******@:    
```

3. Use the connection ID in Airflow's S3 Operators and Hooks to perform operations against the UltiHash cluster. The DAG shown below leverages the connection `ultihash` created in the previous step to provision S3 bucket on UltiHash. 
```
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator, S3DeleteBucketOperator
from airflow.utils.dates import days_ago
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

BUCKET_NAME="bucket-test"
AWS_CONN_ID="ultihash"    # Specify the connection with UltiHash 

def bucket_exists():
    s3 = S3Hook(AWS_CONN_ID)  # Make sure your S3 Hooks leverage the connection with UltiHash.
    if s3.check_for_bucket(BUCKET_NAME):
        raise Exception("Bucket %s still exists after removal" % BUCKET_NAME)
    else:
        print("Bucket %s has been successfully removed" % BUCKET_NAME)
 
with DAG(
    dag_id='create_delete_bucket',
    schedule_interval=None,
    start_date=days_ago(2),
    max_active_runs=1,
    tags=['testing'],
) as dag:

    # Create a bucket with BUCKET_NAME on Ultihash
    create_bucket = S3CreateBucketOperator(
        task_id='create_s3_bucket',
        bucket_name=BUCKET_NAME,
        aws_conn_id=AWS_CONN_ID   # Make sure your S3 Operators leverage the connection with UltiHash
    )

    # Delete the previously created bucket
    delete_bucket = S3DeleteBucketOperator(
        task_id='delete_s3_bucket',
        bucket_name=BUCKET_NAME,
        aws_conn_id=AWS_CONN_ID   # Make sure your S3 Operators leverage the connection with UltiHash
    )

    # Check if the bucket still exists
    check_bucket = PythonOperator(
        task_id='check_if_bucket_exists',
        python_callable=bucket_exists
    )

    create_bucket >> delete_bucket >> check_bucket
```