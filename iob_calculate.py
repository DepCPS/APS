from sys import argv
import numpy as np
import pandas as pd

insulin_list =[]

def iobCalcBilinear(treatment_insulin, minsAgo, dia=3.0): 

    default_dia = 3.0 # assumed duration of insulin activity, in hours
    peak = 75;        # assumed peak insulin activity, in minutes
    end = 180;        # assumed end of insulin activity, in minutes

    # Scale minsAgo by the ratio of the default dia / the user's dia 
    # so the calculations for activityContrib and iobContrib work for 
    # other dia values (while using the constants specified above)
    timeScalar = default_dia / dia; 
    scaled_minsAgo = timeScalar * minsAgo


    activityContrib = 0;  
    iobContrib = 0;       

    # Calc percent of insulin activity at peak, and slopes up to and down from peak
    # Based on area of triangle, because area under the insulin action "curve" must sum to 1
    # (length * height) / 2 = area of triangle (1), therefore height (activityPeak) = 2 / length (which in this case is dia, in minutes)
    # activityPeak scales based on user's dia even though peak and end remain fixed
    activityPeak = 2 / (dia * 60)  
    slopeUp = activityPeak / peak
    slopeDown = -1 * (activityPeak / (end - peak))

    if (scaled_minsAgo < peak) :

        # activityContrib = treatment_insulin * (slopeUp * scaled_minsAgo)

        x1 = (scaled_minsAgo / 5) + 1;  # scaled minutes since bolus, pre-peak; divided by 5 to work with coefficients estimated based on 5 minute increments
        iobContrib = treatment_insulin * ( (-0.001852*x1*x1) + (0.001852*x1) + 1.000000 )

    elif (scaled_minsAgo < end) :

        minsPastPeak = scaled_minsAgo - peak
        # activityContrib = treatment_insulin * (activityPeak + (slopeDown * minsPastPeak))

        x2 = ((scaled_minsAgo - peak) / 5);  # scaled minutes past peak; divided by 5 to work with coefficients estimated based on 5 minute increments
        iobContrib = treatment_insulin * ( (0.001323*x2*x2) + (-0.054233*x2) + 0.555560 )
    
    return(  iobContrib)

def cal_single_iob(treatment_insulin,dia=3):
    iob = 0
    insulin_list.append(treatment_insulin) #update the insulin list with the newest treatment_insulin
    time_scale = int(dia*60/5)

    if len(insulin_list) > time_scale:
        insulin_list.pop(0) #remove the oldest inslin history if length of linslin list is larger than time scale

    length = min(time_scale,len(insulin_list))

    # print(iob)
    
    return (iob)

# dia: no. of hours insulin active in body
def cal_iob_list(ratelist,dia=3):
    ioblist=[]
    time_scale = int(dia*60/5)

    for index in range(len(ratelist)):
        remain_ratelist= ratelist[max(0,index-time_scale+1):index+1]

        iob = 0
        minsAgo = 0 
        for i in range(len(remain_ratelist)):
            minsAgo += 5 #5 minutes a step
            iob += iobCalcBilinear(remain_ratelist[-1-i],minsAgo,dia)

        ioblist.append(iob)

    return ioblist

if __name__ == "__main__":
    # linst = [0.076575,0.021975,0.019775,0.018783333,0.018075,0.0175,0.016891667,0.016066667,0.014866667,0.013141667,0.011025,0.009008333,0.007583333,0.007225,0.008316667,0.0107,0.01345,0.015633333,0.016366667,0.014875,0.011241667,0.006725,0.002558333,0,0,0.002575,0.006733333,0.011208333,0.01485,0.016633333,0.016341667,0.014766667,0.012716667,0.010941667,0.010116667,0.01045,0.011475,0.01275,0.013858333,0.014441667,0.014391667,0.013991667,0.013516667,0.013216667,0.013358333,0.014216667,0.016058333,0.019183333,0.023875,0.024541667,0.016758333,0.0133,0.011016667,0.009683333,0.009108333,0.009058333,0.009325,0.009666667,0.00985,0.009666667,0.00915,0.008658333,0.008541667,0.009141667,0.010741667,0.013258333,0.016091667,0.018658333,0.020391667,0.020783333,0.0198,0.018016667,0.016008333,0.014308333,0.013425,0.013466667,0.014041667,0.014758333,0.015266667,0.015233333,0.0146,0.013641667,0.012633333,0.011833333,0.011483333,0.011691667,0.01235,0.013375,0.014683333,0.016191667,0.0178,0.019375,0.020775,0.021866667,0.022508333,0.022558333,0.021866667,0.020275,0.017633333,0.016633333,0.01995,0.022216667,0.024525,0.026808333,0.029025,0.031108333,0.032991667,0.034625,0.035925,0.036858333,0.0375,0.038058333,0.038775,0.039858333,0.041508333,0.043625,0.045775,0.047525,0.048441667,0.048158333,0.046675,0.0445,0.042133333,0.040058333,0.0387,0.03815,0.038041667,0.038025,0.03775,0.036916667,0.035458333,0.033616667,0.031625,0.029725,0.028133333,0.026941667,0.026125,0.025633333,0.02545,0.025541667,0.025833333,0.026175,0.026433333,0.026483333,0.026166667,0.025341667,0.023866667,0.021583333,0.018325,0.015525]
    # ioblist=cal_iob_list(linst)
    # print(ioblist)
    df = pd.read_csv('test_data.csv')

    insulin_rate = df['rate'].tolist()
    calculated_iob = cal_iob_list(insulin_rate)
    recorded_iob = df['IOB'].tolist()

    together = np.c_[recorded_iob, calculated_iob]

    np.set_printoptions(suppress=True)
    print(together)




# float(argv[1]),float(argv[2])