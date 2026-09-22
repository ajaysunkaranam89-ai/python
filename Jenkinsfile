pipeline {
    agent any

    environment {
        APP_NAME        = "python-app"
        NAMESPACE       = "python-app"
        IMAGE_NAME      = "python-k8s-app"
        IMAGE_TAG       = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('Load Image into Kind') {
            steps {
                echo "Loading Docker image into Kind cluster..."
                sh """
                    kind load docker-image ${IMAGE_NAME}:${IMAGE_TAG}
                """
            }
        }

        stage('Deploy Namespace') {
            steps {
                echo "Creating/updating Kubernetes namespace..."
                sh """
                    kubectl apply -f k8s/namespace.yaml
                """
            }
        }

        stage('Deploy ConfigMap') {
            steps {
                echo "Deploying ConfigMap..."
                sh """
                    kubectl apply -f k8s/configmap.yaml -n ${NAMESPACE}
                """
            }
        }

        stage('Deploy Secret') {
            steps {
                echo "Deploying Secret..."
                sh """
                    kubectl apply -f k8s/secret.yaml -n ${NAMESPACE}
                """
            }
        }

        stage('Deploy PVC') {
            steps {
                echo "Deploying PVC..."
                sh """
                    kubectl apply -f k8s/pvc.yaml -n ${NAMESPACE}
                """
            }
        }

        stage('Deploy Application') {
            steps {
                echo "Deploying Python application..."
                sh """
                    kubectl apply -f k8s/deployment.yaml -n ${NAMESPACE}
                    kubectl apply -f k8s/service.yaml -n ${NAMESPACE}
                """
            }
        }

        stage('Deploy Ingress') {
            steps {
                echo "Deploying Ingress..."
                sh """
                    kubectl apply -f k8s/ingress.yaml -n ${NAMESPACE}
                """
            }
        }

        stage('Update Image') {
            steps {
                echo "Updating deployment image..."
                sh """
                    kubectl set image deployment/${APP_NAME} ${APP_NAME}=${IMAGE_NAME}:${IMAGE_TAG} -n ${NAMESPACE}
                """
            }
        }

        stage('Wait for Rollout') {
            steps {
                echo "Waiting for Kubernetes rollout..."
                sh """
                    kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE} --timeout=180s
                """
            }
        }

        stage('Verify Deployment') {
            steps {
                echo "Checking Kubernetes resources..."
                sh """
                    kubectl get pods -n ${NAMESPACE}
                    kubectl get deployment -n ${NAMESPACE}
                    kubectl get service -n ${NAMESPACE}
                    kubectl get ingress -n ${NAMESPACE}
                """
            }
        }
    }

    post {
        success {
            echo "======================================"
            echo "Deployment SUCCESSFUL"
            echo "Application: ${APP_NAME}"
            echo "Namespace: ${NAMESPACE}"
            echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
            echo "======================================"
        }
        failure {
            echo "======================================"
            echo "Deployment FAILED"
            echo "Check Jenkins console output."
            echo "======================================"
        }
    }
}
