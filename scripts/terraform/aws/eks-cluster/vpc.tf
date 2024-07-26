module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.5.2"

  name = var.vpc_name
  cidr = var.vpc_cidr

  azs = var.vpc_azs

  public_subnets  = var.vpc_public_subnets
  private_subnets = var.vpc_private_subnets

  # Provision a single NAT gateway for the entire VPC for the sake of cost reduction
  enable_nat_gateway = true
  single_nat_gateway = true

  enable_flow_log = false
}