FROM openfaas/of-watchdog:0.7.2 as watchdog

FROM node:12.11.1-stretch-slim

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

RUN npm install redoc-cli -g

WORKDIR /app
RUN mkdir -p /app
COPY functions.yaml /app

ENV fprocess="redoc-cli serve --port 9090 ./functions.yaml"
ENV write_debug="false"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:9090"

EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
