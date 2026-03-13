# ═══════════════════════════════════════════════════════════
# Module: storage — variables.tf
# ═══════════════════════════════════════════════════════════

variable "project_name" {
  description = "Nombre del proyecto. Se usa como prefijo en todos los recursos."
  type        = string
}

variable "environment" {
  description = "Entorno de deployment (dev, staging, prod)."
  type        = string
}
