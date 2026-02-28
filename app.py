"""
Dog Breed Classifier — Flask backend.
Accepts image or PDF upload, runs ImageNet gate (dog/cat/other), then breed model or easter egg.
"""

import base64
import io
import os
from pathlib import Path

# Use project-local cache so we don't need write access to ~/.cache
_PROJECT_ROOT = Path(__file__).resolve().parent
_CACHE_DIR = _PROJECT_ROOT / ".cache"
os.makedirs(_CACHE_DIR / "torch" / "hub", exist_ok=True)
os.makedirs(_CACHE_DIR / "huggingface", exist_ok=True)
import torch
torch.hub.set_dir(str(_CACHE_DIR / "torch" / "hub"))
os.environ.setdefault("HF_HOME", str(_CACHE_DIR / "huggingface"))
os.environ.setdefault("TRANSFORMERS_CACHE", str(_CACHE_DIR / "huggingface"))
from flask import Flask, jsonify, render_template, request
from PIL import Image
from torchvision import models, transforms

# Optional: PDF support
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

# Hugging Face dog breed model (loaded on first use)
BREED_PROCESSOR = None
BREED_MODEL = None
IMAGENET_GATE = None
IMAGENET_TRANSFORM = None

# ImageNet class index ranges (PyTorch 0-999)
DOG_IMAGENET_START, DOG_IMAGENET_END = 151, 269   # 151-268 inclusive
CAT_IMAGENET_START, CAT_IMAGENET_END = 281, 286   # 281-285 (tabby, tiger cat, Persian, etc.)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif", "bmp", "pdf"}
MAX_CONTENT_MB = 10

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024


def allowed_file(filename: str) -> bool:
    ext = (Path(filename).suffix or "").lstrip(".").lower()
    return ext in ALLOWED_EXTENSIONS


