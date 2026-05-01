# load_docs_2_3.py

from pathlib import Path
from app.kb_types_2 import MedicalDoc

SOURCE_TYPE_MAP = { # translate folder names into the offical source labels used by your schema
    "patient_education": "patient_education",
    "discharge_instructions": "discharge_instruction",
    "medication_guides": "medication_guide",
    "clinic_policies": "clinic_policy",
}

def infer_topic_from_filename(filename: str) -> str:
    # Convert file name into a readable topic
    return filename.replace(".txt", "").replace("_", " ").strip()


def infer_risk_level(source_type: str) -> str:
    # Medication and discharge instructions are usually more sensitive
    if source_type in {"medication_guide", "discharge_instruction"}: return "high"
    if source_type == "patient_education": return "medium"
    return "low"

def load_txt_doc(file_path: Path, source_type: str) -> MedicalDoc:
    text = file_path.read_text(encoding="utf-8").strip()
    if not text: raise ValueError(f"Empty document: {file_path}")
    topic = infer_topic_from_filename(file_path.name)

    return MedicalDoc(
        doc_id=file_path.stem,
        title=file_path.stem.replace("_", " ").title(),
        source_type=source_type,
        topic=topic,
        risk_level=infer_risk_level(source_type),
        text=text,
    )

def load_documents(base_dir: str = "kb/raw_docs") -> list[MedicalDoc]:
    documents: list[MedicalDoc] = []
    root = Path(base_dir)
    for folder_name, source_type in SOURCE_TYPE_MAP.items():
        folder_path = root / folder_name
        if not folder_path.exists(): continue
        for file_path in sorted(folder_path.glob("*.txt")): #This searches inside that folder for any txt file
            try: documents.append(load_txt_doc(file_path, source_type))
            except ValueError as e: print(f"Skipping file: {e}")
    return documents

