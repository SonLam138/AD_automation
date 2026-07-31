from ldap3 import Server, Connection, ALL

server = Server(
    "192.168.1.9",
    port=636,
    use_ssl=True,
    get_info=ALL
)

print("creating connection")

conn = Connection(
    server,
    user="Administrator@automate.com.vn",
    password="C0anhtien@123"
)

print("binding")

print(conn.bind())
print(conn.result)