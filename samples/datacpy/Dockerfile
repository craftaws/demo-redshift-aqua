# The AWS base images provide the following environment variables:
# - LAMBDA_TASK_ROOT=/var/task
# - LAMBDA_RUNTIME_DIR=/var/runtime
FROM public.ecr.aws/lambda/python:3.8

RUN  pip3 install redshift_connector boto3 --target "${LAMBDA_TASK_ROOT}"

COPY redshift_data_copy.py ${LAMBDA_TASK_ROOT}
CMD [ "redshift_data_copy.run" ]
