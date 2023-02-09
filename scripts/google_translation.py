import googletrans

translator = googletrans.Translator()

str1 = "나는 한국인 입니다."
str2 = "I like burger."
result1 = translator.translate(str1, dest='en')
result2 = translator.translate(str2, dest='ko')

print(f"나는 한국인 입니다. => {result1.text}")
print(f"I like burger. => {result2.text}")