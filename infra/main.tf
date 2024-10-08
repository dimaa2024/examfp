provider "aws" {
  region = "us-east-1"
}

resource "aws_secretsmanager_secret" "restaurant_api_secrets" {
  name = "restaurant_api_secrets"
}

resource "aws_secretsmanager_secret_version" "restaurant_api_secrets_version" {
  secret_id     = aws_secretsmanager_secret.restaurant_api_secrets.id
  secret_string = jsonencode({
    SECRET_KEY             = "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "sqlite:///restaurants.db"
    ADMIN_PASSWORD         = "admin"
  })
}

resource "aws_instance" "restaurant_api" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "RestaurantSearchAPI"
  }
}