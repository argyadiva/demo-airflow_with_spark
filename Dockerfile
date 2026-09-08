FROM apache/airflow:2.3.4

# Install the Java runtime required by PySpark.
# Debian 11 (bullseye) sudah EOL: arahkan apt ke archive.debian.org.
USER root
RUN printf 'deb [check-valid-until=no] http://archive.debian.org/debian bullseye main\n' > /etc/apt/sources.list && \
    sed -i 's/^deb /#deb /' /etc/apt/sources.list.d/*.list 2>/dev/null || true && \
    apt-get update && \
    apt-get install -y --no-install-recommends openjdk-11-jre-headless && \
    apt-get clean;

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

USER airflow
COPY requirements.txt .
RUN pip install -r requirements.txt