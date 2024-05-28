from flask import Flask,render_template
import pandas as pd
import jieba.analyse
from translate import Translator
from geotext import GeoText
import math
from flask import Flask, send_from_directory  

from flask import Flask, request,session, render_template, redirect, url_for, flash
from flask_session import Session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
Session(app)

# MySQL配置
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Maoyurui20041023'
app.config['MYSQL_DB'] = 'personal'

mysql = MySQL(app)

@app.route('/')
def index():
    session['username'] = 'example'  
    return render_template('login.html')  # 包含登录和注册表单的 HTML 文件
  
@app.route('/register', methods=['POST','GET'])  
def register():  
    if request.method == 'POST':  
        # 从表单获取数据  
        name = request.form['username']  
        sex = request.form['sex']  
        year = request.form['year']  
        month = request.form['month']  
        day = request.form['day']  
        password = request.form['password']  # 原始密码  
        school = request.form['school']  
        news_preferences = request.form.getlist('news')  
  
        # 将数据插入到数据库  
        cursor = mysql.connection.cursor()  
        cursor.execute('''  
            INSERT INTO users (name, sex, birth_year, birth_month, birth_day, password, school, news_preferences)   
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)  
        ''', (name, sex, year, month, day, password, school, ','.join(news_preferences)))  
        mysql.connection.commit()  
        cursor.close()  
      
    # 如果不是POST请求，返回注册表单  
    return render_template('login.html')  

@app.route('/templates/login.html', methods=['POST','GET'])
def login():
    username = request.form.get('username')
    print(username)
    password = request.form.get('password')
    print(password)
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE name = %s', (username,))
        user = cursor.fetchone()
        cursor.execute('SELECT password FROM users WHERE name = %s', (username,))
        password2= cursor.fetchone()
        cursor.close()
        print(password2[0])
        
        if user and password==password2[0]:  # 假设password在第5个字段
            session['user'] = username
            flash('登录成功！', 'success')
            print('hi')
            return render_template('preference.html')
        else: 
            print("No")
            return render_template('login.html')
    else:
        print("not connected")
    return render_template('login.html')

@app.route('/templates/preference')
def preference():
    if 'user' in session:
        return render_template('preference.html')  # 确保在 templates 文件夹中有一个 preference.html 文件
    else:
        return redirect(url_for('/templates/index'))
    return render_template('preference.html')
  
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  
DATA_DIR = os.path.join(BASE_DIR, 'data/Political news')  
  
@app.route('/data/Political news/<filename>')  
def serve_file(filename):  
    return send_from_directory(DATA_DIR, filename, as_attachment=True)
  
@app.route('/templates/index.html')  
def menu():  
    return render_template('index.html')  

