
provider "aws" {
  region = "af-south-1"
}

resource "aws_instance" "a1os_node" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"
}

