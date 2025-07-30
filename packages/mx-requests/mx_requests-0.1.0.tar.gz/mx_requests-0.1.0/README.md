# 🔑 MontgomeryNX Proxy Requests Wrapper

A drop-in replacement for Python's `requests` that routes all calls through the [MontgomeryNX](https://www.montgomerynx.com) scraping proxy.

## 📦 Installation

```bash
pip install mx_requests
```

## 🚀 Usage

In place of import requests,

```python
import mx_requests

mx_requests.set_api_key("your_api_key")
response =mx_requests.get("https://example.com")
print(response.text)
```

Behind the scenes, the URL is rewritten to:

`https://proxy.montgomerynx.com/<your_api_key>/https://example.com`

## 🔐 API Key

Call once `set_api_key("your_api_key")` before making requests.

## ✨ Features

- One-liner replacement for `requests`
- IP rotation, retries, and caching handled automatically
- Works with all HTTP methods: `get`, `post`, `put`, `delete`, `head`, `options`
- No extra dependencies beyond `requests`
- Perfect for scraping-friendly public sites

## 📜 Legal Notice

This service is intended solely for accessing publicly available web content. Use on sites that require login or explicitly disallow scraping is not permitted. Keys may be suspended for misuse.
