pipeline {
    agent any

    environment {
    	SRC_DIR = 'dashboards'
    }

    stages {
        stage('Build') {
            steps {
                echo "Building ${env.JOB_NAME}"
            }
        }
        stage('Test') {
            steps {
	        echo 'Testing'
            	sh 'python -m pytest || true'
		echo 'Linting'
		sh "pylint ${env.SRC_DIR}"
	    }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying'
            }
        }
    }
    post {
        always {
            echo 'We built ${env.JOB_NAME}'
        }
        success {
            echo 'Woohoo! It was a success.'
        }
        failure {
            echo 'Oops! It failed.'
        }
        unstable {
            echo 'Not even sure when this can get called.'
        }
        changed {
            echo '---the status of build has changed---'
        }
    }
}