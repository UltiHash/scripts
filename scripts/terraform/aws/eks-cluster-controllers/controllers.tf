locals {
  karpenter_release_name = "karpenter"
  karpenter_namespace    = "kube-system"
  karpernter_node_pools = {
    for filepath in fileset(path.module, "karpenter-manifests/*.node-pool.yaml") :
    split("/", split(".", filepath)[0])[1] => file(filepath)
  }
}

resource "helm_release" "local-path-provisioner" {
  name       = "local-path-provisioner"
  repository = "https://charts.containeroo.ch"
  chart      = "local-path-provisioner"
  version    = "0.0.26"

  namespace        = "local-path-provisioner"
  create_namespace = true
}

module "load-balancer-controller" {
  source  = "DNXLabs/eks-lb-controller/aws"
  version = "0.9.0"

  cluster_identity_oidc_issuer     = data.terraform_remote_state.eks_cluster.outputs.cluster_oidc_issuer_url
  cluster_identity_oidc_issuer_arn = data.terraform_remote_state.eks_cluster.outputs.cluster_oidc_provider_arn
  cluster_name                     = data.terraform_remote_state.eks_cluster.outputs.cluster_name

  helm_chart_version = "1.7.1"
}

data "template_file" "nginx_ingress_controller" {
  template = file("./controllers-values/nginx-ingress.yaml")
  vars = {
    load_balancer_subnets = join(", ", data.terraform_remote_state.eks_cluster.outputs.vpc_public_subnets)
  }
}

resource "helm_release" "nginx_ingress_controller" {
  name       = "nginx-ingress-controller"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  version    = "4.9.1"

  namespace = "kube-system"

  values = [
    data.template_file.nginx_ingress_controller.rendered
  ]

  depends_on = [
    module.load-balancer-controller
  ]
}

module "karpenter" {
  source  = "terraform-aws-modules/eks/aws//modules/karpenter"
  version = "20.2.1"

  cluster_name = data.terraform_remote_state.eks_cluster.outputs.cluster_name

  enable_irsa                     = true
  irsa_oidc_provider_arn          = data.terraform_remote_state.eks_cluster.outputs.cluster_oidc_provider_arn
  irsa_namespace_service_accounts = ["${local.karpenter_namespace}:${local.karpenter_release_name}"]
}

data "template_file" "karpenter" {
  template = file("./controllers-values/karpenter.yaml")
  vars = {
    cluster_name                 = data.terraform_remote_state.eks_cluster.outputs.cluster_name
    cluster_endpoint             = data.terraform_remote_state.eks_cluster.outputs.cluster_endpoint
    karpenter_interruption_queue = module.karpenter.queue_name
    karpenter_iam_role           = module.karpenter.iam_role_arn
  }
}

resource "helm_release" "karpenter" {
  name       = local.karpenter_release_name
  namespace  = local.karpenter_namespace
  repository = "oci://public.ecr.aws/karpenter"
  chart      = "karpenter"
  version    = "0.35.1"

  values = [
    data.template_file.karpenter.rendered
  ]
}

data "template_file" "karpenter_ec2_node_class" {
  template = file("./karpenter-manifests/ec2-nvme.node-class.yaml")
  vars = {
    node_registration_role = module.karpenter.node_iam_role_name
  }
}

resource "kubernetes_manifest" "installation" {
  for_each = merge(local.karpernter_node_pools, { "ec2-node-class" : data.template_file.karpenter_ec2_node_class.rendered })

  manifest = yamldecode(each.value)

  depends_on = [
    helm_release.karpenter
  ]
}