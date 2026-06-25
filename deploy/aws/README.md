# AWS Deployment Guide

Deploy AI Resume Analyzer to AWS using various services.

## Option 1: AWS Elastic Beanstalk

### Prerequisites
- AWS CLI installed and configured
- EB CLI installed: `pip install awsebcli`

### Steps

1. **Initialize Elastic Beanstalk**
```bash
cd backend
eb init -p python-3.11 ai-resume-analyzer --region us-east-1
```

2. **Create environment**
```bash
eb create production-env
```

3. **Set environment variables**
```bash
eb setenv OPENAI_API_KEY=your-key-here
eb setenv ANTHROPIC_API_KEY=your-key-here
eb setenv ENVIRONMENT=production
```

4. **Deploy**
```bash
eb deploy
```

5. **Open application**
```bash
eb open
```

## Option 2: AWS ECS (Elastic Container Service)

### Prerequisites
- Docker images pushed to ECR
- ECS cluster created

### Steps

1. **Build and push Docker image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t ai-resume-analyzer-backend ./backend

# Tag image
docker tag ai-resume-analyzer-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-resume-analyzer:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-resume-analyzer:latest
```

2. **Create task definition** (see `task-definition.json`)

3. **Create service**
```bash
aws ecs create-service \
  --cluster ai-resume-analyzer-cluster \
  --service-name ai-resume-analyzer-service \
  --task-definition ai-resume-analyzer-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

## Option 3: AWS Lambda + API Gateway

### Prerequisites
- Serverless Framework: `npm install -g serverless`

### Steps

1. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt -t ./package
```

2. **Deploy with Serverless**
```bash
serverless deploy --stage production
```

## Frontend Deployment (S3 + CloudFront)

1. **Build frontend**
```bash
cd frontend
npm run build
```

2. **Create S3 bucket**
```bash
aws s3 mb s3://ai-resume-analyzer-frontend
```

3. **Upload files**
```bash
aws s3 sync dist/ s3://ai-resume-analyzer-frontend --acl public-read
```

4. **Create CloudFront distribution**
```bash
aws cloudfront create-distribution \
  --origin-domain-name ai-resume-analyzer-frontend.s3.amazonaws.com \
  --default-root-object index.html
```

## Environment Variables

Set these in AWS Systems Manager Parameter Store or Secrets Manager:

```bash
aws ssm put-parameter \
  --name /ai-resume-analyzer/openai-api-key \
  --value "your-key" \
  --type SecureString

aws ssm put-parameter \
  --name /ai-resume-analyzer/anthropic-api-key \
  --value "your-key" \
  --type SecureString
```

## Monitoring

- **CloudWatch Logs**: Automatic logging
- **CloudWatch Metrics**: CPU, memory, requests
- **X-Ray**: Distributed tracing (optional)

## Cost Estimation

- **ECS Fargate**: ~$30-50/month (2 tasks)
- **S3 + CloudFront**: ~$5-10/month
- **API Gateway**: Pay per request
- **Total**: ~$40-70/month

## Scaling

- **Auto Scaling**: Configure based on CPU/memory
- **Load Balancer**: Distribute traffic
- **Multi-AZ**: High availability