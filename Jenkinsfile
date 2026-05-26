def deployToGKE(String namespace, String envLabel) {
    env.NAMESPACE = namespace
    // Create Jenkins credentials with secret text.
    // notification-smtp-user     → SMTP_USER
    // notification-smtp-password → SMTP_PASSWORD
    // notification-database-url  → DATABASE_URL  (e.g. mysql+pymysql://user:pass@host:3306/db)
    // The same key names must match what is in k8s/secret.yaml
    withCredentials([
        string(credentialsId: 'notification-smtp-user', variable: 'SMTP_USER'),
        string(credentialsId: 'notification-smtp-password', variable: 'SMTP_PASSWORD'),
        string(credentialsId: 'notification-database-url', variable: 'DATABASE_URL')
    ]) {
        sh """
            echo "******************* Deploying to ${envLabel} Environment *********************"
            echo "Deploying into this namespace: ${NAMESPACE}"
            kubectl get pods -n ${NAMESPACE}
            # Substitute namespace and image in all manifests
            sed -i "s|\\\${NAMESPACE}|${NAMESPACE}|g" k8s/*.yaml
            sed -i "s|\\\${IMAGE_NAME}|${IMAGE_NAME}|g" k8s/deploy.yaml
            sed -i "s|\\\${IMAGE_TAG}|${GIT_COMMIT}|g" k8s/deploy.yaml

            # Inject secrets into secret.yaml
            sed -i "s|{{SMTP_USER}}|${SMTP_USER}|g" k8s/secret.yaml
            sed -i "s|{{SMTP_PASSWORD}}|${SMTP_PASSWORD}|g" k8s/secret.yaml
            sed -i "s|{{DATABASE_URL}}|${DATABASE_URL}|g" k8s/secret.yaml

            echo "Applying k8s manifests in ${envLabel} namespace"
            kubectl apply -f k8s/
            echo "Deployment to ${envLabel} namespace is completed"
        """
    }
}

def gkeAuth(String clusterName, String zone, String projectId) {
    sh """
        echo "******************************* Authenticating to GKE **************************"
        gcloud container clusters get-credentials ${clusterName} --zone ${zone} --project ${projectId}
        echo "******************** Validating the Cluster access *********************"
        kubectl get nodes
    """
}

