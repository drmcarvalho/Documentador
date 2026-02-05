from agent import DocumentadorAgent, make_request

if __name__ == '__main__':
    """docAgent = DocumentadorAgent()
    docAgent.start()"""
    r, code = make_request("https://httpbin.org/json", None, {"accept": "application/json"})
    print(code)
    print(r.read().decode())
