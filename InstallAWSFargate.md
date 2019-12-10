#### 1. Fargate configure 設定
```bash
$ ecs-cli configure \
--cluster django-fargate \
--default-launch-type FARGATE \
--config-name django-fargate \
--region {your_region}
```
出力:
```bash
INFO[0000] Saved ECS CLI cluster configuration django-fargate.
```
#### 2. Fargate configure profile 設定
```bash
$ ecs-cli configure profile \
--access-key {access_key} \
--secret-key {secret_key} \
--profile-name django-fargate-profile
```
出力:
```
INFO[0000] Saved ECS CLI profile configuration django-fargate-profile.
```

#### 3. Fargate用のクラスター作成
```bash
$ ecs-cli up \
--cluster-config django-fargate \
--ecs-profile django-fargate-profile
```
出力:
```bash
INFO[0001] Created cluster                               cluster=django-fargate region={your_region}
INFO[0002] Waiting for your cluster resources to be created... 
INFO[0002] Cloudformation stack status                   stackStatus=CREATE_IN_PROGRESS
INFO[0064] Cloudformation stack status                   stackStatus=CREATE_IN_PROGRESS
VPC created: {your_vpc_id}
Security Group created: {your_security_group_id}
Subnet created: {your_subnet_id_1}
Subnet created: {your_subnet_id_2}
Cluster creation succeeded.
```
※このタイミングでCloudFormationのstackが作成されます</br>
※作成されたVPC内にAmazon RDS for PostgreSQLを作成しておいてください。詳しい手順は割愛します。([PostgreSQL データベースを作成、接続する](https://aws.amazon.com/jp/getting-started/tutorials/create-connect-postgresql-db/))
#### 4. Security Groupを作成し、80番ポートへのTCPアクセスを許可
```bash
$ aws ec2 create-security-group \
--group-name django-fargate-app-sg \
--description "for django-fargate-app" \
--vpc-id {your_vpc_id}
```
出力:
```bash
{
    "GroupId": "{your_security_group_id}"
}
```
80番ポートへのTCPアクセスを許可
```bash
$ aws ec2 authorize-security-group-ingress \
--group-id {your_security_group_id} \
--protocol tcp \
--port 80 \
--cidr 0.0.0.0/0
```
#### 5. AWS ELB (Application Load Balancer)を作成
```bash
$ aws elbv2 create-load-balancer \
--name django-fargate-alb \
--subnets {your_subnet_id_1} {your_subnet_id_2} \
--security-groups {your_security_group_id}
```
出力:</br>
※出力には、次の形式でロードバランサーの Amazon リソースネーム (ARN) とアクセスドメイン(DNSName)が含まれます。
```bash
arn:aws:elasticloadbalancing:region:aws_account_id:loadbalancer/app/django-fargate-alb/e5ba62739c16e642
django-fargate-alb-XXXXXXXXXX.ap-northeast-1.elb.amazonaws.com
```
#### 6. ターゲットグループの作成
```bash
$ aws elbv2 create-target-group \
--name django-fargate-target-group \
--protocol HTTP \
--port 80 \
--target-type ip \
--health-check-path /imgrecognition/upload/ \
--vpc-id {your_vpc_id}
```
出力:</br>
※出力には、以下の形式でターゲットグループの ARN が含まれます。
```bash
arn:aws:elasticloadbalancing:region:aws_account_id:targetgroup/django-fargate-target-group/209a844cd01825a4
```
#### 7. ロードバランサとターゲットグループを紐付けるリスナーを作成
```bash
$ aws elbv2 create-listener \
--load-balancer-arn {your_load_balancer_arn} \
--protocol HTTP --port 80 \
--default-actions Type=forward,TargetGroupArn={your_target_group_arn}
```
出力:</br>
※出力には、以下の形式でリスナーの ARN が含まれます。
```bash
arn:aws:elasticloadbalancing:region:aws_account_id:listener/app/bluegreen-alb/e5ba62739c16e642/665750bec1b03bd4
```
#### 8. 環境変数の情報を設定する
以下のファイルで利用するために、「.env」ファイルに環境変数を設定します。
* ecs-params.yml
* docker-compose.prod.yml
.envを以下の内容で作成</br>

```bash
# ロードバランサーDNS
LOADBALANCER_DNS="XXXXX.region.elb.amazonaws.com"
# AWS ECR パス
CONTAINER_REGISTRY_PATH="123456789012.dkr.ecr.region.amazonaws.com"
# AWS VPC Subnet ID
SUBNET_ID_1="subnet-XXXXXXXXXXXXXXXXX"
SUBNET_ID_2="subnet-XXXXXXXXXXXXXXXXX"
# AWS Security Group ID
SECURITY_GROUP_ID="sg-XXXXXXXXXXXXXXXXX"
# AWS RDS エンドポイント パス
RDS_ENDPOINT="XXXXXX.region.rds.amazonaws.com"
```
作成後に</br>

```bash
$ export $(cat .env | grep -v ^# | xargs)
```

#### 9. AWS System Manager のパラメータストア設定
インスタンスで利用するRDSエンドポイントを環境変数に設定するために、AWS System Manager > パラメータストア で</br>
「django-fargate-db-endpoint」というパラメータを作成し、RDSエンドポイントを値として登録しておきます。

#### 10. IAMロールでタスクロールを作成
タスクで実行されたコンテナからAWS RekognitionおよびAWS Translateを利用するために、</br>
「ポリシー」とそれをアタッチした「ロール」(RoleForECSDjango)を作成する。</br>
※ecs-params.yml内の「task_role_arn」で「RoleForECSDjango」を指定しています。
<details>
<summary>「ポリシー」の内容はこちら</summary>

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "RecognitionReadOnlyAccess",
            "Effect": "Allow",
            "Action": [
                "rekognition:CompareFaces",
                "rekognition:DetectFaces",
                "rekognition:DetectLabels",
                "rekognition:ListCollections",
                "rekognition:ListFaces",
                "rekognition:SearchFaces",
                "rekognition:SearchFacesByImage",
                "rekognition:DetectText",
                "rekognition:GetCelebrityInfo",
                "rekognition:RecognizeCelebrities",
                "rekognition:DetectModerationLabels",
                "rekognition:GetLabelDetection",
                "rekognition:GetFaceDetection",
                "rekognition:GetContentModeration",
                "rekognition:GetPersonTracking",
                "rekognition:GetCelebrityRecognition",
                "rekognition:GetFaceSearch",
                "rekognition:DescribeStreamProcessor",
                "rekognition:ListStreamProcessors"
            ],
            "Resource": "*"
        },
        {
            "Sid": "TranslateReadOnlyAccess",
            "Action": [
                "translate:TranslateText",
                "translate:GetTerminology",
                "translate:ListTerminologies",
                "comprehend:DetectDominantLanguage",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
</details>

#### 11. Fargate サービスのcreate
```bash
$ ecs-cli compose -f docker-compose.prod.yml service create \
--target-group-arn {your_target_group_arn} \
--container-name nginx \
--container-port 80 \
--create-log-groups
```
出力:
```bash
INFO[0000] Using ECS task definition                     TaskDefinition="django_img_recognition:1"
INFO[0001] Created an ECS service                        service=django_img_recognition taskDefinition="django_img_recognition:1"
```
#### 12. Fargate タスクの起動
```bash
$ ecs-cli compose -f docker-compose.prod.yml service scale 1
```
※「scale N」には実行するタスク数を設定してください</br>
出力:
```bash
INFO[0001] Using ECS task definition                     TaskDefinition="django_img_recognition:1"
INFO[0001] Updated ECS service successfully              desiredCount=1 force-deployment=false service=django_img_recognition
INFO[0032] (service django_img_recognition) has started 1 tasks: (task xxx).  timestamp="YYYY-MM-DD hh:mm:ss +0000 UTC"
INFO[0062] Service status                                desiredCount=1 runningCount=1 serviceName=django_img_recognition
INFO[0062] (service django_img_recognition) registered 1 targets in (target-group {your_target_group_arn})  timestamp="YYYY-MM-DD hh:mm:ss +0000 UTC"
INFO[0062] ECS Service has reached a stable state        desiredCount=1 runningCount=1 serviceName=django_img_recognition
```
※Log Groupが存在する場合はWARNが出力するが影響ありません
#### 13. FargateDocker環境のアクセスURL
http://{ロードバランサのアクセス先ドメイン}/imgrecognition/upload/

#### 14. (タスク停止する場合)Fargate タスクの停止
```bash
$ ecs-cli compose -f docker-compose.prod.yml service scale 0
```
#### 15. (サービス停止する場合)Fargate サービスの停止
```bash
$ ecs-cli compose -f docker-compose.prod.yml service down
```