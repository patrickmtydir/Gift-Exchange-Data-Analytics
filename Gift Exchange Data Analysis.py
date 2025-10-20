import pandas as pd
import statsmodels.api as sm
import numpy as np
import math
from linearmodels.panel import PanelOLS
from scipy.stats import norm, ranksums
import builtins
control_data=pd.DataFrame()
treatment_data=pd.DataFrame()
all_data=pd.DataFrame()
summary_stats=pd.DataFrame()

#Importing Data into dataframes and creating session and treatment variables
for treatment in ["Effort Before", "Effort After"]: #, "Binary Effort"
    for session in list(range(1,8)):
        file_path=f"{treatment}/Session {session}"
        data= pd.read_excel(file_path+"/Transactions.xlsx")
        data["session"]=f"{session}"
        if treatment == "Effort Before":
            data["treatment"]=0
            control_data=pd.concat([control_data,data])
            all_data=pd.concat([all_data,data])
        if treatment == "Effort After":
            data["treatment"]=1
            treatment_data=pd.concat([treatment_data,data])
            all_data=pd.concat([all_data,data])        

        # Summary Statistics
        data["total_surplus"]=data["worker_surplus"]+data["firm_surplus"]
        data["firm_surplus_share"]=data["firm_surplus"]/data["total_surplus"]
        Averages=data.groupby("session").mean()
        Averages["session"]=f"{session}"
        Averages["treatment"]=f"{treatment}"
        columns=['wage',"effort","worker_surplus","firm_surplus","total_surplus", "firm_surplus_share","session","treatment"]
        Averages.to_csv(file_path+"/Summary Statistics.csv", columns=columns, index=False)
        summary_stats=pd.concat([summary_stats,Averages])

        # Summary Table
        mean_wage_groups=data.groupby(pd.cut(data['wage'], [29, 44, 59, 74, 89, 104, 126])).mean().round(2)
        med_wage_groups=data.groupby(pd.cut(data['wage'], [29, 44, 59, 74, 89, 104, 126])).median().round(2)
        count_wage_groups=data.groupby(pd.cut(data['wage'], [29, 44, 59, 74, 89, 104, 126])).count()
        table_data={"Average Observed Effort Level":mean_wage_groups["effort"], "Median Observed Effort Level":med_wage_groups["effort"], "n":count_wage_groups["firm_id"]}
        table_dataframe=pd.DataFrame(table_data)
        custom_labels = ["30 to 44", "45 to 59", "60 to 74", "75 to 89", "90 to 104", "105 to 125"]
        table_dataframe = table_dataframe.fillna("-")
        table_dataframe.index = custom_labels
        table_dataframe.index.name = "Wage Range"
        table_dataframe["Average Observed Effort Level"]=table_dataframe["Average Observed Effort Level"].astype(str)
        table_dataframe["Median Observed Effort Level"]=table_dataframe["Median Observed Effort Level"].astype(str)
        str = builtins.str
        with open(file_path+"/Session Summary Table"+" "+f"{treatment} "+f"{session}"+"table.tex","w") as f:
            f.write(table_dataframe.to_latex(index=True, column_format="cccc", multirow=False))

    # End of session loop
# End of treatment loop

# Aggregate Differences and Stats

# Summary Statistics
summary_stats.to_csv("Aggregated Summary Statistics.csv", columns=columns, index=False)

# Summary Tables
mean_wage_groups_control=control_data.groupby(pd.cut(control_data['wage'], [29, 44, 59, 74, 89, 104, 126])).mean().round(2)
med_wage_groups_control=control_data.groupby(pd.cut(control_data['wage'], [29, 44, 59, 74, 89, 104, 126])).median().round(2)
count_wage_groups_control=control_data.groupby(pd.cut(control_data['wage'], [29, 44, 59, 74, 89, 104, 126])).count()
table_data_control={"Average Observed Effort Level":mean_wage_groups_control["effort"], "Median Observed Effort Level":med_wage_groups_control["effort"], "n":count_wage_groups_control["firm_id"]}
table_dataframe_control=pd.DataFrame(table_data_control)
custom_labels = ["30 to 44", "45 to 59", "60 to 74", "75 to 89", "90 to 104", "105 to 125"]
table_dataframe_control = table_dataframe_control.fillna("-")
table_dataframe_control.index = custom_labels
table_dataframe_control.index.name = "Wage Range"
table_dataframe_control["Average Observed Effort Level"]=table_dataframe_control["Average Observed Effort Level"].astype(str)
table_dataframe_control["Median Observed Effort Level"]=table_dataframe_control["Median Observed Effort Level"].astype(str)
str = builtins.str
with open("Summary Table Effort After.tex","w") as f:
    f.write(table_dataframe_control.to_latex(index=True, column_format="cccc", multirow=False))

