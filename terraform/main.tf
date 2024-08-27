terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

data "google_secret_manager_secret_version" "terraform_sa_key" {
  secret = google_secret_manager_secret.terraform_sa_key.id
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = data.google_secret_manager_secret_version.terraform_sa_key.secret_data
}

resource "google_artifact_registry_repository" "resume_tailor_repo" {
  location      = "us-central1"
  repository_id = "resume-tailor-repo"
  description   = "Docker repository for Resume Tailor application"
  format        = "DOCKER"
}
data "google_container_cluster" "devops_project" {
  name     = "devops-project"
  location = "us-central1"
}
resource "google_service_account" "terraform_sa" {
  account_id   = "terraform-sa"
  display_name = "Terraform Service Account"
}
resource "google_project_iam_member" "terraform_sa_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.terraform_sa.email}"
}
resource "google_service_account_key" "terraform_sa_key" {
  service_account_id = google_service_account.terraform_sa.name
}
output "terraform_sa_key" {
  value     = google_service_account_key.terraform_sa_key.private_key
  sensitive = true
}
variable "project_id" {
  description = "The ID of the project"
  type        = string
}

variable "region" {
  description = "The region to use"
  type        = string
  default     = "us-central1"
}
resource "google_secret_manager_secret" "terraform_sa_key" {
  secret_id = "terraform-sa-key"
  replication {
    automatic = true
  }
}
resource "google_secret_manager_secret_version" "terraform_sa_key" {
  secret = google_secret_manager_secret.terraform_sa_key.id
  secret_data = base64decode(google_service_account_key.terraform_sa_key.private_key)
}