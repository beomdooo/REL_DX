from shiny import App, render, ui
from pathlib import Path

here = Path(__file__).parent

intro_page = ui.page_fluid(
    ui.tags.style("""
        .title {
            color: #059077;
            font-size: 26px;
            margin-bottom: 0;
            font-weight: 450;
        }
        body {
            background-color: #eaf8f9;
        }
        element.style {
            width: 100%;
            height: 80px; 
        }
        .banner {
        margin-top: 30px;
        position: relative;
        text-align: center;
        color: white;
        }
        .banner img {
        border-radius: 15px;
        width: 100%;
        height: 380px;
        }
        .banner-text {
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translate(-50%, -50%);
        }


        #click_button {
            background-color: #059077;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size:20px;
            transition: all 0.2s ease;
        }
        #click_button:hover{
            background-color: #024035;
            transform: translateY(2px);
        }
        .section-links {
        display: flex;
        justify-content: space-around;
        margin-top: 50px;
        }
        .section-link {
            border-radius: 15px;
            height: 180px;
            background-color: white;
            text-align: center;
            font-weight: bold;
            font-size: 22px;
            padding: 30px;
            margin: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .section-link img {
        width: 60px;
        height: auto;
    }

    """),
    ui.h1("Reliability Information System", class_="title"),
    ui.div(
        ui.output_image("intro_page"),
        ui.div(
            ui.h1(),
            ui.HTML("""
                    <button id = 'click_button' onclick="location.href='/main/'">
                            Click Here
                    </button>"""),
            class_="banner-text"
        ),
        class_="banner"
    ),
    ui.div(
        ui.div(
            ui.output_image("system",height='80px'),
            ui.p("신뢰성 시험 관제"),
            class_="section-link"
        ),
        ui.div(
            ui.output_image("predict",height='80px'),
            ui.p("신뢰성 분석/예측"),
            class_="section-link"
        ),
        ui.div(
            ui.output_image("brain",height='80px'),
            ui.p("신뢰성 설계 지원"),
            class_="section-link"
        ),
        class_="section-links",
    )
)

def intro_server(input, output, session):
    
    @render.image  
    def intro_page():
        img = {"src": here / "image" / "intro_page.png", "width": "100px"}  
        return img 
    
    @render.image  
    def system():
        img = {"src": here / "image" / "system.png", "width": "100px"}  
        return img 
    
    @render.image  
    def predict():
        img = {"src": here / "image" / "predict.png", "width": "100px"}  
        return img 
    
    @render.image  
    def brain():
        img = {"src": here / "image" / "brain.png", "width": "100px"}  
        return img 
    pass

app = App(intro_page, intro_server)
