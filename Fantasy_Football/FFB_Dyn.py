from espnff import League
#import fantasy_data
import pyexcel as p
import html5lib
from selenium import webdriver
import requests
from lxml import html
import time
import glob
import os
import pandas as pd
import numpy as np


class Model():
	def __init__(self,year,leagueID,cookie1,cookie2):
		self.projQB = pd.DataFrame()
		self.projRB = pd.DataFrame()
		self.projWR = pd.DataFrame()
		self.projTE = pd.DataFrame()
		self.league_id =leagueID
		self.year = year
		#self.league  = League(self.league_id,self.year, espn_s2 = cookie1 , swid = cookie2)
		#self.teams = self.league.teams
		'''
		self.teams[0].keepers = {'Josh Gordon':6,'JuJu Smith-Schuster':6}
		self.teams[1].keepers = {'David Johnson':16,'Michael Thomas':11}
		self.teams[2].keepers = {'Jordan Howard':11,'Marvin Jones':6}
		self.teams[3].keepers = {'Adam Thielen':7,'Dalvin Cook':42}
		self.teams[4].keepers = {'DeAndre Hopkins':42,'Melvin Gordon':15}
		self.teams[5].keepers = {'Joe Mixon':32,'Travis Kelce':23}
		self.teams[6].keepers = {'Ezekiel Elliott':56,'Jerick McKinnon':6}
		self.teams[7].keepers = {'Devonta Freeman':16,'Todd Gurley':53}
		self.teams[8].keepers = {'Leonard Fournette':43,'Keenan Allen':32}
		self.teams[9].keepers = {'Alvin Kamara':6,'Kareem Hunt':16}
		self.teams[0].tradeCosts = -15
		self.teams[2].tradeCosts = -5
				'''

		#self.settings  = self.league.settings
		#self.regSeason = self.settings.reg_season_count
		self.numTeams = 12
		#self.numKeepers  = self.settings.keeper_count
		self.rosterConstr = {'QB':1,'RB':2,'WR':2,'TE':1,'RB/WR/TE':2,'BE':10}
		self.auctionCap = 200
		self.keeperCost = 0
		self.tradeCosts = 0
		self.numKept = 0
		self.scoring  = {'pYards':0.04,'Int':-1,'pTD':4,'p2PT':2,'rshYards':0.1,'rshTD':6,'rsh2PT':2,'recYards':0.1,'recTD':6,'rec':0.5,'rec2PT':2,'KRTD':6,
			'FRTD':6,'PRTD':6,'intTD':6,'fumL':-2,'BPTD':6,'ret2PT':2,'sfty':1}
		self.positions = ['QB','RB','WR','TE']
		self.projQB = pd.read_csv("projQB.csv", index_col = 'Player')
		self.projQB.dropna(inplace=True)
		self.projQB['YDS'] = self.projQB['YDS'].str.replace(',','')
		self.projQB.ix[:,1:] = self.projQB.ix[:,1:].astype(float)
		self.projRB = pd.read_csv("projRB.csv", index_col = 'Player')
		self.projRB.dropna(inplace=True)
		self.projRB['YDS'] = self.projRB['YDS'].str.replace(',','')
		self.projRB.ix[:,1:] = self.projRB.ix[:,1:].astype(float)
		self.projWR = pd.read_csv("projWR.csv", index_col = 'Player')
		self.projWR.dropna(inplace=True)
		self.projWR['YDS'] = self.projWR['YDS'].str.replace(',','')
		self.projWR.ix[:,1:] = self.projWR.ix[:,1:].astype(float)
		self.projTE = pd.read_csv("projTE.csv", index_col = 'Player')
		self.projTE.dropna(inplace=True)
		self.projTE['YDS'] = self.projTE['YDS'].str.replace(',','')
		self.projTE.ix[:,1:] = self.projTE.ix[:,1:].astype(float)
		'''
		for team in range(0,len(self.teams)):
			self.keeperCost+=sum(self.teams[team].keepers.values())
			self.tradeCosts+=self.teams[team].tradeCosts
			self.numKept+=len(self.teams[team].keepers.keys())
			for keeper in self.teams[team].keepers:
				if keeper in self.projQB.index:
					self.projQB.drop(keeper,axis =0, inplace = True)
				elif keeper in self.projRB.index:
					self.projRB.drop(keeper,axis = 0, inplace = True)
				elif keeper in self.projWR.index:
					self.projWR.drop(keeper,axis=0, inplace = True)
				elif keeper in self.projTE.index:
					self.projTE.drop(keeper, axis = 0, inplace = True)
				else:
					print (keeper)
					print("you fucked up Aaron")
					
				'''

		 
		self.freeMoney = (self.numTeams*200)+(self.tradeCosts)-self.keeperCost-((len(self.rosterConstr.keys())-1)*self.numTeams)+(self.numKept*self.numTeams)
		#print (self.rosterConstr)
		pass

	def updateProj(self,fileName):
		scoreQB = pd.Series([0,0,self.scoring['pYards'],self.scoring['pTD'],self.scoring['Int'],0,self.scoring['rshYards'],self.scoring['rshTD'],self.scoring['fumL']])
		scoreRB = pd.Series([0,self.scoring['rshYards'],self.scoring['rshTD'],self.scoring['rec'],self.scoring['recYards'],self.scoring['recTD'],self.scoring['fumL']])
		scoreWR = pd.Series([self.scoring['rec'],self.scoring['recYards'],self.scoring['recTD'],0,self.scoring['rshYards'],self.scoring['rshTD'],self.scoring['fumL']])
		print (self.projQB.ix[:,1:-2])
		print (scoreQB)
		scoreTE = pd.Series([self.scoring['rec'],self.scoring['recYards'],self.scoring['recTD'],self.scoring['fumL']])
		tempPQB = self.projQB.ix[:,1:-1]
		tempPRB = self.projRB.ix[:,1:-1]
		tempPWR = self.projWR.ix[:,1:-1]
		tempPTE = self.projTE.ix[:,1:-1]
		tierQB = self.projQB.ix[:,-1]
		tierRB = self.projRB.ix[:,-1]
		tierWR = self.projWR.ix[:,-1]
		tierTE = self.projTE.ix[:,-1]
		tempPQB = tempPQB.apply(lambda x: np.asarray(x) * np.asarray(scoreQB), axis=1)
		self.projQB['FPTS'] = tempPQB.sum(axis = 1)
		tempPRB = tempPRB.apply(lambda x: np.asarray(x) * np.asarray(scoreRB), axis=1)
		self.projRB['FPTS'] = tempPRB.sum(axis = 1)
		tempPWR = tempPWR.apply(lambda x: np.asarray(x) * np.asarray(scoreWR), axis=1)
		self.projWR['FPTS'] = tempPWR.sum(axis = 1)
		tempPTE = tempPTE.apply(lambda x: np.asarray(x) * np.asarray(scoreTE), axis=1)
		self.projTE['FPTS'] = tempPTE.sum(axis = 1)
		startPos = ['QB','RB','WR','TE','RB/WR/TE']
		startNum  = [self.rosterConstr[i] for i in startPos]
		starters = [i*self.numTeams for i in startNum]
		starters[1] = int(starters[1]+0.25*starters[4])
		starters[2] = int(starters[2]+0.75*starters[4])
		starters = starters[0:4]
		benchNum  = self.rosterConstr['BE']*self.numTeams
		bench = [0.20*benchNum,0.30*benchNum,0.30*benchNum,0.2*benchNum]
		#print(starters)
		#print(bench)
		totalDraft = [int(sum(x)) for x in zip(starters, bench)]
		#print(totalDraft)
		
		rosterBaseQB = self.projQB.ix[totalDraft[0]-1,'FPTS']
		rosterBaseRB = self.projRB.ix[totalDraft[1]-1,'FPTS']
		rosterBaseWR = self.projWR.ix[totalDraft[2]-1,'FPTS']	
		rosterBaseTE = self.projTE.ix[totalDraft[3]-1,'FPTS']
		benchPlusQB = self.projQB.ix[(int(starters[0]*2))-1,'FPTS']
		benchPlusRB = self.projRB.ix[(int(starters[1]*1.5))-1,'FPTS']
		benchPlusWR = self.projWR.ix[(int(starters[2]*3))-1,'FPTS']	
		benchPlusTE = self.projTE.ix[(int(starters[3]*1.5))-1,'FPTS']
		starterQB = self.projQB.ix[(starters[0])-1,'FPTS']
		starterRB = self.projRB.ix[(starters[1])-1,'FPTS']
		starterWR = self.projWR.ix[(starters[2])-1,'FPTS']	
		starterTE = self.projTE.ix[(starters[3])-1,'FPTS']
		starterPlusQB = self.projQB.ix[(int(starters[0]*0.5))-1,'FPTS']
		starterPlusRB = self.projRB.ix[(int(starters[1]*0.5))-1,'FPTS']
		starterPlusWR = self.projWR.ix[(int(starters[2]*0.5))-1,'FPTS']	
		starterPlusTE = self.projTE.ix[(int(starters[3]*0.5))-1,'FPTS']
		threshQB=[rosterBaseQB,benchPlusQB,starterQB,starterPlusQB]
		threshRB=[rosterBaseRB,benchPlusRB,starterRB,starterPlusRB]
		threshWR=[rosterBaseWR,benchPlusWR,starterWR,starterPlusWR]
		threshTE=[rosterBaseTE,benchPlusTE,starterTE,starterPlusTE]
		#print(self.projRB)
		#print (threshRB)
		threshDataQB = pd.DataFrame(0,index = self.projQB.index, columns = ('1','2','3','4'))
		threshDataRB = pd.DataFrame(0,index = self.projRB.index, columns = ('1','2','3','4'))
		threshDataWR = pd.DataFrame(0,index = self.projWR.index, columns = ('1','2','3','4'))
		threshDataTE = pd.DataFrame(0,index = self.projTE.index, columns = ('1','2','3','4'))
		for col in range(0,threshDataRB.shape[1]):
			threshDataQB.ix[:,str(col+1)] = self.projQB['FPTS'] - threshQB[col]
			threshDataRB.ix[:,str(col+1)] = self.projRB['FPTS'] - threshRB[col]
			threshDataWR.ix[:,str(col+1)] = self.projWR['FPTS'] - threshWR[col]
			threshDataTE.ix[:,str(col+1)] = self.projTE['FPTS'] - threshTE[col]
			
		threshDataQB[threshDataQB<0] = 0
		threshDataRB[threshDataRB<0] = 0
		threshDataWR[threshDataWR<0] = 0
		threshDataTE[threshDataTE<0] = 0
		sumBase = threshDataQB.sum().sum() + threshDataRB.sum().sum() + threshDataWR.sum().sum() + threshDataTE.sum().sum()
		margPtsPerUnit = sumBase/self.freeMoney
		threshDataQB = (threshDataQB.sum(axis =1)/margPtsPerUnit)+1
		threshDataRB = (threshDataRB.sum(axis =1)/margPtsPerUnit)+1
		threshDataWR = (threshDataWR.sum(axis =1)/margPtsPerUnit)+1
		threshDataTE = (threshDataTE.sum(axis =1)/margPtsPerUnit)+1
		posQB = pd.DataFrame(np.zeros((threshDataQB.shape[0],1)), index  = threshDataQB.index)
		posQB.ix[:,:] = 'QB'
		threshDataQB = pd.concat([threshDataQB, posQB, tierQB], axis=1)
		threshDataQB.columns = ['price','pos','tier']
		posRB = pd.DataFrame(np.zeros((threshDataRB.shape[0],1)), index  = threshDataRB.index)
		posRB.ix[:,:] = 'RB'
		threshDataRB = pd.concat([threshDataRB, posRB, tierRB], axis=1)
		threshDataRB.columns = ['price','pos','tier']
		posWR = pd.DataFrame(np.zeros((threshDataWR.shape[0],1)), index  = threshDataWR.index)
		posWR.ix[:,:] = 'WR'
		threshDataWR = pd.concat([threshDataWR, posWR, tierWR], axis=1)
		threshDataWR.columns = ['price','pos','tier']
		posTE = pd.DataFrame(np.zeros((threshDataTE.shape[0],1)), index  = threshDataTE.index)
		posTE.ix[:,:] = 'TE'
		threshDataTE = pd.concat([threshDataTE, posTE, tierTE], axis=1)
		threshDataTE.columns = ['price','pos','tier']
		threshDataQB = threshDataQB.sort_values(by=['price'],ascending = False)
		threshDataRB = threshDataRB.sort_values(by=['price'],ascending  = False)
		threshDataWR = threshDataWR.sort_values(by=['price'], ascending = False )
		threshDataTE = threshDataTE.sort_values(by=['price'], ascending = False)
		#threshDataQB = threshDataQB.sort_values(by=['tier'],ascending = True)
		#threshDataRB = threshDataRB.sort_values(by=['tier'],ascending  = True)
		#threshDataWR = threshDataWR.sort_values(by=['tier'], ascending = True )
		#threshDataTE = threshDataTE.sort_values(by=['tier'], ascending = True)
		#auctionPD = threshDataQB.append([threshDataRB,threshDataWR,threshDataTE])
		writer = pd.ExcelWriter(fileName)
		auctionPD = pd.concat([threshDataQB,threshDataRB,threshDataWR,threshDataTE],axis = 1)
		#print (self.freeMoney)
		#print (margPoints)
		#print(threshDataWR)
		#print (threshDataRB)
		#print(self.projRB['FPTS'])
		#print(threshDataQB)
		#print(threshDataTE)
		#print (auctionPD)
		threshDataQB.to_excel(writer,'sheet1',startrow = 0,startcol = 0)
		threshDataRB.to_excel(writer,'sheet1',startrow = 0,startcol = 5)
		threshDataWR.to_excel(writer,'sheet1',startrow = 0,startcol = 10)
		threshDataTE.to_excel(writer,'sheet1',startrow = 0,startcol = 15)
		wb = writer.book
		ws = writer.sheets['sheet1']
		format1 = wb.add_format({'bg_color': '#C6EFCE',
							   'font_color': '#006100'})
		format2 = wb.add_format({'bg_color': '#FFFFFF',
							   'font_color': '#006100'})
		format3 = wb.add_format({'bg_color': '#808080',
							   'font_color': '#FFFFFF'})
		format4 = wb.add_format({'bg_color': '#FFFF00',
							   'font_color': '#000000'})
		format5 = wb.add_format({'bg_color': '#FF6600',
							   'font_color': '#000000'})
		format6 = wb.add_format({'bg_color': '#FF00FF',
							   'font_color': '#000000'})
		format7 = wb.add_format({'bg_color': '#800000',
							   'font_color': '#FFFFFF'})
		format8 = wb.add_format({'bg_color': '#800080',
							   'font_color': 'FFFFFF'})
		format9 = wb.add_format({'bg_color': '#000080',
							   'font_color': '#FFFFFF'})
		format10 = wb.add_format({'bg_color': '#00FF00',
							   'font_color': '#0000FF','bold':True, 'italic':True})
		for i in range(1,threshDataWR.shape[0]):

				ws.conditional_format('A%s:D%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=D%s=1'%(i),
										 'value': 50,
										 'format': format1})
				ws.conditional_format('A%s:D%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=D%s=2'%(i),
										 'value': 50,
										 'format': format2})
				ws.conditional_format('A%s:D%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=D%s=3'%(i),
										 'value': 50,
										 'format': format3})
				ws.conditional_format('A%s:D%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=D%s=4'%(i),
										 'value': 50,
										 'format': format4})
				ws.conditional_format('A%s:D%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=D%s=5'%(i),
										 'value': 50,
										 'format': format5})
				ws.conditional_format('A%s:D%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=D%s=6'%(i),
										 'value': 50,
										 'format': format6})
				ws.conditional_format('A%s:D%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=D%s=7'%(i),
										 'value': 50,
										 'format': format7})
				ws.conditional_format('A%s:D%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=D%s=8'%(i),
										 'value': 50,
										 'format': format8})
				ws.conditional_format('A%s:D%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=D%s=9'%(i),
										 'value': 50,
										 'format': format9})
				ws.conditional_format('A%s:D%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=D%s=10'%(i),
										 'value': 50,
										 'format': format10})



				ws.conditional_format('F%s:I%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=I%s=1'%(i),
										 'value': 50,
										 'format': format1})
				ws.conditional_format('F%s:I%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=I%s=2'%(i),
										 'value': 50,
										 'format': format2})
				ws.conditional_format('F%s:I%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=I%s=3'%(i),
										 'value': 50,
										 'format': format3})
				ws.conditional_format('F%s:I%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=I%s=4'%(i),
										 'value': 50,
										 'format': format4})
				ws.conditional_format('F%s:I%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=I%s=5'%(i),
										 'value': 50,
										 'format': format5})
				ws.conditional_format('F%s:I%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=I%s=6'%(i),
										 'value': 50,
										 'format': format6})
				ws.conditional_format('F%s:I%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=I%s=7'%(i),
										 'value': 50,
										 'format': format7})
				ws.conditional_format('F%s:I%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=I%s=8'%(i),
										 'value': 50,
										 'format': format8})
				ws.conditional_format('F%s:I%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=I%s=9'%(i),
										 'value': 50,
										 'format': format9})
				ws.conditional_format('F%s:I%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=I%s=10'%(i),
										 'value': 50,
										 'format': format10})


				ws.conditional_format('K%s:N%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=N%s=1'%(i),
										 'value': 50,
										 'format': format1})
				ws.conditional_format('K%s:N%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=N%s=2'%(i),
										 'value': 50,
										 'format': format2})
				ws.conditional_format('K%s:N%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=N%s=3'%(i),
										 'value': 50,
										 'format': format3})
				ws.conditional_format('K%s:N%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=N%s=4'%(i),
										 'value': 50,
										 'format': format4})
				ws.conditional_format('K%s:N%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=N%s=5'%(i),
										 'value': 50,
										 'format': format5})
				ws.conditional_format('K%s:N%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=N%s=6'%(i),
										 'value': 50,
										 'format': format6})
				ws.conditional_format('K%s:N%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=N%s=7'%(i),
										 'value': 50,
										 'format': format7})
				ws.conditional_format('K%s:N%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=N%s=8'%(i),
										 'value': 50,
										 'format': format8})
				ws.conditional_format('K%s:N%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=N%s=9'%(i),
										 'value': 50,
										 'format': format9})
				ws.conditional_format('K%s:N%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=N%s=10'%(i),
										 'value': 50,
										 'format': format10})



				ws.conditional_format('P%s:S%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=S%s=1'%(i),
										 'value': 50,
										 'format': format1})
				ws.conditional_format('P%s:S%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=S%s=2'%(i),
										 'value': 50,
										 'format': format2})
				ws.conditional_format('P%s:S%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=S%s=3'%(i),
										 'value': 50,
										 'format': format3})
				ws.conditional_format('P%s:S%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=S%s=4'%(i),
										 'value': 50,
										 'format': format4})
				ws.conditional_format('P%s:S%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=S%s=5'%(i),
										 'value': 50,
										 'format': format5})
				ws.conditional_format('P%s:S%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=S%s=6'%(i),
										 'value': 50,
										 'format': format6})
				ws.conditional_format('P%s:S%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=S%s=7'%(i),
										 'value': 50,
										 'format': format7})
				ws.conditional_format('P%s:S%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=S%s=8'%(i),
										 'value': 50,
										 'format': format8})
				ws.conditional_format('P%s:S%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=S%s=9'%(i),
										 'value': 50,
										 'format': format9})
				ws.conditional_format('P%s:S%s'%(i,threshDataWR.shape[0]) ,{'type': 'formula',
										 'criteria': '=S%s=10'%(i),
										 'value': 50,
										 'format': format10})
		#print (auctionPD.shape[1])	
		#writer2 = pd.ExcelWriter('testAuctionPD.xlsx')
		#auctionPD.to_excel(writer2)
		#print(enumerate(auctionPD))
		total_series = [threshDataQB.index,threshDataRB.index,threshDataWR.index,threshDataTE.index]
		columns1 = [0,5,10,15]
		columns = {'0':0,'1':1,'2':2,'3':3,'4':5,'5':6,'6':7,'7':8,'8':10,'9':11,'10':12,'11':13,'12':15,'13':16,'14':17,'15':18}
		for idx,val in enumerate(columns1):  # loop through all columns
			series = total_series[idx]
			#print(idx)
			#print (series)
			max_len = max((
				series.astype(str).map(len).max(),  # len of largest item
				len(str(series.name))  # len of column name/header
				)) + 1  # adding a little extra space
			ws.set_column(val, val, max_len)  # set column width

		wb.close()




		writer.save

		#auctionPD.to_excel('auctionPricing.xlsx')
		return auctionPD


	
