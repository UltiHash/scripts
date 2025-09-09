resource "kubernetes_secret" "dockerconfigjson" {
  metadata {
    name      = "registry-credentials"
    namespace = "default"
  }

  type = "kubernetes.io/dockerconfigjson"

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "registry.ultihash.io" = {
          "username" = var.registry_username
          "password" = var.registry_password
          "auth"     = base64encode("${var.registry_username}:${var.registry_password}")
        }
      }
    })
  }
}

resource "kubernetes_secret" "opaque" {
  metadata {
    name      = "ultihash"
    namespace = "default"
  }

  data = {
    customer_id  = var.customer_id
    access_token = var.access_token
    token        = var.monitoring_token
  }

  type = "Opaque"
}

resource "helm_release" "ultihash" {
  name       = "ultihash"
  repository = "oci://registry.ultihash.io/stable"
  chart      = "ultihash-cluster"
  timeout    = var.helm_chart_installation_timeout

  namespace = "default"

  values = [
    file("./ultihash-helm-values.yaml")
  ]

  depends_on = [
    kubernetes_secret.dockerconfigjson,
    kubernetes_secret.opaque
  ]
}
