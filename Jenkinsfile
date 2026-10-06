pipeline {
    agent any

    environment {
        APP_NAME        = "python-app"
        NAMESPACE       = "python-app"
        IMAGE_NAME      = "python-k8s-app"
        IMAGE_TAG       = "${BUILD_NUMBER}"
        REGISTRY_PUSH   = "registry.registry.svc.cluster.local:5000"
        REGISTRY_PULL   = "localhost:30600"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('Check commit') {
            // Jenkins' own manifest-update commit must not trigger another build (avoids an
            // infinite build loop, since SCM polling can't tell its own commit apart from a
            // real code change otherwise).
            steps {
                script {
                    def msg = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
                    env.SKIP_CI = msg.contains('[skip ci]') ? 'true' : 'false'
                    if (env.SKIP_CI == 'true') {
                        currentBuild.description = 'Skipped: manifest-update commit'
                        echo 'Latest commit was made by Jenkins - nothing to build.'
                    }
                }
            }
        }

        stage('SonarQube Analysis') {
            // Scanner runs as a throw-away container in the dind daemon; the workspace is copied in with
            // docker cp (dind can't see /var/jenkins_home). Settings live in sonar-project.properties.
            // sonar.qualitygate.wait=true fails this stage if the quality gate fails.
            when { environment name: 'SKIP_CI', value: 'false' }
            steps {
                withCredentials([usernamePassword(credentialsId: 'Sonarcube', usernameVariable: 'SONAR_USER', passwordVariable: 'SONAR_PASS')]) {
                    sh '''
                        export SONAR_TOKEN="$SONAR_PASS"
                        CID=$(docker create --network host \
                            -e SONAR_HOST_URL=http://sonarqube.sonarqube.svc.cluster.local:9000 \
                            -e SONAR_TOKEN \
                            sonarsource/sonar-scanner-cli -Dsonar.qualitygate.wait=true)
                        trap 'docker rm -f "$CID" >/dev/null 2>&1' EXIT
                        docker cp . "$CID":/usr/src
                        docker start -a "$CID"
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            when { environment name: 'SKIP_CI', value: 'false' }
            steps {
                echo "Building Docker image..."
                sh """
                    docker build -t ${REGISTRY_PUSH}/${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('Push Image to Registry') {
            when { environment name: 'SKIP_CI', value: 'false' }
            steps {
                echo "Pushing Docker image to in-cluster registry..."
                sh """
                    docker push ${REGISTRY_PUSH}/${IMAGE_NAME}:${IMAGE_TAG}
                """
            }
        }

        stage('Update Manifest & Push') {
            when { environment name: 'SKIP_CI', value: 'false' }
            steps {
                echo "Updating deployment manifest with new image tag..."
                sh """
                    sed -i "s#image: .*#image: ${REGISTRY_PULL}/${IMAGE_NAME}:${IMAGE_TAG}#" k8s/deployment.yaml
                """
                withCredentials([usernamePassword(credentialsId: 'git', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    sh """
                        git config user.email "jenkins@ci.local"
                        git config user.name "Jenkins CI"
                        git add k8s/deployment.yaml
                        git commit -m "ci: update python-app image to ${IMAGE_TAG} [skip ci]" || echo "No changes to commit"
                        urlencode() { printf '%s' "\$1" | sed -e 's/%/%25/g' -e 's/@/%40/g' -e 's/:/%3A/g' -e 's#/#%2F#g' -e 's/ /%20/g'; }
                        GIT_USER_ENC=\$(urlencode "\${GIT_USER}")
                        GIT_TOKEN_ENC=\$(urlencode "\${GIT_TOKEN}")
                        git push "https://\${GIT_USER_ENC}:\${GIT_TOKEN_ENC}@github.com/ajaysunkaranam89-ai/python.git" HEAD:main
                    """
                }
                echo "Argo CD will detect this commit and sync it to the cluster automatically."
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
