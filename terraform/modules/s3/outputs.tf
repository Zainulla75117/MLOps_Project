output "bucket_name" {
  description = "MLflow artifacts S3 bucket name"
  value       = aws_s3_bucket.mlflow_artifacts.id
}

output "bucket_arn" {
  description = "MLflow artifacts S3 bucket ARN"
  value       = aws_s3_bucket.mlflow_artifacts.arn
}

output "dvc_bucket_name" {
  description = "DVC remote S3 bucket name"
  value       = aws_s3_bucket.dvc_remote.id
}

output "dvc_bucket_arn" {
  description = "DVC remote S3 bucket ARN"
  value       = aws_s3_bucket.dvc_remote.arn
}