mean_wage_groups_treatment=treatment_data.groupby(pd.cut(treatment_data['wage'], [29, 44, 59, 74, 89, 104, 126])).mean().round(2)
med_wage_groups_treatment=treatment_data.groupby(pd.cut(treatment_data['wage'], [29, 44, 59, 74, 89, 104, 126])).median().round(2)
count_wage_groups_treatment=treatment_data.groupby(pd.cut(treatment_data['wage'], [29, 44, 59, 74, 89, 104, 126])).count()
table_data_treatment={"Average Observed Effort Level":mean_wage_groups_treatment["effort"], "Median Observed Effort Level":med_wage_groups_treatment["effort"], "n":count_wage_groups_treatment["firm_id"]}
table_dataframe_treatment=pd.DataFrame(table_data_treatment)
custom_labels = ["30 to 44", "45 to 59", "60 to 74", "75 to 89", "90 to 104", "105 to 125"]
table_dataframe_treatment = table_dataframe_treatment.fillna("-")
table_dataframe_treatment.index = custom_labels
table_dataframe_treatment.index.name = "Wage Range"
table_dataframe_treatment["Average Observed Effort Level"]=table_dataframe_treatment["Average Observed Effort Level"].astype(str)
table_dataframe_treatment["Median Observed Effort Level"]=table_dataframe_treatment["Median Observed Effort Level"].astype(str)
str = builtins.str
with open("Summary Table Effort Before.tex","w") as f:
    f.write(table_dataframe_treatment.to_latex(index=True, column_format="cccc", multirow=False))

# Wage vs Effort Recieved in Previous Round Regression
# Wage vs Effort Recieved in Previous Round - Effort After
wage_vs_effort_before_list=[]
for row in range(len(control_data)):
    round_number_row=control_data.iloc[row]
    round_number=round_number_row["round_number"]
    session_number=round_number_row["session"]
    if round_number >1:
        firm_id=round_number_row["firm_id"]
        worker_id=round_number_row["worker_id"]
        wage_offered=round_number_row["wage"]
        treatment=round_number_row["treatment"]
        previous_round=round_number-1
        effort_recieved_row=control_data.loc[(control_data["round_number"]==previous_round) & (control_data["firm_id"]==firm_id) & (control_data["session"]==session_number),"effort"]
        if len(effort_recieved_row)>0:
            effort_recieved=effort_recieved_row.item()
            wage_vs_effort_before_list.append({"round_number":round_number, "firm_id":firm_id, "effort_recieved":effort_recieved, "wage_offered":wage_offered, "session":session_number, "treatment":treatment, "worker_id":worker_id})
wage_vs_effort_before_data=pd.DataFrame(wage_vs_effort_before_list) 
wage_vs_effort_before_data_control=wage_vs_effort_before_data.copy(deep=False) 

# Wage vs Effort Recieved in Previous Round - Effort Before
wage_vs_effort_before_list=[]
for row in range(len(treatment_data)):
    round_number_row=treatment_data.iloc[row]
    round_number=round_number_row["round_number"]
    session_number=round_number_row["session"]
    if round_number >1:
        firm_id=round_number_row["firm_id"]
        worker_id=round_number_row["worker_id"]
        wage_offered=round_number_row["wage"]
        treatment=round_number_row["treatment"]
        previous_round=round_number-1
        effort_recieved_row=treatment_data.loc[(treatment_data["round_number"]==previous_round) & (treatment_data["firm_id"]==firm_id) & (treatment_data["session"]==session_number),"effort"]
        if len(effort_recieved_row)>0:
            effort_recieved=effort_recieved_row.item()
            wage_vs_effort_before_list.append({"round_number":round_number, "firm_id":firm_id, "effort_recieved":effort_recieved, "wage_offered":wage_offered, "session":session_number, "treatment":treatment, "worker_id":worker_id})
wage_vs_effort_before_data=pd.DataFrame(wage_vs_effort_before_list)   
wage_vs_effort_before_data_treatment=wage_vs_effort_before_data.copy(deep=False) 
wage_vs_effort_before_data_control["const"]=1
wage_vs_effort_before_data_treatment["const"]=1

