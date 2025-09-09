locals {
  # Generate EKS access entries based on the provided cluster admins list
  access_entries = {
    for user_arn in var.cluster_admins :
    split("/", user_arn)[1] => {
      principal_arn = user_arn
      policy_associations = {
        permissions = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.2.1"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  # Provision cluster nodes and control plane endpoints in the private VPC subnets
  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.private_subnets

  # Make the cluster API reachable via Internet
  cluster_endpoint_public_access = true

  # Allow the following users full access to the cluster
  access_entries = local.access_entries

  # Disable EKS control plane logging
  cluster_enabled_log_types   = []
  create_cloudwatch_log_group = false

  # Setup the essential cluster controllers
  cluster_addons = {
    vpc-cni = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    coredns = {
      most_recent = true
    }
  }

  # Define the commmon configuration for all managed node groups
  eks_managed_node_group_defaults = {
    platform       = "bottlerocket"
    instance_types = ["c5.large"]
    disk_size      = 20
  }

  # Provision a node group to host the EKS cluster controllers
  eks_managed_node_groups = {

    management = {
      min_size     = 1
      max_size     = 1
      desired_size = 1
      subnet_ids   = [module.vpc.private_subnets[0]]
    }
  }

}
