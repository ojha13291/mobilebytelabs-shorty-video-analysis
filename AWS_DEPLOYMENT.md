# AWS Deployment Guide for Instagram Reels Analyzer

This guide provides instructions for deploying the Instagram Reels Analyzer application to AWS using various services.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally
- Git repository with your application code

## Deployment Options

### Option 1: AWS Elastic Container Service (ECS) with Fargate

This is the recommended approach for containerized applications.

#### Step 1: Create an ECR Repository

```bash
aws ecr create-repository --repository-name instagram-reels-analyzer --image-scanning-configuration scanOnPush=true
```

#### Step 2: Authenticate Docker to ECR

```bash
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<your-region>.amazonaws.com
```

#### Step 3: Build and Push Docker Image

```bash
docker build -t instagram-reels-analyzer .
docker tag instagram-reels-analyzer:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/instagram-reels-analyzer:latest
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/instagram-reels-analyzer:latest
```

#### Step 4: Create ECS Cluster, Task Definition, and Service

1. Create an ECS cluster in the AWS Management Console
2. Create a Task Definition:
   - Use the Fargate launch type
   - Specify the ECR image URI
   - Configure CPU and memory requirements (recommended: 2 vCPU, 4GB memory)
   - Set environment variables for:
     - MISTRAL_API_KEY
     - INSTA_USER (optional)
     - INSTA_PASS (optional)
   - Map port 8501
3. Create a Service:
   - Use the Fargate launch type
   - Configure desired number of tasks (start with 1)
   - Set up Application Load Balancer for HTTPS access
   - Configure auto-scaling if needed

### Option 2: AWS Elastic Beanstalk with Docker

#### Step 1: Install EB CLI

```bash
pip install awsebcli
```

#### Step 2: Initialize EB Application

```bash
eb init -p docker instagram-reels-analyzer
```

#### Step 3: Create Environment and Deploy

```bash
eb create instagram-reels-analyzer-env
```

#### Step 4: Configure Environment Variables

In the AWS Management Console:
1. Go to Elastic Beanstalk > Environments > Your Environment
2. Navigate to Configuration > Software
3. Add environment variables:
   - MISTRAL_API_KEY
   - INSTA_USER (optional)
   - INSTA_PASS (optional)

### Option 3: AWS App Runner

For a simpler deployment process:

1. Push your Docker image to ECR as in Option 1
2. Create an App Runner service in the AWS Management Console
3. Select your ECR image
4. Configure environment variables
5. Set port to 8501

## Security Considerations

1. **Secrets Management**: Store sensitive information like API keys and credentials in AWS Secrets Manager or Parameter Store
2. **Network Security**: Configure security groups to restrict access
3. **IAM Roles**: Use the principle of least privilege for service roles
4. **HTTPS**: Configure SSL/TLS for all public endpoints

## Monitoring and Scaling

1. Set up CloudWatch alarms for CPU, memory, and application metrics
2. Configure auto-scaling based on these metrics
3. Use AWS X-Ray for tracing (requires additional configuration)

## Cost Optimization

1. Use Fargate Spot instances for non-critical workloads
2. Implement auto-scaling to match demand
3. Consider using Reserved Instances for predictable workloads
4. Monitor costs with AWS Cost Explorer

## Troubleshooting

1. Check CloudWatch Logs for application logs
2. Verify security group and network configurations
3. Ensure environment variables are correctly set
4. Check container health checks

## Continuous Deployment

Consider setting up a CI/CD pipeline using AWS CodePipeline, GitHub Actions, or similar tools to automate the build and deployment process.