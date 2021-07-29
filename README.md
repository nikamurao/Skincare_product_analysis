# Decoding the pricing of your skincare product

*(insert some background to the problem)*

<img src="https://user-images.githubusercontent.com/70846659/127411930-6e253e9d-8168-4fab-a4e3-881522caf583.png" data-canonical-src="https://gyazo.com/eb5c5741b6a9a16c692170a41a49c858.png" width="600" height="400" />

## Objectives
This project set out to do the following: 

**1) Gather insights on main price determinants for skincare**
- What makes one product more expensive than the other? Are products targeting specific skincare concerns priced more expensively than others? How about those catering to specific skin types? Is price affected by ratings, number of ratings or likes, or number of reviews? To what extent does branding influence the prices?
- Which products are under- or over-priced according to market patterns? 

**2) Analysing product ingredients**
- What are the most common ingredients used? Can we identify some 'base formula' ingredients used in skincare? 
- What ingredients tend to be associated with cheap vs. average vs. expensive products? 
- Can we find 'dupes'? Looking solely at ingredients, can we spot some potential alternatives to our favorite products? How similar is product A to product B?

## I. Data gathering
As the project requires extensive product coverage and detailed information at the product level, e-commerce websites are, by far, the richest data sources and remain unmatched by readily available datasets online. For this project, I have chosen to tap into one of the largest international beauty retailers, Sephora, as my main data source. Sephora sells thousands of products from brands originating from all around the world and across many product types. Its product pages also contain a variety of product information including but not limited to number of reviews, likes, ratings, ingredients list, active ingredients, awards received, suitable skin types, skin concerns addressed, and clinical results published. Being a key player in the beauty industry, it also covers majority of the most popular skincare products. 

Data was collected using web scraping with Python, Scrapy and Selenium (to deal with Javascript/dynamic pages and 'lazy load'), creating a product database for over 1,800 products across four main categories (cleansers, eye treatments, moisturizers, treatments). 

## II. Data cleaning pre-processing  

Data cleaning and preparation was an intensive and crucial step as a large proportion of information returned by web-scraping was unstructured text and not fully standardised. Generally, the main steps taken are the following: (more details available here)
1. addressing and imputing missing values
2. manually correcting some errors spotted 
3. inspecting for and treating outliers 
4. correcting data types and standardising format (i.e. converting 68k, 1000, $3 to a uniform format)
5. text pre-processing 

## III. Feature extraction and generation 
Majority of the product data was contained in the 'About the Product', 'Ingredients' and 'Highlights' section of the webpage and were retrieved as full text. In order to extract information from this and generate new features, regular expressions were extensively used to detect or list out information such as: 
- skin concerns addressed (i.e. dark circles, uneven skin tone, acne, aging, dullness, etc.)
- any excluded ingredients mentioned
- skin types the product is suitable for 
- clinical results published
- product formulation
- active or highlighted ingredients
- what it is good for (as noted by Sephora)
- any specific acids being used (i.e. AHA, BHA, glycolic, ascorbic)
- product size

In some cases, it was not a simple binary classification (i.e. whether clinical results were published) or a mutually-exclusive category such that we can proceed directly to one-hot encoding. Oftentimes, there could be numerous labels for a feature. For example, a product could be targeting more than one skin concern (i.e. acne and uneven skin tone) and could also be suitable for a few skin types (i.e. normal, dry and sensitive). In this case, the details for each feature were noted in a list for each product. Then, I analysed how many unique labels there were for that feature for the entire dataset (as this will indicate the number of additional features to generate). If there were too many categories, these were narrowed down to the few main ones by either combining various labels or by using 'Other' to represent the minority labels. Numerous features were generated with this approach. 

Some simplification of the ingredients was also required as there were numerous variations for the same ingredient (Aqua/Water/Eau, Aqua/Eau, Water/Eau, Aqua/Water, Water). Initially, there were c. 6,000 unique ingredients but this was reduced by half through FuzzyMatch similarity. 

An important consideration for the project was to use price per volume instead of price alone as we should expect price to vary directly with the amount of the product. Circling back to the original problem, the objective is to learn insights into what differentiates a premium from a cheap or an average product and vice versa so the approach taken was to treat this as a classification rather than a prediction problem. Predicting the exact price of the product is not as important as determining its market positioning. The target variable (price affordability - cheap, average, expensive) was derived by first dividing the dollar price by the size (used oz) and creating the cheap, average and expensive categories by partitioning the price per volume into terciles. 

