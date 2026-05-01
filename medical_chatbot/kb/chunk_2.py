# chunk_2_3.py
# Split long docs into smaller pieces. 
"""
Why? Bcz retrieval works better on smaller focused passages than one giant file.
eg. one discharge instruction file may contain: wound care; bathing rules; medication schedule; warning signs; follow-up instructions
What we do?
- split by paragraph
- combine paragrahs into chunks up to a size limit
- preserve meaning as much as possible

Step 3 updates
1. add light text cleaning - clean_text()
2. fill chunk_index
3. fill char_count
4. handle very large single paragraphs a bit better
5. format the code a little more clearly
"""

from app.kb_types_2 import MedicalDoc, MedicalChunk

def clean_text(text:str) -> str: # normalize messy line endings
    text = text.replace("\r\n", "\n")
    text = text.strip()
    return text

def split_into_paragraphs(text: str) ->list[str]: 
    return [p.strip() for p in text.split("\n\n") if p.strip()] #"\n\n" - new para; if p.strip() ensure empty strings not included
        # first split each paragraph; then strip for each paragraph

def split_large_paragraph(paragraph: str, max_chars: int) -> list[str] : # Avoid one giant paragrah could become one oversized chunk.
    if len(paragraph) <= max_chars: return [paragraph]
    pieces = []
    start = 0
    while start < len(paragraph):
        end = start + max_chars
        pieces.append(paragraph[start:end].strip())
        start= end
    return [p for p in pieces if p]

def chunk_doc(doc: MedicalDoc, # the parameter doc is expected to be an instance of MedicalDocument class
              max_chars: int=600) -> list[MedicalChunk]:
        # eg. Car=type; my_car = actual object
    cleaned_text = clean_text(doc.text)
    paragraphs = split_into_paragraphs(cleaned_text)

    expanded_paragraphs = []
    for paragraph in paragraphs: 
        expanded_paragraphs.extend(split_large_paragraph(paragraph, max_chars=max_chars))

    chunks: list[MedicalChunk] = []
    current_text=""
    chunk_index = 0

    for paragraph in expanded_paragraphs:
        if current_text and len(current_text) + len(paragraph) +2 > max_chars: # if I add this next para, will the cur chunk become too big?
            chunk_text = current_text.strip()
            chunks.append(MedicalChunk(
                chunk_id=f"{doc.doc_id}:chunk_{chunk_index}",
                doc_id=doc.doc_id,
                title=doc.title,
                source_type=doc.source_type,
                topic=doc.topic, 
                risk_level=doc.risk_level,
                text=chunk_text,
                chunk_index=chunk_index,
                char_count=len(chunk_text)
            ))
            chunk_index += 1
            current_text = paragraph
        else: current_text += ("\n\n" if current_text else "") + paragraph # Add this para to the cur chunk

    if current_text.strip(): #After the loop is finished, if there is still text left, save it as the last chunk.
        chunk_text = current_text.strip()
        chunks.append(
            MedicalChunk(
                chunk_id=f"{doc.doc_id}:chunk_{chunk_index}",
                doc_id=doc.doc_id,
                title=doc.title,
                source_type=doc.source_type,
                topic=doc.topic,
                risk_level=doc.risk_level,
                text=chunk_text,
                chunk_index=chunk_index,
                char_count=len(chunk_text)
            )
        )
    return chunks







