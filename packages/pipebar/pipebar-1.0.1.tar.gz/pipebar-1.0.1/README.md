![preview](https://raw.githubusercontent.com/fabfawufawd/PipeBar/refs/heads/main/screen.png)

Lightweight and stylish command-line progress bar written in pure **Python** with colorful ANSI output. Perfect for downloads, iterations, or pipelines where you want clean, responsive visual feedback.

---

## 🚀 Features

- ⏱️ ETA and speed tracking
- 🎨 Colorful and modern terminal output (no external dependencies)
- 📦 Works as iterator or manual `.update()` style
- ✅ Minimal and production-ready

---

## 🧪 Usage

```python
from pipebar import ProgressBar

n = 100_000_000

with ProgressBar(total=n, unit='M', scale=1_000_000) as pbar:
    result = 0

    for i in range(n):
        result += i ** 2
        pbar.update()

print(f'Result: {result}')
```

---

## 📁 For file downloads

```python
from pipebar import ProgressBar
import requests
import os

red = '\033[38;2;235;64;52m'
end = '\033[0m'

def download_file(url):
    url = url.strip('/')
    file_name = url.split('/')[-1]
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    total_size_mb = total_size / (1024 * 1024)
    print(f'Downloading {file_name} ({total_size_mb:.1f} MB)')
    
    with ProgressBar(total=total_size, unit='MB', scale=1024*1024) as pbar:
        try:
            with open(file_name, 'wb') as file:
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    pbar.update(len(data))
        except KeyboardInterrupt:
            print(f'\n{red}ERROR: Aborted by user.{end}')
            if os.path.exists(file_name):
                os.remove(file_name)
            raise SystemExit(0)

download_file('http://ipv4.download.thinkbroadband.com/200MB.zip')
```

---

## ⚙️ ProgressBar Parameters

| Parameter    | Type        | Default | Description                                                                                |
| ------------ | ----------- | ------- | ------------------------------------------------------------------------------------------ |
| `iterable`   | `Iterable`  | `None`  | Optional iterable to wrap. If provided, `ProgressBar` acts as a generator.                 |
| `total`      | `int`       | `None`  | Total number of units (e.g., items, bytes). Required for ETA/speed display.                |
| `unit`       | `str`       | `'it'`  | Unit name (e.g., `'MB'`, `'files'`, `'records'`). Displayed after progress numbers.        |
| `scale`      | `int/float` | `1`     | Scale factor to convert units (e.g., `1024*1024` to convert bytes to MB).                  |
| `bar_length` | `int`       | auto    | Visual length of the progress bar in characters. Auto-adjusts to terminal size if not set. |
