variable "ec2_type"{

	default = "t2.micro"
	type = string
}

variable "ec2_ami_id"{

        default = "ami-0360c520857e3138f"
        type = string
}

variable "ec2_block_storage"{

        default = 12
        type = number
}

