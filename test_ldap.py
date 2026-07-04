from ldap3 import Server
from ldap3 import Connection
from ldap3 import ALL

server = Server(
    "DC-01.automate.com.vn",
    port=636,
    use_ssl=True,
    get_info=ALL
)

conn = Connection(
    server,
    user="svc_ad_capability@automate.com.vn",
    password="Password123!",
    auto_bind=True
)

print(conn.bound)