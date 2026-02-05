import json

from agent import DocumentadorAgent, make_request
import constants
import pathlib


if __name__ == '__main__':
    """docAgent = DocumentadorAgent()
    docAgent.start()"""

    """content, code = make_request("https://httpbin.org/json", None, {"accept": "application/json"})
    print(code)
    print(content)"""

    _prompt_cfg = "Please convert the following code into a Control Flow Graph using graphviz dot language syntax.\n" \
                  "```\n" \
                  "{code}\n" \
                  "```\n"\
                  "The output must be only the CFG diagram in DOT language.\n"
    prompt = _prompt_cfg.format(code="""
    def start(self):
        for target in (self._watch_config, self._watch_files):
            p = Process(target=target, daemon=True)
            self._processes.append(p)
            p.start()
        try:
            for process in self._processes:
                process.join()
        except KeyboardInterrupt:
            logger.info("Exited")
    """)

    content, code = make_request(
        constants.API_URL_GEMINI,
        {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        },
        {
            constants.API_KEY_GEMINI_HEADER: constants.API_KEY,
            "Content-Type": "application/json"
        },
        "POST",
    )

    print(code)
    print(json.loads(content))

    """path = pathlib.Path('C:\\temp\\report2.csv')
    print(path.resolve())"""

    textResponse = """{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "```dot\n    digraph CFG {\n        node [shape=box, fontname=\"Courier\"];\n        edge [fontname=\"Courier\"];\n\n        START [label=\"START\", shape=oval];\n        \n        LOOP1_HEAD [label=\"for target in (\\n  self._watch_config, \\n  self._watch_files\\n)\", shape=diamond];\n        \n        LOOP1_BODY [label=\"p = Process(target=target, daemon=True)\\nself._processes.append(p)\\np.start()\"];\n        \n        TRY_START [label=\"TRY\"];\n        \n        LOOP2_HEAD [label=\"for process in self._processes\", shape=diamond];\n        \n        LOOP2_BODY [label=\"process.join()\"];\n        \n        EXCEPT_KI [label=\"except KeyboardInterrupt\", shape=diamond];\n        \n        LOG_EXIT [label=\"logger.info(\\\"Exited\\\")\"];\n        \n        END [label=\"END\", shape=oval];\n\n        /* Flow Logic */\n        START -\u003e LOOP1_HEAD;\n        \n        LOOP
1_HEAD -\u003e LOOP1_BODY [label=\"next target\"];\n        LOOP1_BODY -\u003e LOOP1_HEAD;\n        \n        LOOP1_HEAD -\u003e TRY_START [label=\"loop finished\"];\n        \n        TRY_START -\u003e LOOP2_HEAD;\n        \n  
      LOOP2_HEAD -\u003e LOOP2_BODY [label=\"next process\"];\n        LOOP2_BODY -\u003e LOOP2_HEAD;\n        \n        LOOP2_HEAD -\u003e END [label=\"loop finished\"];\n        \n        /* Exception Flow */\n        LOOP2_HE
AD -\u003e EXCEPT_KI [label=\"interrupt\", style=dashed];\n        LOOP2_BODY -\u003e EXCEPT_KI [label=\"interrupt\", style=dashed];\n        \n        EXCEPT_KI -\u003e LOG_EXIT [label=\"caught\"];\n        LOG_EXIT -\u003e END;\n        EXCEPT_KI -\u003e END [label=\"other exception\", style=dotted];\n    }\n```",
            "thoughtSignature": "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"
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 127,
    "candidatesTokenCount": 438,
    "totalTokenCount": 1804,
    "promptTokensDetails": [
      {
        "modality": "TEXT",
        "tokenCount": 127
      }
    ],
    "thoughtsTokenCount": 1239
  },
  "modelVersion": "gemini-3-flash-preview",
  "responseId": "ic2EafG3AqHqz7IPopXvwQU"
}
    """
    """data = json.loads(textResponse, strict=False)
    print(data)"""