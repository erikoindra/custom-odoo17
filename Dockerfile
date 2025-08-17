FROM odoo:17.0

USER root

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY ./addons /opt/odoo/odoo17/addons
COPY ./custom/mc /opt/odoo/odoo17/custom/mc