## III. Exploratory data analysis (EDA)
Some initial EDA has revealed that certain features could be more predictive of price. As shown below, price tends to vary with the product category. Eye creams are typically expensive whilst toners and cleansers are consistently cheap. 
![image](![image](https://user-images.githubusercontent.com/70846659/127484783-33078b43-b4ec-410f-ac94-0d2277c11e56.png))

It was also found liquid and lotion formulas tend to be cheaper than serums and oils on average. 
Vegan products, contrary to my initial hypothesis, do not necessarily cost more than non-vegan products. In fact, the average price for products marked as vegan are slightly lower. 

![image](https://user-images.githubusercontent.com/70846659/127437291-9d7cd732-8440-450c-98df-f08485759a7a.png) ![image](https://user-images.githubusercontent.com/70846659/127437302-634b373d-f06f-48c2-a5ac-7a669f03f5f6.png)

(add insights from the ingredients file)
(More details on EDA findings here)

## IV. Data preparation for training 
As many models work with only numerical data, categorical features like brand, product type and skin concerns were one-hot encoded. Feature scaling was also performed for a few features (such as number of likes and number of reviews) to prevent distance-based ML techniques from becoming biased towards the large scale of the data.

A high-level summary of the feature set is presented below: 
![image](https://user-images.githubusercontent.com/70846659/127437029-7772584d-d829-4b0c-93b0-11310ddce07b.png)

The dataset was split 70/30 between training and test before modelling.

## V. Modelling
Various machine learning techniques were explored in the project, including logistic regression, support vector machines (SVM)After , decision tree classifier, Random Forest, XGBoost and Gradient Boosting.

For each of the techniques, the methodology was as follows: 
1) Trained the base model (using default parameters)
2) Tune the parameters to check for performance improvement (used nested cross-validation) 
3) Derive insights to understand how it is predicting affordability and what features are important 
- I have experimented using machine learning techniques (SVM, logistic regression, Random Forest, PCA) for feature selection. This proved effective as generally the model performance has either been maintained or improved while using a smaller dataset (i.e. 108/175 features using SVM for feature selection and 125/175 features using logistic regression). 

The initial project did not consider the ingredients as a feature for the model. However, upon some deliberation, I have decided to explore and extend the project to see if the use of certain ingredients could be more predictive of pricing or whether this will only introduce noise to the model. The model results for the main and extended project will be presented. 

**Model performance**

Cross validated performance, based on accuracy, precision, recall and f1 score, was compared across the models. Generally, the model accuracy has ranged between betewen 70-80%. 

![image](https://user-images.githubusercontent.com/70846659/127489134-48b72b3c-fb52-4b95-aa7f-31a341909eff.png)

The pre-selected models were then evaluated on the test set. The results are: 

*Without ingredients*: Support vector machine (SVM) using a linear kernel trained on 108 features only 
- Accuracy score on test: 74.1%
- Average ROC AUC score: 80.8% (cheap - 83.9%, expensive - 84.4%, average - 74.1%)
- F1 score: 0.74

*With ingredients*: XGBoost trained on the full feature set 
- Accuracy score on test: 76.1% 
- Average ROC AUC score: 82.3% (cheap - 86.1%, expensive - 85.0%, average - 75.7%)
- F1 score: 0.76
- 
*(Naive classifier / baseline model accuracy: 35%)*

The confusion matrix reveals that not surprisingly, the model has better predictive power for the cheap and expensive categories, compared to the average.  

## VI. Predictions of the model / Output
*What insights can we gain from the model?*

SHAP was used to illustrate how the final model (XGBoost) was making the predictions. Here are the SHAP values for the various features: 

![image](https://user-images.githubusercontent.com/70846659/127482841-c5508acb-efc7-4743-8293-345bd7a8aed4.png)

It can also be used to explain an individual observation. For example: 
![image](https://user-images.githubusercontent.com/70846659/127490050-cbe6a551-b8c6-43f0-9bdd-f73379c872d3.png)


## VII. Deployment
The model was retained on the entire dataset and is currently being deployed through Streamlit.

The link will be included soon but in the meantime, here is a preview of what you can do with the model:
1) Analyse how a product has been priced and the prediction of its category according to our model
2) Return the most similar products based on ingredients
3) Compare products based on ingredients 

## VII. Future Improvements 



___________________________________________________________

More details about the methodology can also be found here and here. 
Feel free to connect with me through LinkedIn [x] or through email [x]. 


![GitHub Logo]
(https://blogscdn.thehut.net/app/uploads/sites/1160/2018/01/080819-Feature-Prods.jpg)
(https://cdn.shopify.com/s/files/1/0648/1955/files/skin_care_bottles.jpg?v=1606930679)
(https://cdn.shopify.com/s/files/1/0071/6197/0758/files/shutterstock_1416346496_1024x1024.jpg?v=1594210464)
(https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRDOLEbDcJZmvZLbl7VZ0t_CNlCx-klvKd8VadIK_Zv4uEltSqdb2cI0N7yGb-iIIBOIUs&usqp=CAU)
(https://user-images.githubusercontent.com/70846659/127411930-6e253e9d-8168-4fab-a4e3-881522caf583.png)
