#!/usr/bin/env python3

from aws_cdk import core as cdk
from samples.redshift import RedshiftStack

app = cdk.App()
RedshiftStack(app, "DemoAqua")

app.synth()