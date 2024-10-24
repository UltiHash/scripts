# PySpark Integration

This document provides information regarding the integration between UltiHash and PySpark

## Spark Configuration

Spark relies on [S3A module](https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html) to provide connectivity with endpoints suppording S3 protocol. Below is an example of the S3A module configuration that connects PySpark with the UltiHash cluster:
```python
from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder.appName("AppName").getOrCreate()
sc = spark.sparkContext

# AWS access and secret keys could be any, since authentication is not yet supported by UltiHash
sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", "mocked")  # Replace with the corresponding UltiHash credentials
sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "mocked")  # Replace with the corresponding UltiHash credentials
# The S3 endpoint is a URL pointing to the deployed UltiHash cluster
# It has to contain the scheme (http or https) and the domain name of the cluster endpoint
sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", "https://ultihash.cluster.io")
# S3 path style access has to be enabled
sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
``` 
In case the UltiHash cluster URL is http-based, need to add the following line into the configuration:
```
sc._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")
```

The full example of the PySpark integration could be found [here](./integration.py)