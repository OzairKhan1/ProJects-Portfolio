resource "aws_key_pair" "terraformKey" {
  key_name   = "terraformKey"
  public_key = file("/home/ubuntu/.ssh/id_ed25519.pub")
}

resource "aws_default_vpc" "myVpc" {
  tags = {
    Name = "myVpc"
  }
}

resource "aws_security_group" "mySgroup" {
  name        = "FlaskMysqlSgroup"
  description = "This will be used for Flask-Mysql-App"
  vpc_id      = aws_default_vpc.myVpc.id

  tags = {
    Name = "mySg"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSh"
  }

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "mySql"
  }

  ingress {
    from_port   = 30004
    to_port     = 30004
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "NodePort for FlaskApp"
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
     description = "flaskApp port"
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Jenkins"
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Grafana"
  }

  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Prometheus"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "terraInstance" {
  key_name               = aws_key_pair.terraformKey.key_name
  vpc_security_group_ids = [aws_security_group.mySgroup.id]
  ami                    = var.ec2_ami_id
  instance_type          = var.ec2_type

  # Root volume (8 GB)
  root_block_device {
    volume_size = var.ec2_block_storage
    volume_type = "gp3"
  }

  tags = {
    Name = "Flask-Mysql-app"
  }
}
