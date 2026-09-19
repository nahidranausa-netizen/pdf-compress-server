import subprocess
from flask import Flask, request, send_file
import os

app = Flask(__name__)

@app.route('/compress', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400
    
    file = request.files['file']
    input_path = "/tmp/input.pdf"
    output_path = "/tmp/output.pdf"
    
    # ফাইল সেভ করা
    file.save(input_path)

    # Ghostscript কমান্ড (কোয়ালিটি ভালো রাখার জন্য /printer ব্যবহার করা হলো)
    gs_cmd = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/printer", "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", input_path
    ]
    
    try:
        subprocess.run(gs_cmd, check=True)
        
        # 🚀 MAGIC LOGIC: SMART PADDING
        min_size_bytes = 76 * 1024  # টার্গেট সাইজ ৭৬ কেবি
        actual_size = os.path.getsize(output_path)
        
        # যদি সাইজ ৭৬ কেবির কম হয়, তবে বাকি সাইজটুকু ফাঁকা ডেটা (Null Bytes) দিয়ে পূরণ করবে
        if actual_size < min_size_bytes:
            padding_size = min_size_bytes - actual_size
            with open(output_path, "ab") as f:
                f.write(b'\0' * padding_size)
        # -------------------------------------------------------------
        
        return send_file(output_path, as_attachment=True, download_name="compressed.pdf", mimetype='application/pdf')
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # প্রসেস শেষে টেম্পোরারি ফাইলগুলো ক্লিন করা
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