pipeline {
    agent {
        label 'k8s-slave'
    }
    parameters {
        booleanParam(name: 'skipSonar', defaultValue: true, description: 'Skip SonarQube analysis and Quality gate')
        choice(name: 'buildOnly', choices: 'no\nyes', description: 'Build Docker image only, no push')
        choice(name: 'dockerPush', choices: 'no\nyes', description: 'Build and Push Docker image')
        choice(name: 'deployToDev', choices: 'no\nyes', description: 'Deploy to Dev Environment')
        choice(name: 'deployToTest', choices: 'no\nyes', description: 'Deploy to Test Environment')
        choice(name: 'deployToStage', choices: 'no\nyes', description: 'Deploy to Stage Environment')
        choice(name: 'deployToProd', choices: 'no\nyes', description: 'Deploy to Prod Environment')
    }
    environment {
        REGISTRY_URL             = "docker.io"
        IMAGE_REPOSITORY         = "devopswithcloudhub/notification-service"
        REGISTRY_CREDENTIALS_ID  = credentials('docker-credentials')

        DEV_CLUSTER_NAME   = "np-cluster"
        DEV_CLUSTER_ZONE   = "us-east4-a"
        DEV_PROJECT_ID     = "project-fe6816d0-c7fc-4c9b-bd7"

        TEST_CLUSTER_NAME  = "np-cluster"
        TEST_CLUSTER_ZONE  = "us-east4-a"
        TEST_PROJECT_ID    = "project-fe6816d0-c7fc-4c9b-bd7"

        STAGE_CLUSTER_NAME = "np-cluster"
        STAGE_CLUSTER_ZONE = "us-east4-a"
        STAGE_PROJECT_ID   = "project-fe6816d0-c7fc-4c9b-bd7"

        PROD_CLUSTER_NAME  = "np-cluster"
        PROD_CLUSTER_ZONE  = "us-east4-a"
        PROD_PROJECT_ID    = "project-fe6816d0-c7fc-4c9b-bd7"
    }
    stages {
        stage('Prepare Tag') {
            when {
                anyOf {
                    expression { params.buildOnly == 'yes' }
                    expression { params.dockerPush == 'yes' }
                    expression { params.deployToDev == 'yes' }
                    expression { params.deployToTest == 'yes' }
                    expression { params.deployToStage == 'yes' }
                    expression { params.deployToProd == 'yes' }
                }
            }
            steps {
                script {
                    env.IMAGE_NAME = env.REGISTRY_URL + "/" + env.IMAGE_REPOSITORY
                    echo "Using Registry: ${env.REGISTRY_URL}"
                    echo "Using Repository: ${env.IMAGE_REPOSITORY}"
                    echo "Using Image Tag: ${GIT_COMMIT}"
                    echo "Full Image is: ${env.IMAGE_NAME}:${GIT_COMMIT}"
                }
            }
        }
        stage('Sonarqube') {
            when {
                allOf {
                    expression { !params.skipSonar }
                    anyOf {
                        expression { params.buildOnly == 'yes' }
                        expression { params.dockerPush == 'yes' }
                    }
                }
            }
            steps {
                script {
                    def scannerHome = tool 'SonarQubeScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
                timeout(time: 2, unit: 'MINUTES') {
                    script {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }
        stage('Build Docker Image') {
            when {
                expression { params.buildOnly == 'yes' }
                expression { params.dockerPush == 'yes' }
            }
            steps {
                echo "Building the image"
                sh "docker build --no-cache -t ${env.IMAGE_NAME}:${GIT_COMMIT} ."
            }
        }
        stage('Push Image') {
            when {
                expression { params.dockerPush == 'yes' }
            }
            steps {
                echo "********************************* Docker Login *****************************"
                sh "docker login -u ${env.REGISTRY_CREDENTIALS_ID_USR} -p ${env.REGISTRY_CREDENTIALS_ID_PSW} ${env.REGISTRY_URL}"
                echo "********************************* Docker Push *****************************"
                sh "docker push ${env.IMAGE_NAME}:${GIT_COMMIT}"
            }
        }
        stage('DeployToDevEnvironment') {
            when {
                expression { params.deployToDev == 'yes' }
            }
            steps {
                script {
                    gkeAuth(env.DEV_CLUSTER_NAME, env.DEV_CLUSTER_ZONE, env.DEV_PROJECT_ID)
                    deployToGKE('i27-helpdesk-dev', 'Dev')
                }
            }
        }
        stage('DeployToTestEnvironment') {
            when {
                expression { params.deployToTest == 'yes' }
            }
            steps {
                script {
                    gkeAuth(env.TEST_CLUSTER_NAME, env.TEST_CLUSTER_ZONE, env.TEST_PROJECT_ID)
                    deployToGKE('i27-helpdesk-test', 'Test')
                }
            }
        }
        stage('DeployToStageEnvironment') {
            when {
                allOf {
                    expression { params.deployToStage == 'yes' }
                    anyOf {
                        branch 'release*'
                        tag pattern: "v\\d{1,2}\\.\\d{1,2}\\.\\d{1,2}", comparator: "REGEXP"
                    }
                }
            }
            steps {
                script {
                    gkeAuth(env.STAGE_CLUSTER_NAME, env.STAGE_CLUSTER_ZONE, env.STAGE_PROJECT_ID)
                    deployToGKE('i27-helpdesk-stage', 'Stage')
                }
            }
        }
        stage('DeployToProdEnvironment') {
            when {
                allOf {
                    expression { params.deployToProd == 'yes' }
                    anyOf {
                        tag pattern: "v\\d{1,2}\\.\\d{1,2}\\.\\d{1,2}", comparator: "REGEXP"
                    }
                }
            }
            steps {
                timeout(time: 300, unit: 'SECONDS') {
                    input message: 'Approve Deployment to production ???', submitter: 'sivasre,phanisekhar'
                }
                script {
                    gkeAuth(env.PROD_CLUSTER_NAME, env.PROD_CLUSTER_ZONE, env.PROD_PROJECT_ID)
                    deployToGKE('i27-helpdesk-prod', 'Prod')
                }
            }
        }
    }
}
