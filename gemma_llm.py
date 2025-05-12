
from langchain_ollama import OllamaLLM # type: ignore
from langchain.prompts import PromptTemplate # type: ignore
from langchain.chains import LLMChain # type: ignore
from langchain_core.output_parsers import StrOutputParser
from db import PushToMongo
import json
# Load Ollama with Gemma model
#llm = OllamaLLM(model="gemma3:4b")

vision = OllamaLLM(model="gemma3:4b", temperature=0.1, max_tokens=2000)

llm = OllamaLLM(model="gemmaGpu")

analyser = OllamaLLM(model="gemma3:1b")

# the prompt template
prompt = PromptTemplate(
    input_variables=["text"],
    template="""
You are an expert in web data extraction and analysis. From the given web-scraped text, extract and return a single structured RAW JSON object strictly following the schema below. DO NOT include any Markdown or code blocks.

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

Ensure the response is a **single, complete, and valid JSON object** only — without comments, Markdown, or explanations.
"""
)
prompt2 = PromptTemplate(
    input_variable=["text"],
    template="""
    You are a Data Analyser so you need to process the given JSON data to store it a vector database so prepare a detailed text covering all details, no markdowns, donot hallucinate and stick with factual data with is given
    do not deviate and add unnecessary extra data
    \"\"\" {text}\"\"\"
    """
)

response_chain = prompt | llm | StrOutputParser()

analyse_chain = prompt2|analyser|StrOutputParser()

input_text = """  உச்சநீதிமன்ற தீர்ப்பால் பல்கலைக்கழக NEWS 18 RY தமிழ்நாடு சட்டங்களில் என்ன மாற்றம்? தமிழ்நாடு கால்நடை அறிவியல் பல்கலை, தமிழ்நாடு கால்நடை அறிவியல் பல்கலை, சட்டம் 1989 சட்டத்திருத்தம் 2023 வேந்தர்; வேந்தர்' துணை வேந்தரை என்பது நியமிப்ப்பார் அரசு என மாற்றம்"""
#run llm
response = response_chain.invoke({"text": input_text})
response_striped = response.strip().removeprefix("```json").removesuffix("```").strip()

print("raw Output:\n", response)

try:
    parsed = json.loads(response_striped)
    print("\n✅ Parsed JSON:\n", parsed)
    mongo_uploader = PushToMongo()
    mongo_uploader.push_json(json_data=parsed)
except json.JSONDecodeError:
    print("\n⚠️ Output is not valid JSON:\n", response)

analyser_response = analyse_chain.invoke({"text":response_striped})
print("Analyser response: ",analyser_response)