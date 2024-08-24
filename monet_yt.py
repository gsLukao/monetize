from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import argparse
import subprocess
import time
import socket
import random
import json
import os


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; AS; rv:11.0) like Gecko"
]

LOG_FILE = "ips.log"
HEADERS_DIR = "headers"

def v_lk(link):
    if not link.startswith(('http://', 'https://')):
        link = 'https://' + link
    print(f"Link validado: {link}")
    return link

def cic():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        print("Conexão com a Internet verificada.")
        return True
    except OSError:
        print("Não foi possível conectar à Internet.")
        return False

def rrtor():
    
    print("Reiniciando o serviço Tor...")
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'tor'], check=True)
        time.sleep(10)
        print("Serviço Tor reiniciado.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao reiniciar o Tor: {e}")

def pegar_ip():
    
    try:
        response = subprocess.run(['curl', '--socks5-hostname', '127.0.0.1:9050', 'https://api.ipify.org'], check=True, stdout=subprocess.PIPE)
        ip = response.stdout.decode().strip()
        print(f"IP atual obtido: {ip}")
        return ip
    except subprocess.CalledProcessError as e:
        print(f"Erro ao obter o IP atual: {e}")
        return None

def registro_ip(ip):
    
    try:
        with open(LOG_FILE, 'r+') as file:
            logged_ips = file.read().splitlines()
            if ip not in logged_ips:
                file.write(ip + '\n')
                print(f"IP registrado no log: {ip}")
            else:
                print(f"IP {ip} já está registrado.")
    except FileNotFoundError:
        with open(LOG_FILE, 'w') as file:
            file.write(ip + '\n')
            print(f"Arquivo de log criado e IP registrado: {ip}")

def save_hd(ip, headers):
    os.makedirs(HEADERS_DIR, exist_ok=True)
    headers_file = os.path.join(HEADERS_DIR, f"{ip}.json")
    with open(headers_file, 'w') as f:
        json.dump(headers, f)
    print(f"Headers salvos para o IP {ip}.")

def carrega_hd(ip):

    headers_file = os.path.join(HEADERS_DIR, f"{ip}.json")
    if os.path.exists(headers_file):
        with open(headers_file, 'r') as f:
            headers = json.load(f)
        print(f"Headers carregados para o IP {ip}.")
        return headers
    return None

def ipr():

    print("Tentando obter um novo IP...")
    for attempt in range(2):
        rrtor()
        current_ip = pegar_ip()
        if current_ip and not verifica_ip(current_ip):
            return current_ip
        print(f"IP repetido. Tentando novamente ({attempt + 1}/2)...")
    print("Não foi possível obter um IP diferente.")
    return None

def verifica_ip(ip):

    try:
        with open(LOG_FILE, 'r') as file:
            logged_ips = file.read().splitlines()
            return ip in logged_ips
    except FileNotFoundError:
        return False

def aceitar(driver):

    try:
        if "consent.youtube.com/m?continue=" in driver.current_url:
            print("Página de consentimento/cookie do YouTube detectada.")
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Accept all']"))
            )
            accept_button.click()
            WebDriverWait(driver, 10).until(EC.staleness_of(accept_button))
            print("Consentimento aceito.")
    except Exception as e:
        print(f"Erro ao lidar com a página de consentimento: {e}")

