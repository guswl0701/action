# Django 앱 이미지 푸시
resource "null_resource" "push_django_image" {
  triggers = {
    always_run = "${timestamp()}"
  }

  provisioner "local-exec" {
    command = <<EOF
      aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin ${data.aws_ecr_repository.django_app.repository_url}
      docker pull wangamy/newticket:latest
      docker tag wangamy/newticket:latest ${data.aws_ecr_repository.django_app.repository_url}:latest
      docker push ${data.aws_ecr_repository.django_app.repository_url}:latest
    EOF
  }
}

# ECS 서비스가 새 이미지를 사용하도록 강제 업데이트
resource "null_resource" "force_ecs_deployment" {
  triggers = {
    django_image_update = null_resource.push_django_image.id
  }

  provisioner "local-exec" {
    command = "aws ecs update-service --cluster ${data.aws_ecs_cluster.main.cluster_name} --service ${data.aws_ecs_service.app.service_name} --force-new-deployment --region ap-northeast-2"
  }

  depends_on = [null_resource.push_django_image]
}

# 기존 리소스 참조를 위한 data 소스 추가
data "aws_ecr_repository" "django_app" {
  name = "django-app-repo"
}

data "aws_ecs_cluster" "main" {
  cluster_name = "main-cluster"
}

data "aws_ecs_service" "app" {
  cluster_arn = data.aws_ecs_cluster.main.arn
  service_name = "app-service"
}