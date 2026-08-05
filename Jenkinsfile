pipeline {
  agent any

  environment {
    DOCKERHUB_USER = 'sergejpovzaniuk'
    IMAGE_NAME = 'devops-exam-app'
    IMAGE = "${DOCKERHUB_USER}/${IMAGE_NAME}"
  }

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '20'))
    skipStagesAfterUnstable()
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Test') {
      steps {
        sh '''
          set -e
          docker run --rm \
            -v "$PWD":/app \
            -w /app \
            python:3.12-slim \
            bash -lc "pip install -q -r requirements-dev.txt && pytest -q"
        '''
      }
      post {
        failure {
          error('Tests failed — blocking Build/Publish/Deploy')
        }
      }
    }

    stage('Build') {
      when {
        expression { currentBuild.currentResult == null || currentBuild.currentResult == 'SUCCESS' }
      }
      steps {
        script {
          env.IMAGE_TAG = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        }
        sh "docker build -t ${IMAGE}:${IMAGE_TAG} -t ${IMAGE}:latest ."
      }
    }

    stage('Publish') {
      when {
        expression { currentBuild.currentResult == null || currentBuild.currentResult == 'SUCCESS' }
      }
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            set -e
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker push ${IMAGE}:${IMAGE_TAG}
            docker push ${IMAGE}:latest
          '''
        }
      }
    }

    stage('Deploy') {
      when {
        allOf {
          branch 'main'
          expression { currentBuild.currentResult == null || currentBuild.currentResult == 'SUCCESS' }
        }
      }
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-exam', variable: 'KUBECONFIG')]) {
          sh '''
            set -e
            kubectl apply -f k8s/deployment.yaml
            kubectl set image deployment/devops-exam-app app=${IMAGE}:${IMAGE_TAG}
            kubectl rollout status deployment/devops-exam-app --timeout=180s
          '''
        }
      }
    }
  }

  post {
    always {
      script {
        def msg = "Job: ${env.JOB_NAME}\nBuild: ${env.BUILD_URL}\nBranch: ${env.BRANCH_NAME}\nResult: ${currentBuild.currentResult}"
        echo "NOTIFY: ${msg}"
        try {
          emailext(
            subject: "Jenkins ${env.JOB_NAME} #${env.BUILD_NUMBER}: ${currentBuild.currentResult}",
            body: msg,
            to: '${DEFAULT_RECIPIENTS}'
          )
        } catch (err) {
          echo "email-ext skipped: ${err}"
        }
      }
    }
    cleanup {
      sh 'docker logout || true'
    }
  }
}
