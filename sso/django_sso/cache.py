import os
import redis

def requestJWT():
    pass

def cacheToken(jwt):
    return connection.setex(jwt, '1', session_default)

def isTokenCached(jwt):
    return connection.get(jwt)

def requestToken():
    jwt  = requestJWT()
    return cacheToken(jwt)

def graduateToken():
    pass

def revokeToken():
    pass

if __name__ == '__main__':
    print (f"[+] connecting")
    session_default = 1500
    env_port = 22222
    env_pass = "CheiZah8oop3Nu9fkabe3aiPaWieT3ohaigh2Iay"
    env_pass = os.environ.get
    connection = redis.Redis('localhost', port=env_port, password=env_pass)
    print (f"[+] {len(connection.client_list())} clients connected")
    connection.close()
    print ("[+] connection closed")
