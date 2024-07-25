# Setup UltiHash on AWS 
This guide describes the full installation process of UltiHash in AWS environment including: 
- provision of EKS cluster in a dedicated VPC
- deployment of the essential Kubernetes controllers
- installation of UltiHash on the EKS cluster 

The UltiHash setup to be installed by following this guide consists of these parts:
- entrypoint: specify instance type
- database: specify instance type
- deduplicator and storage: specify instance type

The overall available disk space provided by this UltiHash setup is 10 TB. In case the larger storage capacity is required, feel free to scale out the number of storage service instances.

Please note, that this setup is suited for the testing purposes to verify the abilities of UltiHash as well as its integration with various tools and technologies. Since the product is yet in the development phase, avoid deploying it in the production environment!

# Warning! It is the staging setup, not production.

Perform the following actions step by step. You will deploy UH cluster on EKS suited for 10 TB of storage
Need to specify the cost for 1 hour

## Prerequisites
- AWS account (admin privileges)
- configured AWS CLI
- terraform
- The credentials received from UltiHash

Perhaps all some images. Client has to understand what exactly is provisioned. And how much it costs in advance.

# Preconfiguration
Since the Terrafom state for this setup has to be stored on S3, need to provision an S3 bucket.
Execute this command:
```
aws s3api create-bucket --bucket terraform-state-test-setup --create-bucket-configuration LocationConstraint=eu-central-1
```
Here the bucket name is `terraform-state-test-setup` and the region is `eu-central-1`

# Download the repository
```
git clone https://github.com/UltiHash/howto-uh.git
cd howto-uh/
```

## EKS Cluster Setup
Since UltiHash has to be deployed on Kubernetes cluster, need to provision EKS cluster on AWS
This will deploy EKS cluster in a dedicated VPC.
Reverence to the code
```
cd terraform/aws/eks-cluster
```
Update the bucket name in the `main.tf`
Update the configuration in `config.tfvars`
Initialize the Terraform project
```
terraform init
```
Deploy the EKS cluster
```
terraform apply --var-file config.tfvars
```
Wait until it succeeds. At the end you will get the working EKS cluster.

To access the cluster by using kubectl run this:
```
aws eks update-kubeconfig --name ultihash-test --region eu-central-1
```

## Install Controllers on EKS
Reference to the code
Need to install essential controllers so UltiHash would correctly function.
Need to install Load Balancer controller to provision NLB, Nginx Controller
After terraform apply wait for the NLB to be created

## UltiHash Installation
Reference to the code

# Test UltiHash
Reference to the code (Upload, Download)

# Uninstall everything
uninstall all terraform code in the backward order