from pydantic import BaseModel
from .core import DATA, Damage, extract, mode

def prompts():
    if mode()=='demo': return {'note':'No inference in demo. Run live to compare free-form vs structured prompts.',
        'vague':'What is in this image?', 'structured':'Extract product, damage type, severity and visible serial; use null for unreadable fields.'}
    from .core import client, image_url
    p=DATA/'claim_photos/claim_01.png'
    vague=client().responses.create(model=__import__('os').getenv('VISION_MODEL','gpt-4.1-mini'),input=[{'role':'user','content':[
        {'type':'input_text','text':'What is in this image?'},{'type':'input_image','image_url':image_url(p)}]}])
    structured=extract(Damage,'Extract visible damage and product fields; use null when unreadable.',[p])
    return {'vague':vague.output_text,'structured':structured.model_dump(),'vague_usage':vague.usage.model_dump()}

def table_qa():
    class TableAnswer(BaseModel):
        days:int
        evidence_required:str
    if mode()=='demo': result={'days':7,'evidence_required':'photo and invoice'}
    else: result=extract(TableAnswer,'How many days after delivery is cracked-case coverage available, and what evidence is required?',
                            [DATA/'charts/warranty_table.png']).model_dump()
    return {'prediction':result,'expected':{'days':7,'evidence_required':'photo and invoice'},'days_correct':result['days']==7}
