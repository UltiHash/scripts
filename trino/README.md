# Trino Integration

This document provides information regarding the integration between UltiHash and Apache Trino

## Trino Configuration

To work with UltiHash, Apache Trino should rely on one of the following connectors:
- [Hive](https://trino.io/docs/current/connector/hive.html) - supports two different access schemes: native S3 API and [S3A driver](https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html)
- [Delta Lake](https://trino.io/docs/current/connector/delta-lake.html) - access is performed via the S3A diver
- [Apache Iceberg](https://trino.io/docs/current/connector/iceberg.html#connector-iceberg--page-root) - access is performed via the S3A diver

The file [deltalake.properties](./deltalake.properties) provides configuration for the Delta Lake connector. Replace `hive.metastore.uri` and `hive.s3.endpoint` with Hive Metastore URL and UltiHash URL correspondingly. Recommended to use due to improved performance. Set the variables `hive.s3.aws-access-key` and `hive.s3.aws-secret-key` to the corresponding UltiHash credentials (see [User and policy Management](https://docs.ultihash.io/2.-administration/8.-user-and-policy-management)).

The file [iceberg.properties](./iceberg.properties) provides configuration for the Iceberg connector. Replace `hive.metastore.uri` and `hive.s3.endpoint` with Hive Metastore URL and UltiHash URL correspondingly. Set the variables `hive.s3.aws-access-key` and `hive.s3.aws-secret-key` to the corresponding UltiHash credentials (see [User and policy Management](https://docs.ultihash.io/2.-administration/8.-user-and-policy-management)).

The file [ultihashs3.properties](./ultihashs3.properties) provides configuration for the Hive connector with the native S3 API. Replace `hive.metastore.uri` and `s3.endpoint` with Hive Metastore URL and UltiHash URL correspondingly. The parameter `s3.region` could be assigned any value. Set the variables `s3.aws-access-key` and `s3.aws-secret-key` to the corresponding UltiHash credentials (see [User and policy Management](https://docs.ultihash.io/2.-administration/8.-user-and-policy-management)).

The file [ultihashs3a.properties](./ultihashs3a.properties) provides configuration for the Hive connector with the S3A driver. Replace `hive.metastore.uri` and `hive.s3.endpoint` with Hive Metastore URL and UltiHash URL correspondingly. Set the variables `hive.s3.aws-access-key` and `hive.s3.aws-secret-key` to the corresponding UltiHash credentials (see [User and policy Management](https://docs.ultihash.io/2.-administration/8.-user-and-policy-management)).

:ledger: It is recommended to use `Delta Lake` or `Iceberg` connector to achive higher performance.   