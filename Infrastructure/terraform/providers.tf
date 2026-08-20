# ============================================================
# Terraform Root — Bengaluru Traffic MLOps Infrastructure
# ============================================================
# Provisions: VPC, EKS, ECR, S3 on AWS (ap-south-1)
# ============================================================

terraform {
  required_version = ">= 1.15.8"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "mlops-cluster-tf-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "mlops-cluster-tf-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "bengaluru-traffic-mlops"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
