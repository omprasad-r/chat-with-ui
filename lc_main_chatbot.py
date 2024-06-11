#from st_pages import Page, add_page_title, show_pages
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
import streamlit as st
from streamlit_chat import message
import streamlit.config
import codecs
import docx2txt
from PyPDF2 import PdfReader
#import pdfplumber
from io import StringIO
from lc_utils import *
from lc_vector_search import *
import os

st.set_page_config(layout="wide")

# show_pages(
#     [
#         #Page("example_app/streamlit_app.py", "Home", "🏠"),
#         # Can use :<icon-name>: or the actual icon
#         #Page("example_app/example_one.py", "Example One", ":books:"),
#         # The pages appear in the order you pass them
#         #Page("example_app/example_four.py", "Example Four", "📖"),
#         #Page("example_app/example_two.py", "Example Two", "✏️"),
#         # Will use the default icon and name based on the filename if you don't
#         # pass them
#         Page("lc_main_chatbot.py"),
#         Page("test_page.py")
#         #Page("example_app/example_five.py", "Example Five", "🧰"),
#     ]
# )

# add_page_title()  # Optional method to add title and icon to current page

st.subheader("Advantage Experience Virtual Assist")

##Custom Styles
custom_styles = """
                <style>
                    div.stAlert{
                        display:none;
                    }
                    div#media-outer-container{
                        display:flex;
                        flex-wrap:wrap;
                        padding:0 5%;
                    }
                    div#media-outer-container .media-container{
                        width:100%;
                        flex:45%;
                        padding:2.5%;
                        margin:2.5%;
                        height:460px;
                        border:1px solid #ccc;
                    }
                    div#media-outer-container .media-container .image-caption{
                        text-align:center;
                    }
                    div#media-outer-container .media-container .image-container{
                        text-align:center;
                        height:90%;
                    }
                    div#media-outer-container .media-container .image-container img{
                        max-width:100%;
                        vertical-align:middle;
                        position:relative;
                        top:50%;
                        transform: translateY(-50%);
                    }
                    div#reflinks-container{
                        padding:7%;
                    }
                </style>
                """
st.markdown(custom_styles, unsafe_allow_html= True)

def refresh_ui():
    st.session_state['data_source'] = "--select--"
    init_pinecone(st.session_state['vector_index'])

show_sidebar = False;
show_sidebar_list = st.experimental_get_query_params()