def download_csv(Pos):
		global final_file
		print (Pos)
		print('____________________________________________________________')
		if Pos == 'QB':
			link = 'https://www.fantasypros.com/nfl/stats/qb.php'
			final_file = "FantasyPros_Fantasy_Football_Statistics_QB.csv"
		elif Pos ==  'RB':
			link = 'https://www.fantasypros.com/nfl/stats/rb.php'
			final_file = "FantasyPros_Fantasy_Football_Statistics_RB.csv"
		elif Pos == 'WR':
			link = 'https://www.fantasypros.com/nfl/stats/wr.php'
			final_file = "FantasyPros_Fantasy_Football_Statistics_WR.csv"
		elif Pos == 'TE':
			link = 'https://www.fantasypros.com/nfl/stats/te.php'
			final_file = "FantasyPros_Fantasy_Football_Statistics_TE.csv"
		elif Pos == 'Snap': 
			link = 'https://www.fantasypros.com/nfl/reports/snap-counts/'
			final_file = "FantasyPros_Fantasy_Football_2017_Offense_Snap_Counts.csv"
		elif Pos == 'Target':
			link = 'https://www.fantasypros.com/nfl/reports/targets/'
			final_file = "FantasyPros_Fantasy_Football_2017_Target_Leaders.csv"
		elif Pos == 'proj%s' %Pos[-2:]:
			link = 'https://www.fantasypros.com/nfl/projections/%s.php' %Pos[-2:]
			print('____________________________________________________________________')
			print (link)
			print ('____________________________________________________________________')

			final_file  = 'FantasyPros_Fantasy_Football_Projections_%s.csv'%Pos[-2:]
		
		#session_requests = requests.session()


		url = "https://www.fantasypros.com/nfl/stats/qb.php?ownership=e&scoring=HALF"
		#login_payload = {"username":"<mwyatt9214@gmail.com>","password":"<CJ15035300>","crsfmiddlewaretoken":"<d1if2O0wT5qlXGcXnwCCEdzdDWfZv9GB>"}
		#result = session_requests.get(url)
		#tree = html.formstring(result.text)
		#autheticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]

		#result = session_requests.post(url, data = login_payload, headers = dict(referer=url))


		#login_payload = {"username":"<mwyatt9214@gmail.com>","password":"<CJ15035300>","crsfmiddlewaretoken":"<d1if2O0wT5qlXGcXnwCCEdzdDWfZv9GB>"}

		driver = webdriver.Chrome("C:\\Users\mateo\chromedriver.exe")
		driver.implicitly_wait(10)
		driver.get('https://secure.fantasypros.com/accounts/login/?next=http://www.fantasypros.com/index.php?loggedin&loggedout')
		time.sleep(3)
		username=driver.find_element_by_id('id_username')
		password=driver.find_element_by_id('id_password')
		time.sleep(3)
		username.send_keys("mrw7fq@virginia.edu")
		password.send_keys("CJ15035300")

		driver.find_element_by_xpath('/html/body/div/div[2]/div/div[2]/form/button').click()
		#print(driver.title)
		print('____________________________________________________________________')
		print (link)
		print ('____________________________________________________________________')
		driver.get(link)
		if Pos == 'proj%s' %Pos[-2:]:
			print ("I AM HERE")
			print(Pos)
			driver.find_element_by_xpath('/html/body/div[3]/div[6]/div/div[1]/div/div[1]/div[2]/div/a[2]/i').click()
		else:
			driver.find_element_by_xpath('/html/body/div[3]/div[6]/div/div[1]/div/div[1]/div[2]/a[2]/i').click()
		

		
		time.sleep(3)
		p.save_book_as(file_name="C:\\Users\mateo\Downloads\{0}".format(final_file),
			   dest_file_name=Pos+'.csv')
		os.remove("C:\\Users\mateo\Downloads\{0}".format(final_file))
		
		''' 
		xlsxFile = Pos+".xlsx"
		wb1 = load_workbook(xlsxFile)
		#os.chdir(owd)
		wb2 = load_workbook('Fantasy_Football_Analysis.xlsx')
		print (list(wb1.get_sheet_names()))

		sheet1 = wb1.get_sheet_by_name(final_file)
		sheet2 = wb2.get_sheet_by_name('{0}_raw'.format(Pos))

		for i,row in enumerate(sheet1.iter_rows()):
			for j,col in enumerate(row):
				sheet2.cell(row=i+1,column=j+1).value = col.value
		wb1.save(xlsxFile)
		wb2.save('Fantasy_Football_Analysis.xlsx')
		
		os.remove("C:\\Users\mateo\Downloads\{0}".format(final_file))
		os.remove(Pos+'.xlsx')
			'''

		pass


