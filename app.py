import os
import fitz  # PyMuPDF
import random
import string
from flask import Flask, request, send_file

app = Flask(__name__)

# র‍্যান্ডম ক্যারেক্টার জেনারেট করার ফাংশন (যাতে কমপ্রেসন অ্যালগরিদম একে ছোট করতে না পারে)
def generate_random_text(size_in_bytes):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size_in_bytes))

@app.route('/compress', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400
    
    file = request.files['file']
    input_path = "/tmp/input.pdf"
    output_path = "/tmp/output.pdf"
    
    file.save(input_path)
    
    try:
        doc = fitz.open(input_path)
        
        # ধাপ ১: স্ট্যান্ডার্ড অপ্টিমাইজেশন (টেক্সট কোয়ালিটি ১০০% ঠিক থাকবে)
        doc.save(output_path, garbage=3, deflate=True)
        
        # ধাপ ২: স্মার্ট মেটাডেটা প্যাডিং (যদি সাইজ ৭৫ কেবির কম হয়)
        actual_size = os.path.getsize(output_path)
        target_size = 75 * 1024  # টার্গেট সাইজ ৭৫ কেবি
        
        if actual_size < target_size:
            padding_needed = target_size - actual_size
            
            # মেটাডেটার ভেতরে র‍্যান্ডম ভ্যালু অ্যাড করে সাইজ বাড়ানো
            dummy_text = generate_random_text(padding_needed)
            metadata = doc.metadata
            metadata['keywords'] = dummy_text  # এটি পিডিএফের স্ট্যান্ডার্ড মেটাডেটা ফিল্ড
            doc.set_metadata(metadata)
            
            # নতুন সাইজ অনুযায়ী ফাইলটি পুনরায় সেভ করা
            doc.save(output_path, garbage=3, deflate=True)
            
        doc.close()

        return send_file(output_path, as_attachment=True, download_name="compressed.pdf", mimetype='application/pdf')
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # টেম্পোরারি ফাইল ক্লিনআপ
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
