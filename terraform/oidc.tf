locals {
  plan_name  = "gh_cac_report_plan_role"
  admin_name = "gh_cac_report_apply_role"
}

module "gh_oidc_roles" {
  source   = "github.com/cds-snc/terraform-modules//gh_oidc_role?ref=v7.0.2"
  org_name = "cds-snc"
  roles = [
    {
      name      = local.plan_name
      repo_name = "aws-guardrails-cac-solution"
      claim     = "*"
    },
    {
      name      = local.admin_name
      repo_name = "aws-guardrails-cac-solution"
      claim     = "ref:refs/heads/main"
    }
  ]

  billing_tag_value = var.billing_code

}

data "aws_iam_policy" "readonly" {
  name = "ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "readonly" {
  role       = local.plan_name
  policy_arn = data.aws_iam_policy.readonly.arn
}

module "attach_tf_plan_policy" {
  source            = "github.com/cds-snc/terraform-modules//attach_tf_plan_policy?ref=v6.1.5"
  account_id        = var.aws_account_id
  role_name         = local.plan_name
  bucket_name       = "cac-guardrails-tfstate"
  lock_table_name   = "terraform-state-lock-dynamo"
  billing_tag_value = var.billing_code
}

data "aws_iam_policy" "admin" {
  name = "AdministratorAccess"
}

resource "aws_iam_role_policy_attachment" "admin" {
  role       = local.admin_name
  policy_arn = data.aws_iam_policy.admin.arn
}