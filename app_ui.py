import os
os.chdir('D:\pyproject\shiny')
from shiny import App, ui, render, Inputs, Outputs, Session, req, reactive
import pandas as pd
from faicons import icon_svg
from pathlib import Path
import time
import asyncio

import plotly.express as px
from shinywidgets import output_widget, render_widget
import seaborn as sns
import matplotlib.pyplot as plt



#*** render.함수의 값이랑, 불러오는 데이터의 이름이 달라야함 ***#


#VPDS 데이터
crt_path = os.getcwd()
model_list = pd.read_excel('DB/model_list_df.xlsx')

model_list['Start'] = model_list['Start'].str.slice(0,10)
model_list['End'] = model_list['End'].str.slice(0,10)
model_list['Start']=pd.to_datetime(model_list['Start'])
model_list['End']= pd.to_datetime(model_list['End'])
model_list['Start']=model_list['Start'].dt.strftime('%Y-%m-%d')
model_list['End']=model_list['End'].dt.strftime('%Y-%m-%d')

#신뢰성 시험데이터 총합
all_Rtest_data = pd.read_csv('DB/combined_model_test_R.csv')
all_Rtest_data.reset_index(inplace=True)
#신뢰성 시험 상세 데이터 총합
all_R_Detail_data = pd.read_csv('DB/combined_Rmerged_all.csv')
all_R_Detail_data.reset_index(inplace = True)

#cssfile 불러오기
css_file = Path(__file__).parent / "sub_file" / "styles.css"

##### <1> 시험관리 #####
### page1) 플랫폼 홈
page1 =  ui.page_fixed(

    ui.card(
        ui.card_header('시험상황'),
        ui.layout_column_wrap(
            ui.value_box(
                "NG",
                ui.input_action_link("ng", int(model_list.value_counts(['Status'])['NG'])),     
                showcase = icon_svg('circle-xmark'),
                showcase_layout="left center"
                
            ),
            ui.value_box(
                "OK",
                ui.input_action_link("ok", int(model_list.value_counts(['Status'])['OK'])),
                showcase= icon_svg('check')
            ),
            ui.value_box(
                "Test",
                ui.input_action_link("test", int(model_list.value_counts(['Status'])['Test'])),
                showcase= icon_svg('rotate-right'),
            ),
            ui.value_box(
                "Reqeust",
                ui.input_action_link("rq", int(model_list.value_counts(['Status'])['Request'])),
                showcase=icon_svg('comment-dots')
                
            ),
            ui.value_box(
                "Plan",
                ui.input_action_link("plan", int(model_list.value_counts(['Status'])['Plan'])),
                showcase=icon_svg('pen-to-square')
            ),
            height =150
        )
    ),
    ui.layout_columns(
        ui.card(
            #output_widget('dvpv_plot'),
                
            ui.output_plot('dvpv_sns_plot')
        ),
        ui.card(
            ui.card_header('DV PV 카운트'),
            ui.output_table('pivot_table'),
        ),
        col_widths=(7,5),
    )
)


##### <2-1> 신뢰성 시험현황 tab_bar #####

### 2-1) Model_list
page2_1 = ui.page_fixed( 
                    
            ui.card(

                ui.row(

                        ui.input_select(    
                            id = 'select_company',
                            label = "본부", 
                            choices = ['HE','H&A','VS','BS','All'],
                            ),
                                  
                        ui.input_select(    
                            id = 'Grade',
                            label = "Grade", 
                            choices = {'All':'All','A':'A','B':'B','C':'C','D':'D'},
                            ),             
                        
                        ui.input_select(    
                            id = 'Event',
                            label = "Event", 
                            choices = {'All':'All','DV':'DV','PV':'PV'},
        
                            ),
                        
                        ui.input_select(    
                            id = 'select_reliability',
                            label = "신뢰성시험 유무", 
                            choices = ['All','Y','N'],
                    
                            ),  
                        ui.input_select(
                            id = 'Status',
                            label = 'Status',
                            choices = ['All', 'Test','Ok','NG' ,'Request','Plan']
                        ),
                        ui.input_date_range("start_date", "Start Date", start="2024-02-01",end="2024-12-30"),
                        ui.input_date_range("end_date", "End Date", start="2024-02-01", end="2024-12-30")
                        
                ),
                
                ui.output_data_frame(id = "test_status_df")
    )
)



