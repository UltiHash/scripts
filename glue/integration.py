# Copyright 2026 UltiHash Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
s3_endpoint = "https://ultihash.cluster.io" # Replace with the URL of our UltiHash cluster

sc = SparkContext()
sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", "mocked") # Replace with the corresponding UltiHash credentials
sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "mocked") # Replace with the corresponding UltiHash credentials
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