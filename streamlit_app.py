import os
import requests
import streamlit as st
from claims.core import DATA, mode

st.set_page_config(page_title='Smart Claims Desk',page_icon='📦')
st.title('Smart Claims Desk')
st.caption(f'Fictional workshop • {mode()} mode • Draft decisions only')
base=st.sidebar.text_input('API URL','http://127.0.0.1:8000')
token=st.sidebar.text_input('API token',os.getenv('APP_API_TOKEN','local-workshop-token'),type='password')
headers={'X-API-Key':token}
with st.form('claim'):
    sample=st.checkbox('Use bundled router photo + invoice + English voice note',True)
    uploads=st.file_uploader('Evidence',type=['png','jpg','jpeg','pdf','wav','mp3','m4a','mp4'],accept_multiple_files=True)
    product=st.selectbox('Product',['router','phone','monitor'])
    amount=st.number_input('Invoice total (INR)',min_value=1.0,value=2360.0)
    days=st.number_input('Days since delivery',min_value=0,value=2)
    submitted=st.form_submit_button('Analyze claim')
if submitted:
    try:
        if sample:
            names=['claim_photos/claim_01.png','invoices/invoice_01.pdf','voice_notes/voice_01.wav']
            parts=[('files',(p.name,p.read_bytes())) for n in names for p in [DATA/n]]
        else: parts=[('files',(f.name,f.getvalue())) for f in uploads]
        if not parts: st.warning('Add evidence first.')
        else:
            with st.spinner('Reading evidence and checking policy...'):
                r=requests.post(base+'/claims',headers=headers,files=parts,data={'product':product,'amount':amount,'delivery_days':days},timeout=300)
                r.raise_for_status(); st.session_state['result']=r.json()
    except Exception as e: st.error(str(e))
if result:=st.session_state.get('result'):
    st.json(result)
    st.download_button('Download result JSON',__import__('json').dumps(result,indent=2),'claim.json')
    if result['pending_review']:
        st.warning('Awaiting an authorized reviewer. No final approval yet.')
        reviewer=st.text_input('Reviewer name')
        secret=st.text_input('Reviewer token',type='password')
        decision=st.selectbox('Reviewer decision',['approve','reject'])
        if st.button('Submit review'):
            try:
                r=requests.post(base+f"/claims/{result['thread_id']}/review",headers={**headers,'X-Reviewer-Token':secret},json={'decision':decision,'reviewer':reviewer},timeout=60)
                r.raise_for_status(); st.session_state['result']=r.json(); st.rerun()
            except Exception as e: st.error(str(e))
