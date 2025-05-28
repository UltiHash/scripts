aws_region = "eu-central-1" # AWS region to deploy the EKS cluster

# Configuration for the VPC in which the EKS cluster will be deployed
vpc_name            = "ultihash-test"                    # Human readable name for the VPC
vpc_cidr            = "10.0.0.0/16"                      # IPv4-address range allocated for the VPC
vpc_azs             = ["eu-central-1a", "eu-central-1b"] # AZs in which the VPC will reside
vpc_public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]     # IPv4 ranges allocated for the public VPC subnets 
vpc_private_subnets = ["10.0.16.0/20", "10.0.32.0/20"]   # IPv4 ranges allocated for the private VPC subnets 

# EKS cluster configuration

cluster_name    = "ultihash-test" # Human readable name for the EKS cluster
cluster_version = "1.32"          # Kubernetes engine version for the EKS cluster

cluster_admins = [
  "arn:aws:iam::account_id:user/test-user" # REQUIRED TO CHANGE: List of IAM roles or IAM users to grant admin access to the EKS cluster
]