from pathlib import Path
from urllib.request import urlretrieve
import zipfile

DATA = Path('data')
DATA.mkdir(exist_ok=True)
FILES = {
    'metadata': 'https://storage.googleapis.com/rxrx/rxrx1/rxrx1-metadata.zip',
    'embeddings': 'https://storage.googleapis.com/rxrx/rxrx1/rxrx1-dl-embeddings.zip',
}
for name, url in FILES.items():
    zip_path = DATA / f'{name}.zip'
    if not zip_path.exists():
        print(f'Downloading {name}...')
        urlretrieve(url, zip_path)
    out = DATA / name
    out.mkdir(exist_ok=True)
    marker = out / '.done'
    if not marker.exists():
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(out)
        marker.write_text('ok')
    print(f'{name}: ready at {out}')
print('Data ready.')
