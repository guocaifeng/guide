# 1 脚本范例

大部分语法规则是Groovy来实现的，但是有一些特定语法是pipeline有的  
1.推荐使用script来实现相应的功能

```text
def git_url = "http://guocaifeng:guocaifeng@gitlab.cyai.com/common-service/rabbitmq.git"
def git_path = "rabbitmq"
def registry_url = "dockerhub.cyai.com"
def appstr = ""
def imagestr = ""
def project_num = ""


pipeline {
    agent any
    options {
        timeout(time: 1, unit: 'HOURS')
    }
    parameters {
        string(name: 'git_tag', defaultValue: 'git_tag', description: '项目源码的tag号')
        string(name: 'upgrade_app', defaultValue: 'YES', description: '更新或首次部署，YES为更新，NO为安装，默认值YES')
    }
    stages {
        stage('Tag Check') {
			steps {
			    script {
			        echo "0.Tag Check"
                    if("${git_tag}".matches('^\\d(\\.\\d+){1,2}\$')){
                            echo "${git_tag}"
                    }else if("${git_tag}".matches('^\\d(\\.\\d+){1,2}-[0-9]{8}-[a-z]{2,3}-.*')){
                        publish_position = "${git_tag}".split("-")[2]
                        if ("${env.JOB_NAME}"[0..2].indexOf("${publish_position}")!=-1){
                            echo "${git_tag}"
                        }else {
                            throw new Exception("git_tag参数错误,请按照规范填写!!! 当前版本:${git_tag}")
                        }
                    }else{
                        throw new Exception("git_tag参数错误,请按照规范填写!!! 当前版本:${git_tag}")
                    }
			    }
		    }
		    post {
                success {
                    echo "tag check success"
                }
                failure {
                    echo "tag check failed"
                }
            }
		}
		stage('Clone Code') {
			steps {
			    script {
                    echo "1.Clone Code"
                    //sh(script:"date '+%F_%H-%M-%S'",returnStdout:true).trim()
                    sh "rm -rf /home/gitlab/${git_tag} && mkdir -p /home/gitlab/${git_tag} &&  cd /home/gitlab/${git_tag}  && git clone --branch ${git_tag} ${git_url}"
			    }
		    }
		    post {
                success {
                    echo "git clone code success"
                }
                failure {
                    echo "git clone code failed"
                }
            }
		}
		stage('Build Images') {
			steps {
                script {
                    echo "2.Build Docker Images"

                    sh "chmod +x /home/gitlab/${git_tag}/${git_path}/build.sh"
                    sh "cd /home/gitlab/${git_tag}/${git_path} && ./build.sh -n=rabbitmq -v=${git_tag}"
                    sh "cd /home/gitlab/${git_tag}/${git_path} && ./build.sh -n=rabbitmq-init -v=${git_tag}"
                }
		    }
		    post {
                success {
                    echo "docker build success"
                }
                failure {
                    echo "docker build failed"
                }
            }
		}
		stage('Push Images') {
			steps {
			    script {
                    echo "3.Push Docker Images"

                    sh "sudo docker login ${registry_url} -u admin -p admin"
                    sh "sudo docker push ${registry_url}/rabbitmq/rabbitmq:${git_tag}"
                    sh "sudo docker push ${registry_url}/rabbitmq/rabbitmq-init:${git_tag}"
                }
			}
		    post {
                success {
                    echo "docker push success"
                }
                failure {
                    echo "docker push failed"
                }
            }
		}
		stage('Push Charts'){
		    steps {
			    script {
                    echo "4.Push Charts"
                    sh """sed -i "s/image_tag1/${git_tag}/g" /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq/values.yaml"""
                    sh """sed -i "s/image_tag2/${git_tag}/g" /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq/values.yaml"""
                    sh """sed -i "s/chart_version/${git_tag}/g" /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq/Chart.yaml"""
                    echo "-------------replace success-------------"

                    if("${git_tag}".matches('^\\d(\\.\\d+){1,2}\$')){
                        sh "helm lint /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq"
                        sh "helm push -f /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq chartmuseum-pro"
                        sh """
                            /usr/bin/expect <<-EOF
                                spawn ssh -t rancher@10.5.1.121
                                expect {
                                "*yes/no*" { send "yes\r";exp_continue }
                                "*password*" { send "qwe-123\r" }
                                }
                                expect {
                                "*rancher@rancher-master*" { send "cd clear-catalog\r" }
                                }
                                expect {
                                "*rancher@rancher-master*" { send "./clearcatalog.sh -c=pro -p=rabbitmq -v=${git_tag}\r" }
                                }
                                expect {
                                "*rancher@rancher-master*" { send "exit\r" }
                                }
                                set timeout 3000
                                expect eof
                        """
                        echo "refresh chartmuseum-dev charts in paas"
                        sh """
                            curl -k -u "$PAAS_KEY:$PAAS_SECRET" \
                                -X POST \
                                -H 'Accept: application/json' \
                                -H 'Content-Type: application/json' \
                                -d '{}' \
                                'https://paas.cyai.com/v3/clusterCatalogs/c-mxjpp:chartmuseum-pro?action=refresh'
                            """
                    }else{
                        publish_position = "${git_tag}".split("-")[2]
                        if ( "${publish_position}" == "dev") {
                            sh "helm lint /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq"
                            sh "helm push -f /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq chartmuseum-dev"
                            sh """
                                /usr/bin/expect <<-EOF
                                    spawn ssh -t rancher@10.5.1.121
                                    expect {
                                    "*yes/no*" { send "yes\r";exp_continue }
                                    "*password*" { send "qwe-123\r" }
                                    }
                                    expect {
                                    "*rancher@rancher-master*" { send "cd clear-catalog\r" }
                                    }
                                    expect {
                                    "*rancher@rancher-master*" { send "./clearcatalog.sh -c=dev -p=rabbitmq -v=${git_tag}\r" }
                                    }
                                    expect {
                                    "*rancher@rancher-master*" { send "exit\r" }
                                    }
                                    set timeout 3000
                                    expect eof
                            """
                            echo "refresh chartmuseum-dev charts in paas"
                            sh """
                                curl -k -u "$PAAS_KEY:$PAAS_SECRET" \
                                    -X POST \
                                    -H 'Accept: application/json' \
                                    -H 'Content-Type: application/json' \
                                    -d '{}' \
                                    'https://paas.cyai.com/v3/clusterCatalogs/c-wf24z:chartmuseum-dev?action=refresh'
                                """
                        }else if("${publish_position}" == "dt"){
                            sh "helm lint /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq"
                            sh "helm push -f /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq chartmuseum-dt"
                            sh """
                                /usr/bin/expect <<-EOF
                                    spawn ssh -t rancher@10.5.1.121
                                    expect {
                                    "*yes/no*" { send "yes\r";exp_continue }
                                    "*password*" { send "qwe-123\r" }
                                    }
                                    expect {
                                    "*rancher@rancher-master*" { send "cd clear-catalog\r" }
                                    }
                                    expect {
                                    "*rancher@rancher-master*" { send "./clearcatalog.sh -c=dt -p=rabbitmq -v=${git_tag}\r" }
                                    }
                                    expect {
                                    "*rancher@rancher-master*" { send "exit\r" }
                                    }
                                    set timeout 3000
                                    expect eof
                            """
                            echo "refresh chartmuseum-dev charts in paas"
                            sh """
                                curl -k -u "$PAAS_KEY:$PAAS_SECRET" \
                                    -X POST \
                                    -H 'Accept: application/json' \
                                    -H 'Content-Type: application/json' \
                                    -d '{}' \
                                    'https://paas.cyai.com/v3/clusterCatalogs/c-mkq5h:chartmuseum-dt?action=refresh'
                                """
                        }else if("${publish_position}" == "st"){
                            sh "helm lint /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq"
                            sh "helm push -f /home/gitlab/${git_tag}/${git_path}/charts/rabbitmq chartmuseum-st"
                            sh """
                                /usr/bin/expect <<-EOF
                                    spawn ssh -t rancher@10.5.1.121
                                    expect {
                                    "*yes/no*" { send "yes\r";exp_continue }
                                    "*password*" { send "qwe-123\r" }
                                    }
                                    expect {
                                    "*rancher@rancher-master*" { send "cd clear-catalog\r" }
                                    }
                                    expect {
                                    "*rancher@rancher-master*" { send "./clearcatalog.sh -c=st -p=rabbitmq -v=${git_tag}\r" }
                                    }
                                    expect {
                                    "*rancher@rancher-master*" { send "exit\r" }
                                    }
                                    set timeout 3000
                                    expect eof
                            """
                            echo "refresh chartmuseum-dev charts in paas"
                            sh """
                                curl -k -u "$PAAS_KEY:$PAAS_SECRET" \
                                    -X POST \
                                    -H 'Accept: application/json' \
                                    -H 'Content-Type: application/json' \
                                    -d '{}' \
                                    'https://paas.cyai.com/v3/clusterCatalogs/c-2qm5f:chartmuseum-st?action=refresh'
                                """
                        } else {
                            throw new Exception("git_tag参数错误,请按照规范填写!!! 当前版本:${git_tag}")
                        }
                    }
                    echo "-------------refresh success-------------"
                }
			}
		    post {
                success {
                    echo "helm push success"
                }
                failure {
                    echo "helm push failed"
                }
            }
		}
		stage('Deploy App') {
			steps {
			    script {
			        echo "5.Deplpy app in PaaS"

                    if("${git_tag}".matches('^\\d(\\.\\d+){1,2}\$')){
                        project_num="31"
                        sleep(new Random().nextInt(30)) //防止dev dt等同时构建导致异常
                    }else{
                        publish_position = "${git_tag}".split("-")[2]
                        if ( "${publish_position}" == "dev") {
                            project_num="39"
                            sleep(new Random().nextInt(15)) //防止dev dt等同时构建导致异常
                        }else if("${publish_position}" == "dt"){
                            project_num="14"
                            sleep(new Random().nextInt(15)) //防止dev dt等同时构建导致异常
                        }else if("${publish_position}" == "st"){
                            project_num="10"
                            sleep(new Random().nextInt(15)) //防止dev dt等同时构建导致异常
                        }else {
                            throw new Exception("git_tag参数错误,请按照规范填写!!! 当前版本:${git_tag}")
                        }
                    }

                    sh """
                        /usr/bin/expect <<-EOF
                          set time 30
                          spawn rancher login $PAAS_URL --token $PAAS_TOKEN
                          expect {
                            "*yes/no" { send "yes\r";exp_continue}
                            "*Project" { send "${project_num}\r" }
                          }
                          set timeout 3000
                          expect eof
                    """
                    sh "rancher catalog refresh --all"
                    upgrade_app = "${upgrade_app}"
                    if ( upgrade_app == 'YES') {
                            sh "rancher app upgrade rabbitmq ${git_tag}"
                    } else {
                            sh "rancher app install --namespace public rabbitmq --version ${git_tag}"
                    }
                }
			}
		    post {
                success {
                    echo "app deployed success"
                }
                failure {
                    echo "app deployed failed"
                }
            }
		}
		stage('Clear') {
			steps {
			    echo "5.Clear"

			    script {
			        sh "rm -rf /home/gitlab/${git_tag}"
                }
			}
			post {
                success {
                    echo "clear success"
                }
                failure {
                    echo "clear failed"
                }
            }
		}
    }
}
```

详细内容请参考
https://jenkins.io/zh/doc/book/pipeline/syntax/
