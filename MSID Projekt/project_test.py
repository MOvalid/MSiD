import pdb
import patsy

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

from sklearn import preprocessing
from sklearn.model_selection import train_test_split, cross_val_score
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LassoCV, RidgeCV
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error

players = pd.read_csv('all_players_2021_2022.csv')

print(players.info())

print(players.head())


position_counts = players['Pos'].value_counts().reset_index()

for i, count in enumerate(position_counts['Pos']):
    plt.text(i, count + 0.1, str(count), ha='center')

sns.barplot(x='index', y='Pos', data=position_counts)
plt.xlabel('Pozycja')
plt.ylabel('Liczba zawodników')
plt.show()


club_counts = players['club'].value_counts()


club_with_most_players = club_counts.idxmax()
most_players_count = club_counts.max()

club_with_least_players = club_counts.idxmin()
least_players_count = club_counts.min()


print("Klub z największą liczbą piłkarzy:",
      club_with_most_players, f'({most_players_count})')
print("Klub z najmniejszą liczbą piłkarzy:",
      club_with_least_players, f'({least_players_count})')

total_yellow_cards = players.groupby(['Player', 'Pos'])['CrdY'].sum()
total_yellow_cards = total_yellow_cards.sort_values(ascending=False)
top_10_table = pd.DataFrame(total_yellow_cards.head(10))
top_10_table.reset_index(inplace=True)
top_10_table.index = range(1, len(top_10_table) + 1)
top_10_table.columns = ['Player', 'Position', 'TotalYellowCards']

print("Top 10 piłkarzy z największą ilością żółtych kartek ogólnie:")
print(top_10_table)
print()

players['CrdY/90'] = players['CrdY'] / players['90s']
yellow_cards_per_90 = players.groupby(['Player', 'Pos'])['CrdY/90'].mean()
yellow_cards_per_90 = yellow_cards_per_90.sort_values(ascending=False)
top_10_table = pd.DataFrame(yellow_cards_per_90.head(10))
top_10_table.reset_index(inplace=True)
top_10_table.index = range(1, len(top_10_table) + 1)
top_10_table.columns = ['Player', 'Position', 'YellowCardsPer90']

print("Top 10 piłkarzy z największą ilością żółtych kartek na 90 minut:")
print(top_10_table)
print()

most_fouling_players = players.groupby(['Player', 'Pos', 'club'])['Fls'].sum()
most_fouling_players = most_fouling_players.sort_values(ascending=False)
top_10_table = pd.DataFrame(most_fouling_players.head(10))
top_10_table.reset_index(inplace=True)
top_10_table.index = range(1, len(top_10_table) + 1)
top_10_table.columns = ['Player', 'Position', 'Club','TotalFouls']

print("Top 10 piłkarzy z największą ilością popełnionych fauli ogólnie:")
print(top_10_table)
print()

position_crdY = players.groupby(['Pos'])['CrdY/90'].mean().reset_index()
sns.barplot(x = 'Pos',y='CrdY/90',data=position_crdY)     
plt.ylabel('Yellow cards per 90 mintues')
plt.show()

players['Fls/90'] = players['Fls'] / players['90s']
fouls_per_90 = players.groupby(['Player', 'Pos'])['Fls/90'].mean()
fouls_per_90 = fouls_per_90.sort_values(ascending=False)
top_10_table = pd.DataFrame(fouls_per_90.head(10))
top_10_table.reset_index(inplace=True)
top_10_table.index = range(1, len(top_10_table) + 1)
top_10_table.columns = ['Player', 'Position', 'FoulsPer90']

print("Top 10 piłkarzy z największą ilością popełnionych fauli na 90 minut:")
print(top_10_table)
print()


players['CrdR/90'] = players['CrdR'] / players['90s']


forwards = players[players['Pos'].str.contains('FW')].reset_index(drop=True)
midfielders = players[players['Pos'].str.contains('MF')].reset_index(drop=True)
defenders = players[players['Pos'].str.contains('DF')].reset_index(drop=True)
goalkeepers = players[players['Pos'].str.contains('GK')].reset_index(drop=True)

# cards_stats = players.loc[:, ['Player', 'CrdY', '2CrdY', 'CrdR', 'CrdY/90']]
# players.pop('CrdY')
# players.pop('2CrdY')
# players.pop('CrdR')



