# AWS Glue Integration

This document provides information regarding the integration between UltiHash and AWS Glue

## AWS Glue Configuration

AWS Glue relies on [S3A module](https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html) to provide connectivity with endpoints suppording S3 protocol. Below is an example of the S3A module configuration that connects AWS Glue with the UltiHash cluster:
```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
 
## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Define the UltiHash endpoint URL 
s3_endpoint = "https://ultihash.cluster.io"

sc = SparkContext()
# AWS access and secret keys could be any, since authentication is not yet supported by UltiHash
sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", "mocked")
sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "mocked")
# The S3 endpoint is a URL pointing to the deployed UltiHash cluster
sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", s3_endpoint)
# S3 path style access has to be enabled
sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")

glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
``` 
In case the UltiHash cluster URL is http-based, need to add the following line into the configuration:
```python
sc._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")
```

The full example of the AWS Glue integration could be found [here](./integration.py)