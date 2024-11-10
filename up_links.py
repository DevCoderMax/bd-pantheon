import requests
from bs4 import BeautifulSoup

# URL de Solicitação
url = 'https://www.invertexto.com/ajax/notepad.php'

# Cabeçalhos da Requisição
headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Cookie': 'PHPSESSID=q7lruh1n5uj4ajq241kvtdcffv; clever-counter-83219=0-1; __gads=ID=05509c1732992c29:T=1725490627:RT=1725490627:S=ALNI_Ma1B2ILICBF1MmpLPymm_QdUOeN_w; __gpi=UID=00000a4f5916f2c7:T=1725490627:RT=1725490627:S=ALNI_Mbi6wkXXWQnR-k-28J6OFcC1sRNAg; __eoi=ID=3a4a597f30180c4c:T=1725490627:RT=1725490627:S=AA-AfjZcpuKb9-IiwxDDReSVb3MZ; FCNEC=%5B%5B%22AKsRol8AQ_417qAzn9W8-9uzPdoBbXcu7ORJo3vUjZRIxNR_8XvJJy_rJGX4_IXZbn1akd9pO-OjGsD5fw-KC5DnB2NnbmYggaAutMt5O2WX19O-bCpkFly1W2esqpqf8DxWce4OgvznWGepac98-a-5vjhbXHKvzQ%3D%3D%22%5D%5D',
    'Origin': 'https://www.invertexto.com',
    'Referer': 'https://www.invertexto.com/eternal',
    'Sec-CH-UA': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'X-Requested-With': 'XMLHttpRequest'
}

def salvar_conteudo(conteudo):
    # Dados da Requisição
    data = {
        'token': 'oEPWrESoJiRoshhtYBmI5Q8K1JOQSP7a',
        'saved_text': conteudo  # \n é utilizado para representar uma quebra de linha
    }

    # Enviando a Requisição POST
    response = requests.post(url, headers=headers, data=data)

    # Imprimindo a Resposta
    return 'Status Code: ' + str(response.status_code) + '\n' + 'Response Text: ' + response.text

# URL de Solicitação para a nova função
url_get = 'https://www.invertexto.com/eternal'

# Cabeçalhos da Requisição para a nova função
headers_get = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Cache-Control': 'max-age=0',
    'Cookie': 'PHPSESSID=q7lruh1n5uj4ajq241kvtdcffv; clever-counter-83219=0-1; __gads=ID=05509c1732992c29:T=1725490627:RT=1725490627:S=ALNI_Ma1B2ILICBF1MmpLPymm_QdUOeN_w; __gpi=UID=00000a4f5916f2c7:T=1725490627:RT=1725490627:S=ALNI_Mbi6wkXXWQnR-k-28J6OFcC1sRNAg; __eoi=ID=3a4a597f30180c4c:T=1725490627:RT=1725490627:S=AA-AfjZcpuKb9-IiwxDDReSVb3MZ; FCNEC=%5B%5B%22AKsRol8AQ_417qAzn9W8-9uzPdoBbXcu7ORJo3vUjZRIxNR_8XvJJy_rJGX4_IXZbn1akd9pO-OjGsD5fw-KC5DnB2NnbmYggaAutMt5O2WX19O-bCpkFly1W2esqpqf8DxWce4OgvznWGepac98-a-5vjhbXHKvzQ%3D%3D%22%5D%5D',
    'Referer': 'https://www.invertexto.com/notepad',
    'Sec-CH-UA': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
}

def obter_conteudo():
    # Enviando a Requisição GET
    response = requests.get(url_get, headers=headers_get)
    
    # Analisando o HTML da resposta
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Procurando a URL do ngrok no conteúdo da textarea
    ngrok_url = soup.find('textarea', {'name': 'saved_text'}).text.strip()
    
    # Retornando a URL do ngrok
    return ngrok_url

print(obter_conteudo())