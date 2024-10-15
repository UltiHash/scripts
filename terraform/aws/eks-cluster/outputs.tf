output "vpc_public_subnets" {
  description = "IDs of the public VPC subnets"
  value       = module.vpc.public_subnets
}

output "cluster_name" {
  description = "Name of the provisioned EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Kubernetes API server endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  description = "Certificate data required to communicate with the EKS cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_oidc_provider_arn" {
  description = "OIDC Provider ARN used by the EKS cluster"
  value       = module.eks.oidc_provider_arn
}

output "cluster_oidc_issuer_url" {
  description = "OIDC Issuer URL used by the EKS cluster"
  value       = module.eks.cluster_oidc_issuer_url
}


