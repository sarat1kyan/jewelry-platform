import os, time, jwt
def create_agent_jwt(agent_id: str) -> str:
    secret = os.getenv("JWT_SECRET", "secret")
    payload = {"sub": agent_id, "iat": int(time.time()), "exp": int(time.time()) + 86400, "iss": os.getenv("JWT_ISSUER", "sls-platform")}
    return jwt.encode(payload, secret, algorithm="HS256")
