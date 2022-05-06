## Developer guide

### Get the dependencies & the dev dependencies
```bash
cd app && pip install -r requirements.txt -r requirements.dev.txt
```

### Format the code
```bash
cd app && autopep8 --in-place --aggressive --aggressive *.py
```

### Build the Docker image
```bash
docker build -t tydom2mqtt .
```

### Run the Docker image
```bash
docker run -it --rm -e TYDOM_MAC="001A25123456" -e TYDOM_PASSWORD="secret" tydom2mqtt
```
