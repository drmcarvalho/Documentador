from agent import DocumentadorAgent, make_request
import pathlib


if __name__ == '__main__':
    """docAgent = DocumentadorAgent()
    docAgent.start()"""

    """content, code = make_request("https://httpbin.org/json", None, {"accept": "application/json"})
    print(code)
    print(content)"""

    """_prompt_cfg = "Please convert the following code into a Control Flow Graph using graphviz dot language syntax.\n" \
                  "```\n" \
                  "{code}\n" \
                  "```\n"\
                  "The output must be only the CFG diagram in DOT language.\n"
    print(_prompt_cfg.format(code="Teste de codigo\nLinha 2"))"""
    path = pathlib.Path('C:\\temp\\report2.csv')
    print(path.resolve())
