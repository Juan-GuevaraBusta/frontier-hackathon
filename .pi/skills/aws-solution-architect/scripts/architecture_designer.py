#!/usr/bin/env python3
"""Recommends AWS architecture patterns and services based on startup requirements."""

import argparse
import json
import sys

PATTERNS = {
    "serverless-web": {
        "name": "Serverless Web Application",
        "services": ["S3", "CloudFront", "API Gateway", "Lambda", "DynamoDB", "Cognito"],
        "cost_range": "$50-500/month",
        "best_for": ["SaaS", "mobile backend", "low-traffic web"],
    },
    "event-driven": {
        "name": "Event-Driven Microservices",
        "services": ["EventBridge", "Lambda", "SQS", "Step Functions", "DynamoDB", "S3"],
        "cost_range": "$100-1000/month",
        "best_for": ["async workflows", "decoupled microservices"],
    },
    "three-tier": {
        "name": "Modern Three-Tier Application",
        "services": ["ALB", "ECS Fargate", "Aurora", "ElastiCache", "CloudFront", "S3"],
        "cost_range": "$300-2000/month",
        "best_for": ["e-commerce", "CMS", "dynamic web apps"],
    },
    "real-time": {
        "name": "Real-Time Data Processing",
        "services": ["Kinesis", "Lambda", "S3", "Athena", "QuickSight", "CloudWatch"],
        "cost_range": "$200-1500/month",
        "best_for": ["IoT", "analytics", "log streaming"],
    },
    "graphql": {
        "name": "GraphQL API Backend",
        "services": ["AppSync", "Lambda", "DynamoDB", "Cognito"],
        "cost_range": "$50-400/month",
        "best_for": ["mobile apps", "SPA", "flexible queries"],
    },
    "multi-region": {
        "name": "Multi-Region High Availability",
        "services": ["Route 53", "CloudFront", "Lambda/ECS", "DynamoDB Global Tables", "S3 CRR"],
        "cost_range": "1.5-2x single region",
        "best_for": ["global apps", "DR", "compliance"],
    },
}

TYPE_TO_PATTERN = {
    "web-app": "three-tier",
    "mobile-backend": "serverless-web",
    "saas": "serverless-web",
    "data-pipeline": "real-time",
    "microservices": "event-driven",
    "iot": "real-time",
    "graphql-api": "graphql",
}


def recommend(app_type: str, users: int, budget: float, compliance: list[str]) -> dict:
    pattern_key = TYPE_TO_PATTERN.get(app_type, "serverless-web")
    if users >= 100_000 or "multi-region" in compliance:
        pattern_key = "multi-region"
    elif users < 1_000 and budget < 200:
        pattern_key = "serverless-web"

    pattern = PATTERNS[pattern_key]
    stage = "mvp" if users < 10_000 else "growth" if users < 100_000 else "scale-up"

    return {
        "recommended_pattern": pattern_key,
        "pattern_name": pattern["name"],
        "services": pattern["services"],
        "estimated_cost": pattern["cost_range"],
        "startup_stage": stage,
        "compliance_notes": _compliance_notes(compliance),
        "next_steps": [
            f"Run: python scripts/serverless_stack.py --pattern {pattern_key}",
            f"Run: python scripts/iac_generator.py --format cloudformation --pattern {pattern_key}",
            "Validate with: python scripts/security_auditor.py",
        ],
    }


def _compliance_notes(compliance: list[str]) -> list[str]:
    notes = []
    mapping = {
        "gdpr": "Use eu-west-1 or eu-central-1; enable encryption and data residency controls",
        "hipaa": "Use BAA-eligible services only; VPC private subnets; CloudTrail audit logging",
        "soc2": "Enable AWS Config, Audit Manager, least-privilege IAM",
        "pci-dss": "Isolate cardholder data; WAF on API Gateway; no sensitive data in logs",
    }
    for c in compliance:
        if c in mapping:
            notes.append(mapping[c])
    return notes


def main() -> None:
    parser = argparse.ArgumentParser(description="AWS architecture pattern recommender")
    parser.add_argument("--type", required=True, choices=list(TYPE_TO_PATTERN.keys()))
    parser.add_argument("--users", type=int, default=1000)
    parser.add_argument("--budget", type=float, default=500)
    parser.add_argument("--compliance", default="", help="Comma-separated: gdpr,hipaa,soc2,pci-dss")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    compliance = [c.strip().lower() for c in args.compliance.split(",") if c.strip()]
    result = recommend(args.type, args.users, args.budget, compliance)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"Pattern: {result['pattern_name']} ({result['recommended_pattern']})")
    print(f"Stage: {result['startup_stage']}")
    print(f"Services: {', '.join(result['services'])}")
    print(f"Cost: {result['estimated_cost']}")
    if result["compliance_notes"]:
        print("\nCompliance:")
        for note in result["compliance_notes"]:
            print(f"  - {note}")
    print("\nNext steps:")
    for step in result["next_steps"]:
        print(f"  - {step}")


if __name__ == "__main__":
    main()
