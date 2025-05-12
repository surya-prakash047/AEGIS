from llm_part.gemma3 import LLMProcessor

input = " SNJ 10000 GRANULATED SUGAR HEADLINES பஹல்காம் தாக்குதல் தக்க பதிலடி கொடுக்கப்படும்; தந்த வளன   /THANTHITV WWW.THANTHITV.COM ம13  /THANTHIONETV THANTHI TV"

model = LLMProcessor()

response = model.generate_response(input=input)
#print(response)