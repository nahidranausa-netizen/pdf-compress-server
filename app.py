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
    
    file.save(input_path)

    gs_cmd = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/screen", "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", input_path
    ]
    
    try:
        subprocess.run(gs_cmd, check=True)
        return send_file(output_path, as_attachment=True, download_name="compressed.pdf", mimetype='application/pdf')
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
