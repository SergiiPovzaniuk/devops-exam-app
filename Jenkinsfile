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
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -q -r requirements-dev.txt
          pytest -q
        '''
      }
    }

    stage('Build') {
      steps {
        script {
          env.IMAGE_TAG = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        }
        sh "docker build -t ${IMAGE}:${IMAGE_TAG} -t ${IMAGE}:latest ."
      }
    }

    stage('Publish') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker push ${IMAGE}:${IMAGE_TAG}
            docker push ${IMAGE}:latest
          '''
        }
      }
    }

    stage('Deploy') {
      when {
        branch 'main'
      }
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-exam', variable: 'KUBECONFIG')]) {
          sh '''
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