wage_vs_effort_before_data_control["firm_identification"]=wage_vs_effort_before_data_control["session"].astype(str)+"_"+wage_vs_effort_before_data_control["firm_id"].astype(str)
wage_vs_effort_before_data_control=wage_vs_effort_before_data_control.set_index(["firm_identification","round_number"])
control_model=PanelOLS(wage_vs_effort_before_data_control["wage_offered"],wage_vs_effort_before_data_control[["const","effort_recieved"]],entity_effects=True, drop_absorbed=True)
control_result=control_model.fit()
print("Wage vs Effort Recieved in Previous Round OLS, Effort After Data\n",control_result)

wage_vs_effort_before_data_treatment["firm_identification"]=wage_vs_effort_before_data_treatment["session"].astype(str)+"_"+wage_vs_effort_before_data_treatment["firm_id"].astype(str)
wage_vs_effort_before_data_treatment=wage_vs_effort_before_data_treatment.set_index(["firm_identification","round_number"])
treatment_model=PanelOLS(wage_vs_effort_before_data_treatment["wage_offered"],wage_vs_effort_before_data_treatment[["const","effort_recieved"]],entity_effects=True, time_effects=True, drop_absorbed=True)
treatment_result=treatment_model.fit()
print("Wage vs Effort Recieved in Previous Round OLS, Effort Before Data\n",treatment_result)

z_stat=(control_result.params["effort_recieved"]-treatment_result.params["effort_recieved"])/(math.sqrt(control_result.std_errors["effort_recieved"]**2+(treatment_result.std_errors["effort_recieved"])**2))
p_value=1-norm.cdf(z_stat)
print("Z-stats Wage vs Effort Recieved in Previous Round OLS effort recieved\n","z=",z_stat,", p=", p_value)
z_stat=(control_result.params["const"]-treatment_result.params["const"])/(math.sqrt(control_result.std_errors["const"]**2+(treatment_result.std_errors["const"])**2))
p_value=1-norm.cdf(z_stat)
print("Z-stats Wage vs Effort Recieved in Previous Round OLS effort CONST\n","z=",z_stat,", p=", p_value)
#control_data = control_data.reset_index(drop=True)
#treatment_data = treatment_data.reset_index(drop=True)
# Wage vs Surplus Recieved in Previous Round - Effort After
wage_vs_surplus_before_list=[]
for row in range(len(control_data)):
    round_number_row=control_data.iloc[row]
    round_number=round_number_row["round_number"]
    session_number=round_number_row["session"]
    if round_number >1:
        firm_id=round_number_row["firm_id"]
        wage_offered=round_number_row["wage"]
        treatment=round_number_row["treatment"]
        previous_round=round_number-1
        surplus_recieved_row=control_data.loc[(control_data["round_number"]==previous_round) & (control_data["firm_id"]==firm_id) & (control_data["session"]==session_number),"firm_surplus"]
        if len(surplus_recieved_row)>0:
            surplus_recieved=surplus_recieved_row.item()
            wage_vs_surplus_before_list.append({"round_number":round_number, "firm_id":firm_id, "surplus_recieved":surplus_recieved, "wage_offered":wage_offered, "session":session_number, "treatment":treatment})
wage_vs_surplus_before_data=pd.DataFrame(wage_vs_surplus_before_list)

# Wage vs Surplus Recieved in Previous Round - Effort Before
wage_vs_surplus_before_list=[]
for row in range(len(treatment_data)):
    round_number_row=treatment_data.iloc[row]
    round_number=round_number_row["round_number"]
    session_number=round_number_row["session"]
    if round_number >1:
        firm_id=round_number_row["firm_id"]
        wage_offered=round_number_row["wage"]
        treatment=round_number_row["treatment"]
        previous_round=round_number-1
        surplus_recieved_row=treatment_data.loc[(treatment_data["round_number"]==previous_round) & (treatment_data["firm_id"]==firm_id) & (treatment_data["session"]==session_number),"firm_surplus"]
        if len(surplus_recieved_row)>0:
            surplus_recieved=surplus_recieved_row.item()
            wage_vs_surplus_before_list.append({"round_number":round_number, "firm_id":firm_id, "surplus_recieved":surplus_recieved, "wage_offered":wage_offered, "session":session_number, "treatment":treatment})
wage_vs_surplus_before_data=pd.DataFrame(wage_vs_surplus_before_list)

