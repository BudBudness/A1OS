terraform {
  required_version = ">= 1.5"
}

variable "product_name" {
  type    = string
  default = "build-a-new-application-feature"
}

output "product_name" {
  value = var.product_name
}
