import easyocr

# 
reader = easyocr.Reader(['ko', 'en'], gpu=False)
result = reader.readtext('./images/receipt.jpeg')

for (bbox, text, confidence) in result :
  print(f"인식: {text} (신뢰도 {confidence:.2f})")