# Basic OLS with no fixed effects. Normalizing effort to be between 0 and 0.9 to avoid boundary issues and get true prosocial parameter
control_data["const"]=1
treatment_data["const"]=1
control_data["effort"]=control_data["effort"]-0.1
treatment_data["effort"]=treatment_data["effort"]-0.1

control_data["session_dummy"]=control_data["session"]
control_data=pd.get_dummies(control_data, columns=["session_dummy"])
control_data["worker_identification"]=control_data["session"].astype(str)+"_"+control_data["worker_id"].astype(str)
control_data["firm_identification"]=control_data["session"].astype(str)+"_"+control_data["firm_id"].astype(str)
control_data=control_data.set_index(["worker_identification","round_number"])
control_model=PanelOLS(control_data["effort"],control_data[["const","wage"]],entity_effects=False, drop_absorbed=True)
control_result=control_model.fit()
print("Basic OLS with no fixed effects, Effort After Data\n",control_result)

treatment_data["session_dummy"]=treatment_data["session"]
treatment_data=pd.get_dummies(treatment_data, columns=["session_dummy"])
treatment_data["worker_identification"]=treatment_data["session"].astype(str)+"_"+treatment_data["worker_id"].astype(str)
treatment_data["firm_identification"]=treatment_data["session"].astype(str)+"_"+treatment_data["firm_id"].astype(str)
treatment_data=treatment_data.set_index(["worker_identification","round_number"])
treatment_model=PanelOLS(treatment_data["effort"],treatment_data[["const","wage"]],entity_effects=False, drop_absorbed=True)
treatment_result=treatment_model.fit()
print("Basic OLS with no fixed effects, Effort Before Data\n",treatment_result)

z_stat=(control_result.params["wage"]-treatment_result.params["wage"])/(math.sqrt(control_result.std_errors["wage"]**2+(treatment_result.std_errors["wage"])**2))
p_value=1-norm.cdf(z_stat)
print("Z-stats Basic OLS with no fixed effects\n","z=",z_stat,", p=", p_value)
z_stat=(control_result.params["const"]-treatment_result.params["const"])/(math.sqrt(control_result.std_errors["const"]**2+(treatment_result.std_errors["const"])**2))
p_value=norm.cdf(z_stat)
print("Z-stats Basic OLS with no fixed effects CONST\n","z=",z_stat,", p=", p_value)

# Basic OLS with individual fixed effects
control_model=PanelOLS(control_data["effort"],control_data[["const","wage"]],entity_effects=True, drop_absorbed=True)
control_result=control_model.fit()
print("Basic OLS with individual fixed effects, Effort After Data\n",control_result)

treatment_model=PanelOLS(treatment_data["effort"],treatment_data[["const","wage"]],entity_effects=True, drop_absorbed=True)
treatment_result=treatment_model.fit()
print("Basic OLS with individual fixed effects, Effort Before Data\n",treatment_result)

z_stat=(control_result.params["wage"]-treatment_result.params["wage"])/(math.sqrt(control_result.std_errors["wage"]**2+(treatment_result.std_errors["wage"])**2))
p_value=1-norm.cdf(z_stat)
print("Z-stats Basic OLS with individual fixed effects\n","z=",z_stat,", p=", p_value)
z_stat=(control_result.params["const"]-treatment_result.params["const"])/(math.sqrt(control_result.std_errors["const"]**2+(treatment_result.std_errors["const"])**2))
p_value=norm.cdf(z_stat)
print("Z-stats Basic OLS with individual fixed effects CONST\n","z=",z_stat,", p=", p_value)

# Basic OLS with time fixed effects
control_model=PanelOLS(control_data["effort"],control_data[["const","wage"]],time_effects=True, drop_absorbed=True)
control_result=control_model.fit()
print("Basic OLS with period fixed effects, Effort After Data\n",control_result)

treatment_model=PanelOLS(treatment_data["effort"],treatment_data[["const","wage"]],time_effects=True, drop_absorbed=True)
treatment_result=treatment_model.fit()
print("Basic OLS with period fixed effects, Effort Before Data\n",treatment_result)

z_stat=(control_result.params["wage"]-treatment_result.params["wage"])/(math.sqrt(control_result.std_errors["wage"]**2+(treatment_result.std_errors["wage"])**2))
p_value=1-norm.cdf(z_stat)
print("Z-stats Basic OLS with time fixed effects\n","z=",z_stat,", p=", p_value)
z_stat=(control_result.params["const"]-treatment_result.params["const"])/(math.sqrt(control_result.std_errors["const"]**2+(treatment_result.std_errors["const"])**2))
p_value=norm.cdf(z_stat)
print("Z-stats Basic OLS with time fixed effects CONST\n","z=",z_stat,", p=", p_value)

