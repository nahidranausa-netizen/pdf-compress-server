import os
import subprocess
import fitz  # PyMuPDF
import random
import string
from flask import Flask, request, send_file

app = Flask(__name__)

# র‍্যান্ডম ক্যারেক্টার জেনারেট করার ফাংশন
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
        # ধাপ ১: Ghostscript দিয়ে ইমেজ/পিডিএফ কমপ্রেস করা (এটি সাইজ নিশ্চিতভাবে কমাবে)
        gs_cmd = [
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/screen", "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={gs_output_path}", input_path
        ]
        subprocess.run(gs_cmd, check=True)
        
        # ধাপ ২: PyMuPDF দিয়ে সাইজ চেক করা এবং প্যাডিং করা
        actual_size = os.path.getsize(gs_output_path)
        target_size = 76 * 1024  # টার্গেট সাইজ ৭৬ কেবি
        
        if actual_size < target_size:
            doc = fitz.open(gs_output_path)
            padding_needed = target_size - actual_size
            
            # সেফ মেটাডেটার ভেতরে র‍্যান্ডম ভ্যালু অ্যাড করে সাইজ ৭৫-৮০ কেবি করা
            dummy_text = generate_random_text(padding_needed)
            metadata = doc.metadata
            metadata['keywords'] = dummy_text
            doc.set_metadata(metadata)
            
            doc.save(final_output_path, garbage=3, deflate=True)
            doc.close()
        else:
            # যদি সাইজ আগে থেকেই বড় থাকে, তবে সেটাই ফাইনাল আউটপুট হিসেবে সেভ হবে
            os.rename(gs_output_path, final_output_path)

        return send_file(final_output_path, as_attachment=True, download_name="compressed.pdf", mimetype='application/pdf')
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # সার্ভার ক্লিন রাখা
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(gs_output_path): os.remove(gs_output_path)
        if os.path.exists(final_output_path): os.remove(final_output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
