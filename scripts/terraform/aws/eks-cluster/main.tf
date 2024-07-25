terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "terraform-state-test-setup" # Update the bucket name for the Terraform state 
    key    = "eks-cluster/terraform.tfstate"
    region = "eu-central-1" # Update the bucket region for the Terraform state 
  }
}

provider "aws" {
  region = var.aws_region
}