def main():
		'''
		download_csv("QB")
		print("QB done")
		download_csv('RB')
		print("RB done")
		download_csv('WR')
		print("WR done")
		download_csv('TE')
		print("TE done")
		download_csv('Snap')
		print("Snap done")
		download_csv('Target')
		print("Target done")
		
		download_csv("projqb")
		print("QB done")
		download_csv('projrb')
		print("RB done")
		download_csv('projwr')
		print("WR done")
		download_csv('projte')
		print("TE done")
		print ('jackass')
			'''
		model = Model(2017,leagueID = 1178400,cookie1 = 'AEBjs0LkqW50z8EngoJwTYKwXhm9We0o%2FnO2%2BvSvJt1pE10GvjKn7KdKVMtRDFbEeFYsDcKY54FcfXTbAHxAjaFlDvfGM3jU0uHKz6vHm6TCdALj1VvPaPEse%2BuODLBXcMv6EFkiTpo9V32CpIttwcPr%2BzT%2BhWoxl8CzpQDznFxBF%2Bb3YpyD9FbWt%2FflzAWT%2FwBvhxyNa3p1CwWJCw6PwgwBWeuCOl6mS0bXvT0A8vHCAuUEkUDrENNbCIBSaJmW7%2FQ%3D',cookie2 = "{D76A21AE-1340-48D5-8A6D-6A69EB6865E3}")
		updatedProj  = model.updateProj('auctionPricing.xlsx')
		#model2 = Model(2017,leagueID = 1059005,cookie1 = 'AECHcPkU32zUeGc68PJYLKPyC36sQTMjX2X9AUqSp2GQIu5hY6AFrKAUN3eZhgX6Vqdb680eANmnXT6O9KwZo3mi5ZSNDYnjntceL8j6LZGtd5w0io%2B5l6ZgfHyC9RsZMeT2N%2FhZ8CY6Sh1Ic1rIE3zg7TFn%2BR4CA0V0kAavD%2FZPMwsWjsqfwqBKy4d9km%2BU75IhgO0riE8ydMusPA6TCI8gC5Bph0BMOc9sS%2BUYfxLl2wBPQLR1%2FZynjjc0uPv77sA%3D',cookie2 ="{D76A21AE-1340-48D5-8A6D-6A69EB6865E3}" )
		#updatedProj2  = model2.updateProj('auctionPricing2.xlsx')
if __name__ == '__main__':
	main()