# Basic OLS with individual and time fixed effects
control_model=PanelOLS(control_data["effort"],control_data[["const","wage"]],entity_effects=True, time_effects=True, drop_absorbed=True)
control_result=control_model.fit()
print("Basic OLS with individual and period fixed effects, Effort After Data\n",control_result)

treatment_model=PanelOLS(treatment_data["effort"],treatment_data[["const","wage"]],entity_effects=True, time_effects=True, drop_absorbed=True)
treatment_result=treatment_model.fit()
print("Basic OLS with individual and period fixed effects, Effort Before Data\n",treatment_result)

z_stat=(control_result.params["wage"]-treatment_result.params["wage"])/(math.sqrt(control_result.std_errors["wage"]**2+(treatment_result.std_errors["wage"])**2))
p_value=1-norm.cdf(z_stat)
print("Z-stats Basic OLS with individual and period fixed effects\n", "z=",z_stat,", p=", p_value)
z_stat=(control_result.params["const"]-treatment_result.params["const"])/(math.sqrt(control_result.std_errors["const"]**2+(treatment_result.std_errors["const"])**2))
p_value=norm.cdf(z_stat)
print("Z-stats Basic OLS with individual and period fixed effects CONST\n","z=",z_stat,", p=", p_value)

# Setting Up Simultaneous Regressions and also creating a csv file for R analysis
all_data["const"]=1
all_data["effort"]=all_data["effort"]-0.1
all_data["worker_identification"]=all_data["session"].astype(str)+"_"+all_data["worker_id"].astype(str)+all_data["treatment"].astype(str)
all_data["firm_identification"]=all_data["session"].astype(str)+"_"+all_data["firm_id"].astype(str)+all_data["treatment"].astype(str) 
all_data["total_surplus"]=all_data["worker_surplus"]+all_data["firm_surplus"]
all_data["worker_surplus_share"]=all_data["worker_surplus"]/all_data["total_surplus"]
all_data.to_csv("r_data.csv")
all_data=all_data.set_index(["worker_identification","round_number"])
all_data["EB_x_wage"]=all_data["treatment"]*all_data["wage"]


# Simultaneous Regression, no fixed effects
full_model=PanelOLS(all_data["effort"],all_data[["const","wage","EB_x_wage","treatment"]],entity_effects=False, time_effects=False, drop_absorbed=True)
full_result=full_model.fit()
print("Simultaneous OLS with no fixed effects\n", full_result)

# Simultaneous Regression, with period fixed effects
full_model=PanelOLS(all_data["effort"],all_data[["const","wage","EB_x_wage","treatment"]],entity_effects=False, time_effects=True, drop_absorbed=True)
full_result=full_model.fit()
print("Simultaneous OLS with period fixed effects\n", full_result)

# Simultaneous Regression, with period and individual fixed effects
full_model=PanelOLS(all_data["effort"],all_data[["const","wage","EB_x_wage","treatment"]],entity_effects=True, time_effects=True, drop_absorbed=True)
full_result=full_model.fit()
print("Simultaneous OLS with individual and period fixed effects\n", full_result)

# Simultaneous Regression, with period and session fixed effects
all_data=all_data.reset_index()
all_data["session_identification"]=all_data["session"].astype(str)+"_"+all_data["treatment"].astype(str)
all_data=all_data.set_index(["session_identification","round_number"])
full_model=PanelOLS(all_data["effort"],all_data[["const","wage","EB_x_wage","treatment"]],entity_effects=True, time_effects=True, drop_absorbed=True)
full_result=full_model.fit()
print("Simultaneous OLS with period and session fixed effects\n", full_result)
all_data=all_data.reset_index()
all_data=all_data.set_index(["worker_identification","round_number"])

# Simultaneous Regression, with individual fixed effects
full_model=PanelOLS(all_data["effort"],all_data[["const","wage","EB_x_wage","treatment"]],entity_effects=True, time_effects=False, drop_absorbed=True)
full_result=full_model.fit()
print("Simultaneous OLS with individual fixed effects\n", full_result)

