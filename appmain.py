import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statistics import mean 

st.title("Streamlit For :blue[Wave] :blue[Analysis] ")

st.markdown("#### IMPORT DATA")
uploaded_file = st.file_uploader("Choose a CSV file")

# Ploting Graph Function.
def plotingLine_data(size, xaxis, yaxis , temp_label):
    fig = plt.figure(figsize=size) 
    plt.title(temp_label[0])   
    plt.xlabel(temp_label[1])   
    plt.ylabel(temp_label[2])
    plt.plot(xaxis, yaxis) 
    st.pyplot(fig)
    return

#Warnning to use this Fn.
def plotAverageLine(maenWave , start ,end):
    plt.plot([start, end], [maenWave, maenWave], color = 'orange', alpha=1.0)
    #st.pyplot()
    return


# Check import Data.
if uploaded_file is not None:
    column_names=['Time(ms)','Distance']
    #Get Dataframe frome CSV file and named it 
    df = pd.read_csv(uploaded_file, names=column_names )

    #Show Dataframe Table.
    st.dataframe(df, use_container_width = True )

    #Ploting graph 
    template = ['Wave-Analysis-Test01' , 'Time(ms)' , 'Distance(cm)']
    plotingLine_data(size=(15,5), xaxis = df['Time(ms)'], yaxis = df['Distance'] ,temp_label = template)


else:
    st.warning("you need to upload a csv or excel file")


#Insert Specific Data  
col1, col2= st.columns(2)
with col1:
    start_interval = st.number_input('Insert a START interval')

with col2:
    end_interval = st.number_input('Insert a END interval')

#Insert maen wave by yourself (0 == defult)
select_maen_fn = st.number_input('Insert a mean wave')
if uploaded_file is not None:
    st.write("Mean of Distance = " + str(round(mean(df['Distance']),3)) + " cm")
btn = st.button('Plotting Graph')   


#ReRange Dataframe scrop Fn.
def dataRange(dataframe ,start ,end):
    df_reRange = dataframe.loc[(dataframe['Time(ms)'] >= start ) & (dataframe['Time(ms)'] <= end) ]
    return df_reRange

#Find Cutting Point 
def cuttingMean(dataOrigin , dataReRange, meanWave):
    xtm_inMeanWave = []
    for item in dataReRange.index :
        first_time = dataOrigin['Time(ms)'][item]
        fisrt_d = dataOrigin['Distance'][item]
        Second_time = dataOrigin['Time(ms)'][item+1]
        Second_d = dataOrigin['Distance'][item+1]

        if (fisrt_d > meanWave) & (Second_d < meanWave) | (fisrt_d < meanWave) & (Second_d > meanWave) :
            ##Find slope with two point
            slope = (Second_d-fisrt_d)/(Second_time-first_time)
            ##sloving linnaer eqation
            x_eqa = (meanWave - fisrt_d + slope*first_time)/slope
            xtm_inMeanWave.append(x_eqa)
    return xtm_inMeanWave

def analysis_HL(dataOrigin, meanWave, cutpoint_1, cutpoint_2):
    rangetofind = dataOrigin.loc[(dataOrigin['Time(ms)'] >= cutpoint_1 ) & (dataOrigin['Time(ms)'] <= cutpoint_2)]
    mean_dis_interval = mean(rangetofind['Distance'])

    df_LHest = pd.DataFrame(columns=['State'])

    if ( mean_dis_interval > meanWave) :
        distance_max = rangetofind.max()
        time_and_distance_max = rangetofind.loc[(rangetofind['Distance'] == distance_max['Distance'] )]
        #Export dataframe
        df_LHest = df_LHest.append(time_and_distance_max, ignore_index = True)
        df_LHest['State'] = 'HIGHT'

    elif ( mean_dis_interval < meanWave) :   
        distance_min = rangetofind.min()
        time_and_distance_min = rangetofind.loc[(rangetofind['Distance'] == distance_min['Distance'] )]
        #Export dataframe
        df_LHest = df_LHest.append(time_and_distance_min, ignore_index = True)
        df_LHest['State'] = 'LOW'

    return df_LHest

