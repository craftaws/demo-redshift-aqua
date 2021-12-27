# The AWS base images provide the following environment variables:
# - LAMBDA_TASK_ROOT=/var/task
# - LAMBDA_RUNTIME_DIR=/var/runtime
FROM public.ecr.aws/lambda/python:3.8

WORKDIR /opt
COPY e6787197-fc19-4f2c-a1bf-d893bd52a229-tpc-h-tool.zip .
RUN yum install unzip -y && unzip e6787197-fc19-4f2c-a1bf-d893bd52a229-tpc-h-tool.zip
COPY makefile /opt/TPC-H_Tools_v3.0.0/dbgen

RUN yum install make gcc -y

WORKDIR /opt/TPC-H_Tools_v3.0.0/dbgen
RUN make

RUN mkdir -p ${LAMBDA_RUNTIME_DIR}/dbgen
WORKDIR ${LAMBDA_RUNTIME_DIR}/dbgen

RUN /opt/TPC-H_Tools_v3.0.0/dbgen/dbgen -b /opt/TPC-H_Tools_v3.0.0/dbgen/dists.dss -s 3

RUN  pip3 install boto3 --target "${LAMBDA_TASK_ROOT}"

COPY loader.py ${LAMBDA_TASK_ROOT}
CMD [ "loader.load" ]
