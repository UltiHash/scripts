# Presto Integration

This document provides information regarding the integration between UltiHash and Apache Presto

## Presto Configuration

To work with UltiHash, Apache Presto should rely on the following connector:
- [Hive](https://prestodb.io/docs/current/connector/hive.html) - supports the [S3A driver](https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html)

The file [ultihash.properties](./ultihash.properties) provides configuration for the Hive connector with the S3A driver. Replace `hive.metastore.uri` and `hive.s3.endpoint` with Hive Metastore URL and UltiHash URL correspondingly. Set the variables `hive.s3.aws-access-key` and `hive.s3.aws-secret-key` to the corresponding UltiHash credentials (see [User and policy Management](https://docs.ultihash.io/2.-administration/8.-user-and-policy-management)).