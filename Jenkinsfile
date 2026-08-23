pipeline {
    agent any

    environment {
        APP_NAME = 'buffet-reservation-app'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Lint & Code Check') {
            steps {
                echo 'Running Python syntax checks...'
                sh 'python3 -m py_compile main.py models.py database.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building application Docker image...'
                sh 'docker build -t buffet-app:latest .'
            }
        }

        stage('Verify Containers') {
            steps {
                echo 'Verifying Docker Compose stack config...'
                sh 'docker compose config'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution complete.'
        }
        success {
            echo 'Build successfully finished!'
        }
        failure {
            echo 'Build failed. Please check logs.'
        }
    }
}
