#!/usr/bin/env python3
"""Generates a serverless stack CloudFormation template (Lambda, API Gateway, DynamoDB)."""

import argparse
from pathlib import Path
from textwrap import dedent


def generate_template(stack_name: str) -> str:
    return dedent(f"""\
        AWSTemplateFormatVersion: '2010-09-09'
        Description: Serverless stack - {stack_name}

        Parameters:
          StageName:
            Type: String
            Default: prod

        Resources:
          ApiGateway:
            Type: AWS::ApiGatewayV2::Api
            Properties:
              Name: !Sub '${{StageName}}-{stack_name}-api'
              ProtocolType: HTTP
              CorsConfiguration:
                AllowOrigins: ['*']
                AllowMethods: ['GET', 'POST', 'PUT', 'DELETE']
                AllowHeaders: ['Content-Type', 'Authorization']

          LambdaExecutionRole:
            Type: AWS::IAM::Role
            Properties:
              AssumeRolePolicyDocument:
                Version: '2012-10-17'
                Statement:
                  - Effect: Allow
                    Principal:
                      Service: lambda.amazonaws.com
                    Action: sts:AssumeRole
              ManagedPolicyArns:
                - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
              Policies:
                - PolicyName: DynamoDBAccess
                  PolicyDocument:
                    Version: '2012-10-17'
                    Statement:
                      - Effect: Allow
                        Action:
                          - dynamodb:GetItem
                          - dynamodb:PutItem
                          - dynamodb:Query
                          - dynamodb:UpdateItem
                        Resource: !GetAtt DataTable.Arn

          ApiFunction:
            Type: AWS::Lambda::Function
            Properties:
              FunctionName: !Sub '${{StageName}}-{stack_name}-handler'
              Runtime: python3.12
              Handler: index.handler
              Role: !GetAtt LambdaExecutionRole.Arn
              Timeout: 29
              MemorySize: 256
              Environment:
                Variables:
                  TABLE_NAME: !Ref DataTable
              Code:
                ZipFile: |
                  import json, os, boto3
                  dynamodb = boto3.resource('dynamodb')
                  table = dynamodb.Table(os.environ['TABLE_NAME'])

                  def handler(event, context):
                      return {{
                          'statusCode': 200,
                          'headers': {{'Content-Type': 'application/json'}},
                          'body': json.dumps({{'message': 'OK', 'path': event.get('rawPath')}})
                      }}

          DataTable:
            Type: AWS::DynamoDB::Table
            Properties:
              TableName: !Sub '${{StageName}}-{stack_name}-data'
              BillingMode: PAY_PER_REQUEST
              AttributeDefinitions:
                - AttributeName: pk
                  AttributeType: S
                - AttributeName: sk
                  AttributeType: S
              KeySchema:
                - AttributeName: pk
                  KeyType: HASH
                - AttributeName: sk
                  KeyType: RANGE
              PointInTimeRecoverySpecification:
                PointInTimeRecoveryEnabled: true

          ApiIntegration:
            Type: AWS::ApiGatewayV2::Integration
            Properties:
              ApiId: !Ref ApiGateway
              IntegrationType: AWS_PROXY
              IntegrationUri: !Sub 'arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/${{ApiFunction.Arn}}/invocations'
              PayloadFormatVersion: '2.0'

          ApiRoute:
            Type: AWS::ApiGatewayV2::Route
            Properties:
              ApiId: !Ref ApiGateway
              RouteKey: 'ANY /{{proxy+}}'
              Target: !Sub 'integrations/${{ApiIntegration}}'

          ApiStage:
            Type: AWS::ApiGatewayV2::Stage
            Properties:
              ApiId: !Ref ApiGateway
              StageName: !Ref StageName
              AutoDeploy: true

          LambdaPermission:
            Type: AWS::Lambda::Permission
            Properties:
              Action: lambda:InvokeFunction
              FunctionName: !Ref ApiFunction
              Principal: apigateway.amazonaws.com
              SourceArn: !Sub 'arn:aws:execute-api:${{AWS::Region}}:${{AWS::AccountId}}:${{ApiGateway}}/*'

        Outputs:
          ApiEndpoint:
            Value: !Sub 'https://${{ApiGateway}}.execute-api.${{AWS::Region}}.amazonaws.com/${{StageName}}'
          TableName:
            Value: !Ref DataTable
    """)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate serverless CloudFormation stack")
    parser.add_argument("--stack-name", default="startup-api")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    args = parser.parse_args()

    template = generate_template(args.stack_name)
    if args.output:
        Path(args.output).write_text(template)
        print(f"Wrote {args.output}")
    else:
        print(template)


if __name__ == "__main__":
    main()
