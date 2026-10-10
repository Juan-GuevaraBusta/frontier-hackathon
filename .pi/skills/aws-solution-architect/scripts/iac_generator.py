#!/usr/bin/env python3
"""Generates CloudFormation, CDK, or Terraform skeletons for common patterns."""

import argparse
from pathlib import Path
from textwrap import dedent

PATTERNS = ("serverless-web", "event-driven", "three-tier", "real-time", "graphql", "multi-region")


def cloudformation(pattern: str, project: str) -> str:
    services = {
        "serverless-web": ["S3", "CloudFront", "ApiGateway", "Lambda", "DynamoDB", "Cognito"],
        "event-driven": ["EventBridge", "SQS", "Lambda", "StepFunctions", "DynamoDB"],
        "three-tier": ["ALB", "ECS", "Aurora", "ElastiCache", "CloudFront"],
        "real-time": ["Kinesis", "Lambda", "S3", "Athena"],
        "graphql": ["AppSync", "Lambda", "DynamoDB"],
        "multi-region": ["Route53", "CloudFront", "Lambda", "DynamoDBGlobalTable"],
    }.get(pattern, ["Lambda", "DynamoDB"])

    resources = "\n".join(
        f"  # TODO: Define AWS::{svc} resource for {project}\n  {svc}Resource:\n    Type: AWS::CloudFormation::WaitConditionHandle"
        for svc in services
    )
    return dedent(f"""\
        AWSTemplateFormatVersion: '2010-09-09'
        Description: {pattern} pattern for {project}

        Parameters:
          Environment:
            Type: String
            Default: dev
            AllowedValues: [dev, staging, prod]

        Resources:
        {resources}

        Outputs:
          Environment:
            Value: !Ref Environment
    """)


def terraform(pattern: str, project: str) -> str:
    return dedent(f"""\
        # {pattern} pattern for {project}
        terraform {{
          required_version = ">= 1.5"
          required_providers {{
            aws = {{
              source  = "hashicorp/aws"
              version = "~> 5.0"
            }}
          }}
        }}

        provider "aws" {{
          region = var.aws_region
        }}

        variable "aws_region" {{
          default = "us-east-1"
        }}

        variable "environment" {{
          default = "dev"
        }}

        variable "project_name" {{
          default = "{project}"
        }}

        # TODO: Add modules/resources for {pattern}
        # Recommended: terraform-aws-modules/lambda, terraform-aws-modules/vpc
    """)


def cdk(pattern: str, project: str) -> str:
    return dedent(f'''\
        #!/usr/bin/env python3
        """CDK skeleton: {pattern} pattern for {project}"""
        import aws_cdk as cdk
        from aws_cdk import Stack
        from constructs import Construct


        class {project.replace("-", "_").title()}Stack(Stack):
            def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
                super().__init__(scope, construct_id, **kwargs)
                # TODO: Add constructs for {pattern}
                # e.g. aws_lambda, aws_dynamodb, aws_apigatewayv2


        app = cdk.App()
        {project.replace("-", "_").title()}Stack(app, "{project}-stack")
        app.synth()
    ''')


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate IaC skeletons")
    parser.add_argument("--format", choices=["cloudformation", "terraform", "cdk"], required=True)
    parser.add_argument("--pattern", choices=PATTERNS, default="serverless-web")
    parser.add_argument("--project", default="startup-app")
    parser.add_argument("--output", "-o", help="Output file path")
    args = parser.parse_args()

    generators = {
        "cloudformation": cloudformation,
        "terraform": terraform,
        "cdk": cdk,
    }
    ext = {"cloudformation": ".yaml", "terraform": ".tf", "cdk": "_stack.py"}[args.format]
    content = generators[args.format](args.pattern, args.project)

    if args.output:
        Path(args.output).write_text(content)
        print(f"Wrote {args.output}")
    else:
        default_name = f"{args.project}-{args.pattern}{ext}"
        Path(default_name).write_text(content)
        print(f"Wrote {default_name}")


if __name__ == "__main__":
    main()
