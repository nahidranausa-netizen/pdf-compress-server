import os
import subprocess
import fitz  # PyMuPDF
import random
import string
from flask import Flask, request, send_file

app = Flask(__name__)

# Random character generate korar function
def generate_random_text(size_in_bytes):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size_in_bytes))

@app.route('/compress', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400
    
    file = request.files['file']
    input_path = "/tmp/input.pdf"
    gs_output_path = "/tmp/gs_output.pdf"
    final_output_path = "/tmp/final_output.pdf"
    
    file.save(input_path)
    
    try:
        # Ghostscript diye prothome size komano
        gs_cmd = [
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/screen", "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={gs_output_path}", input_path
        ]
        subprocess.run(gs_cmd, check=True)
        
        actual_size = os.path.getsize(gs_output_path)
        
        # 🔥 MAGIC LOGIC: 71 KB theke 79 KB er moddhe random target size generate korbe
        target_size = random.randint(71, 79) * 1024  
        
        if actual_size < target_size:
            doc = fitz.open(gs_output_path)
            padding_needed = target_size - actual_size
            
            # Random size onujayi dummy text add kora
            dummy_text = generate_random_text(padding_needed)
            metadata = doc.metadata
            metadata['keywords'] = dummy_text
            doc.set_metadata(metadata)
            
            doc.save(final_output_path, garbage=3, deflate=True)
            doc.close()
        else:
            os.rename(gs_output_path, final_output_path)

        return send_file(final_output_path, as_attachment=True, download_name="compressed.pdf", mimetype='application/pdf')
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # Server clean rakha
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(gs_output_path): os.remove(gs_output_path)
        if os.path.exists(final_output_path): os.remove(final_output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
