# 🌐 Python Script: Navegação Anônima Automatizada com Tor e Chrome/Chromium

Este script Python permite a navegação anônima automatizada na web utilizando o navegador Chrome ou Chromium em conjunto com o serviço Tor. Ele permite o processamento de múltiplos links a partir de um arquivo de texto, garantindo que cada link seja acessado a partir de um IP diferente, gerado pelo Tor. 🚀

## 🛠️ Funcionalidades

- **Navegação Anônima**: Utiliza o serviço Tor para garantir anonimato ao navegar por URLs.
- **Alteração Automática de IP**: A cada requisição, o script pode reiniciar o serviço Tor para garantir um novo IP.
- **Armazenamento de Headers**: Os headers das requisições são salvos para cada IP usado, permitindo reutilização futura.
- **Processamento de Múltiplos Links**: Suporte para processar uma lista de URLs a partir de um arquivo de texto.
- **Aceitação Automática de Consentimentos**: Detecta e aceita automaticamente páginas de consentimento, como as do YouTube.
- **Manipulação de Vídeos**: Aguarda a reprodução de vídeos em páginas carregadas.

## ⚙️ Requisitos

- Python 3.6+
- Selenium WebDriver
- Serviço Tor instalado e configurado no sistema
- Chrome ou Chromium instalado e o correspondente ChromeDriver

## 📦 Instalação

1. **Clone o repositório:**

```bash
git clone https://github.com/gsLukao/monetize.git
cd monetize
```

2. **Instale as dependências:**

É recomendável utilizar um ambiente virtual.

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Certifique-se de que o Tor está rodando:**

Para sistemas Linux:

```bash
sudo systemctl start tor
```

## 🚀 Uso

### Processar um Único Link

Para abrir uma única URL utilizando o Tor e o navegador Chrome/Chromium:

```bash
python3 script.py -l https://example.com
```

### Processar Múltiplos Links a Partir de um Arquivo

Para processar uma lista de URLs de um arquivo de texto, com reinício automático após o término da lista:

```bash
python3 script.py -L urls.txt
```

### Parâmetros Disponíveis

- `-l, --link`: Especifica uma única URL para abrir.
- `-L, --list`: Especifica um arquivo de texto contendo uma lista de URLs.
- `--browser`: Define o navegador a ser utilizado (padrão: `chromium-browser`).
- `--window-size`: Define o tamanho da janela do navegador (padrão: `100,400`).
- `--delay`: Define o tempo de espera (em segundos) entre as solicitações (padrão: `6`).
- `--max-retries`: Define o número máximo de tentativas de reinício do processamento de URLs (padrão: `3`).

### Exemplo de Uso

Para processar uma lista de URLs com um atraso de 10 segundos entre as solicitações:

```bash
python3 script.py -L urls.txt --delay 10
```

## 📄 Logs e Headers

- **Log de IPs**: Os IPs utilizados são armazenados no arquivo `ips.log`.
- **Headers**: Os headers das requisições são salvos em arquivos JSON, armazenados no diretório `headers`.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para colaborar. 

---

💡 **Dica:** Utilize este script de forma responsável e em conformidade com as leis locais. O anonimato é uma ferramenta poderosa, mas deve ser usado com cautela e ética.
