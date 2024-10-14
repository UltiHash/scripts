'''
  This script serves as an example of the integration between AWS Glue and UltiHash cluster.
  The script reads the file "sample_data.csv" from the bucket "input" and writes it to the bucket "output".
'''

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
sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", "mocked")
sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "mocked")
sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", s3_endpoint)
sc._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")
sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")

glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read the dataset sample_data.csv from the bucket input
df = spark.read.option("header", "true").csv("s3a://input/sample_data.csv")

# Write the dataset to the bucket
df.write.format("csv").option("header", "true").mode("overwrite").save("s3a://output/data/")

job.commit()