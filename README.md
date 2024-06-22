# 🚀 Auto Get Sonic Faucet

Python script to automate the process of getting Sonic Faucet using multiple wallets. This script is designed to handle CAPTCHA solving, proxy usage, and logging.

## ✨ Features
- 🤖 Solve CAPTCHA automatically using 2Captcha
- 🌐 Support for proxy usage (HTTP only)
- 📂 Handle multiple wallets from a file
- 💾 Save successful wallet signatures to a file

## 📋 Requirements
- 🐍 Python3
- 🤖 2Captcha APIKEY (minimum deposit $2)
- 🌐 Proxy (optional)

## 🛠️ Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Tnodes/auto-get-sonic-faucet.git
   ```
2. Navigate to the cloned directory:
   ```bash
   cd auto-get-sonic-faucet
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Setup
1. Create a `.env` file in the same directory with the following content:
   ```
   API_KEY=your_2captcha_api_key
   ```
2. Prepare your `proxy.txt` (optional) and `wallet.txt` files in the same directory.
   - `proxy.txt` should contain one proxy per line in the format `username:password@ip:port` for authenticated proxies or `ip:port` for non-authenticated proxies.
     - **Note:** Only HTTP proxies are supported.
   - `wallet.txt` should contain one wallet address per line.

## 🚀 Usage
Run the script with the following command:
```bash
python main.py
```

## 📄 Notes
- Ensure you have a valid 2Captcha API key and update it in the `.env` file.
- Successful wallet signatures are saved to `successful_wallets.txt`.

## 🔔 Telegram
Join to my telegram channel:
https://t.me/tdropid

## 💖 Support Our Work
🌟 If you have found this script helpful, we invite you to support its development by making a donation. Your generosity enables us to continue improving and expanding our work. Below are the wallet addresses where you can contribute:

```
EVM: 0xC76AE3B69478Eab1a093642548c0656e83c18623
SOL: 7xDtSzUS8Mrbfqa79ThyQHbcDsFK9h4143A1fqTsxJwt
BTC: bc1q7ulh39d644law0vfst4kl8shkd4k58qyjtlsyu
```

Thank you for your support! 🙏