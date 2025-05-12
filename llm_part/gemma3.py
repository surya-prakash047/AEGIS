from langchain_ollama import OllamaLLM  # type: ignore
from langchain.prompts import PromptTemplate  # type: ignore
from langchain.chains import LLMChain  # type: ignore
from langchain_core.output_parsers import StrOutputParser
from db import PushToMongo
import json
import re


class LLMProcessor:
    def __init__(self):
        self.llm = OllamaLLM(model="gemmaGpu")
        self.analyser = OllamaLLM(model="gemma3:1b")

        self.prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            You are an expert in web data extraction and analysis. From the given web-scraped text, extract and return a single structured RAW JSON object strictly following the schema below. DO NOT include any Markdown or code blocks or any quotes.
            give only one JSON response
            \"\"\"{text}\"\"\"




            Return ONLY valid JSON with the following fields:

            - 'location': location of the incident (e.g., "Chennai, Tamil Nadu")
            - 'time': date or datetime of the incident, in ISO format or JavaScript `new Date()` format
            - 'severity': level of severity – one of "high", "medium", or "low"
            - 'source': source of the data (e.g., "Weather Department"). If not present, use "miscellaneous"
            - 'impact': a short description of the event's impact
            - 'description': a brief one-line explanation of what happened
            - 'affectedArea': the size of the affected area (in km², if available; else a rough numeric estimate)
            - 'casualties': number of casualties (set 0 if not mentioned)
            - 'status': current status of the incident (e.g., "active", "contained", "resolved")
            - 'processed_by': set this to "AI Analysis System"
            - 'processing_time': current time of processing, in ISO or JavaScript `new Date()` format
            - 'analysis': a detailed 2–3 line analysis of the situation, trends, or patterns
            - 'recommendations': an array of 3–5 recommended actions
            - 'lastUpdated': same as `processing_time`

            
            """
        )   

        self.prompt2 = PromptTemplate(
            input_variables=["text"],
            template="""
            You are a Data Analyser so you need to process the given JSON data to store it a vector database so prepare a detailed text covering all details, no markdowns, donot hallucinate and stick with factual data with is given
            do not deviate and add unnecessary extra data
            \"\"\" {text}\"\"\"
            """
        )

    

        self.response_chain = self.prompt | self.llm | StrOutputParser()
        self.analyse_chain = self.prompt2 | self.analyser | StrOutputParser()

    def format_context(self, docs,max_chars=1000):
        """
        Turn a list of Document objects into a single string for prompt injection.
        Truncates each doc to avoid excessively long prompts.
        """
        entries = []
        for doc in docs:
            text = doc.page_content.strip()
            # Optional: include structured output examples
            example = json.dumps(doc.metadata.get("output", {}), indent=None)
            entries.append(f"Input: {text}\nOutput: {example}")
        # Join with separators and crop total length
        context = "\n\n---\n\n".join(entries)
        return context[:max_chars]


    def generate_response(self, input):

        response = self.response_chain.invoke({"text": input})
        response_striped = response.strip().removeprefix(" ```json").removesuffix("```").strip()

        print("Agent1 Done")

          # Remove triple quotes and markdown formatting
        cleaned = re.sub(r'^[\s`"\n]*json[\s`"\n]*', '', response, flags=re.IGNORECASE)
        cleaned = cleaned.strip().removeprefix('```json').removesuffix('```').strip()
        cleaned = cleaned.strip('"\n ')

        try:
            parsed = json.loads(cleaned)
            print("\n✅ Parsed JSON:\n", parsed)
            mongo_uploader = PushToMongo()
            mongo_uploader.push_json(json_data=parsed)
        except json.JSONDecodeError:
            print("\n⚠️ Output is not valid JSON:\n", cleaned)

        #analyser_response = self.analyse_chain.invoke({"text": response_striped})
        print("Analyser Done")
        return cleaned
