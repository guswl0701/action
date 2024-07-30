# Django 앱 이미지 푸시
resource "null_resource" "push_django_image" {
  provisioner "local-exec" {
    command = <<EOF
      aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin ${aws_ecr_repository.django_app.repository_url}
      docker pull wangamy/newtickettopia:latest
      docker tag wangamy/newtickettopia:latest ${aws_ecr_repository.django_app.repository_url}:latest
      docker push ${aws_ecr_repository.django_app.repository_url}:latest
    EOF
  }

  depends_on = [aws_ecr_repository.django_app]
}

# ECS 서비스가 새 이미지를 사용하도록 강제 업데이트
resource "null_resource" "force_ecs_deployment" {
  provisioner "local-exec" {
    command = "aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.app.name} --force-new-deployment --region ap-northeast-2"
  }

  depends_on = [
    null_resource.push_django_image,
    null_resource.build_and_push_nginx_image,
    aws_ecs_service.app
  ]
}
