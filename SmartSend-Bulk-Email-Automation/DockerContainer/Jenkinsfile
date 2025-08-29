pipeline {
    agent { label 'docNode' } // Runing on workerNodes name docNode. 

    environment {
        IMAGE_NAME = "ozairkhan1/smartsend"
    }

    stages {
        stage('Creating Docker File') {
            steps {
                dir('/home/ubuntu/Jenkins/workspace/EmailAutomation/SmartSend-Bulk-Email-Automation/DockerContainer') {
                    sh 'docker build -t $IMAGE_NAME:latest .'
                }
            }
        }

        stage('Docker Login and Push') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerHub-cred',
                                                      usernameVariable: 'DOCKER_USER',
                                                      passwordVariable: 'DOCKER_PASS')]) {
                        // Login to DockerHub
                        sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'

                        // Push the image
                        sh 'docker push $IMAGE_NAME:latest'
                        sh 'docker run -d -p 8501:8501 -v smartsend_logs:/SmartSend/logs ozairkhan1/smartsend:latest'
                        // Logout for safety
                        sh 'docker logout'
                    } // closes withCredentials
                } // closes script
            }
        }
    }
}
