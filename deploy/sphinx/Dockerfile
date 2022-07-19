FROM debian:jessie-slim
WORKDIR /opt/app
ADD ./sphinxsearch_2.3.2-beta-1_jessie_amd64.deb ep.sh ./
RUN apt-get update && apt-get install -y libexpat1 libmysqlclient18 libodbc1 libpq5 && \
    dpkg -i ./sphinxsearch_2.3.2-beta-1_jessie_amd64.deb && \
    rm -rf /var/cache/apt/archives /var/lib/apt/lists/*. && \
    rm sphinxsearch_2.3.2-beta-1_jessie_amd64.deb && \
    chmod a+x *.sh && \
    # redirect logs to stdout
    ln -sv /dev/stdout /var/log/query.log && \
    ln -sv /dev/stdout /var/log/searchd.log

# USER sphinxsearch
ENTRYPOINT ["/opt/app/ep.sh"]
CMD ['searchd', '--nodetach', '-c', '/etc/sphinxsearch/sphinx.conf']