'''
  This script serves as an example of the integration between PySpark and UltiHash cluster.
  The script uploads the local CSV file to the UltiHash cluster and then downloads it from there.
'''
from pyspark.sql import SparkSession
from sys import argv

# UltiHash cluster endpoint URL
s3_endpoint = argv[1]  # For example, https://ultihash.cluster.io
# Bucket provisioned on the UltiHash cluster in advance
s3_bucket = argv[2] # For example, "datasets"
# Path to the local CSV file
dataset_file_name = argv[3] # For example, "sample_data.csv"

# Create Spark session
spark = SparkSession.builder.appName("UH Integration Test").getOrCreate()
sc = spark.sparkContext

# Set the AWS access and secret keys to the corresponding UltiHash cluster credentials
sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", "mocked")
sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "mocked")
# The S3 endpoint is a URL pointing to the deployed UltiHash cluster
sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", s3_endpoint)
# S3 path style access has to be enabled
sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")

#In case the UltiHash cluster URL is http-based, need to add the following line into the configuration:
#sc._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")

# Read the local CSV file
df = spark.read.csv(dataset_file_name,header=True,escape="\"")

# Write the dataset to the bucket
df.write.format("csv").option("header", "true").mode("overwrite").save("s3a://%s/%s" % (s3_bucket, dataset_file_name))

# Read the dataset from the bucket
df_new = spark.read.option("header", "true").csv("s3a://%s/%s" % (s3_bucket, dataset_file_name))

# Show the first five lines of the dataset
df_new.show(5,0)