# ui.output_data_frame(id = "test_status_df")
#'''
#            ui.card(
     #           ui.input_date_range("start", "Start Date", start="1960-01-01", width = '200px')  
    #            ),
   #         ui.card(
  #              ui.input_date_range("end", "End Date", start="1960-01-01", width = '200px')
 #'''


### 2-2) 시험정보
page2_2 =  ui.page_fillable(

        ui.layout_column_wrap(
            ui.card(
                ui.card_header(
                    "신뢰성 시험 현황",
                ),
                ui.output_data_frame(id = "test_depth_2"),
                full_screen=True
            ),
            ui.card(
                ui.card_header('시험 상세 현황'),

                ui.output_data_frame(id = 'test_depth_3'), #리액트데이터 불러오기
                
                full_screen=True
            )
        ),
    
        ui.row(
        ui.card(
            ui.output_data_frame(id='test_depth_4'),
            full_screen=True
        )
    ) 
)


###################################
#############레이아웃###############

#page2(신뢰성 시험 현황) tab <레이아웃>
page2= ui.page_navbar(  
        ui.nav_panel("Model List", page2_1),
        ui.nav_panel("시험정보", page2_2),
        ui.nav_menu(
            "Other links",
            ui.nav_panel("Sub", "Panel D content"),
            "----",
            "Description:",
            ui.nav_control(
                ui.a("LGSS", href="http://nlgss.lge.com/xmms/webroot/main.do?lang=ko", target="_blank")
            ),
        ),
        id="top_tab",        
    )

