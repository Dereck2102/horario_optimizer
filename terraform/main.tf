provider "aws" {
  region = "us-east-1"
}

# 1. ECR Repository
resource "aws_ecr_repository" "repo" {
  name = "horarios-uce"
  force_delete = true
}

# 2. Networking (Default VPC for simplicity)
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Group - REVERTED NAME FOR IN-PLACE UPDATE
resource "aws_security_group" "sg" {
  name        = "horarios-sg"
  description = "Allow port 80"
  vpc_id      = data.aws_vpc.default.id

  # Changed to Port 80
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. IAM Role (Try to use LabRole provided by Academy)
data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

# 4. ECS Cluster
resource "aws_ecs_cluster" "cluster" {
  name = "horarios-cluster"
}

# 5. Log Group
resource "aws_cloudwatch_log_group" "logs" {
  name = "/ecs/horarios-uce"
  retention_in_days = 1
}

# 6. Task Definition - UPDATED FOR PORT 80
resource "aws_ecs_task_definition" "task" {
  family                   = "horarios-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = data.aws_iam_role.lab_role.arn
  task_role_arn            = data.aws_iam_role.lab_role.arn

  container_definitions = jsonencode([
    {
      name      = "horarios-uce"
      image     = "${aws_ecr_repository.repo.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.logs.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# 7. ECS Service
resource "aws_ecs_service" "service" {
  name            = "horarios-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.task.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  force_new_deployment = true

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.sg.id]
    assign_public_ip = true
  }
}

output "ecr_repo_url" {
  value = aws_ecr_repository.repo.repository_url
}
