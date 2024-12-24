# Destiny 2 Player Statistics

## Introduction

## Getting Started

### Checkout Code

### Retrieve X-API Key from Bungie

### Initialize Destiny 2 Manifest

Now that you have your X-API Key, you can initialize the Destiny 2 manifest. Read more about the manifest below. This process does not need to be done more than once.

To create your local manifest, you need to do a couple of things: **Add your X-API Key** and **Create a path for the manifest**.

1. **Add your X-API Key**: Add your X-API Key as an environment variable to `.env` 

```python
X_API_KEY = "Your API Key Here"  # Get this from Bungie
```

2. **Create a path for the manifest**: Add a path to the destination folder for the manifest files as an environment variable to `.env`. It is recommended they are store outside the repo.

```python
PATH_TO_MANIFEST = "/Your/Path/Here/" 
```

Be sure the environment variabe names match exactly!

Once you've set your environment variables, you can run `destiny_manifest.py`, and if successful, you should find three files in your destination folder: `Manifest.content`, `manifest.pickle`, and `MANZIP`.