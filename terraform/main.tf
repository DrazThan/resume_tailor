terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = "trim-keep-432409-n4"
  region  = "us-central1"
  credentials = file("/home/tal/code/resume_tailor/terraform/terraform-sa-key.json")

}

resource "google_artifact_registry_repository" "resume_tailor_repo" {
  location      = "us-central1"
  repository_id = "resume-tailor-repo"
  description   = "Docker repository for Resume Tailor application"
  format        = "DOCKER"
}