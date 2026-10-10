#!/usr/bin/env python3
"""Analyzes AWS cost profiles and returns optimization recommendations."""

import argparse
import json

RECOMMENDATIONS = {
    "serverless": [
        "Right-size Lambda memory (test 128MB–1024MB for cost/performance balance)",
        "Set CloudWatch Logs retention to 7–14 days for non-prod",
        "Use DynamoDB on-demand for variable traffic; provisioned for steady loads",
        "Replace NAT Gateway with VPC endpoints for S3, DynamoDB, Secrets Manager",
        "Enable S3 Intelligent-Tiering for unpredictable access patterns",
    ],
    "containers": [
        "Use Fargate Spot for non-critical workloads (up to 70% savings)",
        "Right-size task CPU/memory based on CloudWatch Container Insights",
        "Use Savings Plans for steady Fargate/EC2 usage",
        "Consolidate dev/staging onto smaller clusters with namespace isolation",
    ],
    "general": [
        "Tag all resources (Environment, Team, CostCenter) for Cost Explorer allocation",
        "Enable AWS Budgets alerts at 80% and 100% of monthly target",
        "Review Trusted Advisor cost optimization checks monthly",
        "Delete unused EBS volumes, Elastic IPs, and old AMIs/snapshots",
        "Use S3 lifecycle policies: Standard → IA → Glacier for backups",
        "Prefer same-AZ traffic to reduce data transfer charges",
    ],
}

SPEND_THRESHOLDS = [
    (500, "Focus on serverless MVP stack; avoid NAT Gateway in dev"),
    (2000, "Evaluate Savings Plans for predictable compute; add ElastiCache"),
    (10000, "Reserved capacity, multi-region only where SLA requires it"),
]


def optimize(monthly_spend: float, workload: str) -> dict:
    recs = list(RECOMMENDATIONS.get(workload, [])) + RECOMMENDATIONS["general"]
    stage_advice = next((msg for limit, msg in SPEND_THRESHOLDS if monthly_spend < limit), SPEND_THRESHOLDS[-1][1])

    potential_savings = "15-30%" if monthly_spend > 500 else "10-20%"
    return {
        "monthly_spend_usd": monthly_spend,
        "workload": workload,
        "stage_advice": stage_advice,
        "potential_savings": potential_savings,
        "recommendations": recs,
        "quick_wins": recs[:3],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="AWS cost optimization advisor")
    parser.add_argument("--monthly-spend", type=float, required=True)
    parser.add_argument("--workload", choices=["serverless", "containers", "general"], default="general")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = optimize(args.monthly_spend, args.workload)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"Monthly spend: ${result['monthly_spend_usd']:,.0f}")
    print(f"Potential savings: {result['potential_savings']}")
    print(f"Stage advice: {result['stage_advice']}\n")
    print("Recommendations:")
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    main()