#page3, Risk Data
page3 = ui.page_fillable(
    ui.card(
        ui.HTML("""
    <head>
    <meta charset="utf-8">
    <style>
        table { 
            width: 100%; /* 테이블의 폭 */ 
            margin: 20px auto; /* 중앙 정렬 및 위아래 여백 */ 
            border-collapse: collapse; /* 격자 라인 합치기 */ } 
        th, td { 
            border: 1px solid #ddd; /* 테두리 스타일 */ 
            padding: 8px; /* 내부 여백 */ 
            text-align: center; /* 텍스트 중앙 정렬 */ } 
        thead { background-color: #f2f2f2; /* 헤더 배경색 */ } 
        tr:hover { background-color: #e8e8e8; /* 마우스 오버 시 배경색 */ } 
    </style>
    </head>
    <body>
        <table border="1" class='risk_table'><신뢰성 시험 리스크 현항
            <thead class='risk_head'>
                <tr><th rowspan="3">본부</th><th rowspan="3">사업부</th><th rowspan="3">사업담당</th><th colspan="2">점검모델</th><th colspan="5">이상징후(건)</th><th colspan="3">핵심리스크</th>
                </tr>
                <tr><th rowspan="2">개발완료</th><th rowspan="2">당월</th><th colspan="2">발생</th><th colspan="2">해소</th>
                    <th rowspan="2">잔여</th><th rowspan="2">발생</th><th rowspan="2">해소</th><th rowspan="2">잔여</th>
                </tr>
                <tr>
                    <th>누적</th><th>당월</th><th>누적</th><th>당월</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td rowspan="13">H&A</td><td rowspan="4">키친솔루션</td><td>냉장고</td><td>10</td><td>8</td><td>3</td><td style="background-color: #ffffcc;">-</td><td>3</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>2</td><td>2</td><td>0</td>
                </tr>
                <tr>
                    <td>워터케어</td></td><td>2</td><td>4</td><td>-</td><td style="background-color: #ffffcc;">-</td><td>-</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td>빌트인/쿠킹</td></td><td>5</td><td>6</td><td>6</td><td style="background-color: #ffffcc;">-</td><td>3</td><td style="background-color: #ffffcc;">-</td><td sytle="font-color: red;">3</td><td>2</td><td>0</td><td>2</td>
                </tr>
                <tr>
                    <td>식세기</td></td><td>2</td><td>-</td><td>-</td><td style="background-color: #ffffcc;">-</td><td>-</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td rowspan="4">리빙솔루션</td><td>세탁기</td></td><td>10</td><td>8</td><td>9</td><td style="background-color: #ffffcc;">-</td><td>7</td><td style="background-color: #ffffcc;">1</td><td sytle="color: red;">2</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td>건조기</td></td><td>2</td><td>1</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td>청소기</td></td><td>5</td><td>2</td><td>-</td><td style="background-color: #ffffcc;">-</td><td>-</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td>홈뷰티</td></td><td>-</td><td>1</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>-</td><td style="background-color: #ffffcc;">-</td><td sytle="color: red;">1</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td rowspan="3">에어솔루션</td><td>SAC</td></td><td>6</td><td>3</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td>RAC</td></td><td>2</td><td>2</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td>에어케어</td></td><td>1</td><td>2</td><td>2</td><td style="background-color: #ffffcc;">-</td><td>3</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td rowspan="2">부품솔루션</td><td>컴프</td></td><td>9</td><td>8</td><td>3</td><td style="background-color: #ffffcc;">-</td><td>3</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td>모터</td></td><td>4</td><td>3</td><td>-</td><td style="background-color: #ffffcc;">-</td><td>-</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td rowspan="2">HE</td><td colspan="2">TV</td></td><td>5</td><td>2</td><td>-</td><td style="background-color: #ffffcc;">-</td><td>-</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td colspan="2">오디오</td></td><td>5</td><td>3</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td rowspan="2">BS</td><td colspan="2">ID</td></td><td>7</td><td>1</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    ><td colspan="2">IT</td></td><td>11</td><td>5</td><td>3</td><td style="background-color: #ffffcc;">-</td><td>3</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>1</td><td>1</td><td>0</td>
                </tr>
                <tr>
                    <td rowspan="2">VS</td><td colspan="2">IVI</td></td><td>2</td><td>27</td><td>6</td><td style="background-color: #ffffcc;">-</td><td>6</td><td style="background-color: #ffffcc;">1</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
                <tr>
                    <td colspan="2">ADAS</td></td><td>1</td><td>1</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>1</td><td style="background-color: #ffffcc;">-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                </tr>
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="3">Total</td></td><td>89</td><td>87</td><td>39</td><td style="background-color: #ffffcc;">0</td><td>33</td><td style="background-color: #ffffcc;">2</td><td>6</td><td>5</td><td>3</td><td>2</td>
                </tr>
            </tfoot>
     </table>
     </body>""")
    )
)

#페이지 레이아웃
main_page = ui.page_fillable(
    ui.h1('Reliability Information System', class_='title'),
    ui.navset_pill_list( 
            ui.nav_panel("Test Manage", page1, icon = icon_svg('magnifying-glass')),
            ui.nav_panel("Test Status", page2, icon =icon_svg('table')),
            ui.nav_panel("Risk Status", page3, icon = icon_svg('trowel-bricks')),
            ui.nav_panel('Lifetime Prediction', ui.h1('Launching Soon...', class_='working'), icon=icon_svg('magnifying-glass-chart')),
            ui.nav_panel('Product Parts',ui.h1('Launching Soon...', class_='working'),icon=icon_svg('screwdriver-wrench')),
            ui.nav_panel('Field Parts',ui.h1('Launching Soon...', class_='working'),icon=icon_svg('users')),
            ui.nav_panel("Design Support", ui.h1('Launching Soon...', class_='working'),icon=icon_svg('compass-drafting')),
            ui.nav_panel("Failure Mechanism", ui.h1('Launching Soon...', class_='working'),icon=icon_svg('gears')),
            ui.nav_panel('Chat Bot', ui.h1('Launching Soon...', class_='working'),icon=icon_svg('robot')),
    

            well = False,
            widths=(2,10),
            

      
        ), 
    ui.include_css(css_file),
)