control_data["total_surplus"]=control_data["worker_surplus"]+control_data["firm_surplus"]
treatment_data["total_surplus"]=treatment_data["worker_surplus"]+treatment_data["firm_surplus"]
control_data["worker_surplus_share"]=control_data["worker_surplus"]/control_data["total_surplus"]
treatment_data["worker_surplus_share"]=treatment_data["worker_surplus"]/treatment_data["total_surplus"]
control_averages=control_data.groupby("session").mean()
treatment_averages=treatment_data.groupby("session").mean()
effort_rank=ranksums(control_averages["effort"],treatment_averages["effort"], alternative="two-sided")
print("effort rank sum:", effort_rank)
wage_rank=ranksums(control_averages["wage"],treatment_averages["wage"], alternative="two-sided")
print("wage rank sum:",wage_rank)
worker_surplus_rank=ranksums(control_averages["worker_surplus"],treatment_averages["worker_surplus"], alternative="two-sided")
print("worker_surplus rank sum:",worker_surplus_rank)
firm_surplus_rank=ranksums(control_averages["firm_surplus"],treatment_averages["firm_surplus"], alternative="two-sided")
print("firm_surplus rank sum:",firm_surplus_rank)
total_surplus_rank=ranksums(control_averages["total_surplus"],treatment_averages["total_surplus"], alternative="two-sided")
print("total_surplus rank sum:",total_surplus_rank)
worker_surplus_share_rank=ranksums(control_averages["worker_surplus_share"],treatment_averages["worker_surplus_share"], alternative="two-sided")
print("worker_surplus_share rank sum:",worker_surplus_share_rank)

print("Medians of Efort",print(all_data.groupby("treatment")["effort"].median()))
print("Medians of Wages",print(all_data.groupby("treatment")["wage"].median()))
print("Medians of Worker_Surplus",print(all_data.groupby("treatment")["worker_surplus"].median()))
print("Medians of Firm_Surplus",print(all_data.groupby("treatment")["firm_surplus"].median()))
print("Medians of total_surplus",print(all_data.groupby("treatment")["total_surplus"].median()))
print("Medians of worker_surplus_share",print(all_data.groupby("treatment")["worker_surplus_share"].median()))
print("Percent accepting highest offer",print(all_data.groupby("treatment")["highest_offer_accepted_boolean"].mean()))



#Round 1 analysis
control_data=control_data.reset_index()
treatment_data=treatment_data.reset_index()
control_data_round1=control_data[control_data["round_number"]==1]
treatment_data_round1=treatment_data[treatment_data["round_number"]==1]
control_averages_round1=control_data_round1.groupby("session").mean()
treatment_averages_round1=treatment_data_round1.groupby("session").mean()
wage_rank_round1=ranksums(control_averages_round1["wage"],treatment_averages_round1["wage"], alternative="two-sided")
print("wage rank sum ROUND 1:",wage_rank_round1)

round_12_wages_control=control_data[control_data["round_number"]==12]
round_12_wages_treatment=treatment_data[treatment_data["round_number"]==12]
round_12_wages_control_avg=round_12_wages_control.groupby("session").mean()
round_12_wages_treatment_avg=round_12_wages_treatment.groupby("session").mean()
print("Round 12 Average Wages", round_12_wages_control_avg["wage"].mean(), round_12_wages_treatment_avg["wage"].mean())
wage_rank=ranksums(round_12_wages_control_avg["wage"],round_12_wages_treatment_avg["wage"], alternative="two-sided")
print("round 12 wage rank sum:",wage_rank)

#Payment Calculations
'''
def round_negative(value):
    if value < 0:
        return round(value)
    else:
        return value
'''

all_data=all_data.reset_index()
payment_worker_surplus=all_data.groupby("worker_identification").sum()["worker_surplus"]
#print("Minimum total surplus for a worker:",payment_worker_surplus.min())
# No bankrupt workers
payment_worker_surplus=payment_worker_surplus/25+7
num_subjects=payment_worker_surplus.size
payment_firm_surplus=all_data.groupby("firm_identification").sum()["firm_surplus"]
payment_firm_surplus=payment_firm_surplus/25+7
num_subjects=num_subjects+payment_firm_surplus.size
sum_firms=payment_firm_surplus.sum()
sum_workers=payment_worker_surplus.sum()
average_payment=(sum_workers+sum_firms)/num_subjects
#print(num_subjects) #To double check number of subjects is correct. Should be 140
print(average_payment)

#Calculate the average of initial wage offers in period 1 across treatments. 