def aguardar(driver):

    print("Aguardando reprodução do vídeo...")
    attempts = 2
    start_time = time.time()

    while attempts > 0:
        try:
            video_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, 'video'))
            )
            total_duration = driver.execute_script("return arguments[0].duration", video_element)
            
            if total_duration is None:
                print("Não foi possível obter a duração do vídeo.")
                return None

            video_end_time = start_time + total_duration
            print(f"Duração total do vídeo: {total_duration} segundos.")
            print(f"Hora atual (página carregada): {time.strftime('%H:%M:%S', time.localtime(start_time))}")
            print(f"Previsão de encerramento: {time.strftime('%H:%M:%S', time.localtime(video_end_time))}")

            while True:
                current_time = time.time()
                elapsed_time = current_time - start_time
                remaining_time = total_duration - elapsed_time
                time_to_end = video_end_time - current_time

                
                if remaining_time < 10 and elapsed_time < total_duration:
                    print("Vídeo carregado parcialmente. Reiniciando a reprodução...")
                    driver.execute_script("arguments[0].currentTime = 0", video_element)  
                    time.sleep(5)  

                if time_to_end <= 10:
                    print(f"Hora atual: {time.strftime('%H:%M:%S', time.localtime(current_time))}.")
                    print(f"Previsão de encerramento foi há {int(-time_to_end)} segundos. Processando o próximo link.")
                    return total_duration

                if elapsed_time >= total_duration + 3:
                    print("Tempo previsto excedido. Prosseguindo para o próximo link.")
                    return total_duration

                time.sleep(1)

        except StaleElementReferenceException:
            print("Elemento de vídeo obsoleto. Tentando re-localizar...")
            attempts -= 1
            if attempts > 0:
                continue
            print("Elemento de vídeo perdido após várias tentativas. Encerrando processamento do link atual.")
            return None
        except TimeoutException:
            attempts -= 1
            if attempts > 0:
                print(f"Elemento de vídeo não encontrado. Tentando novamente ({2 - attempts}/2)...")
                continue
            print("Não foi possível encontrar o vídeo. Encerrando processamento do link atual.")
            return None

def olinks(link, browser='chromium-browser', window_size='100,400'):

    link = v_lk(link)
    user_agent = random.choice(USER_AGENTS)
    headers = {'User-Agent': user_agent}

    current_ip = pegar_ip()
    if current_ip:
        saved_headers = carrega_hd(current_ip)
        if saved_headers:
            headers = saved_headers
        else:
            save_hd(current_ip, headers)

    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=socks5://127.0.0.1:9050')
    chrome_options.add_argument(f'--user-agent={user_agent}')
    chrome_options.add_argument(f'--window-size={window_size}')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--autoplay-policy=no-user-gesture-required')

    chrome_service = Service('/snap/bin/chromium.chromedriver')

    try:
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.get(link)
        print(f"Link {link} aberto com {browser}.")

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(driver, 60).until(lambda d: d.execute_script("return document.readyState") == "complete")
        print("Página carregada.")

        aceitar(driver)

        video_duration = aguardar(driver)
        if video_duration:
            print(f"Tempo total do vídeo: {video_duration} segundos.")
            time.sleep(video_duration)  

    except Exception as e:
        print(f"Erro ao abrir o link {link} com {browser}: {e}")
    finally:
        driver.quit()
        print("Navegador fechado.")

def links(file_path, browser='chromium-browser', window_size='100,400', delay=6, max_retries=3):

    print(f"Processando links do arquivo: {file_path}")
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]

        retry_count = 0
        while retry_count < max_retries:
            for link in urls:
                if link:
                    current_ip = pegar_ip()
                    if current_ip and verifica_ip(current_ip):
                        print("IP repetido. Tentando obter novo IP...")
                        current_ip = ipr()
                        if not current_ip:
                            print("Não foi possível obter novo IP.")
                    
                    if current_ip:
                        registro_ip(current_ip)

                    olinks(link, browser=browser, window_size=window_size)

                    print(f"Aguardando {delay} segundos antes do próximo link...")
                    time.sleep(delay)

            retry_count += 1
            print(f"Reiniciando o processamento das URLs. Tentativa {retry_count}/{max_retries}...")

    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")

def main():

    parser = argparse.ArgumentParser(description="Navegação anônima com Tor e navegador.")
    parser.add_argument('-l', '--link', help='URL para abrir.')
    parser.add_argument('-L', '--list', help='Arquivo com URLs.')
    parser.add_argument('--browser', default='chromium-browser', help='Navegador a ser usado.')
    parser.add_argument('--window-size', default='100,100', help='Tamanho da janela do navegador.')
    parser.add_argument('--delay', type=int, default=6, help='Tempo de espera (em segundos) entre as solicitações.')
    parser.add_argument('--max-retries', type=int, default=3, help='Número máximo de tentativas de reinício do processamento.')
    args = parser.parse_args()

    if args.link:
        olinks(args.link, browser=args.browser, window_size=args.window_size)
    elif args.list:
        links(args.list, browser=args.browser, window_size=args.window_size, delay=args.delay, max_retries=args.max_retries)
    else:
        print("Por favor, forneça uma URL (-l) ou um arquivo de URLs (-L).")

if __name__ == "__main__":
    main()
