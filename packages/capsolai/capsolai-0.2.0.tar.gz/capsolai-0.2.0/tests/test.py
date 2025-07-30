from capsolai import CaptchaSolver

cs = CaptchaSolver(
    "github-signup",
    key="C-AI-9646F42A4F98B2A4D385029284B8980A" # empty key for testing purposes
)

print(cs.balance())

print(cs.solve(
    proxy="http://user:pass@proxyserver:port",
    blob="blob_data",
    browser="firefox",
    operating_system="windows",
    version=139
))