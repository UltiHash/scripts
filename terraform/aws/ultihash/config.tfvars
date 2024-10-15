aws_region = "eu-central-1"

registry_username = "test-user"           # REQUIRED TO CHANGE: Username for registry.ultihash.io
registry_password = "test-user-password"  # REQUIRED TO CHANGE: Password for registry.ultihash.io

ultihash_license = "Test-License:10240:Bplb7lZQIK+mIXyPsasadsaARSDrakfds7tdvrcASbndpL43axS7Ccd9TyuL4v03zHsFzPOyW7sL+uouBw=="  # REQUIRED TO CHANGE: UltiHash license
monitoring_token = "8tEFwDsduD6gSHM2"     # REQUIRED TO CHANGE: UltiHash monitoring token

helm_chart_installation_timeout = 600     # Time to install the UltiHash helm chart. Increase only in case of the "context deadline exceeded" error