#-------------------------------------------------------------------------------
#################################
##########서버 함수###############
#################################

def server(input=Inputs, output=Outputs, session=Session):
    
    @reactive.effect
    @reactive.event(input.ng)
    def _():
        m = ui.modal(  
            ui.output_data_frame('ng_df'),
            title="NG",  
            easy_close=True,
            size = 'xl'  
        )  
        ui.modal_show(m)  
        
    #ng_table
    @render.data_frame
    def ng_df():
        ng_data = pd.read_excel('DB/test_status/ng_table.xlsx')
        return render.DataGrid(ng_data )
        
    @reactive.effect
    @reactive.event(input.ok)
    def _():
        m = ui.modal(  
            ui.output_data_frame('ok_df'),
            title="OK",  
            easy_close=True,
            size = 'l'  
        )  
        ui.modal_show(m) 

    #ok_table
    @render.data_frame
    def ok_df():
        ok_data = pd.read_excel('DB/test_status/ok_table.xlsx')
        return render.DataGrid(ok_data )
             
    @reactive.effect
    @reactive.event(input.test)
    def _():
        m = ui.modal(  
            ui.output_data_frame('test_df'),
            title="Test",  
            easy_close=True,
            size = 'l'  
        )  
        ui.modal_show(m)  
    #test_table
    @render.data_frame
    def test_df():
        test_data = pd.read_excel('DB/test_status/test_table.xlsx')
        return render.DataGrid(test_data )
             
             
    @reactive.effect
    @reactive.event(input.rq)
    def _():
        m = ui.modal(  
            ui.output_data_frame('request_df'),  
            title="Request",  
            easy_close=True,  
            size = 'l'
        )  
        ui.modal_show(m)  
    @render.data_frame
    def request_df():
        rq_data = pd.read_excel('DB/test_status/rq_table.xlsx')
        return render.DataGrid(rq_data )
                 
    @reactive.effect
    @reactive.event(input.plan)
    def _():
        m = ui.modal(  
            ui.output_data_frame('plan_df'),  
            title="Plan",  
            easy_close=True,  
            size = 'l'
        )  
        ui.modal_show(m)  
    @render.data_frame
    def plan_df():
        plan_data = pd.read_excel('DB/test_status/plan_table.xlsx')
        return render.DataGrid(plan_data)        
                
    #1 dv_pv 데이터 테이블 렌더링
    @render.data_frame  
    def dvpv_df():
        dv_pv =  pd.read_csv('DB/dv_pv.csv')
        return render.DataGrid(data = dv_pv )
        
    #1-2 dv_pv 그래프 (plotly)
    # @render_widget
    # def dvpv_plot():
    #     dv_pv =  pd.read_csv('DB/dv_pv.csv')
    #     barplot = px.bar(data_frame = dv_pv, x='year', y='count',color='dgrade', barmode = 'group',facet_col='event' )
    #     return barplot
    
    #1-2 dv_pv 그래프 (seaborn)
    @render.plot
    def dvpv_sns_plot():
        dv_pv =  pd.read_csv('DB/dv_pv.csv')
        ax = sns.catplot(x='year',y='count', hue = 'dgrade',col='event',data = dv_pv, kind='bar')
        
        ax.fig.suptitle('test counted by Grade')
        plt.tight_layout()
        return ax
    
    #1-3
    @render.table
    def pivot_table():
        df_pivot = pd.read_csv('DB/df_pivot.csv')
        return df_pivot
    
    #2-1 날짜 반응함수1
    @reactive.calc
    def date_out():
        return input.start_date()
    
    #2-1 날짜 반응함수2
    @reactive.calc
    def date_out2():
        return input.end_date()
    
    
    #2-1 모델별 시험현황 반응함수
    @reactive.calc
    def test_status_calc():
        
        df = model_list
        df['Start'] = pd.to_datetime(df['Start'])
        df['End'] = pd.to_datetime(df['End'])
        
        df = df[(df['Start']>=pd.Timestamp(date_out()[0])) &(df['Start']<=pd.Timestamp(date_out()[1]))]
        df = df[(df['End']>=pd.Timestamp(date_out2()[0])) &(df['End']<=pd.Timestamp(date_out2()[1]))]
        df['Start']=df['Start'].dt.strftime('%Y-%m-%d')
        df['End']=df['End'].dt.strftime('%Y-%m-%d')
        
        
        if input.select_reliability() == 'Y':
            df = df[df['신뢰성시험유무']=='Y']
        elif input.select_reliability() == 'N':
            df =df[df['신뢰성시험유무']=='N']
        else:
            pass
        
        if input.Status() == 'All':
            pass
        else:
            df = df[df['Status']==input.Status()]
            
        if input.Grade() == 'All':
            pass
        else:
            df = df[df['Grade'].str.startswith(input.Grade())]
            
        if input.Event() == 'All':
            pass
        else:
            df = df[df['Event'].str.contains(input.Event())]
        
        out = df.reset_index()
        
        return out
    
    #2-1 모델별 시험현황 데이터 테이블 렌더링
    @render.data_frame  
    def test_status_df():
        return render.DataGrid(data = test_status_calc(), width = '100%', row_selection_mode= 'single')
    
    #2-1 테이블 반응함수
    @reactive.calc
    def test_depth_2_filtering():
        test_status = test_status_calc()
        
        selected_idx = req(input.test_status_df_selected_rows())
        pk = test_status.iloc[selected_idx]['PK']  
        depth_2_table = all_Rtest_data[all_Rtest_data['Model_PK']==pk].drop(['index','PK'] , axis =1)
        return depth_2_table    
    
    #2-2-1 depth2 테이블
    @render.data_frame
    def test_depth_2():
        return render.DataGrid(data = test_depth_2_filtering().drop(['Model_PK'],axis = 1), width = '100%', row_selection_mode='single')
    

    #2-2-1 반응함수
    @reactive.calc
    def test_depth_3_filtering():
        df_depth_2 = test_depth_2_filtering()
        df_depth_3 = all_R_Detail_data
        
        selected_idx = req(input.test_depth_2_selected_rows()) # 인덱스 값 하나 반환
        pk = df_depth_2.iloc[selected_idx]['Model_PK'] #반환 type : int
        tc_id = df_depth_2.iloc[selected_idx]['TC_ID'] #반환 type : str
        
        df_depth_3 = df_depth_3[df_depth_3['Model_PK']==pk]
        depth_3_table = df_depth_3[df_depth_3['TC_ID'].str.contains(tc_id)]
        depth_3_table = depth_3_table.drop(['index', 'Assignee', 'Reporter'], axis =1 )
        return depth_3_table
    
    #2-2-2 depth3 테이블
    @render.data_frame
    def test_depth_3():
        return render.DataGrid(data = test_depth_3_filtering()[['TC_ID','Test_Item','Test_Case','Status','Summary','Comment']], width = '100%', row_selection_mode= 'single')
    
    
    #2-2-3 depth4 반응함수
    @reactive.calc
    def test_depth_4_filtering():
        df_depth_3 = test_depth_3_filtering()
        
        selected_idx= req(input.test_depth_3_selected_rows())
        
        tc_id = df_depth_3.iloc[selected_idx]['TC_ID']
        
        depth_4_table = df_depth_3[df_depth_3['TC_ID']==tc_id]
        return depth_4_table[['Test_Condition','Test_Spec','VPD_Evidence','Ref_Doc']]
    
    #2-2-3 depth4 테이블
    @render.data_frame
    def test_depth_4():
        return render.DataGrid(data = test_depth_4_filtering(), width = '100%',)
    
    
    #3 risk_data
    @render.table(index= True)
    def risk_df():
        risk_data = pd.read_csv('DB/risk_data.csv')
        return risk_data.fillna('')
    
    
#-------------------------------------------------------------------------------
    
app = App(main_page, server)

