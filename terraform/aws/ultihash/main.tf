terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "2.12.1"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.26.0"
    }
  }
  backend "s3" {
    bucket = "terraform-state-test-setup"   # REQUIRED TO CHANGE: Update the bucket name for the Terraform state
    key    = "ultihash/terraform.tfstate"
    region = "eu-central-1"                 # REQUIRED TO CHANGE: Update the bucket region for the Terraform state
  }
}

data "terraform_remote_state" "eks_cluster" {
  backend = "s3"

  config = {
    bucket = "terraform-state-test-setup" # REQUIRED TO CHANGE: Update the bucket name for the Terraform state
    key    = "eks-cluster/terraform.tfstate"
    region = "eu-central-1"               # REQUIRED TO CHANGE: Update the bucket region for the Terraform state
  }
}

provider "helm" {
  registry {
    url      = "oci://registry.ultihash.io"
    username = var.registry_username
    password = var.registry_password
  }
  kubernetes {
    host                   = data.terraform_remote_state.eks_cluster.outputs.cluster_endpoint
    cluster_ca_certificate = base64decode(data.terraform_remote_state.eks_cluster.outputs.cluster_certificate_authority_data)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      args        = ["eks", "get-token", "--region", var.aws_region, "--cluster-name", data.terraform_remote_state.eks_cluster.outputs.cluster_name]
      command     = "aws"
    }
  }
}

provider "kubernetes" {
  host                   = data.terraform_remote_state.eks_cluster.outputs.cluster_endpoint
  cluster_ca_certificate = base64decode(data.terraform_remote_state.eks_cluster.outputs.cluster_certificate_authority_data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args        = ["eks", "get-token", "--region", var.aws_region, "--cluster-name", data.terraform_remote_state.eks_cluster.outputs.cluster_name]
    command     = "aws"
  }
}