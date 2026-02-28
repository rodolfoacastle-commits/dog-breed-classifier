---
title: Dog Breed Classifier
emoji: 🐕
colorFrom: purple
colorTo: orange
sdk: docker
app_port: 7860
---

# Dog Breed Classifier

Upload a photo or PDF (first page) of a dog to get top-3 breed predictions with circular percentage graphs and recommended dog sweaters. Cat uploads trigger a “No Cats Allowed!” easter egg.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

First run will download the Hugging Face dog-breeds model (one-time).

### Etsy API (optional but recommended)

Sweater recommendations use the [Etsy Open API v3](https://developers.etsy.com/documentation/). Without credentials the app shows placeholder sweaters; with them you get real Etsy listings.

1. Register an app at [etsy.com/developers/register](https://www.etsy.com/developers/register).
2. Copy your **keystring** and **shared secret** from [Your Apps](https://www.etsy.com/developers/your-apps).
3. Create a `.env` file in the project root (see `.env.example`):
   ```
   ETSY_API_KEYSTRING=your_keystring_here
   ETSY_SHARED_SECRET=your_shared_secret_here
   ```

## Run

```bash
flask run
# or: python app.py
# or: ./run.sh   (uses port 5001)
```

Open http://127.0.0.1:5000 (or 5001 if using `./run.sh`) and upload an image or PDF.

**Important:** After any code change, restart the Flask server (Ctrl+C then run the command again) or the old code will keep running and errors may persist.

## Pushing to GitHub

The project is already a git repo with an initial commit. To put it on GitHub:

1. **Set your Git identity** (if you haven’t already):
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your@email.com"
   ```

2. **Create a new repository on GitHub**
   - Go to [github.com/new](https://github.com/new).
   - Choose a name (e.g. `dog-breed-classifier`), leave “Add a README” **unchecked**, then click **Create repository**.

3. **Add the remote and push** (replace `YOUR_USERNAME` and `REPO_NAME` with your GitHub username and repo name):
   ```bash
   cd /Users/rodolfocastillo/Hackathon
   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```
   If GitHub asks you to sign in, use a [Personal Access Token](https://github.com/settings/tokens) as the password when prompted.

After that, your repo will be on GitHub and you can share the link.

## Deploy to Hugging Face Spaces

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space) — select **Docker** as the SDK.
2. Push this repo to the Space (or link your GitHub repo).
3. In the Space **Settings**, add your Etsy secrets as environment variables:
   - `ETSY_API_KEYSTRING`
   - `ETSY_SHARED_SECRET`
4. The Space will build the Docker image and deploy automatically.

The Dockerfile pre-downloads the ML model at build time so the app starts quickly.

## Optional

- Replace `static/barking-dog.gif` with a real barking-dog GIF for the cat easter egg.
