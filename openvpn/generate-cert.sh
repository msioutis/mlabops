#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <hostname>"
    exit 1
fi

CERT_HOST=$1

TMP_KEY_DIR=/root/manual-keys/${CERT_HOST}-keys

. /usr/share/openvpn/easy-rsa/2.0/vars

export KEY_PROVINCE="CA"
export KEY_CITY="SanFrancisco"
export KEY_ORG="M-Lab"
export KEY_EMAIL=mail@host.domain
export KEY_OU=changeme

export KEY_CN=${CERT_HOST}
export KEY_NAME=${CERT_HOST}

mkdir -p $TMP_KEY_DIR
cd $TMP_KEY_DIR

openssl req -batch -days 3650 -nodes -new -newkey rsa:1024 -keyout \
    $CERT_HOST.key -out $CERT_HOST.csr \
    -config /usr/share/openvpn/easy-rsa/2.0/openssl-1.0.0.cnf 2>&1

echo Generating $CERT_HOST.crt...
php /var/www/html/sign-csr.php $CERT_HOST $CERT_HOST.csr >$CERT_HOST.crt

