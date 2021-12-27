#!/usr/bin/env python3

from aws_cdk import App
from samples.redshift import RedshiftStack

app = App()
RedshiftStack(app, "DemoAqua")

app.synth()