FROM postgres

ADD ext.sh /docker-entrypoint-initdb.d
RUN chmod 744 /docker-entrypoint-initdb.d/ext.sh
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["postgres"]