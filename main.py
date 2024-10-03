import requests
import random
import time
import re
import sys
from fake_useragent import UserAgent
from twocaptcha import TwoCaptcha, ApiException, ValidationException, NetworkException, TimeoutException
from typing import List, Optional
from loguru import logger
from dotenv import load_dotenv
import os

load_dotenv()
logger.remove(0)
logger.add(sys.stderr, level='DEBUG', colorize=True, format="{time:HH:mm:ss} <level>| {level: <7} | {message}</level>")

def load_lines(file_path: str) -> List[str]:
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logger.warning(f"{file_path} not found, continuing without it")
        return []

def generate_fake_user_agent() -> str:
    return UserAgent().random

def solve_captcha(solver: TwoCaptcha, sitekey: str, url: str, useragent: str, max_attempts: int = 3) -> Optional[str]:
    for attempt in range(max_attempts):
        try:
            logger.info("Solving CAPTCHA...")
            result = solver.turnstile(sitekey=sitekey, url=url, useragent=useragent)
            logger.info("CAPTCHA solved")
            return result['code']
        except (ValidationException, NetworkException, TimeoutException, ApiException) as e:
            logger.error(f"Error solving CAPTCHA: {e}")
            if attempt < max_attempts - 1:
                backoff_time = 2 ** (attempt + 1)
                logger.info(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
    logger.error("Failed to solve CAPTCHA after maximum attempts")
    return None

def make_api_request(api_url: str, captcha_code: str, proxy: Optional[str], max_attempts: int = 3) -> Optional[str]:
    headers = generate_headers()
    api_url_with_captcha = api_url.format(captcha_code=captcha_code)
    proxies = {'http': proxy} if proxy else None
    log_message = 'with' if proxy else 'without'
    logger.info(f'Making request to API {log_message} proxy...')

    for attempt in range(max_attempts):
        try:
            response = requests.get(api_url_with_captcha, headers=headers, proxies=proxies)
            return handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            if attempt < max_attempts - 1:
                backoff_time = 2 ** (attempt + 1)
                logger.info(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
    logger.error("Failed to make API request after maximum attempts")
    return None

def generate_headers() -> dict:
    user_agent = generate_fake_user_agent()
    platform_match = re.search(r'\([^;]+', user_agent)
    system_platform = platform_match.group(0)[1:] if platform_match else "Unknown"
    return {
        "path": "/airdrop/{captcha_code}",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        "Dnt": "1",
        "Origin": "https://faucet.sonic.game",
        "Priority": "u=1, i",
        "Referer": "https://faucet.sonic.game/",
        "User-Agent": user_agent,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": f'"{system_platform}"'
    }

def handle_response(response: requests.Response) -> Optional[str]:
    if response.status_code == 200:
        try:
            data = response.json()
            if data['status'] == 'ok':
                logger.info(f"Response Status: {data['status']}")
                return data['data']['data'].strip()
            else:
                logger.error(f"Error in API response: {data}")
        except ValueError:
            logger.error("Error: Received invalid JSON")
            logger.error(f"Response content: {response.content}")
    elif response.status_code == 429:
        logger.warning("Received 429 Too Many Requests, skipping to next wallet")
        return "too_many_requests"
    elif response.status_code == 401:
        logger.warning("Received 401 You might be a robot, skipping to next wallet")
        return "might_be_a_robot"
    else:
        logger.error(f"Error: {response.status_code}, Response content: {response.content}")
    return None

def save_wallet_signature(wallet: str, signature: str) -> None:
    with open('successful_wallets.txt', 'a') as file:
        file.write(f'{wallet},{signature}\n')

def banner() -> None:
    art = """
 _________________________________________
|        AUTO GET SONIC FAUCET            |
|   GITHUB: https://github.com/Tnodes     |
|   TELEGRAM: https://t.me/tdropid        |   
|_________________________________________|     
    """
    print(art)

def choose_network() -> str:
    while True:
        print("\nChoose the network:")
        print("1. Devnet")
        print("2. Testnet")
        choice = input("Enter your choice (1 or 2): ")
        if choice == '1':
            return "devnet"
        elif choice == '2':
            return "testnet"
        else:
            print("Invalid choice. Please enter 1 or 2.")

def main() -> None:
    banner()

    api_key = os.getenv("API_KEY")
    if not api_key:
        logger.error("API key not found in environment variables")
        return
    
    network = choose_network()
    
    sitekey = '0x4AAAAAAAc6HG1RMG_8EHSC'
    url = 'https://faucet.sonic.game/'
    
    if network == "devnet":
        api_base_url = "https://faucet-api.sonic.game/airdrop/"
    else:  # testnet
        api_base_url = "https://faucet-api-grid-1.sonic.game/airdrop/"
    
    proxies = load_lines('proxy.txt')
    wallets = load_lines('wallet.txt')
    
    if not wallets:
        logger.error("No wallets to process.")
        return

    solver = TwoCaptcha(api_key)

    for wallet in wallets:
        logger.info(f"Processing wallet: {wallet}")
        api_url = f"{api_base_url}{wallet}/0.5/{{captcha_code}}"
        proxy = random.choice(proxies) if proxies else None
        captcha_code = solve_captcha(solver, sitekey, url, generate_fake_user_agent())
        
        if not captcha_code:
            logger.error(f"Unable to solve CAPTCHA after multiple attempts for wallet {wallet}, skipping request")
            continue
        
        signature = make_api_request(api_url, captcha_code, proxy)
        if signature and signature not in ["too_many_requests", "might_be_a_robot"]:
            logger.info(f"Successfully received signature for wallet {wallet}, {signature}")
            save_wallet_signature(wallet, signature)
        
        time.sleep(20)

if __name__ == "__main__":
    main()