if(show_sidebar_list != {}):
    show_sidebar = show_sidebar_list['admin']

    if(show_sidebar[0] == "True" or show_sidebar[0] == "true" ):
        st.sidebar.header("Index enterprise data from URLs, Sitemap or Documents.")
        
        vector_databases = st.secrets["vector-databases"]
        selected_index = st.sidebar.selectbox(
            "Please select the DataSource for data indexing.",
            vector_databases, key = "vector_index", 
                on_change = refresh_ui
        )
        print("sttt ",st.session_state.vector_index)
        # if(selected_index != ""):
        #     st.session_state.data_source = ""
        # building upload function
        if selected_index != "--select index--":
            add_selectbox = st.sidebar.selectbox(
                "Please select the DataSource for data indexing.",
                ("--select--","URL input", "Website Sitemap", "Document Upload", "AEM Repo"), key="data_source"
            )
            print(add_selectbox)
            ##------ Enter URL to scraps --------###
            if (add_selectbox == "URL input"):            
                urls_text = st.sidebar.text_input('Enter comma separated URLs to index. (e.g. https://www.example1.com, https://www.example2.com)','')
                
                if(st.sidebar.button("Submit")):
                    if( urls_text != ""):
                        urls = urls_text.split(",")
                        print(urls)
                        i = 1;
                        for url in urls:
                            print("content for URL "+url)
                            #st.sidebar.progress(i)
                            i = i + 1
                            status = add_chunks_to_index(url)
                            if (status == 'success'):
                                st.sidebar.success('Success indexing URL: '+url, icon="✅")
                            else:
                                st.sidebar.error('Error indexing URL: '+url, icon="🚨")
                            print("content printed")
                    else:
                        st.sidebar.write('Please enter URLs to index.')
            
            ##------ Enter Sitemap to scraps --------###
            if (add_selectbox == "Website Sitemap"):            
                st.sidebar.write('This function is yet to be enabled.')
            ##------ Enter AEM repo details to index --------###
            if (add_selectbox == "AEM Repo"):            
                st.sidebar.write('This function is yet to be enabled.')
            ##------ Upload documents (txt,doc,PDF) to index --------###
            if (add_selectbox == "Document Upload"):
                uploaded_files = st.sidebar.file_uploader("Choose files to upload...!!!",type=['txt','pdf','doc','docx','csv'], accept_multiple_files=True)
                for file in uploaded_files:
                        file_upload_status = "success"
                        if file is not None:
                            try:
                                print(file)
                                file_type = file.type
                                raw_text = ""
                                print("File uploaded:", file.name)
                                print("File type : ", file_type)
                                if(file_type == "text/plain"):
                            # # To convert to a string based IO:
                                # stringio = StringIO(bytes_data.decode("utf-8"))
                                    print("text data")
                                    # print(file.read())
                            # # To read file as string:
                                # string_data = stringio.read()
                                # string_data = bytes_data.decode("utf-8")
                                #string_data = codecs.decode(bytes_data, 'UTF-8')  
                                    raw_text = str(file.read(),"utf-8")
                                # print("string data")
                                # print(string_data)
                                elif(file_type == "application/pdf"):
                                    pdfreader = PdfReader(file)
                                    count = len(pdfreader.pages)
                                    raw_text = ""
                                    for i in range(count):
                                        page = pdfreader.pages[i]
                                        raw_text += page.extract_text()
                                else:
                                    raw_text = docx2txt.process(file)
                            except Exception as e:
                                # Handle the exception
                                print("An error occurred:", e)
                                file_upload_status="failure"
                            print("printing raw text")
                            print(raw_text)
                            status = "indexing_failed"
                            if (file_upload_status == 'success'):
                                status = index_file_content(raw_text,file.name)
                            if (status == 'success'):
                                st.sidebar.success('Success indexing file: '+file.name, icon="✅")
                            else:
                                st.sidebar.error('Error indexing file: '+file.name, icon="🚨")
                # ##-------- table to store URLs --------##
                    # if "data" not in st.session_state:
                    #     st.session_state.data = pd.DataFrame(
                    #         {"URL": []}
                    #     )


                    # def callback():
                    #     edited_rows = st.session_state["data_editor"]["edited_rows"]
                    #     rows_to_delete = []

                    #     for idx, value in edited_rows.items():
                    #         if value["x"] is True:
                    #             rows_to_delete.append(idx)

                    #     st.session_state["data"] = (
                    #         st.session_state["data"].drop(rows_to_delete, axis=0).reset_index(drop=True)
                    #     )

                    # columns = st.session_state["data"].columns
                    # column_config = {column: st.column_config.Column(disabled=True) for column in columns}

                    # modified_df = st.session_state["data"].copy()
                    # modified_df["x"] = False
                    # # Make Delete be the first column
                    # modified_df = modified_df[["x"] + modified_df.columns[:-1].tolist()]

                    # st.sidebar.data_editor(
                    #     modified_df,
                    #     key="data_editor",
                    #     on_change=callback,
                    #     hide_index=True,
                    #     column_config=column_config,
                    # )
                    # if title:
                    #     st.write("There is some value. Processing...")
                    #     print(len(modified_df))
                    #     modified_df.loc[len(modified_df)] = [1,2]

if 'responses' not in st.session_state:
    st.session_state['responses'] = ["How can I assist you?"]

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

if 'images_imageURI_response' not in st.session_state:
    st.session_state['images_imageURI_response'] = []

if 'images_imageTarget_response' not in st.session_state:
    st.session_state['images_imageTarget_response'] = []

if 'images_caption_response' not in st.session_state:
    st.session_state['images_caption_response'] = []

