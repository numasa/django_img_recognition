# django_img_recognition

## Description
Amazon Rekognitionを利用した画像認識が可能なPython/Django製のWebアプリケーション

## Requirement
* python 3.7
* pip
* pipenv
* docker
* docker-compose
* awscli (AWS CLI)
* ecs-cli (Amazon ECS CLI)

## Install
### Local
---
#### git clone
```bash
$ git clone https://github.com/numasa/django_img_recognition.git
$ cd django_img_recognition/django
```
#### pipenv install
```bash
$ pipenv install
```
#### runserver
```bash
$ pipenv run python manage.py runserver
```
### ローカルDocker
---
#### ローカルDockerからECRログイン
```bash
$ aws ecr get-login --region {your_region} --no-include-email
```
→出力した内容をコマンド実行してログイン
#### ローカルDocker環境のbuild
```bash
$ cd django_img_recognition/
$ docker-compose -f docker-compose.dev.yml build
```
#### ローカルDocker環境のup
```bash
$ docker-compose -f docker-compose.dev.yml up
```
#### ローカルDocker環境のアクセスURL
http://localhost/imgrecognition/upload/

#### (停止する場合)ローカルDocker環境のdown
```bash
$ docker-compose -f docker-compose.dev.yml down
```

### AWS Fargate環境
---
#### Fargate configure 設定
```bash
$ ecs-cli configure \
--cluster django-fargate \
--default-launch-type FARGATE \
--config-name django-fargate \
--region {your_region}

INFO[0000] Saved ECS CLI cluster configuration django-fargate.
```
#### Fargate configure profile 設定
```bash
$ ecs-cli configure profile \
--access-key {access_key} \
--secret-key {secret_key} \
--profile-name django-fargate-profile

INFO[0000] Saved ECS CLI profile configuration django-fargate-profile.
```

#### Fargate用のクラスター作成
```bash
$ ecs-cli up \
--cluster-config django-fargate \
--ecs-profile django-fargate-profile

INFO[0001] Created cluster                               cluster=django-fargate region={your_region}
INFO[0002] Waiting for your cluster resources to be created... 
INFO[0002] Cloudformation stack status                   stackStatus=CREATE_IN_PROGRESS
INFO[0064] Cloudformation stack status                   stackStatus=CREATE_IN_PROGRESS
VPC created: {your_vpc_id}
Subnet created: {your_subnet_id_1}
Subnet created: {your_subnet_id_2}
Cluster creation succeeded.
```
※このタイミングでCloudFormationのstackが作成されます
#### VPCに付与されたSecurity Group Idを確認
```bash
$ aws ec2 describe-security-groups --filters Name=vpc-id,Values={vpc_id} --region {your_region} | grep GroupId

                            "GroupId": "{your_sg_id}",
            "GroupId": "{your_sg_id}",
```
#### ecs-params.ymlを作成
サブネットIDとセキュリティグループIDをecs-params.ymlに記載する
```bash:ecs-params.yml
version: 1
task_definition:
  task_execution_role: ecsTaskExecutionRole
  ecs_network_mode: awsvpc
  task_size:
    mem_limit: 0.5GB
    cpu_limit: 256
run_params:
  network_configuration:
    awsvpc_configuration:
      subnets:
        - "{your_subnet_id_1}"
        - "{your_subnet_id_2}"
      security_groups:
        - "{your_sg_id}"
      assign_public_ip: ENABLED
```
#### AWS ELB (Application Load Balancer)を作成
```bash
$ aws elbv2 create-load-balancer \
--name django-fargate-alb \
--subnets {your_subnet_id_1} {your_subnet_id_2} \
--security-groups {your_sg_id} \
--region {your_region}

※出力には、次の形式でロードバランサーの Amazon リソースネーム (ARN) とアクセスドメイン(DNSName)が含まれます。
arn:aws:elasticloadbalancing:region:aws_account_id:loadbalancer/app/django-fargate-alb/e5ba62739c16e642
django-fargate-alb-XXXXXXXXXX.ap-northeast-1.elb.amazonaws.com
```
#### ターゲットグループの作成
```bash
$ aws elbv2 create-target-group \
--name django-fargate-target-group \
--protocol HTTP \
--port 80 \
--target-type ip \
--vpc-id {your_vpc_id} \
--region {your_region}

※出力には、以下の形式でターゲットグループの ARN が含まれます。arn:aws:elasticloadbalancing:region:aws_account_id:targetgroup/django-fargate-target-group/209a844cd01825a4
```
#### ロードバランサとターゲットグループを紐付けるリスナーを作成
```bash
$ aws elbv2 create-listener \
--load-balancer-arn {your_load_balancer_arn} \
--protocol HTTP --port 80 \
--default-actions Type=forward,TargetGroupArn={your_target_group_arn} \
--region {your_region}

※出力には、以下の形式でリスナーの ARN が含まれます。
arn:aws:elasticloadbalancing:region:aws_account_id:listener/app/bluegreen-alb/e5ba62739c16e642/665750bec1b03bd4
```
#### Fargate サービスのcreate
```bash
$ ecs-cli compose -f docker-compose.prod.yml service create \
--target-group-arn {your_target_group_arn} \
--container-name nginx \
--container-port 80

INFO[0000] Using ECS task definition                     TaskDefinition="django_img_recognition:1"
INFO[0001] Created an ECS service                        service=django_img_recognition taskDefinition="django_img_recognition:1"
```
#### Fargate サービスのup
```bash
$ ecs-cli compose -f docker-compose.prod.yml service up

INFO[0001] Using ECS task definition                     TaskDefinition="django_img_recognition:1"
INFO[0001] Updated ECS service successfully              desiredCount=1 force-deployment=false service=django_img_recognition
INFO[0032] (service django_img_recognition) has started 1 tasks: (task xxx).  timestamp="YYYY-MM-DD hh:mm:ss +0000 UTC"
INFO[0062] Service status                                desiredCount=1 runningCount=1 serviceName=django_img_recognition
INFO[0062] (service django_img_recognition) registered 1 targets in (target-group {your_target_group_arn})  timestamp="YYYY-MM-DD hh:mm:ss +0000 UTC"
INFO[0062] ECS Service has reached a stable state        desiredCount=1 runningCount=1 serviceName=django_img_recognition
```
※Log Groupが存在する場合はWARNが出力するが影響なし
#### Security Groupの80番ポートへのTCPアクセスを許可
```bash
$ aws ec2 authorize-security-group-ingress \
--group-id {your_sg_id} \
--protocol tcp \
--port 80 \
--cidr 0.0.0.0/0 \
--region {your_region}
```
#### FargateDocker環境のアクセスURL
http://{ロードバランサのアクセス先ドメイン}/imgrecognition/upload/

#### Fargate停止
```bash
$ ecs-cli compose -f docker-compose.prod.yml service down
```
#### Fargate用のクラスター削除
```bash
$ ecs-cli down --force \
--cluster-config django-fargate \
--ecs-profile django-fargate-profile

INFO[0001] Waiting for your cluster resources to be deleted... 
INFO[0002] Cloudformation stack status                   stackStatus=DELETE_IN_PROGRESS
INFO[0062] Deleted cluster                               cluster=django-fargate
```
### CI/CD
...