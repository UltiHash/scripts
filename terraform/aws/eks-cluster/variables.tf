variable "aws_region" {
  description = "AWS region to deploy the EKS cluster"
  type        = string
}

variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
}

variable "vpc_azs" {
  description = "List of AZs to be used in the VPC"
  type        = list(string)
}

variable "vpc_cidr" {
  description = "Main IPv4 CIDR to provision in the VPC"
  type        = string
}

variable "vpc_public_subnets" {
  description = "List of public subnets to allocate in the VPC"
  type        = list(string)
}

variable "vpc_private_subnets" {
  description = "List of private subnets to allocate in the VPC"
  type        = list(string)
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes version of the EKS cluster"
  type        = string
}

variable "cluster_admins" {
  description = "List of EKS cluster admins"
  type        = list(string)
}