if 'ref_links_response' not in st.session_state:
    st.session_state['ref_links_response'] = []

openai.api_key = os.getenv('OPENAI_API_KEY')
if 'None' == os.getenv('OPENAI_API_KEY'):
    try:
        openai.api_key = st.secrets['OPENAI_API_KEY']
    except:
        print("error reading secrets")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai.api_key)

if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)


system_msg_template = SystemMessagePromptTemplate.from_template(template="""Answer the question as truthfully as possible using the provided context, 
and if the answer is not contained within the text below, say 'I don't know'""")
human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")
prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)

col1, col2 = st.columns(2)

with col1:
    # container for chat history
    response_container = st.container()
    # container for text box
    textcontainer = st.container()

    with textcontainer:

        if 'something' not in st.session_state:
            st.session_state.something = ''

        def submit():
            st.session_state.something = st.session_state.input
            st.session_state.input = ''

        st.text_input("Query: ", key="input", on_change=submit)
        query = st.session_state.something
        if query:
            st.session_state.something = ''
            with st.spinner("processing..."):
                #conversation_string = get_conversation_string()
                # st.code(conversation_string)
                refined_query = query#query_refiner(conversation_string, query)
                #st.subheader("Refined Query:")
                #st.write(refined_query)
                context = find_match(refined_query)
                response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{query}")
                if "I don't know" in response:
                    images_imageURI_response = ''
                    images_imageTarget_response = ''
                    images_caption_response = ''
                    ref_links_response = ''
                else:
                    image_details = find_match_imageuri(refined_query)
                    images_imageURI_response = image_details[0]
                    images_imageTarget_response = image_details[1]
                    images_caption_response = image_details[2]
                    ref_links_response = image_details[3]
            st.session_state.requests.append(query)
            st.session_state.responses.append(response)
            st.session_state.images_imageURI_response.append(images_imageURI_response)
            st.session_state.images_imageTarget_response.append(images_imageTarget_response)
            st.session_state.images_caption_response.append(images_caption_response)
            st.session_state.ref_links_response.append(ref_links_response)
    with response_container:
        if st.session_state['responses']:

            for i in range(len(st.session_state['responses'])):
                message(st.session_state['responses'][i],key=str(i), avatar_style="identicon",seed="Aneka")
                if i < len(st.session_state['requests']):
                    message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')

with col2:
    image_response_container = st.container()
    links_response_container = st.container()
    with image_response_container:
        if st.session_state['images_imageURI_response']:
            image_response_length = len(st.session_state['images_imageURI_response']) - 1
            image_url = st.session_state['images_imageURI_response'][image_response_length]
            image_target = st.session_state['images_imageTarget_response'][image_response_length]
            image_caption = st.session_state['images_caption_response'][image_response_length]

            if image_url:
                image_markup = """
                    <div class='media-container'> 
                        <div class='image-container'> 
                            <a href='""" + image_target + """' target='_blank'><img src='""" + image_url + """' /></a> 
                        </div> 
                        <div class='image-caption'> 
                            <span>""" + image_caption + """</span> 
                        </div> 
                    </div> 
                    """
                image_markup_container = """<div id='media-outer-container'>""" + image_markup + """</div>"""
                st.markdown(image_markup_container,unsafe_allow_html= True)
    with links_response_container:
        if st.session_state['ref_links_response']:
            reflinks_response_length = len(st.session_state['ref_links_response']) - 1
            reference_link = st.session_state['ref_links_response'][reflinks_response_length]
            if reference_link:
                reflinks_markup = """
                    <div class='ref-link-container'> 
                        <div class='reflink'> 
                            <b>Reference Links:</b> 
                            <ul> 
                                <li><a target=_blank' href='""" + reference_link + """'>""" + reference_link + """</a></li> 
                            </ul> 
                        </div> 
                    </div> 
                    """
                reflink_markup_container = """<div id='reflinks-container'>""" + reflinks_markup + """</div>"""
                st.markdown(reflink_markup_container,unsafe_allow_html= True)