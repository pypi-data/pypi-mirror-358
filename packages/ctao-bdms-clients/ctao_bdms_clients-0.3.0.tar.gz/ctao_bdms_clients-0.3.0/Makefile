###
# TODO: duplicate in config?
export CHART_NAME=bdms
export CHART_LOCATION=chart
include dpps-aiv-toolkit/Makefile


# TODO: move this to kit
export TEST_ARTIFACTS_PATH ?= $(PWD)
export TEST_REPORT_CONFIG ?= $(PWD)/aiv-config.yml
export TEX_CONTENT_PATH ?= $(PWD)/report

build-dev-server-images:
	# TODO: should it be a separate image? it should have a different name
	docker build . -t harbor.cta-observatory.org/dpps/bdms-ingestion-daemon:dev
	./kind -n $(KUBECLUSTER) load docker-image \
		harbor.cta-observatory.org/dpps/bdms-ingestion-daemon:dev


dev: build-dev-server-images
