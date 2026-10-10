#!/usr/bin/env python3
"""AWS security best-practices checklist and compliance validation hints."""

import argparse
import json

CHECKLIST = [
    ("IAM", "No wildcard (*) actions on production roles; use resource-scoped policies"),
    ("IAM", "Enable MFA for root and privileged users"),
    ("IAM", "Use IAM roles for Lambda/ECS/EC2; no long-lived access keys in code"),
    ("S3", "Block Public Access enabled on all buckets"),
    ("S3", "Default encryption (SSE-S3 or SSE-KMS) enabled"),
    ("Secrets", "Credentials in Secrets Manager or SSM Parameter Store (SecureString)"),
    ("Network", "Production workloads in private subnets; ALB/API Gateway as entry point"),
    ("Network", "Security groups follow least privilege (specific ports/sources)"),
    ("Logging", "CloudTrail enabled in all regions; log file validation on"),
    ("Logging", "VPC Flow Logs enabled for production VPCs"),
    ("API", "API Gateway throttling and WAF rules configured"),
    ("Data", "Encryption in transit (TLS 1.2+) for all external endpoints"),
]

COMPLIANCE = {
    "gdpr": [
        "Data residency: deploy in EU regions for EU users",
        "Enable S3 Object Lock or versioning for audit trails",
        "Document data processing; support deletion requests",
    ],
    "hipaa": [
        "Sign AWS BAA; use only HIPAA-eligible services",
        "Encrypt PHI at rest and in transit",
        "Audit all access via CloudTrail; restrict PHI to private subnets",
    ],
    "soc2": [
        "AWS Config rules for continuous compliance monitoring",
        "Centralized logging with restricted access",
        "Regular access reviews and automated key rotation",
    ],
    "pci-dss": [
        "Isolate cardholder data environment (CDE) in dedicated VPC",
        "WAF + TLS 1.2+ on all payment-facing APIs",
        "Never log PAN/CVV; tokenize at gateway",
    ],
}


def audit(compliance: list[str]) -> dict:
    compliance_items = []
    for c in compliance:
        if c in COMPLIANCE:
            compliance_items.append({"framework": c.upper(), "requirements": COMPLIANCE[c]})

    return {
        "security_checklist": [{"category": cat, "item": item} for cat, item in CHECKLIST],
        "compliance": compliance_items,
        "priority_actions": [
            "Enable S3 Block Public Access account-wide",
            "Rotate or remove unused IAM access keys",
            "Set CloudWatch Logs retention (avoid indefinite retention costs)",
            "Review IAM policies for Action: * and Resource: *",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="AWS security audit checklist")
    parser.add_argument("--compliance", default="", help="Comma-separated: gdpr,hipaa,soc2,pci-dss")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    frameworks = [c.strip().lower() for c in args.compliance.split(",") if c.strip()]
    result = audit(frameworks)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("Security Checklist:")
    current_cat = None
    for entry in result["security_checklist"]:
        if entry["category"] != current_cat:
            current_cat = entry["category"]
            print(f"\n[{current_cat}]")
        print(f"  [ ] {entry['item']}")

    if result["compliance"]:
        print("\nCompliance Requirements:")
        for block in result["compliance"]:
            print(f"\n  {block['framework']}:")
            for req in block["requirements"]:
                print(f"    - {req}")

    print("\nPriority Actions:")
    for action in result["priority_actions"]:
        print(f"  ! {action}")


if __name__ == "__main__":
    main()