@app.route('/templates/preference.html')  
def pre():  
    with open('data\Political news\Sina_hot_news_list.csv', 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()
    tags=jieba.analyse.extract_tags(text,topK=30,withWeight=True)
    words=[item[0] for item in tags]
    times=[item[1] for item in tags]
    return render_template('preference.html',words=words,times=times)

@app.route('/templates/hotTopics.html')
def hot_topics():
    data=pd.read_csv("data\Political news\diff_hot_news_href.csv",skiprows=1,names=['标题','链接'])
    titles=data['标题'].values.tolist()
    urls=data['链接'].values.tolist()
    return render_template("hotTopics.html",titles=titles,urls=urls)

@app.route('/templates/economy.html') 
def economy():
    gladata=pd.read_csv("data\Financial news\glamour_stock.csv", skiprows=1,names=["股票", "价格",'涨跌幅'])
    glastocks=gladata['股票'].values.tolist()
    glaprice=gladata['价格'].values.tolist()
    glaadRate=gladata['涨跌幅'].values.tolist()

    golddata = pd.read_csv("data\Financial news\gold_price.csv", skiprows=1,names=["品牌", "产品", "价格"])
    gbrands = golddata["品牌"].values.tolist()
    gaddition = golddata["产品"].values.tolist()
    gprice = golddata["价格"].values.tolist()
    
    stodata=pd.read_csv("data\Financial news\stock_markets.csv",skiprows=1,names=['指数名称','最新价','涨跌额','涨跌幅','行情时间','股市'])
    stonames=stodata['指数名称'].values.tolist()
    stoprice=stodata['最新价'].values.tolist()
    stoadAmount=stodata['涨跌额'].values.tolist()
    stoadRate=stodata['涨跌幅'].values.tolist()
    stotime=stodata['行情时间'].values.tolist()
    for i in range(len(stoadRate)):  
        if isinstance(stoadRate[i], (int, float)) and stoadRate[i] != stoadRate[i]:  # 检查是否为NaN  
            stoadRate[i] = '0'  
        if isinstance(stoprice[i], (int, float)) and stoprice[i] != stoprice[i]:  # 检查是否为NaN  
            stoprice[i] = '0'  
        if isinstance(stoadAmount[i], (int, float)) and stoadAmount[i] != stoadAmount[i]:  # 检查是否为NaN  
            stoadAmount[i] = '0'
    print(stoadRate)

    data=pd.read_csv('data\Financial news\sector_gainers_list.csv',skiprows=1,names=['板块','涨跌幅','领涨股'])
    sectors=data['板块'].values.tolist()
    adRate=data['涨跌幅'].values.tolist()
    stocks=data['领涨股'].values.tolist()

    infdata=pd.read_csv('data\Financial news\sector_fund_flow.csv',skiprows=1,names=['板块名称','流入率','流入额'])
    infsectors=infdata['板块名称'].values.tolist()
    IFRate=infdata['流入率'].values.tolist()
    IFAmount=infdata['流入额'].values.tolist()

    overdata=pd.read_csv('data\Financial news\stock_market_overview.csv')
    overnames=overdata['股市'].values.tolist()
    overrise=overdata['上涨'].values.tolist()
    overflat=overdata['持平'].values.tolist()
    overfell=overdata['下跌'].values.tolist() 
    
    ddata=pd.read_csv('data\Financial news\sector_gainers_list.csv',skiprows=1,names=['板块','涨跌幅','领涨股'])
    dsectors=ddata['板块'].values.tolist()
    dadRate=ddata['涨跌幅'].values.tolist()
    dstocks=ddata['领涨股'].values.tolist()
    return render_template("economy.html",dsectors=dsectors,dadRate=dadRate,dstocks=dstocks,gprice=gprice,gbrands=gbrands,gaddition=gaddition,overnames=overnames,overrise=overrise,overflat=overflat,overfell=overfell,infsectors=infsectors,IFRate=IFRate,IFAmount=IFAmount,sectors=sectors,adRate=adRate,stocks=stocks,stonames=stonames,stoprice=stoprice,stoadAmount=stoadAmount,stoadRate=stoadRate,stotime=stotime,glastocks=glastocks,glaprice=glaprice,glaadRate=glaadRate)


@app.route('/templates/tech.html')
def tech():
    with open('data\Technology news\\tech_rolling_news_titles.csv', 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()
    tags=jieba.analyse.extract_tags(text,topK=30,withWeight=True)
    words=[item[0] for item in tags]
    times=[item[1] for item in tags]
    
    comdata=pd.read_csv('data\Technology news\\tech_hot_news_hiden_titles_comments.csv',skiprows=1,names=['标题','评论数'])
    comdata=pd.read_csv('data\Technology news\\tech_hot_news_hiden_titles_comments.csv',skiprows=1,names=['标题','评论数'])
    comtitles=comdata['标题'].values.tolist()
    comcomments=comdata['评论数'].values.tolist()
    
    itdata=pd.read_csv('data\Technology news\IT_listed_company.csv',skiprows=1,names=['名称','最新价','涨跌幅'])
    itname=itdata['名称'].values.tolist()
    itadRate=itdata['涨跌幅'].values.tolist()
    itprice=itdata['最新价'].values.tolist()
    
    Idata=pd.read_csv('data\Technology news\\tech_news_rank.csv',skiprows=1,names=['标题'])
    Ititles=Idata['标题'].values.tolist()
    
    cardata=pd.read_csv('data\Technology news\\auto_stocks.csv',skiprows=[0,11,22],names=['名称','最低价','涨跌幅'])
    companies=cardata['名称'].values.tolist()
    lowestPrice=cardata['最低价'].values.tolist()
    caradRate=cardata['涨跌幅'].values.tolist()
    print(companies)
    
    tpdata=pd.read_csv('data\Technology news\Chinese_concept_stock_market.csv',skiprows=1,names=['名称','最新价','涨跌幅'])
    TPstocks=tpdata['名称'].values.tolist()
    TPprice=tpdata['最新价'].values.tolist()
    TPrate=tpdata['涨跌幅'].values.tolist()
    
    tsdata=pd.read_csv('data\Technology news\Apple_iphone_ipad_watch_mac_titles.csv',skiprows=1,names=['标题','时间'])
    TStitles=tsdata['标题'].values.tolist()
    TStime=tsdata['时间'].values.tolist()
    
    return render_template("tech.html",TStitles=TStitles,TStime=TStime,TPstocks=TPstocks,TPprice=TPprice,TPrate=TPrate,companies=companies,lowestPrice=lowestPrice,caradRate=caradRate,Ititles=Ititles,itname=itname,itadRate=itadRate,itprice=itprice,itdata=itdata,comtitles=comtitles,comcomments=comcomments,words=words,times=times) 


@app.route('/templates/political.html')
def political():
    with open('data\Political news\international_news_titles.csv', 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()
    translator=Translator(from_lang="ZH",to_lang="EN-US")
    translation=translator.translate(text)
    countries=[]
    places=GeoText(translation)
    print(places)
    for place in places.countries:
        countries.append(place)
    # countries=['North Korea','Japan','Chile','China','United States']
    
    with open('data\Political news\Sina_hot_news_list.csv', 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()
    tags=jieba.analyse.extract_tags(text,topK=40,withWeight=True)
    words=[item[0] for item in tags]
    times=[item[1] for item in tags]
    print(words)
    
    data=pd.read_csv('data\Political news\\front_page_news_titles.csv')
    titles=data.values.tolist()
    urls=pd.read_csv('data\Political news\\front_page_news_href.csv',skiprows=1)
    lightUrl=urls.values.tolist()
    
    data=pd.read_csv('data\Political news\hot_news_hiden_titles_comments1.csv',skiprows=[0],names=['标题','评论数'])
    plComtitles=data['标题'].values.tolist()
    plComSum=data['评论数'].values.tolist()
    
    data=pd.read_csv('data\Political news\\test_cmt_content.csv',skiprows=[1,6,11,16,21],names=['标题','点赞数'])
    plReCom=data['标题'].values.tolist()
    plReSum=data['点赞数'].values.tolist()
    plReSum=[x for x in plReSum if not math.isnan(x)]
    
    data=pd.read_csv('data\Political news\Sina_hot_news_list.csv',names=['c','标题','关注度'])
    ptitles=data['标题'].values.tolist()
    pnum=data['关注度'].values.tolist()
    return render_template("political.html",ptitles=ptitles,pnum=pnum,plReCom=plReCom,plReSum=plReSum,plComtitles=plComtitles,plComSum=plComSum,titles=titles,lightUrl=lightUrl,words=words,times=times,countries=countries)

if __name__=='__main__':
    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'
    app.run(debug=True,port=5000)