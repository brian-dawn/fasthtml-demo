import os
from dotenv import load_dotenv

from aws_cdk import (
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_certificatemanager as acm,
    # Duration,
    App,
    Environment,
    Stack,
    # aws_sqs as sqs,
)
from aws_cdk import aws_apigateway as apigateway
from aws_cdk.aws_lambda import Runtime
from aws_cdk.aws_lambda_python_alpha import PythonFunction, PythonLayerVersion


from aws_cdk.aws_lambda import DockerImageFunction, DockerImageCode
from constructs import Construct

load_dotenv()


class InfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        os.system("cat requirements.lock | grep -v '\\-e' > .layer/requirements.txt")

        layer = PythonLayerVersion(
            self,
            "FastHtmlLayer",
            entry=".layer/",
            compatible_runtimes=[Runtime.PYTHON_3_12],
        )

        lambda_function = PythonFunction(
            self,
            "FastHtmlFunction2",
            entry="src/mess_with_fasthtml/web",
            index="main.py",
            layers=[layer],
            runtime=Runtime.PYTHON_3_12,
            environment={"NO_LIVE": "true"},
        )

        # Create or reference the hosted zone for the domain
        hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone", domain_name="dawn.lol"
        )

        # Create a TLS certificate for the domain using ACM
        certificate = acm.Certificate(
            self,
            "Certificate",
            domain_name="demo.dawn.lol",
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

        # Lets route some web traffic to the lambda now.
        api = apigateway.LambdaRestApi(
            self,
            "FastHtmlApi",
            handler=lambda_function,
            domain_name=apigateway.DomainNameOptions(
                domain_name="demo.dawn.lol",
                certificate=certificate,
            ),
            proxy=True,  # Proxy all requests to the Lambda function
        )
        # Create a DNS record for the API in Route 53
        route53.ARecord(
            self,
            "ApiAliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(route53_targets.ApiGateway(api)),
            record_name="demo",
        )


account = os.getenv("CDK_DEFAULT_ACCOUNT")
if not account:
    raise ValueError("CDK_DEFAULT_ACCOUNT must be set")

region = os.getenv("CDK_DEFAULT_REGION")
if not region:
    raise ValueError("CDK_DEFAULT_REGION must be set")

app = App()

InfraStack(app, "InfraStack", env=Environment(account=account, region=region))

app.synth()
