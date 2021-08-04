import streamlit as st
import pandas as pd
import numpy as np
import json
import pickle
from PIL import Image
import streamlit.components.v1 as components
import xgboost
import shap
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os

#Setting the page configuration
square_icon = Image.open(os.path.abspath('skincare_square.jpeg'))
long_icon = Image.open("images/top_banner.png") #rivate-label-skincare
long_bw = Image.open("images/bw_long.jpeg")
square_logo = Image.open("images/teen_beauty.png")
logo = Image.open("images/logo_trans.png")
end_icon = Image.open("images/lower_banner.png")
st.set_page_config(
    page_title="Product and Ingredient Analysis",
    page_icon=square_logo,
    layout="centered",
    initial_sidebar_state="auto")

#loading necessary files
@st.cache
def fetch_data(path):
    df = pd.read_json(path)
    return df

prod_ingr_matrix1 = fetch_data('../data/processed_data/product_ingr_inventory.json')
dot_prod= fetch_data('../data/processed_data/common_ingr.json')
sim_df= fetch_data('../data/processed_data/cos_sim.json')
df_new = fetch_data('../data/processed_data/combined_data.json')
x_complete = fetch_data('../data/train_test/x_complete.json')
df1 = fetch_data('../data/processed_data/pre_modelling_data.json')

#st.write(df1.head())

#functions 
@st.cache
def similar_prod(item, n=10, all_types = True):
    '''
    return the n most similar products
    '''
    tp = sim_df[item].sort_values(axis=0, ascending=False)
    tp = pd.DataFrame(tp)[0:n+1]
    tp.rename(columns={item:'cos_score'}, inplace=True)
    tp['cos_score']= np.round(tp['cos_score']*100,2)
    for i in list(tp.index):
        tp.loc[i, 'jac_score'] = np.round(jaccard_binary(np.array(prod_ingr_matrix1.loc[item]), np.array(prod_ingr_matrix1.loc[i]))*100,2)
        tp.loc[i, 'num_ingr'] = str(dot_prod[item][i])+'/'+ str(dot_prod[item][item])
        tp.loc[i, 'pricepervol'] = np.round(df_new[df_new['product_name']==i]['pricepervol'].values[0],2)
        tp.loc[i, 'product_type'] = df_new[df_new['product_name']==i]['product_type'].values[0]
        
    if all_types==True:
        return tp 
    else:
        ptype = tp.loc[item, 'product_type']
        return tp.loc[tp['product_type']==ptype]

@st.cache
def compare_ingr(i, item):
    '''
    Returns similarity between two products
    '''
    print(f'Similarity of {i} to {item}')
    tp =pd.DataFrame()
    tp.loc[i, 'cos_score']= np.round(sim_df[item][i]*100,2)
    tp.loc[i, 'jac_score'] = np.round(jaccard_binary(np.array(prod_ingr_matrix1.loc[item]), np.array(prod_ingr_matrix1.loc[i]))*100,2)
    #tp.loc[i, 'num_ingr'] = str(dot_prod[item][i])+'/'+ str(dot_prod[item][item])
    #tp.loc[i, 'pricepervol'] = np.round(df_new[df_new['product_name']==i]['pricepervol'].values[0],2)
    #tp.loc[i, 'product_type'] = df_new[df_new['product_name']==i]['product_type'].values[0]
    return tp

@st.cache
def jaccard_binary(x,y):
    """A function for finding the similarity between two binary vectors"""
    intersection = np.logical_and(x, y)
    union = np.logical_or(x, y)
    similarity = intersection.sum() / float(union.sum())
    return similarity

# loading the trained model
pickle_in = open('../notebooks/xgb_final.pkl', 'rb') 
model = pickle.load(pickle_in)

def st_shap(plot, height=None):
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    components.html(shap_html, height=height)

def explain_instance(prod, model, test_set):
    '''
    df1 - getting index 
    '''
    idx= df1.loc[df1.product_name==prod].index[0]
    X = test_set.loc[[idx]]
    rand_pred = model.predict(X)
    rand_proba = list(model.predict_proba(X))
    st.markdown('***Model\'s prediction***')
    st.write(f'{rand_pred[0]} ({np.round(max(rand_proba[0])*100,2)}% probability)')
    st.markdown('***Actual:***')
    st.write(f'{df1.price_category.loc[idx]} (${np.round(df1.pricepervol.loc[idx],2)} per oz)')


def show_shap(prod, model, test_set):
    '''
    
    '''
    idx= df1.loc[df1.product_name==prod].index[0]
    X = test_set.loc[[idx]]
    rand_pred = model.predict(X)
    rand_proba = list(model.predict_proba(X))

    #shap.initjs()
    explainer2 = shap.TreeExplainer(model)
    shap_values2 = explainer2.shap_values(test_set.loc[[idx]])
    shap_values = explainer2(X)
    class_names= ['average', 'cheap', 'expensive']
    for which_class in (1,0,2):
        st.write(f'{np.round(rand_proba[0][which_class]*100,2)}% likelihood of being {class_names[which_class]}')
        p= shap.force_plot(explainer2.expected_value[which_class], shap_values2[which_class], test_set.loc[[idx]])
        st_shap(p)


products_list = list(set((prod_ingr_matrix1.index)))

#Sidebar
st.sidebar.image(logo, width= 325)
st.sidebar.markdown('''
## About
*A simple user interface to allow you to explore the results of my machine learning model more easily*
''')
st.sidebar.markdown('This is still a work in progress but if you have any suggestions or comments, feel free to connect with me on <a href="https://www.linkedin.com/in/nikki-amurao/">LinkedIn</a>  or drop me an <a href="mailto:amurao.frances@gmail.com">email</a>. <p> </p><p> Enjoy exploring the model! </p>', unsafe_allow_html=True)

st.image(long_icon)
st.markdown('''
## Skincare Product Analysis
### **What would you like to do?**
''')
action= st.radio('',['Analyse pricing','Find similar products', 'Compare to another product'])
product = st.selectbox("Choose your product", sorted(products_list), key='main')

#must add explanations for each column

if action=='Find similar products':
    num = st.slider(label='Number of products to return', min_value=3, max_value=25, value=10)
    restriction = st.checkbox(label='Show all product types', value=True)
    st.header('Similar products')
    st.table(similar_prod(product, num, restriction))

if action=='Compare to another product':
    prod2 = st.selectbox("Compare to", sorted(products_list), key='secondary')
    st.header('Comparison')
    st.table(compare_ingr(prod2, product))

if action=='Analyse pricing':
    explain_instance(product, model, x_complete)
    my_expander = st.beta_expander(label='How did the model make this prediction?', expanded =True)
    with my_expander:
        '''**SHAP VALUES**'''
        show_shap(product, model, x_complete)

    
    expander = st.beta_expander(label='About the classification')
    with expander: 
        '''**Classification criteria**'''
        expander.markdown('''
        - *cheap*: under $15 per oz 
        - *average*: $15 - $56 per oz 
        - *expensive*: over $56 per oz 
        ''')
#df1.product_name==prod

st.image(end_icon)