def normalize_upload_to_image(file_bytes: bytes, filename: str) -> Image.Image:
    """Convert upload to a single PIL Image. Supports PDF (first page) and images."""
    ext = (Path(filename).suffix or "").lstrip(".").lower()
    if ext == "pdf":
        if not HAS_PYMUPDF:
            raise ValueError("PDF support not available; install pymupdf")
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception:
            raise ValueError("Invalid or empty PDF")
        if len(doc) == 0:
            doc.close()
            raise ValueError("Invalid or empty PDF")
        page = doc[0]
        pix = page.get_pixmap(alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return img
    # Image: open with Pillow (handle animated formats by using first frame)
    img = Image.open(io.BytesIO(file_bytes))
    if getattr(img, "n_frames", 1) > 1:
        img.seek(0)
    return img.convert("RGB")


def _get_imagenet_gate():
    global IMAGENET_GATE, IMAGENET_TRANSFORM
    if IMAGENET_GATE is None:
        IMAGENET_GATE = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        IMAGENET_GATE.eval()
        weights = models.ResNet18_Weights.IMAGENET1K_V1
        IMAGENET_TRANSFORM = weights.transforms()
    return IMAGENET_GATE, IMAGENET_TRANSFORM


def run_imagenet_gate(pil_image: Image.Image) -> str:
    """Return 'dog', 'cat', or 'other' based on ImageNet top prediction."""
    model, transform = _get_imagenet_gate()
    tensor = transform(pil_image).unsqueeze(0)
    with torch.no_grad():
        out = model(tensor)
    _, pred = out.max(1)
    # pred can be a 0-d tensor (has .item()) or in some contexts a plain Python int
    idx = int(pred.item() if hasattr(pred, "item") else pred)
    if DOG_IMAGENET_START <= idx < DOG_IMAGENET_END:
        return "dog"
    if CAT_IMAGENET_START <= idx < CAT_IMAGENET_END:
        return "cat"
    return "other"


def _get_breed_model():
    global BREED_PROCESSOR, BREED_MODEL
    if BREED_MODEL is None:
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        model_id = "raffaelsiregar/dog-breeds-classification"
        BREED_PROCESSOR = AutoImageProcessor.from_pretrained(model_id)
        BREED_MODEL = AutoModelForImageClassification.from_pretrained(model_id)
        BREED_MODEL.eval()
    return BREED_PROCESSOR, BREED_MODEL


def run_breed_model(pil_image: Image.Image, top_k: int = 3) -> list:
    """Return list of {name, percentage} for top-k breeds."""
    processor, model = _get_breed_model()
    inputs = processor(images=pil_image, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.nn.functional.softmax(logits, dim=-1)[0]
    top_probs, top_indices = torch.topk(probs, top_k)
    id2label = model.config.id2label
    # id2label can be dict with string keys ("0", "1") or int keys (0, 1); normalize for lookup
    def label_for_index(idx: int):
        if isinstance(id2label, dict):
            return id2label.get(str(idx)) or id2label.get(idx)
        if isinstance(id2label, (list, tuple)) and 0 <= idx < len(id2label):
            return id2label[idx]
        return None
    # Convert to Python lists once so we never call .item() (avoids int/tensor issues)
    prob_list = top_probs.cpu().tolist()
    idx_list = top_indices.cpu().tolist()
    result = []
    for j in range(top_k):
        p_scalar = float(prob_list[j])
        i_scalar = int(idx_list[j])
        name = label_for_index(i_scalar) or f"Breed {i_scalar}"
        result.append({"name": name, "percentage": round(100 * p_scalar, 1)})
    return result


def pil_to_base64_data_url(pil_image: Image.Image, format: str = "JPEG") -> str:
    buf = io.BytesIO()
    pil_image.save(buf, format=format)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{b64}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        if not file or not file.filename:
            return jsonify({"error": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Allowed: images (jpg, png, webp, gif, bmp) or PDF."}), 400

        try:
            file_bytes = file.read()
        except Exception:
            return jsonify({"error": "Could not read file"}), 400

        if not file_bytes:
            return jsonify({"error": "File is empty"}), 400

        # Normalize to image (PDF first page or image)
        try:
            pil_image = normalize_upload_to_image(file_bytes, file.filename)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception:
            return jsonify({"error": "Invalid or unsupported file"}), 400

        gate = run_imagenet_gate(pil_image)

        if gate == "cat":
            return jsonify({
                "is_cat": True,
                "message": "No Cats Allowed!",
            })

        if gate == "other":
            image_data = pil_to_base64_data_url(pil_image)
            return jsonify({
                "is_dog": False,
                "message": "This doesn't look like a dog. Try uploading a photo of a dog for the best results.",
                "image": image_data,
            })

        # Dog: run breed model and sweater service
        breeds = run_breed_model(pil_image, top_k=3)
        from sweater_service import get_sweaters_for_breed
        top_breed_name = breeds[0]["name"] if breeds else "dog"
        sweaters = get_sweaters_for_breed(top_breed_name, limit=4)
        image_data = pil_to_base64_data_url(pil_image)

        return jsonify({
            "is_dog": True,
            "image": image_data,
            "breeds": breeds,
            "sweaters": sweaters,
        })
    except PermissionError as e:
        app.logger.exception("Predict failed: permission error")
        return jsonify({
            "error": "Could not save model files (permission denied). Run the app from a folder where it can create a .cache directory."
        }), 500
    except OSError as e:
        app.logger.exception("Predict failed: OS error")
        msg = str(e).strip() or "A system error occurred."
        return jsonify({"error": f"File or network error: {msg}"}), 500
    except RuntimeError as e:
        app.logger.exception("Predict failed: runtime error")
        err = str(e).strip()
        if "out of memory" in err.lower() or "cuda" in err.lower():
            return jsonify({"error": "Not enough memory to run the model. Try closing other apps or using a smaller image."}), 500
        return jsonify({"error": f"Model error: {err}"}), 500
    except Exception as e:
        app.logger.exception("Predict failed")
        err = str(e).strip()
        return jsonify({"error": err or "Something went wrong. Please try again."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
