from http.server import BaseHTTPRequestHandler
import json, base64, os
import google.generativeai as genai
import PIL.Image
import io

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

PROMPT = """Você é um especialista em micologia. Analise a imagem e responda APENAS em JSON válido:
{
  "nome_provavel": "nome científico e popular",
  "confianca": "alta | média | baixa",
  "alternativas": ["alternativa 1", "alternativa 2"],
  "aviso": "aviso ou null",
  "descricao_curta": "1 frase"
}"""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length)
        
        # Pega a imagem do body (base64)
        data = json.loads(body)
        img_data = base64.b64decode(data['imagem'])
        img = PIL.Image.open(io.BytesIO(img_data))
        
        resposta = model.generate_content([PROMPT, img])
        texto = resposta.text.strip()
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        
        resultado = json.loads(texto)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resultado).encode())
