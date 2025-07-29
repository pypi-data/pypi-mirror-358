from os import environ

import pandas as pd
from sqlalchemy import URL, create_engine

# https://www.postgresql.org/docs/devel/auth-methods.html#gssapi-auth
# https://www.postgresql.org/docs/devel/gssapi-auth.html


# https://stackoverflow.com/questions/64102900/configure-gssapi-to-connect-postgresql-server-using-ad

# https://community.denodo.com/docs/html/document/denodoconnects/8.0/en/Denodo%20Dialect%20for%20SQLAlchemy%20-%20User%20Manual
# pip install denodo-sqlalchemy[flightsql] sqlalchemy psycopg2-binary pandas adbc_driver_flightsql gssapi

# https://pypi.org/project/adbc-driver-flightsql/
# https://arrow.apache.org/adbc/current/driver/flight_sql.html
# https://pypi.org/project/denodo-sqlalchemy/

# https://pypi.org/project/denodo-sqlalchemy/

uri = URL.create(
    "denodo+psycopg2",
    username="server/" + environ["DENODO_SQL_USERNAME"],
    password=environ["DENODO_SQL_PASSWORD"],
    host=["DENODO_SQL_HOST"],
    # 9999,
    port=9996,  # Port for psycopg2 according to documentation
    # If the database doesn't exist, it will fail
    # NOTE "server/" is the servicename for kerberos
    # https://www.postgresql.org/docs/devel/gssapi-auth.html
    database=["DENODO_SQL_DATABASE"],  #
)
# uri = "denodo+psycopg2://<user>:<password>@<host>:<port[9996]>/<database>"
print("URI Ready")
print(uri)

engine = create_engine(uri, connect_args={"sslmode": "require"})
print("Engine Ready")


query = "SELECT * FROM fv_domain_names"

data = pd.read_sql(query, engine)
