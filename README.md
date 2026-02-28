# Dog Breed Classifier

Upload a photo or PDF (first page) of a dog to get top-3 breed predictions with circular percentage graphs and recommended dog sweaters. Cat uploads trigger a “No Cats Allowed!” easter egg.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

First run will download the Hugging Face dog-breeds model (one-time).

## Run

```bash
flask run
# or: python app.py
# or: ./run.sh   (uses port 5001)
```

Open http://127.0.0.1:5000 (or 5001 if using `./run.sh`) and upload an image or PDF.

**Important:** After any code change, restart the Flask server (Ctrl+C then run the command again) or the old code will keep running and errors may persist.

## Optional

- Replace `static/barking-dog.gif` with a real barking-dog GIF for the cat easter egg.
- Plug a real shopping API into `sweater_service.get_sweaters_for_breed()` (see comments in `sweater_service.py`).