def peak_point_Fn(cutting_list,dataOrigin,meanWave):
    dataframe_cutting_tm = pd.DataFrame(cutting_list, columns=['cutting_point_tm'])     #Change list cutting point to dataframe
    dataframe_peak_point = pd.DataFrame(columns=['State', 'Time(ms)', 'Distance'])     #crate df to storage dataframe
    
    for item in range(1,len(dataframe_cutting_tm)) :
        cr1 = dataframe_cutting_tm['cutting_point_tm'][item-1]
        cr2 = dataframe_cutting_tm['cutting_point_tm'][item]
        #peak_fn = analysis_HL(cr1, cr2)
        peak_fn = analysis_HL(dataOrigin = dataOrigin, meanWave= meanWave, cutpoint_1= cr1 , cutpoint_2= cr2)
        dataframe_peak_point = dataframe_peak_point.append(peak_fn, ignore_index = True)
    return dataframe_peak_point

def ExportTable(cuttLoc , PeakLoc):
    col_Export = ['State', 'TC1', 'TC2', 'TC3', 'PK1', 'PK2', 'PK3', 'H1', 'H2', 'H3', 'ABS_TC1-3', 'ABS_PK1-3', 'ABS_H1H3']
    table_Export = pd.DataFrame(columns=col_Export)
    for i in range(len(PeakLoc)-2) :
        TC1 = cuttLoc['CUTTING_Point'][i]
        TC2 = cuttLoc['CUTTING_Point'][i+1]
        TC3 = cuttLoc['CUTTING_Point'][i+2]
        PK1 = PeakLoc['Time(ms)'][i]
        PK2 = PeakLoc['Time(ms)'][i+1]
        PK3 = PeakLoc['Time(ms)'][i+2]
        H1  = PeakLoc['Distance'][i]
        H2  = PeakLoc['Distance'][i+1]
        H3  = PeakLoc['Distance'][i+2]
        State = PeakLoc['State'][i]
        ABS_TC = abs(TC3-TC1)
        ABS_PK = abs(PK3-PK1)
        ABS_H  = abs(H3-H1)

        temp = [State, TC1, TC2, TC3, PK1, PK2, PK3, H1, H2, H3, ABS_TC, ABS_PK, ABS_H]
        temp_df = pd.DataFrame(data=[temp], columns=col_Export)
        table_Export = table_Export.append([temp_df], ignore_index = True)

    return table_Export

def Table1_3(data):
    df_waveH_ordered = data['ABS_H1H3'].sort_values(ignore_index=bool,ascending=False)
    df_Tc_ordered = data['ABS_TC1-3'].sort_values(ignore_index=bool,ascending=False)
    df_Pk_ordered = data['ABS_PK1-3'].sort_values(ignore_index=bool,ascending=False)

    #datawaveH = data_Export.sort_values(by=['ABS_H1H3'], ascending=False)
    #table1, table2, table3 = st.tabs(["Wave Hight", "Period (Tc-Tc)", "Period (Pk-Pk)"])
    #with table1:
        #st.header("Wave Hight Ordered")
        #st.dataframe(df_waveH_ordered, use_container_width = True )
    
    #with table2:
        #st.header("Period (Tc-Tc) Ordered")
        #st.dataframe(df_Tc_ordered, use_container_width = True )

    #with table3:
        #st.header("Period (Pk-Pk) Ordered")
        #st.dataframe(df_Pk_ordered, use_container_width = True )
    

    graph1, graph2, graph3 = st.tabs(["Wave Hight", "Period (Tc-Tc)", "Period (Pk-Pk)"])
    with graph1:
        st.header("Wave Hight Ordered")
        st.dataframe(df_waveH_ordered, use_container_width = True )     #Dataframe 
        st.bar_chart(df_waveH_ordered , use_container_width=True , y='ABS_H1H3')       #graph plotting
        cont_wave = int(round((len(df_waveH_ordered)/3),0))
        maen_H = round( mean(df_waveH_ordered[0: cont_wave] ) ,3)
        #st.write(cont_wave)
        #st.write(maen_H)

    with graph2:
        st.header("Period (Tc-Tc) Ordered")
        st.dataframe(df_Tc_ordered, use_container_width = True )        #Dataframe
        st.bar_chart(df_Tc_ordered , use_container_width=True , y='ABS_TC1-3')          #graph plotting
        cont_Tc = int(round((len(df_Tc_ordered)/3),0))
        maen_Tc = round( mean(df_Tc_ordered[0: cont_Tc] ) ,3)
        #st.write(cont_Tc)
        #st.write(maen_Tc)

    with graph3:
        st.header("Period (Pk-Pk) Ordered")
        st.dataframe(df_Pk_ordered, use_container_width = True )        #Dataframe
        st.bar_chart(df_Pk_ordered , use_container_width=True, y='ABS_PK1-3')          #graph plotting
        cont_Pk = int(round((len(df_Pk_ordered)/3),0))
        maen_Pk = round( mean(df_Pk_ordered[0: cont_Pk] ) ,3)
        #st.write(cont_Pk)
        #st.write(maen_Pk)
    

    ###########PASS############
    #display value H1/3
    col1, col2, col3 = st.columns(3)
    col1.metric(label   = "H 1/3",  value=  str(maen_H) + " cm")
    col2.metric(label   = "Tc 1/3", value=  str(maen_Tc) + " ms")
    col3.metric(label   ="Tpk 1/3", value=  str(maen_Pk) + " ms")
    return

