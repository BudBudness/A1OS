terraform {
  required_version = ">= 1.5"
}

variable "product_name" {
  type    = string
  default = "add-localstorage-chat-history-to-jarvis-chat-html"
}

output "product_name" {
  value = var.product_name
}
