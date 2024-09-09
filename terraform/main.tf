terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# Provider for operations that don't require the service account key
provider "google" {
  alias   = "impersonation"
  project = var.project_id
  region  = var.region
}

# Data source for existing service account
data "google_service_account" "existing_sa" {
  provider   = google.impersonation
  account_id = "terraform-sa@${var.project_id}.iam.gserviceaccount.com"
  project    = var.project_id
}

locals {
  service_account_email = data.google_service_account.existing_sa.email
}

# Assign necessary roles to the service account
resource "google_project_iam_member" "terraform_sa_roles" {
  provider = google.impersonation
  for_each = toset([
    "roles/container.admin",
    "roles/artifactregistry.admin",
    "roles/iam.serviceAccountUser",
    "roles/compute.admin",
    "roles/secretmanager.admin"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${local.service_account_email}"
}

# Create a key for the service account
resource "google_service_account_key" "terraform_sa_key" {
  provider           = google.impersonation
  service_account_id = data.google_service_account.existing_sa.name
}

# Create a secret to store the service account key
resource "google_secret_manager_secret" "terraform_sa_key" {
  provider  = google.impersonation
  project   = var.project_id
  secret_id = "terraform-sa-key"
  
  replication {
    auto {}
  }
}

# Store the service account key in the secret
resource "google_secret_manager_secret_version" "terraform_sa_key" {
  provider    = google.impersonation
  secret      = google_secret_manager_secret.terraform_sa_key.id
  secret_data = base64decode(google_service_account_key.terraform_sa_key.private_key)
}

# Data source to read the secret
data "google_secret_manager_secret_version" "terraform_sa_key" {
  provider = google.impersonation
  project  = var.project_id
  secret   = google_secret_manager_secret.terraform_sa_key.id
  version  = "latest"
  
  depends_on = [google_secret_manager_secret_version.terraform_sa_key]
}

# Main provider using the service account key from Secret Manager
provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = data.google_secret_manager_secret_version.terraform_sa_key.secret_data
}

# Data source for the existing GKE cluster
data "google_container_cluster" "devops_project" {
  name     = "devops-project"
  location = "us-central1-a"
  project  = var.project_id
}

# Artifact Registry repository
resource "google_artifact_registry_repository" "resume_tailor_repo" {
  location      = var.region
  repository_id = "resume-tailor-repo"
  description   = "Docker repository for Resume Tailor application"
  format        = "DOCKER"
  project       = var.project_id
}

# Variables
variable "project_id" {
  description = "The ID of the project"
  type        = string
}

variable "region" {
  description = "The region to use"
  type        = string
  default     = "us-central1"
}

# Outputs
output "gke_cluster_name" {
  value       = data.google_container_cluster.devops_project.name
  description = "Name of the GKE cluster"
}

output "artifact_registry_repository" {
  value       = google_artifact_registry_repository.resume_tailor_repo.name
  description = "Name of the Artifact Registry repository"
}