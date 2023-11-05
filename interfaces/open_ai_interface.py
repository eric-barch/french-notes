import json
import os

import openai
from dotenv import load_dotenv
from global_variables import source_language
from models.note import Note


class OpenAiInterface:
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def call_api(self, systemPrompt: str, string: str):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": systemPrompt},
                {
                    "role": "user",
                    "content": string,
                },
            ],
        )
        return response.choices[0].message.content

    def look_up_tokens(self, text):
        system_prompt = f"""
            For a given string in {source_language}, return an array of JSON objects, one for each 
            bracketed token. Include fields: "token", "pos", "source", "target", "gender", and 
            "number". If the token is a VERB, "source" and "target" should be in their infinitive 
            form. Ensure the response array matches the number of bracketed tokens in the request.
            Use the following examples as guidance to craft your response.

            Generic example:

            Response: {{
                "token": token text, always EXACTLY how it appears in the string,
                "pos": token part of speech abbreviation,
                "source": the {source_language} word,
                "target": English translation of source,
                "gender": "MASC", "FEM", or null, as applicable,
                "number": "SING", "PLUR", or null, as applicable
            }}

            Choose from the following parts of speech: ADJ, ADP, ADV, AUX, CONJ, CCONJ, DET, INTJ, 
            NOUN, NUM, PART, PRON, PROPN, PUNCT, SCONJ, SYM, VERB, X
            
            Other examples:

            Numerical Value:

            Request: "[onze]"
            Response: {{
                "token": "onze",
                "pos": "NUM",
                "source": "onze",
                "target": "eleven",
                "gender": null,
                "number": null
            }}

            Noun:

            Request: "[heures]"
            Response: {{
                "token": "heures",
                "pos": "NOUN",
                "source": "heures",
                "target": "hours",
                "gender": "FEM",
                "number": "PLUR"
            }}

            Adjective:

            Request: "[pleine]"
            Response: {{
                "token": "pleine",
                "pos": "ADJ",
                "source": "pleine",
                "target": "full",
                "gender": "FEM",
                "number": "SING"
            }}
            
            Verb in non-infinitive form:

            Request: "[regardant]"
            Response: {{
                "token": "regardant",
                "pos": "VERB",
                "source": "regarder",
                "target": "to look",
                "gender": null,
                "number": null
            }}

            Short Form/Abbreviated Token:

            Request: "[C']"
            Response: {{
                "token": "C'",
                "pos": "PRON",
                "source": "ce", // inferred from string context
                "target": "it",
                "gender": "MASC",
                "number": "SING"
            }}

            Part of Hyphenated Token:

            Request: "[Ferme]-la" // '-la' is ignored because it is not inside brackets
            Response: {{
                "token": "Ferme",
                "pos": "VERB",
                "source": "fermer",
                "target": "to close",
                "gender": null,
                "number": null
            }}
        """

        print(f"OpenAI request: {text.get_marked_string()}")

        request = text.get_marked_string()
        response = json.loads(self.call_api(system_prompt, request))

        # for debugging
        print(f"OpenAI response: {json.dumps(response, indent=4)}")

        marked_tokens = text.get_marked_tokens()

        if len(response) != len(marked_tokens):
            print(
                f"\n\033[31mWARN:\033[0m received different number of responses than requests sent"
            )

        for i, item in enumerate(response):
            pos = item.get("pos")
            source = item.get("source")
            target = item.get("target")
            gender = item.get("gender")
            number = item.get("number")

            note = Note(pos, source, target, None, gender, number)

            marked_tokens[i].add_note(note)
