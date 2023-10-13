# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
# from sklearn.tree import DecisionTreeRegressor
# from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
# from sklearn.svm import SVR
# from sklearn.metrics import r2_score

# # Load and preprocess the dataset
# df = pd.read_csv("billboard.csv")
# df['Week'] = pd.to_datetime(df['Week'], format='%d-%m-%Y')
# df['Genres'] = df['Genre'].str.split(',')
# df = df.explode('Genre')

# # Flatten the list of genres
# genres_list = [genre for genres in df['Genres'] for genre in genres]

# # Calculate the frequency of each genre
# genre_counts = pd.Series(genres_list).value_counts()

# # Get the genre with the highest frequency
# top_genre = genre_counts.index[0]

# # Filter the dataset for the top genre
# top_genre_data = df[df['Genres'].apply(lambda x: top_genre in x)]

# # Group and aggregate data at the weekly level for the top genre
# grouped = top_genre_data.groupby('Week').size().reset_index(name='Count')

# # Convert dates to numerical representation
# ref_date = grouped['Week'].min()
# grouped['Week_Num'] = (grouped['Week'] - ref_date).dt.days

# # Split the data into training and test sets
# x_train, x_test, y_train, y_test = train_test_split(grouped['Week_Num'], grouped['Count'], test_size=0.2, random_state=0)

# # Reshape the training and test data
# x_train = x_train.values.reshape(-1, 1)
# x_test = x_test.values.reshape(-1, 1)
# y_train = y_train.values.reshape(-1, 1)
# y_test = y_test.values.reshape(-1, 1)

# # Linear Regression
# linear_reg = LinearRegression()
# linear_reg.fit(x_train, y_train)
# linear_pred = linear_reg.predict(x_test)
# linear_score = r2_score(y_test, linear_pred)

# # Decision Tree Regression
# dt_reg = DecisionTreeRegressor(random_state=0)
# dt_reg.fit(x_train, y_train)
# dt_pred = dt_reg.predict(x_test)
# dt_score = r2_score(y_test, dt_pred)

# # Random Forest Regression
# rf_reg = RandomForestRegressor(random_state=0)
# rf_reg.fit(x_train, y_train)
# rf_pred = rf_reg.predict(x_test)
# rf_score = r2_score(y_test, rf_pred)


# # Plot the simplified graph comparing the predicted and actual values
# st.header('Genre Count Over the Weeks - Top Genre: {}\n'.format(top_genre))

# fig, ax = plt.subplots(figsize=(12, 6))
# ax.plot(grouped['Week'], grouped['Count'], color='blue', label='Actual')
# ax.plot(grouped['Week'], linear_reg.predict(grouped['Week_Num'].values.reshape(-1, 1)), color='red', linewidth=2, label='Linear Regression')
# ax.plot(grouped['Week'], dt_reg.predict(grouped['Week_Num'].values.reshape(-1, 1)), color='red', linewidth=2, label='Decision Tree Regression')
# ax.plot(grouped['Week'], rf_reg.predict(grouped['Week_Num'].values.reshape(-1, 1)), color='orange', linewidth=2, label='Random Forest Regression')

# ax.set_xlabel('Week')
# ax.set_ylabel('Genre Count')
# ax.set_title('Genre Count Over the Weeks - Top Genre: ' + top_genre)
# ax.legend()
# st.pyplot(fig)


import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import r2_score

# Load and preprocess the dataset
df = pd.read_csv("billboard.csv")
df['Week'] = pd.to_datetime(df['Week'], format='%d-%m-%Y')
df['Genres'] = df['Genre'].str.split(',')
df = df.explode('Genre')

# Flatten the list of genres
genres_list = [genre for genres in df['Genres'] for genre in genres]

# Calculate the frequency of each genre
genre_counts = pd.Series(genres_list).value_counts()

# Get the genre with the highest frequency
top_genre = genre_counts.index[0]

# Filter the dataset for the top genre
top_genre_data = df[df['Genres'].apply(lambda x: top_genre in x)]

# Group and aggregate data at the weekly level for the top genre
grouped = top_genre_data.groupby('Week').size().reset_index(name='Count')

# Convert dates to numerical representation
ref_date = grouped['Week'].min()
grouped['Week_Num'] = (grouped['Week'] - ref_date).dt.days

# Split the data into training and test sets
x_train, x_test, y_train, y_test = train_test_split(grouped['Week_Num'], grouped['Count'], test_size=0.2, random_state=0)

# Create a dictionary of models
models = {
    "linear": LinearRegression(),
    "decision": DecisionTreeRegressor(random_state=0),
    "random": RandomForestRegressor(random_state=0)
}

# Create a dropdown menu to select the model
model_selection = st.sidebar.selectbox("Select Model:", models.keys())

# Train the selected model
selected_model = models[model_selection]
selected_model.fit(x_train, y_train)

# Make predictions on the test set
test_pred = selected_model.predict(x_test)

# Calculate the R-squared score
test_score = r2_score(y_test, test_pred)

# Plot the predicted and actual values using Plotly
fig = px.scatter(grouped, x='Week', y='Count', color='Actual', hover_name='Week')
fig.add_trace(px.line(grouped, x='Week', y=selected_model.predict(grouped['Week_Num'].values.reshape(-1, 1)), color=model_selection, hover_name='Prediction'))

fig.update_layout(title='Genre Count Over the Weeks - Top Genre: {}'.format(top_genre), xaxis_title='Week', yaxis_title='Genre Count')
st.plotly_chart(fig)

# Display the R-squared score
st.write("R-squared score:", test_score)
