FROM openfaas/classic-watchdog:0.18.0 as watchdog

FROM alpine:3.9

RUN mkdir -p /home/app

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

RUN apk add --update npm

RUN npm install redoc-cli -g

# Add non root user
RUN addgroup -S app && adduser app -S -G app
RUN chown app /home/app

WORKDIR /home/app

COPY functions.yaml /home/app/

USER app

RUN redoc-cli bundle functions.yaml

# Populate example here - i.e. "cat", "sha512sum" or "node index.js"
ENV fprocess="cat redoc-static.html"

# Set to true to see request in function logs
ENV write_debug="false"

EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
