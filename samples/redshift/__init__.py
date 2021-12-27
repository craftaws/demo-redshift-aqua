'Cloudformation Stack for Redshift Aqua Demo'
from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_iam,
    aws_ec2,
    aws_s3,
    aws_lambda,
)
import aws_cdk.aws_redshift_alpha as aws_redshift_alpha

VPC_CIDR="10.10.0.0/16"

class RedshiftStack(Stack):
    'Cloudformation Stack for Redshit Aqua demo'

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        data_bucket = aws_s3.Bucket(self, "aqua-demo-data",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        sample_vpc = aws_ec2.Vpc(self, "redshift-vpc",
            cidr=VPC_CIDR,
            max_azs=2,
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    name= 'isolated',
                    subnet_type=aws_ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )

        sample_vpc.add_interface_endpoint('secretmanager',
            service=aws_ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            subnets=aws_ec2.SubnetSelection(subnets=sample_vpc.isolated_subnets)
        )

        red_cluster_role = aws_iam.Role(self, 'red-cluster-role',
            assumed_by=aws_iam.ServicePrincipal('redshift.amazonaws.com')
        )
        red_cluster_role.add_to_policy(aws_iam.PolicyStatement(
            actions=["s3:GetObject", "s3:ListBucket"],
            resources=[data_bucket.bucket_arn, f"{data_bucket.bucket_arn}/*"]
        ))

        red_security_group = aws_ec2.SecurityGroup(self, 'sg-red-cluster',
            vpc=sample_vpc
        )

        for subnet in sample_vpc.isolated_subnets:
            red_security_group.add_ingress_rule(
                peer=aws_ec2.Peer.ipv4(subnet.ipv4_cidr_block),
                connection=aws_ec2.Port(
                    protocol=aws_ec2.Protocol.ALL,
                   string_representation="to allow from the vpc internal"
                )
        )        

        red_cluster = aws_redshift_alpha.Cluster(self, 'demo-aqua',
            master_user=aws_redshift_alpha.Login(master_username="admin_user"),
            vpc=sample_vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE_ISOLATED),
            security_groups=[red_security_group],
            removal_policy=RemovalPolicy.DESTROY,
            # AQUA is available on clusters with ra3.xlplus, ra3.4xlarge, and ra3.16xlarge node types.
            # https://docs.aws.amazon.com/redshift/latest/mgmt/managing-cluster-aqua.html
            node_type=aws_redshift_alpha.NodeType.RA3_4XLARGE,
            number_of_nodes=2,
            roles=[red_cluster_role]
        )

        data_lambda_role = aws_iam.Role(self, "data_lambda_role",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com")
        )
        data_lambda_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
        )
        data_lambda_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaENIManagementAccess')
        )
        data_lambda_role.add_to_policy(aws_iam.PolicyStatement(
            actions=["s3:PutObject", "s3:ListBucket", "s3:DeleteObject"],
            resources=[data_bucket.bucket_arn, f"{data_bucket.bucket_arn}/*"]
        ))

        data_lambda_role.add_to_policy(aws_iam.PolicyStatement(
            actions=["secretsmanager:GetSecretValue"],
            resources=[red_cluster.secret.secret_arn]
        ))

        data_lambda_role.add_to_policy(aws_iam.PolicyStatement(
            actions=["redshift-data:BatchExecuteStatement"],
            resources=['*']
        ))


        aws_lambda.DockerImageFunction(self, "datagen_lambda",
            code=aws_lambda.DockerImageCode.from_image_asset(
                directory="samples/datagen",
            ),
            role=data_lambda_role,
            timeout=Duration.minutes(10),
            environment={
                'data_bucket_name': data_bucket.bucket_name,
            }
        )

        aws_lambda.DockerImageFunction(self, "datacpy_lambda",
            code=aws_lambda.DockerImageCode.from_image_asset(
                directory="samples/datacpy",
            ),
            role=data_lambda_role,
            timeout=Duration.minutes(10),
            # vpc=sample_vpc,
            # vpc_subnets=aws_ec2.SubnetSelection(subnets=sample_vpc.isolated_subnets),
            environment={
                'REGION': self.region,
                'REDSHIFT_ID': red_cluster.cluster_name,
                'REDSHIFT_SECRET': red_cluster.secret.secret_name,
                'REDSHIFT_IAM_ROLE': red_cluster_role.role_arn,
                'DATA_BUCKET_NAME': data_bucket.bucket_name,
            }
        )
