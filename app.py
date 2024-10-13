from openai import OpenAI
import json
import os
from typing import List, Dict
from docx import Document

# Inisialisasi klien OpenAI
client = OpenAI(api_key="OPEN API KEY DISINI")

def load_document(file_path: str) -> str:
    """Memuat dokumen dari file."""
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.docx':
        try:
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"Error membaca file .docx: {e}")
            return ""
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Jika UTF-8 gagal, coba dengan encoding lain
            try:
                with open(file_path, 'r', encoding='iso-8859-1') as file:
                    return file.read()
            except Exception as e:
                print(f"Error membaca file: {e}")
                return ""

def generate_questions(document: str, num_questions: int = 5) -> List[str]:
    """Menghasilkan pertanyaan berdasarkan dokumen menggunakan OpenAI."""
    prompt = f"""Berdasarkan dokumen berikut, buatlah {num_questions} pertanyaan yang mendetail dan beragam. 
    Pertanyaan-pertanyaan ini harus mencerminkan analisis mendalam tentang isi dokumen:

    {document}

    Buat pertanyaan-pertanyaan yang beragam dan mendalam."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Anda adalah asisten AI yang ahli dalam membuat pertanyaan analitis berdasarkan teks."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Mengakses konten respons
        content = response.choices[0].message.content
        
        if content is None:
            print("Peringatan: Respons dari API kosong. Menggunakan pertanyaan default.")
            return [f"Pertanyaan default {i+1}" for i in range(num_questions)]
        
        # Memisahkan pertanyaan-pertanyaan
        questions = content.strip().split('\n')
        questions = [q.strip() for q in questions if q.strip()]
        
        # Jika tidak ada pertanyaan yang dihasilkan, gunakan pertanyaan default
        if not questions:
            print("Peringatan: Tidak ada pertanyaan yang dihasilkan. Menggunakan pertanyaan default.")
            return [f"Pertanyaan default {i+1}" for i in range(num_questions)]
        
        return questions[:num_questions]  # Memastikan jumlah pertanyaan sesuai yang diminta

    except Exception as e:
        print(f"Error saat menghasilkan pertanyaan: {e}")
        return [f"Pertanyaan default {i+1}" for i in range(num_questions)]

def get_user_answer(question: str) -> str:
    """Mendapatkan jawaban dari pengguna."""
    return input(f"Q: {question}\nA: ")

def export_to_jsonl(qa_pairs: List[Dict], filename: str):
    """Mengekspor pertanyaan dan jawaban ke format JSONL."""
    with open(filename, 'w', encoding='utf-8') as f:
        for pair in qa_pairs:
            json.dump(pair, f, ensure_ascii=False)
            f.write('\n')

def export_to_openai_format(qa_pairs: List[Dict], filename: str):
    """Mengekspor ke format dataset OpenAI."""
    data = [{"messages": [{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": pair["question"]},
                          {"role": "assistant", "content": pair["answer"]}]}
            for pair in qa_pairs]
    
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')

def export_to_gemini_format(qa_pairs: List[Dict], filename: str):
    """Mengekspor ke format dataset Gemini."""
    data = [{"input": pair["question"], "output": pair["answer"]} for pair in qa_pairs]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    try:
        document_path = input("Masukkan path dokumen sumber: ")
        document = load_document(document_path)
        
        if not document:
            print("Tidak dapat membaca dokumen. Program dihentikan.")
            return
        
        num_questions = int(input("Berapa banyak pertanyaan yang ingin Anda hasilkan? "))
        questions = generate_questions(document, num_questions)
        
        qa_pairs = []
        for question in questions:
            answer = get_user_answer(question)
            qa_pairs.append({"question": question, "answer": answer})
        
        # Ekspor hasil
        export_to_jsonl(qa_pairs, "qa_dataset.jsonl")
        export_to_openai_format(qa_pairs, "qa_dataset_openai.jsonl")
        export_to_gemini_format(qa_pairs, "qa_dataset_gemini.json")
        
        print("Sesi tanya jawab selesai. Data telah diekspor ke file JSONL dan JSON.")
    
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        print("Program dihentikan.")

if __name__ == "__main__":
    main()
