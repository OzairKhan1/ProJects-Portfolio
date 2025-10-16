@Library("jShrLibs") _
pipeline {
    agent any

    parameters {
        string(name: 'BUILD_NUMBER', defaultValue: '1', description: 'Build number from upstream job')
    }

    environment {
        IMAGE_NAME = "ozairkhan1/flask-mysql-app"
    }

    stages {
        stage('Updating the Github Manifest File') {
            steps {
                script {
                    gitClone("https://github.com/OzairKhan1/Kubernetes-ManifestFiles.git","main")
                    dir("Kubernetes") {
                        sh """
                            sed -i "s|\\(image: ${IMAGE_NAME}:\\).*|\\1v${params.BUILD_NUMBER}|" app-deployment.yml
                        """
                    }
                }
            }
        }

        stage('Pushing the changes into manifest file') {
            steps {
                script {
                    gitPush(
                        "https://github.com/OzairKhan1/Kubernetes-ManifestFiles.git",
                        "main",
                        "gitHub-creds",
                        "Automated From Jenkins v${params.BUILD_NUMBER}"
                    )
                }
            }
        }
    }

    post {
        success {
            mail to: 'ozairk048@gmail.com',
                 subject: "✅ Pipeline SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: """Hello,

The Jenkins pipeline job '${env.JOB_NAME}' has succeeded.

Docker image updated to: ${IMAGE_NAME}:v${params.BUILD_NUMBER}
Build Number: ${params.BUILD_NUMBER}
Build URL: ${env.BUILD_URL}

Regards,
Jenkins
"""
        }
    }
}
