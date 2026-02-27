import pdfplumber
import os

pdf_path = r"d:\SHLT\cqgs\cqbylw\企业全要素生产率（TFP）相关指标.pdf"
output_path = r"d:\SHLT\cqgs\cqbylw\code\tfp_indicators_summary.md"

try:
    print(f"Extracting text from {pdf_path}...")
    with pdfplumber.open(pdf_path) as pdf:
        text_content = ""
        for page in pdf.pages:
            text_content += page.extract_text() + "\n"
            
    # Simple keyword extraction (simulated logic as we can't do complex NLP here)
    # Ideally, we would parse tables if present
    
    print("Summarizing content...")
    summary = "# 企业全要素生产率 (TFP) 相关指标梳理\n\n"
    summary += "## 1. 原文内容提取\n\n"
    summary += text_content
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)
        
    print(f"Summary saved to {output_path}")

except Exception as e:
    print(f"Error processing PDF: {e}")
    # Fallback: Create a placeholder if PDF reading fails (due to library missing)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# PDF 读取失败\n请手动检查 PDF 内容。")
