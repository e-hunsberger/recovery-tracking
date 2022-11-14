import streamlit as st
import pandas as pd
import plotly.express as px 
import importlib
from datetime import date
import numpy as np


st.write("# Wellbeing Tracking")
st.markdown("## Introduction")
st.markdown("This app is a work-in-progress collaboration with my mom to help her long covid recovery journey. It seemed like high levels of extertion were tied to wellbeing setbacks and increases in fatigue. " +
"This app is designed to calculate limits in activity in order to reduce the chances that overexertion occurs. My mom selected the exertion categories of 'cleaning', 'gardening' and 'dogs'. " +
"Each day, time limits for each of these categores are recommended based on how she ranks how she is feeling, and how she has been feeling in the past few days. " +
"The goal is that she doesn't have to focus on deciding how much she can do, but instead enjoy doing the amount she knows she can do without inducing a setback.")

st.markdown("## User Inputs")
log_file = st.file_uploader("Upload file: (csv with headers 'Date', 'Rank', 'Cleaning', 'Gardening', 'Dogs')",accept_multiple_files=False)

#log_file = "C:\\Users\\ehuns\\OneDrive\\Documents\\Personal\\Mom\\recovery-tracking\\recovery-tracking\\health_progress_data.csv"

if st.checkbox("Continue"):
    data_df = pd.read_csv(log_file,dtype={"Cleaning":"float64","Rank":"float64"},parse_dates = ["Date"])

    rank = st.radio("Select ranking (10 = feeling great, 1 = feeling sh*t)", [1,2,3,4,5,6,7,8,9,10],0)
    note = st.text_input("Note to log with today (e.g. I did 3 hours of gardening today and still feel great!): ")


    #replace any commas in the string 
    note = note.replace(',', '.')

    #if RANK is 5 or more: 
    #only improve if current rank is not a decrease from the day before
    #and if previous dayS also had a rank above 5 (based on "days_before_increase" input)

    #update data
    days_before_increase = 5 #number of days with rank above 5 before time increase allowed
    #if fewer than days_before_increase have been logged, set days_before_increase to the length of the df
    if len(data_df) < days_before_increase:
        days_before_increase = len(data_df)
    
    bad_day = False #flag to see if there was a bad day within days_before_increase. 

    if rank > 4:
        #if current day is worse than previous day, no improvement allowed, but also no decrease 
        if rank < data_df.Rank.iloc[-1]:
            factor = 0
            bad_day = True
            print('here')
        #if current day is not worse than previous day, 
        else:
            for i in range(1,days_before_increase+1):
                if data_df.Rank.iloc[-i] > 4 and bad_day == False:
                    factor = 0.05 #factor for improvement       
                else:
                    factor = 0 #no improvement if there is a day in "days_before_increase" where rank was below 5
                    bad_day = True
                
        #if rank is 5 or more and no bad days within "days_before_increase", new time will be previous time plus previous_time*factor*rank/10
        #eg if rank = 10, previous_time + previous_time*(factor)
        #eg if rank = 5, previous_time + previous_time*0.5*(factor) 
        cleaning_time_calc = data_df.Cleaning.iloc[-1]+data_df.Cleaning.iloc[-1]*factor*rank/10
        gardening_time_calc = data_df.Gardening.iloc[-1]+data_df.Gardening.iloc[-1]*factor*rank/10
        dog_time_calc = data_df.Dogs.iloc[-1]+data_df.Dogs.iloc[-1]*factor*rank/10
        data_update = [date.today().strftime("%m/%d/%Y"),rank,cleaning_time_calc,gardening_time_calc,dog_time_calc,note]

    #if today's RANK is less than five, time decrease will be applied 
    else:
        factor = 0.5 #factor for limiting
        #if rank is less than 5, new time will be previous time - ()
        cleaning_time_calc = data_df.Cleaning.iloc[-1]+data_df.Cleaning.iloc[-1]*factor*(rank-5)/10
        gardening_time_calc = data_df.Gardening.iloc[-1]+data_df.Gardening.iloc[-1]*factor*(rank-5)/10
        dog_time_calc = data_df.Dogs.iloc[-1]+data_df.Dogs.iloc[-1]*factor*(rank-5)/10
        data_update = [date.today().strftime("%m/%d/%Y"),rank,cleaning_time_calc,gardening_time_calc,dog_time_calc,note]

    #state suggested time limits
    st.markdown("## Calculated time limit suggestions:")
    st.markdown("Cleaning: " + str(int(cleaning_time_calc)) + " minutes" )
    st.markdown("Gardening: " + str(int(gardening_time_calc)) + " minutes" )
    st.markdown("Dogs: " + str(int(dog_time_calc)) + " minutes" )

    #replace blank notes with 'none' for plotly label
    data_df.Note.fillna('none',inplace=True)

    st.markdown("## Plots")
    fig = px.line(data_df,x= "Date",y = "Rank",markers=True,custom_data=['Note'],
        title = "Rank over time")

    hovertemp = ' '.join(["<br> <b>Rank: </b> %{y} </br>",
                    "<b>Note: </b> %{customdata[0]} </br>",
                    "<b>Date:</b> %{x} "])
    fig.update_traces( hovertemplate=hovertemp)

    st.plotly_chart(fig)

    df = pd.melt(data_df,id_vars='Date', value_vars=['Cleaning','Gardening','Dogs'], value_name='Time')


    fig = px.line(df,x= "Date",y = "Time",markers=True,color = 'variable',
        title = "Suggested time limits over time")


    st.plotly_chart(fig)
    reset_checkbox = st.checkbox('Reset a time limit:',value = False)
    if reset_checkbox:
        category = st.radio('Category to reset: ' , ["Cleaning","Gardening","Dogs"])
        category_time = st.number_input("Number of minutes for " + category + ": ",0)


    #re-save the csv file if the user selects the checkbox 
    # if st.checkbox('Save results to file',value = False):
    submit_bool =  st.button('Submit')
    if submit_bool:
        data_df.loc[len(data_df.index)] = data_update
        if reset_checkbox:      
            data_df[category].iloc[-1] = category_time
            st.markdown('New time limit submitted')

        #data_df.to_csv(log_file, sep=',',index=False)
        #data_df.Date = data_df.Date.dt.strftime("%m/%d/%Y")
        st.dataframe(data_df)

        st.download_button("Download new csv", data_df.to_csv(index=False), file_name="health_progress_data.csv")

    st.markdown("DISCLAIMER: this app has had no input from medical professionals. The time limit calculations have been done by trial and error in collaboration with my mother. " +
    "I assume no liability for loss or damage resulting from anyone's reliance on the information.")
