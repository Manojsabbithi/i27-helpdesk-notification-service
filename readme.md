# i27 Helpdesk Notification Service

FastAPI notification service for the i27 Helpdesk microservices application.

The service processes helpdesk notification events, builds email content, records notification activity, and sends email through Amazon SES in the AWS environment.

## Service Architecture

```text
Ticket Service
     |
     v
Notification Service
     |
     +--> Amazon SES       email delivery
     |
     +--> MySQL / RDS      notification data
```

The broader AWS infrastructure and platform implementation is documented in:

[i27-helpdesk-aws-infra](https://github.com/Manojsabbithi/i27-helpdesk-aws-infra)

## Amazon SES Integration

The AWS implementation sends email through Amazon SES using the AWS SDK for Python (`boto3`).

The active email path uses the SES v2 client and obtains AWS credentials through the EKS workload identity rather than embedding AWS access keys in the application.

Implemented AWS controls include:

- Amazon SES for application email delivery
- IAM Roles for Service Accounts (IRSA)
- Kubernetes service account mapped to a scoped IAM role
- temporary AWS credentials supplied to the pod by AWS
- AWS Region and sender configuration supplied through runtime environment variables
- no long-lived AWS access keys stored in the application repository

The service fails when the required SES sender configuration is not provided rather than silently using a hard-coded sender.

## Notification Processing

The service processes notification events and determines the appropriate recipients and email content before sending messages through Amazon SES.

The implementation includes:

- event-driven notification processing
- recipient selection
- plain-text and HTML email generation
- reusable email templates
- email delivery through Amazon SES
- notification logging through SQLAlchemy

## Data Layer

The service uses SQLAlchemy and PyMySQL for database access.

In the AWS environment, database configuration is supplied at runtime for integration with the helpdesk MySQL database.

## AWS CI/CD Pipeline

The AWS-specific Jenkins pipeline is defined in `Jenkinsfile.aws`.

```text
Checkout
   |
   v
Python Validation
   |
   v
SonarQube Analysis
   |
   v
Quality Gate
   |
   v
Docker Build
   |
   v
Amazon ECR Push
   |
   v
ECR Image Verification
   |
   v
Amazon EKS Deployment
```

AWS Kubernetes manifests are stored under `k8s/aws/`, including the Deployment, Service, ConfigMap, and IRSA-enabled ServiceAccount.

## Technology

- Python 3.11
- FastAPI
- Uvicorn
- SQLAlchemy
- PyMySQL
- boto3
- Docker
- Jenkins
- SonarQube
- Amazon SES
- Amazon ECR
- Amazon EKS
- IAM / IRSA

## Container

The service runs in a Python 3.11 slim container and exposes port `8084`.

## Project Context

This repository originated from the i27Academy Helpdesk application and is used here as part of an independent AWS DevOps portfolio implementation.

The AWS-focused work includes Amazon SES integration, IRSA-based workload identity, runtime configuration, Jenkins and SonarQube integration, Docker containerization, Amazon ECR publishing, and Amazon EKS deployment.
