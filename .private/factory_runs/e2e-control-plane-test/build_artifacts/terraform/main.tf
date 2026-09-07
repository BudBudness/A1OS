terraform {
  required_version = ">= 1.5"
}

variable "product_name" {
  type    = string
  default = "e2e-control-plane-test"
}

output "product_name" {
  value = var.product_name
}
