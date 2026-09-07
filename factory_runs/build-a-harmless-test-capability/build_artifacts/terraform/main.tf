terraform {
  required_version = ">= 1.5"
}

variable "product_name" {
  type    = string
  default = "build-a-harmless-test-capability"
}

output "product_name" {
  value = var.product_name
}
