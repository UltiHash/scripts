# Setup UltiHash on AWS 
This guide describes the full installation process of UltiHash in AWS environment including: 
- provision of EKS cluster in a dedicated VPC
- deployment of the essential Kubernetes controllers
- installation of UltiHash on the EKS cluster 

The UltiHash setup to be installed by following this guide consists of these parts:
- 1 entrypoint instance hosted on a `c7g.8xlarge` machine fronted by A Network Load Balancer
- 1 database instance on a `c7gd.4xlarge` machine
- 2 pairs of deduplicator and storage on 2 `im4gn.8xlarge` machines  

The overall available disk space provided by this UltiHash setup is 15 TB. In case the larger storage capacity is required, feel free to scale out the number of storage service instances.

Please note, that this setup is suited for the testing purposes to verify the abilities of UltiHash as well as its integration with various tools and technologies. Since the product is yet in the development phase, avoid deploying it in the production environment!

# Prerequisites

## Remote Environment
- AWS account

## Local Environment
- [installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-methods) AWS CLI
- [installed](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) terraform
- [installed](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.28.md#v1280) kubectl of version 1.28
- received credentials from UltiHash representatives such as registry login and password, license, and monitoring token

## Setup S3 Bucket for Terraform States
Since the Terraform state for this setup has to be stored on S3, need to provision a dedicated S3 bucket.
Execute the following command, replacing the `<bucket-name>` and `<aws-region>` placeholders:
```
aws s3api create-bucket --bucket <bucket-name> --create-bucket-configuration LocationConstraint=<aws-region>
```

## Clone the howto-uh repository
Clone the repository by executing the command below:
```
git clone https://github.com/UltiHash/howto-uh.git
```
Later its code will be required to setup UltiHash in AWS environment.

## EKS Cluster Setup
Since UltiHash has to be deployed on Kubernetes cluster, need to provision EKS cluster on AWS. For this purpose use [this Terraform project](../scripts/terraform/aws/eks-cluster/). The project deploys a dedicated VPC and provisions there an EKS cluster with a single `c5.large` machine to host the essential Kubernetes controllers.

Once the [howto-uh](#clone-the-howto-uh-repository) repository is cloned, perform the following actions to deploy the Terraform project:
1. Update the `bucket name` and its `region` in the [main.tf](../scripts/terraform/aws/eks-cluster/main.tf) with the onces done at [the previous step](#setup-s3-bucket-for-terraform-states).
2. Update the configuration in [config.tfvars](../scripts/terraform/aws/eks-cluster/config.tfvars). The only required change is the parameter `cluster_admins` - specify the list of ARNs of IAM users and/or IAM roles that need to have access to the provisioned EKS cluster. Other parameters could be left intact.
3. Initialize and apply the Terraform project
   ```
   cd scripts/terraform/aws/eks-cluster
   terraform init
   terraform apply --var-file config.tfvars
   ```
   Wait until the installation is completed.

Make sure the access to the EKS cluster has been granted to the required IAM users and roles To check that, download the `kubeconfig` for the EKS cluster, executing the command below. Replace the `<cluster-name>` (by default `ultihash-test`) and the `<aws-region>` (by default `eu-central-1`) with the corresponding values defined in [config.tfvars](../scripts/terraform/aws/eks-cluster/config.tfvars)
```
aws eks update-kubeconfig --name <cluster-name> --region <aws-region>
```
Execute the following `kubectl` command to check the available EKS cluster nodes:
```
kubectl get nodes
```
The command has to output a name of a single provisioned EC2 instance.

## Install Controllers on EKS
The next step is installation of the essential Kubernetes controllers on the provisioned EKS cluster. For this purpose use [this Terraform project](../scripts/terraform/aws/eks-cluster-controllers/). The project deploys the following Kuberentes controllers on the EKS cluster:
- `Nginx Ingress` - exposes UltiHash outside of the EKS cluster with a Network Load Balancer 
- `Load Balancer Controller` - provisions a Network Load Balancer for the `Nginx Ingress` controller
- `Karpenter` - provisions EC2 instances on-demand to host UltiHash workloads
- `Local Path Provisioner` - CSI controller that automatically provisions non-persistent volumes for the UltiHash workloads. These volumes are bound to the NVMe SSD instance store available on the machines provisioned by `Karpenter`
- `EBS CSI Driver` - CSI controller that automatically provisions persistent volumes the UltiHash workfloads. The volumes are based on `gp3` storage class and optimised in terms of performance 

 :ledger: Note, that the volumes provisioned by `Local Path Provisioner` are non persistent! Once EC2 instance is removed, all its accosiated volumes will be removed as well. If during the testing, it is required to remove the EC2 instances to save the costs without loosing their volumes, use `EBS CSI Driver` instead. This requires modification of the UltiHash Helm values, which will be explaned [at a later step](#ultihash-installation).

Perform the following actions to deploy the Terraform project:
1. Update the `bucket name` and its `region` in the [main.tf](../scripts/terraform/aws/eks-cluster-controllers/main.tf) with the onces done at [the previous step](#setup-s3-bucket-for-terraform-states).
2. Update the configuration in [config.tfvars](../scripts/terraform/aws/eks-cluster-controllers/config.tfvars) if required. The helm values for the deployed controlers are found [here](../scripts/terraform/aws/eks-cluster-controllers/controllers-values/). It is not recommended to change any of these configurations, the only parameter that should be selected in advance is the `Network Load Balancer type` (`internal` or `internet-facing`) in this [file](../scripts/terraform/aws/eks-cluster-controllers/controllers-values/nginx-ingress.yaml).
3. In case it is required to change the instance types for the UltiHash services, update them in the following [Karpenter manifests](../scripts/terraform/aws/eks-cluster-controllers/karpenter-manifests/)
4. Initialize and apply the Terraform project
   ```
   cd scripts/terraform/aws/eks-cluster-controllers
   terraform init
   terraform apply --var-file config.tfvars
   ```
   Wait until the installation is completed. A Network Load balancer should be provisioned in the same region as the EKS cluster.

## UltiHash Installation
The last step is installation of UltiHash. For this purpose use [this Terraform project](../scripts/terraform/aws/ultihash/).
Perform the following actions to deploy the Terraform project:
1. Update the `bucket name` and its `region` in the [main.tf](../scripts/terraform/aws/ultihash/main.tf) with the ones done at [the previous step](#setup-s3-bucket-for-terraform-states).
2. Update the configuration in [config.tfvars](../scripts/terraform/aws/ultihash/config.tfvars) with the credentials received from UltiHash representatives. The credentials in the `config.tfvars` are mocked. The helm values for UltiHash are found [here](../scripts/terraform/aws/ultihash/ultihash-helm-values.yaml). The only required change in the Helm values is the storage class for `etcd`, `storage`, `deduplicator`, and `database`. In case persistence is not required, use `local-path` storage class. Otherwise select `gp3-high-performance` (in case of `etcd` it will be `ebs-csi-gp3`). Feel free also to scale the number of `entrypoint`, `storage`, and `deduplicator` instances if required.
3. Initialize and apply the Terraform project
   ```
   cd scripts/terraform/aws/ultihash
   terraform init
   terraform apply --var-file config.tfvars
   ```
   Wait until the installation is completed.

The UltiHash cluster is installed in the `default` Kuberentes namespace, you `kubectl` to see the deployed workloads:
```
kubectl get all
```
To access UltiHash, use the domain name of the Network Load Balancer provisioned at [the previous step](#install-controllers-on-eks):
```
aws s3api list-buckets --endpoint-url http://ultihash-test-6a925a272ca1f954.elb.eu-central-1.amazonaws.com/
```
# Uninstall the Environment
To uninstall all previously deployed AWS resources follow these steps:
1. Uninstall UltiHash:
   ```
   cd scripts/terraform/aws/ultihash
   terraform destroy --var-file config.tfvars
   kubectl delete pvc --all
   ``` 
2. Uninstall Kubernetes controllers:
   ```
   cd scripts/terraform/aws/eks-cluster-controllers
   terraform destroy --var-file config.tfvars
   ``` 
3. Uninstall the EKS cluster:
   ```
   cd scripts/terraform/aws/eks-cluster
   terraform destroy --var-file config.tfvars
   ```