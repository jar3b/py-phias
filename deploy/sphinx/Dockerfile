FROM debian:jessie-slim
ADD ./sphinxsearch_2.3.2-beta-1_jessie_amd64.deb .
RUN apt-get update && apt-get install -y libexpat1 libmysqlclient18 libodbc1 libpq5 && \
    dpkg -i ./sphinxsearch_2.3.2-beta-1_jessie_amd64.deb && \
    rm -rf /var/cache/apt/archives /var/lib/apt/lists/*. && \
    rm sphinxsearch_2.3.2-beta-1_jessie_amd64.deb