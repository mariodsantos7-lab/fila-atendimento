terraform {
  required_providers {
    k3d = {
      source  = "pvotal-tech/k3d"
      version = "0.0.7"
    }
  }
}

provider "k3d" {}

resource "k3d_cluster" "fila_cluster" {
  name    = "fila-atendimento"
  servers = 1
  agents  = 1
  image   = "rancher/k3s:v1.27.4-k3s1"
}