# print('FORWARDS')
# print(forwards.corr()['CrdY'])
# print(forwards.corr()['2CrdY'])
# print(forwards.corr()['CrdR'])


# print('MIDFIELDERS')
# print(midfielders.corr()['CrdY'])
# print(midfielders.corr()['2CrdY'])
# print(midfielders.corr()['CrdR'])

# print('DEFENDERS')
# print(defenders.corr()['CrdY'])
# print(defenders.corr()['2CrdY'])
# print(defenders.corr()['CrdR'])

# print('GOALKEEPERS')
# print(goalkeepers.corr()['CrdY'])
# print(goalkeepers.corr()['2CrdY'])
# print(goalkeepers.corr()['CrdR'])



plt.figure(figsize=(10,10))
cmap = sns.cubehelix_palette(rot=-.1, as_cmap=True)
ax = sns.scatterplot(x="Fls", y="CrdY",  hue="Min", size ="Min",
                     palette=cmap, sizes=(10, 200), data=players)
plt.xlabel("Fls")
plt.ylabel("CrdY")
plt.show()


plt.figure(figsize=(20,16))
sns.heatmap(players.corr(),linewidths=.5, annot=True );
plt.yticks(rotation=360)
plt.show()


plt.figure(figsize=(15,15))
sns.barplot(x = 'Age',y='CrdY',data=players, color='yellow')
plt.show()

plt.figure(figsize=(15,15))
sns.barplot(x = 'Age',y='CrdR',data=players, color='red')
plt.show()


pos_crdY = players[players['MP']>30].groupby(['Pos'])['CrdY/90'].mean().reset_index()
pos_crdY = pos_crdY.sort_values(by='CrdY/90', ascending=False)
sns.barplot(x = 'Pos',y='CrdY/90',data=pos_crdY)     
plt.ylabel('Yellow cards per 90 min')
plt.show()


pos_crdY = players[players['MP']<20].groupby(['Pos'])['CrdY/90'].mean().reset_index()
pos_crdY = pos_crdY.sort_values(by='CrdY/90', ascending=False)
sns.barplot(x = 'Pos',y='CrdY/90',data=pos_crdY)     
plt.ylabel('Yellow cards per 90 min')
plt.show()




pos_crdR = players[players['MP']>30].groupby(['Pos'])['CrdR/90'].mean().reset_index()
pos_crdR = pos_crdR.sort_values(by='CrdR/90', ascending=False)
sns.barplot(x = 'Pos',y='CrdR/90',data=pos_crdR)     
plt.ylabel('Red cards per 90 min')
plt.show()


pos_crdR = players[players['MP']<20].groupby(['Pos'])['CrdR/90'].mean().reset_index()
pos_crdR = pos_crdR.sort_values(by='CrdR/90', ascending=False)
sns.barplot(x = 'Pos',y='CrdR/90',data=pos_crdR)     
plt.ylabel('Red cards per 90 min')
plt.show()



x_features = ['Age','MP','Min','90s','Gls','Ast','xG','Gls/90','Ast/90','xG/90','Fls','Fld','Off','Crs','Int','TklW','Recov','Won%'] 

X = players.reindex(columns=x_features)

y = players.loc[:,"CrdY"]

model = sm.OLS(y, X, data=forwards)
results = model.fit()
print(results.summary())




y = players.loc[:,"CrdY/90"]
model = sm.OLS(y, X, data=players)
results = model.fit()
print(results.summary())





lr = LinearRegression()

X, y = players[['Age', 'Fls' ,'90s', 'Gls/90', 'Int']], players[['CrdY/90']]

lr.fit(X, 
       y)
print(lr.intercept_)
print(lr.coef_)

r_sqr = lr.score(X, y)
print(f'r^2 = {r_sqr}')




test_players = pd.read_csv('train_2022_2023')

print(players.shape)
print(test_players.shape)


# predictors = ['Age', 'Fls' ,'90s', 'Gls/90', 'Int']

# predictions = lr.predict(test_players[predictors])
# players['p_CrdY/90'] = predictions
# players.loc[players['p_CrdY/90'] < 0, 'p_CrdY/90'] = 0

# print(players.head())

# error = mean_absolute_error(players['CrdY/90'], players['p_CrdY/90'])
# print(error)