#Plotting Graph report.
def plotDetile(dataOrigin,exprotData,start,end,meanWave,temp_label):
    fig = plt.figure(figsize=(15,5))
    plt.title(temp_label[0], size=20)
    plt.xlabel(temp_label[1], size=15)
    plt.ylabel(temp_label[2], size=15 ,color = 'red')

    plt.plot(dataOrigin['Time(ms)'],dataOrigin['Distance'])       #WaveLine
    plt.plot([start,end], [meanWave,meanWave] ,color='green', alpha=1.0 ,linestyle='-.')        #averageWave Line
    plt.plot(exprotData['PK1'], exprotData['H1'] , color = 'orange', alpha=1.0, linestyle='--')        #PeakWave Line
    
    arr = np.linspace(1,1,len(exprotData['TC1']))
    wave_cut_point = arr * meanWave
    plt.scatter(exprotData['TC1'], wave_cut_point, color = 'red', alpha=1.0 , marker='x')      #scatter location of cutting point

    plt.legend(['Wave Line ','Mean Line ','Peak Line','Cutting Point'] ,loc='best')
    plt.grid()
    st.pyplot(fig)

    return

#Button activate to ploting (pressed)
if btn == True :
    lim_start = start_interval
    lim_end = end_interval

    #Check Data PASS
    df_reRange = dataRange(dataframe= df ,start= lim_start ,end= lim_end)
    #st.dataframe(df_reRange, use_container_width = True )

    #Insert Mean Wave condition.
    if select_maen_fn != 0 :
        meanDefult = select_maen_fn
        cutPoint = cuttingMean(dataOrigin= df, dataReRange= df_reRange, meanWave= meanDefult)

        cutPoint_df = pd.DataFrame(cutPoint,columns=['CUTTING_Point'])

        pk = peak_point_Fn(cutPoint,df_reRange,meanDefult)

        #Calculated Part ;Find length of Wave
        data_Export = ExportTable(cutPoint_df , pk)
        st.header('Report Data')
        st.dataframe(data_Export, use_container_width = True )
        ### TEST graph
        #plotDetile(dataOrigin=df_reRange, exprotData=data_Export, start=lim_start, end=lim_end, meanWave=meanDefult, temp_label=template)
        ### Table report.
        #Table1_3(data=data_Export)

    #( mean == 0 ) defult select mean from fn(). 
    elif select_maen_fn == 0 :
        meanDefult = mean(df_reRange['Distance'])
        cutPoint = cuttingMean(dataOrigin= df, dataReRange= df_reRange, meanWave= meanDefult)

        #st.write('Cutting_Point')
        cutPoint_df = pd.DataFrame(cutPoint,columns=['CUTTING_Point'])
        #st.dataframe(cutPoint_df, use_container_width = True )

        #need 1.cutting Point 2.Fn check Hight or Low
        pk = peak_point_Fn(cutPoint,df_reRange,meanDefult)
        #st.write('Peak Hight Low Point')
        #st.dataframe(pk, use_container_width = True )

        #Calculated Part ;Find length of Wave
        data_Export = ExportTable(cutPoint_df , pk)
        st.header('Report Data')
        st.dataframe(data_Export, use_container_width = True )

    
    ### TEST graph
    plotDetile(dataOrigin=df_reRange, exprotData=data_Export, start=lim_start, end=lim_end, meanWave=meanDefult, temp_label=template)
    ### Table report.
    Table1_3(data=data_Export)

    #Dowload CSV Report Data.
    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')
    
    csv = convert_df(data_Export)
    st.download_button(
        label="Download Report Data As CSV",
        data=csv,
        file_name='Report_Data_Wave_Analysis.csv',
        mime='text/csv',
    )







